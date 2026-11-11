#!/usr/bin/env python3
"""Upload a GOR-9 standalone video package (e.g. videos/mk4_demo) to YouTube (@GOR-9-station)
using photon_platform.studio.uploader, with a resilient multi-connection OAuth 2.0 loopback handler.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

STUDIO_SRC = Path("/home/phi/PROJECTS/photon-platform/studio/src")
if str(STUDIO_SRC) not in sys.path:
    sys.path.insert(0, str(STUDIO_SRC))

from photon_platform.studio.uploader import (  # noqa: E402
    SCOPES,
    _load_client_config,
    get_authenticated_channel,
    get_valid_access_token,
    main as uploader_main,
)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PKG = ROOT / "videos" / "mk4_demo"
CFG_DIR = Path.home() / ".config" / "geometor"
CLIENT_SECRET = CFG_DIR / "youtube_client_secret.json"
GOR9_TOKEN = CFG_DIR / "youtube_token_gor9.json"


def free_port_8085() -> None:
    """Kill any stale local process still holding port 8085 before starting a fresh OAuth flow."""
    my_pid = os.getpid()
    try:
        res = subprocess.run(
            ["fuser", "8085/tcp"],
            capture_output=True,
            text=True,
            check=False,
        )
        for tok in (res.stdout + " " + res.stderr).split():
            if tok.isdigit():
                pid = int(tok)
                if pid != my_pid:
                    print(f"Killing stale process {pid} on port 8085 ...", flush=True)
                    try:
                        os.kill(pid, signal.SIGTERM)
                    except Exception:
                        pass
        time.sleep(0.3)
    except Exception:
        pass


class _ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True


def resilient_oauth_flow(
    client_secret_path: Path = CLIENT_SECRET,
    token_path: Path = GOR9_TOKEN,
    port: int = 8085,
) -> dict:
    """Loopback OAuth 2.0 flow that ignores browser preconnects/favicons until `?code=` arrives."""
    free_port_8085()
    cfg = _load_client_config(client_secret_path)
    client_id = cfg["client_id"]
    client_secret = cfg["client_secret"]
    auth_uri = cfg.get("auth_uri", "https://accounts.google.com/o/oauth2/v2/auth")
    token_uri = cfg.get("token_uri", "https://oauth2.googleapis.com/token")
    redirect_uri = f"http://127.0.0.1:{port}"

    captured: dict[str, str] = {}

    class _CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            if "code" in qs:
                captured["code"] = qs["code"][0]
                body = (
                    "<html><body style='background:#05070b;color:#f59e0b;"
                    "font-family:monospace;padding:40px;'>"
                    "<h2>GOR-9 (@GOR-9-station) YouTube Authorization Complete</h2>"
                    "<p style='color:#e2e8f0;'>Token saved. Uploading Hauser MK-IV Demo now—you can close this tab.</p>"
                    "</body></html>"
                )
                self.send_response(200)
            elif "error" in qs:
                captured["error"] = qs["error"][0]
                body = f"<html><body>Authorization failed: {captured['error']}</body></html>"
                self.send_response(400)
            else:
                body = "<html><body>Waiting for OAuth code...</body></html>"
                self.send_response(204)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            if body:
                self.wfile.write(body.encode("utf-8"))

        def log_message(self, format, *args):  # noqa: A002
            return

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    consent_url = f"{auth_uri}?{urllib.parse.urlencode(params)}"
    print("\n======================================================================", flush=True)
    print("GOR-9 (@GOR-9-station) YOUTUBE OAUTH 2.0 AUTHORIZATION", flush=True)
    print("======================================================================", flush=True)
    print(f"\n   URL: {consent_url}\n", flush=True)

    server = _ReusableHTTPServer(("127.0.0.1", port), _CallbackHandler)
    server.timeout = 1.0
    try:
        env = os.environ.copy()
        env.setdefault("DISPLAY", ":0")
        env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
        env.setdefault("DBUS_SESSION_BUS_ADDRESS", f"unix:path=/run/user/{os.getuid()}/bus")
        subprocess.Popen(
            ["xdg-open", consent_url],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        try:
            webbrowser.open(consent_url)
        except Exception:
            pass

    print(f"Waiting for OAuth callback on {redirect_uri} ...", flush=True)
    t_start = time.monotonic()
    while "code" not in captured and "error" not in captured:
        if time.monotonic() - t_start > 7200:
            server.server_close()
            raise TimeoutError("Timed out after 7200s waiting for OAuth callback")
        try:
            server.handle_request()
        except Exception:
            continue
    server.server_close()

    if "error" in captured or "code" not in captured:
        raise RuntimeError(f"OAuth authorization failed: {captured.get('error', 'no code')}")

    form = urllib.parse.urlencode(
        {
            "code": captured["code"],
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        token_uri,
        data=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        token_data = json.loads(resp.read().decode("utf-8"))

    token_data["client_id"] = client_id
    token_data["client_secret"] = client_secret
    token_data["token_uri"] = token_uri
    token_data["expires_at"] = int(time.time()) + int(token_data.get("expires_in", 3600)) - 60

    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(json.dumps(token_data, indent=2) + "\n", encoding="utf-8")
    os.chmod(token_path, 0o600)
    print(f"Saved OAuth token to: {token_path}", flush=True)

    channel = get_authenticated_channel(token_data["access_token"])
    if channel:
        snippet = channel.get("snippet", {})
        print(
            f"Connected Channel   : {snippet.get('title')} "
            f"({snippet.get('customUrl', channel.get('id'))})",
            flush=True,
        )
    return token_data


def ensure_valid_gor9_token() -> Path:
    try:
        get_valid_access_token(CLIENT_SECRET, GOR9_TOKEN)
        return GOR9_TOKEN
    except Exception as e:
        print(f"OAuth token needs re-authorization ({e}); launching resilient OAuth flow...", flush=True)
        resilient_oauth_flow(CLIENT_SECRET, GOR9_TOKEN)
        return GOR9_TOKEN


def make_packages_public(token_path: Path, pkg_dirs: list[str]) -> None:
    """Set privacyStatus='public' ONLY for the specified video package directories."""
    access_token = get_valid_access_token(CLIENT_SECRET, token_path)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    pkg_paths = [Path(p).resolve() for p in pkg_dirs]
    video_ids: list[str] = []
    yt_files: list[Path] = []
    for pkg_path in pkg_paths:
        yt_file = pkg_path / "youtube.json"
        if not yt_file.exists():
            print(f"  [SKIP] No youtube.json found in {pkg_path}", flush=True)
            continue
        yt_files.append(yt_file)
        d = json.loads(yt_file.read_text(encoding="utf-8"))
        for up in (d.get("uploads") or {}).values():
            vid = up.get("video_id")
            if vid and vid not in video_ids:
                video_ids.append(vid)

    if not video_ids:
        print("No uploaded video IDs found in specified packages.", flush=True)
        return

    ids_param = ",".join(video_ids)
    v_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,status&id={urllib.parse.quote(ids_param)}"
    v_req = urllib.request.Request(v_url, headers=headers, method="GET")
    with urllib.request.urlopen(v_req, timeout=30) as resp:
        v_data = json.loads(resp.read().decode("utf-8"))

    for v_item in v_data.get("items", []):
        vid = v_item["id"]
        snippet = v_item.get("snippet", {})
        status = v_item.get("status", {})
        old_priv = status.get("privacyStatus", "unknown")
        title = snippet.get("title", vid)

        if old_priv == "public":
            print(f"  [ALREADY PUBLIC] {vid} | {title} -> https://youtu.be/{vid}", flush=True)
            continue

        update_payload = {
            "id": vid,
            "snippet": {
                "title": title,
                "description": snippet.get("description", ""),
                "categoryId": str(snippet.get("categoryId", "24")),
                "defaultLanguage": snippet.get("defaultLanguage", "en"),
                "defaultAudioLanguage": snippet.get("defaultAudioLanguage", "en"),
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }
        if snippet.get("tags"):
            update_payload["snippet"]["tags"] = snippet["tags"]

        put_req = urllib.request.Request(
            "https://www.googleapis.com/youtube/v3/videos?part=snippet,status",
            data=json.dumps(update_payload).encode("utf-8"),
            headers=headers,
            method="PUT",
        )
        with urllib.request.urlopen(put_req, timeout=30) as resp:
            resp.read()
        print(f"  [PUBLIC] {vid} ({old_priv} -> public) | {title} -> https://youtu.be/{vid}", flush=True)

    # Sync only the specified packages' youtube.json files to privacyStatus='public'
    for yt_file in yt_files:
        d = json.loads(yt_file.read_text(encoding="utf-8"))
        d["privacyStatus"] = "public"
        for up in (d.get("uploads") or {}).values():
            if isinstance(up, dict):
                up["privacyStatus"] = "public"
        yt_file.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    if "--spawn" in sys.argv[1:]:
        free_port_8085()
        log_path = ROOT / "videos" / "upload_batch.log"
        child_args = [a for a in sys.argv[1:] if a != "--spawn"]
        with open(log_path, "w", encoding="utf-8") as lf:
            proc = subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), *child_args],
                stdout=lf,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        time.sleep(1.5)
        print(f"Spawned uploader PID {proc.pid} -> {log_path}", flush=True)
        if log_path.exists():
            print(log_path.read_text(encoding="utf-8"), flush=True)
        return

    if "--make-public" in sys.argv[1:]:
        target_pkgs = [a for a in sys.argv[1:] if not a.startswith("-")]
        token_path = ensure_valid_gor9_token()
        make_packages_public(token_path, target_pkgs)
        return

    raw_args = [a for a in sys.argv[1:] if a != "--auth"]
    pkg_dirs: list[str] = []
    extra_flags: list[str] = []
    for a in raw_args:
        if a.startswith("-"):
            extra_flags.append(a)
        else:
            pkg_dirs.append(a)
    if not pkg_dirs:
        pkg_dirs = [str(DEFAULT_PKG)]

    token_path = ensure_valid_gor9_token()

    for pkg_dir in pkg_dirs:
        cli_argv = [
            str(Path(pkg_dir).resolve()),
            *extra_flags,
            "--token",
            str(token_path),
            "--target",
            "1080p",
            "--no-playlists",
        ]
        uploader_main(cli_argv)


if __name__ == "__main__":
    main()
