#!/usr/bin/env python3
"""Automated YouTube Data API v3 uploader for GOR-9 (@GOR-9-station).

Features:
- One-time OAuth 2.0 authorization & automatic token refresh for @GOR-9-station
  (stores token in ~/.config/geometor/youtube_token_gor9.json, separate from @geometor)
- Resumable 2560x1440 MP4 upload (renders/gor9_ep01_full_demo.mp4)
- Custom 16:9 thumbnail upload (renders/gor9_ep01_thumbnail_split.jpg, <2MB JPEG)
- Frame-accurate .srt closed-caption track upload (renders/gor9_ep01_full_demo.srt)
- Concise in-world description & chapter markers (no tags)
- Optional --update-banner to push the planet-free 2560x1440 channel banner via API
- Persistent tracking of uploaded video_id and URLs in renders/youtube.json
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parent.parent
EP_DIR = ROOT / "episodes" / "ep01_2736.305_parallelogram"
YT_DIR = EP_DIR / "youtube"

CONFIG_DIR = Path.home() / ".config" / "geometor"
DEFAULT_CLIENT_SECRET = CONFIG_DIR / "youtube_client_secret.json"
DEFAULT_TOKEN_PATH = CONFIG_DIR / "youtube_token_gor9.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def _load_client_config(client_secret_path: Path) -> dict:
    if not client_secret_path.exists():
        raise FileNotFoundError(
            f"OAuth client secret not found at: {client_secret_path}\n"
            "Save your Google Cloud Desktop OAuth client JSON there or pass --client-secret."
        )
    raw = json.loads(client_secret_path.read_text(encoding="utf-8"))
    cfg = raw.get("installed") or raw.get("web")
    if not cfg:
        raise ValueError(
            f"Invalid client_secret JSON in {client_secret_path}: expected 'installed' or 'web' key."
        )
    return cfg


def get_authenticated_channel(access_token: str) -> dict | None:
    url = "https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics,brandingSettings&mine=true"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("items", [])
            return items[0] if items else None
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"Warning: could not query channel info ({e.code}): {err_body}")
        return None


def run_oauth_flow(
    client_secret_path: Path,
    token_path: Path,
    port: int = 8086,
) -> dict:
    """Runs local loopback OAuth 2.0 flow for @GOR-9-station and saves refreshable token."""
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
                    "<html><body style='background:#05080f;color:#e8b85a;"
                    "font-family:monospace;padding:40px;'>"
                    "<h2>GOR-9 (@GOR-9-station) YouTube Authorization Complete</h2>"
                    "<p style='color:#38bdf8;'>14,285.7 kHz USB • Carrier Locked.</p>"
                    "<p style='color:#f4f1ea;'>You can close this tab and return to the terminal.</p>"
                    "</body></html>"
                )
                self.send_response(200)
            else:
                captured["error"] = qs.get("error", ["unknown_error"])[0]
                body = f"<html><body>Authorization failed: {captured['error']}</body></html>"
                self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
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
    print("\n======================================================================")
    print("GOR-9 • GALACTIC OUTPOST RADIO (@GOR-9-station) YOUTUBE OAUTH 2.0")
    print("======================================================================")
    print("1. Opening browser to authorize https://www.youtube.com/@GOR-9-station ...")
    print("   (When prompted, select your Google account and choose the @GOR-9-station channel)")
    print(f"\n   URL: {consent_url}\n")

    server = HTTPServer(("127.0.0.1", port), _CallbackHandler)
    try:
        webbrowser.open(consent_url)
    except Exception:
        pass

    print(f"Waiting for OAuth callback on {redirect_uri} ...")
    server.handle_request()
    server.server_close()

    if "error" in captured or "code" not in captured:
        raise RuntimeError(
            f"OAuth authorization failed: {captured.get('error', 'no code received')}"
        )

    form = urllib.parse.urlencode({
        "code": captured["code"],
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }).encode("utf-8")

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
    token_path.write_text(json.dumps(token_data, indent=2), encoding="utf-8")
    os.chmod(token_path, 0o600)
    print(f"Saved OAuth token to: {token_path}")

    channel = get_authenticated_channel(token_data["access_token"])
    if channel:
        snippet = channel.get("snippet", {})
        print(
            f"Connected Channel   : {snippet.get('title')} "
            f"({snippet.get('customUrl', channel.get('id'))})"
        )
    return token_data


def get_valid_access_token(
    client_secret_path: Path = DEFAULT_CLIENT_SECRET,
    token_path: Path = DEFAULT_TOKEN_PATH,
    auto_auth: bool = True,
) -> str:
    """Loads token_path (or runs OAuth if missing) and refreshes access_token if expired."""
    if not token_path.exists():
        if auto_auth:
            token_data = run_oauth_flow(client_secret_path, token_path)
            return token_data["access_token"]
        raise FileNotFoundError(
            f"YouTube OAuth token not found at {token_path}.\n"
            f"Run `python3 {Path(__file__).name} --auth` first."
        )
    token_data = json.loads(token_path.read_text(encoding="utf-8"))
    now = int(time.time())
    if token_data.get("access_token") and now < int(token_data.get("expires_at", 0)):
        return token_data["access_token"]

    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        if auto_auth:
            token_data = run_oauth_flow(client_secret_path, token_path)
            return token_data["access_token"]
        raise RuntimeError(f"Token in {token_path} has no refresh_token. Re-run with `--auth`.")

    client_id = token_data.get("client_id")
    client_secret = token_data.get("client_secret")
    token_uri = token_data.get("token_uri", "https://oauth2.googleapis.com/token")
    if not (client_id and client_secret):
        cfg = _load_client_config(client_secret_path)
        client_id = cfg["client_id"]
        client_secret = cfg["client_secret"]

    form = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode("utf-8")

    req = urllib.request.Request(
        token_uri,
        data=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        refreshed = json.loads(resp.read().decode("utf-8"))

    token_data["access_token"] = refreshed["access_token"]
    token_data["expires_at"] = int(time.time()) + int(refreshed.get("expires_in", 3600)) - 60
    if "refresh_token" in refreshed:
        token_data["refresh_token"] = refreshed["refresh_token"]

    token_path.write_text(json.dumps(token_data, indent=2), encoding="utf-8")
    os.chmod(token_path, 0o600)
    return token_data["access_token"]


def build_ep01_metadata() -> tuple[str, str]:
    """Build Episode 01 title and concise in-world description with chapter markers (no tags)."""
    timeline_path = EP_DIR / "script" / "ep01_timeline.json"
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    segs = {s["id"]: s for s in timeline["segments"]}

    def fmt_ch(sec: float) -> str:
        s = int(round(sec))
        return f"{s // 60}:{s % 60:02d}"

    s1 = segs["seg1_weather"]
    s2 = segs["seg2_econ"]
    s3 = segs["seg3_hauser"]
    sv3a, sv3b, sv3c = s3["sub_views"]
    s4 = segs["seg4_euclid"]
    s5 = segs["seg5_signoff"]
    s6 = segs.get("seg6_outro")

    chapters = [
        (0.0, "Cold Open • High Basalt Shelf Tower (14,285.7 kHz USB)"),
        (s1["start_sec"], "Space Weather • Relay KZ9-Omega & Marzelvane #4 Phase-Wobble"),
        (s2["start_sec"], "Outpost Economics • Quarry 44-K, Reactor #2 & Fermented Brine Tubers"),
        (sv3a["start_sec"], "Wideband Correlator • Titan-Minor Buoy N-24 (3,890 kHz)"),
        (sv3b["start_sec"], "Wideband Correlator • Callisto Dome-4 'Radio Corrugated' (11,410 kHz)"),
        (sv3c["start_sec"], "Wideband Correlator • Intergalactic M-33 Drift Buoy (1,420.4 MHz)"),
        (s4["start_sec"], "Euclid Signal Detector • The Unsuspecting Parallelogram (Book I, Prop. 34)"),
        (s5["start_sec"], "On the Next Broadcast & Sign-Off"),
    ]
    if s6:
        chapters.append((s6["start_sec"], "O.R.S. 351 Orbital Downlink & Station Credits (+3 kW / Marzelvane Upgrade)"))
    chapter_block = "\n".join(f"{fmt_ch(t)} {title}" for t, title in chapters)

    title = "GOR-9 • Galactic Outpost Radio: The Unsuspecting Parallelogram (14,285.7 kHz USB • 0400 GCT)"
    description = (
        "This is GOR-9. Galactic Outpost Radio, broadcasting at 50 kilowatts from the High Basalt Shelf "
        "on Asteroid 3-5-1 in Sector 9.\n"
        "14,285.7 kHz Upper Sideband • Epoch 2736.305 • 0400 Galactic Coordinated Time.\n\n"
        f"{chapter_block}\n\n"
        "Route physical QSL cards and SINPO reception reports via Titan Packet Buoy N-24, "
        "care of Galactic Outpost Radio, Asteroid 3-5-1, Sector 9.\n"
        "From Asteroid 3-5-1 in Sector 9, this is GOR-9—your eye to the cosmos, ear to the vacuum."
    )
    return title, description


def upload_video_resumable(
    access_token: str,
    mp4_path: Path,
    title: str,
    description: str,
    category_id: str = "24",  # 24 = Entertainment / Sci-Fi, or 28 = Science & Tech
    privacy_status: str = "public",
) -> str:
    """Uploads an MP4 via YouTube Data API v3 resumable upload protocol and returns video_id."""
    file_size = mp4_path.stat().st_size
    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": str(category_id),
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }
    body_bytes = json.dumps(metadata).encode("utf-8")

    init_url = (
        "https://www.googleapis.com/upload/youtube/v3/videos"
        "?uploadType=resumable&part=snippet,status"
    )
    init_req = urllib.request.Request(
        init_url,
        data=body_bytes,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Length": str(file_size),
            "X-Upload-Content-Type": "video/mp4",
        },
        method="POST",
    )
    with urllib.request.urlopen(init_req) as resp:
        upload_url = resp.headers.get("Location")

    if not upload_url:
        raise RuntimeError("YouTube resumable upload did not return a Location header.")

    print(f"  [upload] Streaming {mp4_path.name} ({file_size / (1024 * 1024):.2f} MB) ...")
    video_bytes = mp4_path.read_bytes()
    put_req = urllib.request.Request(
        upload_url,
        data=video_bytes,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Length": str(file_size),
            "Content-Type": "video/mp4",
        },
        method="PUT",
    )
    with urllib.request.urlopen(put_req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result["id"]


def update_video_metadata(
    access_token: str,
    video_id: str,
    title: str,
    description: str,
    category_id: str = "24",
    privacy_status: str = "public",
) -> None:
    metadata = {
        "id": video_id,
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": str(category_id),
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }
    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet,status"
    req = urllib.request.Request(
        url,
        data=json.dumps(metadata).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        method="PUT",
    )
    with urllib.request.urlopen(req) as resp:
        resp.read()


def upload_thumbnail(
    access_token: str,
    video_id: str,
    img_path: Path,
) -> bool:
    """Uploads a custom JPEG or PNG thumbnail (<2MB) for video_id."""
    if not img_path or not img_path.exists():
        return False
    img_bytes = img_path.read_bytes()
    mime = "image/jpeg" if img_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    url = (
        "https://www.googleapis.com/upload/youtube/v3/thumbnails/set"
        f"?videoId={urllib.parse.quote(video_id)}&uploadType=media"
    )
    req = urllib.request.Request(
        url,
        data=img_bytes,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": mime,
            "Content-Length": str(len(img_bytes)),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            resp.read()
        print(f"  [thumb]  Uploaded custom thumbnail: {img_path.name} ({len(img_bytes) // 1024} KB)")
        return True
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"  [!] Thumbnail upload warning for {video_id} ({e.code}): {err_body}")
        return False


def upload_captions_srt(
    access_token: str,
    video_id: str,
    srt_path: Path,
    language: str = "en",
    name: str = "English",
) -> str | None:
    """Uploads an .srt closed-caption track for video_id via multipart/related."""
    if not srt_path or not srt_path.exists():
        return None

    boundary = f"===============gor9_{int(time.time() * 1000)}=="
    snippet_json = json.dumps({
        "snippet": {
            "videoId": video_id,
            "language": language,
            "name": name,
            "isDraft": False,
        }
    }).encode("utf-8")
    srt_bytes = srt_path.read_bytes()

    parts = [
        f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode("utf-8"),
        snippet_json,
        f"\r\n--{boundary}\r\nContent-Type: application/x-subrip; charset=UTF-8\r\n\r\n".encode("utf-8"),
        srt_bytes,
        f"\r\n--{boundary}--\r\n".encode("utf-8"),
    ]
    body = b"".join(parts)

    url = (
        "https://www.googleapis.com/upload/youtube/v3/captions"
        "?uploadType=multipart&part=snippet"
    )
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": f'multipart/related; boundary="{boundary}"',
            "Content-Length": str(len(body)),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            cap_id = data.get("id")
            print(f"  [srt]    Uploaded English closed captions: {srt_path.name} (id={cap_id})")
            return cap_id
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"  [!] Captions upload warning for {video_id} ({e.code}): {err_body}")
        return None


def update_channel_banner(access_token: str, banner_path: Path) -> bool:
    """Uploads planet-free 2560x1440 banner via channelBanners.insert and sets it on the channel."""
    if not banner_path.exists():
        return False
    channel = get_authenticated_channel(access_token)
    if not channel:
        return False
    channel_id = channel["id"]
    branding = channel.get("brandingSettings", {})
    if "image" not in branding:
        branding["image"] = {}

    img_bytes = banner_path.read_bytes()
    insert_url = "https://www.googleapis.com/upload/youtube/v3/channelBanners/insert?uploadType=media"
    req = urllib.request.Request(
        insert_url,
        data=img_bytes,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "image/jpeg",
            "Content-Length": str(len(img_bytes)),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            banner_ext_url = res.get("url")
        if not banner_ext_url:
            return False
        branding["image"]["bannerExternalUrl"] = banner_ext_url
        update_payload = {
            "id": channel_id,
            "brandingSettings": branding,
        }
        up_req = urllib.request.Request(
            "https://www.googleapis.com/youtube/v3/channels?part=brandingSettings",
            data=json.dumps(update_payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=UTF-8",
            },
            method="PUT",
        )
        with urllib.request.urlopen(up_req) as resp:
            resp.read()
        print(f"  [banner] Updated channel banner to planet-free {banner_path.name}")
        return True
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"  [!] Channel banner update warning ({e.code}): {err_body}")
        return False


def list_recent_channel_videos(access_token: str) -> list[dict]:
    """Lists recent uploaded videos on the authenticated channel."""
    url = "https://www.googleapis.com/youtube/v3/search?part=snippet&forMine=true&type=video&maxResults=10"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("items", [])
    except urllib.error.HTTPError:
        return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated YouTube uploader for GOR-9 (@GOR-9-station)")
    parser.add_argument("--auth", action="store_true", help="Run OAuth 2.0 flow to connect @GOR-9-station")
    parser.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])
    parser.add_argument("--video-id", default=None, help="Existing video ID to update metadata/thumbnail/SRT")
    parser.add_argument("--update-banner", action="store_true", help="Also update the channel banner to the planet-free version")
    args = parser.parse_args()

    if args.auth:
        run_oauth_flow(DEFAULT_CLIENT_SECRET, DEFAULT_TOKEN_PATH)
        return

    access_token = get_valid_access_token(DEFAULT_CLIENT_SECRET, DEFAULT_TOKEN_PATH, auto_auth=True)
    channel = get_authenticated_channel(access_token)
    if not channel:
        raise RuntimeError("Could not verify authenticated YouTube channel.")

    snippet = channel.get("snippet", {})
    ch_title = snippet.get("title", "")
    ch_handle = snippet.get("customUrl", "")
    ch_id = channel.get("id", "")
    print(f"Authenticated YouTube Channel: {ch_title} ({ch_handle} • id={ch_id})")

    # Safety check: if connected to @geometor instead of @GOR-9-station, re-run OAuth for @GOR-9-station!
    if "geometor" in ch_handle.lower() and "gor" not in ch_handle.lower():
        print("Connected token belongs to @geometor; launching OAuth flow to select @GOR-9-station...")
        token_data = run_oauth_flow(DEFAULT_CLIENT_SECRET, DEFAULT_TOKEN_PATH)
        access_token = token_data["access_token"]
        channel = get_authenticated_channel(access_token)
        snippet = channel.get("snippet", {}) if channel else {}
        ch_title = snippet.get("title", "")
        ch_handle = snippet.get("customUrl", "")
        ch_id = channel.get("id", "") if channel else ""
        print(f"Switched to Channel: {ch_title} ({ch_handle} • id={ch_id})")

    if args.update_banner:
        banner_path = ROOT / "station" / "branding" / "gor9_youtube_banner_2560x1440.jpg"
        update_channel_banner(access_token, banner_path)

    title, description = build_ep01_metadata()
    mp4_path = EP_DIR / "gor9_ep01.mp4"
    thumb_path = YT_DIR / "gor9_ep01_thumbnail_split.jpg"
    srt_path = YT_DIR / "gor9_ep01.srt"

    if args.video_id:
        video_id = args.video_id
        print(f"Updating existing video {video_id} on {ch_handle}...")
        update_video_metadata(access_token, video_id, title, description, privacy_status=args.privacy)
    else:
        print(f"Uploading new 2560x1440 QHD Episode 01 to {ch_handle} ({args.privacy})...")
        video_id = upload_video_resumable(
            access_token,
            mp4_path,
            title=title,
            description=description,
            privacy_status=args.privacy,
        )
        print(f"  [video]  Uploaded video_id = {video_id} (https://www.youtube.com/watch?v={video_id})")

    thumb_ok = upload_thumbnail(access_token, video_id, thumb_path)
    caption_id = upload_captions_srt(access_token, video_id, srt_path)

    record = {
        "channel_title": ch_title,
        "channel_handle": ch_handle,
        "channel_id": ch_id,
        "episode": "EP01",
        "galactic_epoch": "2736.305",
        "title": title,
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "studio_url": f"https://studio.youtube.com/video/{video_id}/edit",
        "privacy_status": args.privacy,
        "thumbnail_uploaded": thumb_ok,
        "caption_id": caption_id,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    out_json = YT_DIR / "youtube.json"
    out_json.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"\nSaved upload manifest to: {out_json}")
    print(f"Watch URL : {record['url']}")
    print(f"Studio URL: {record['studio_url']}")


if __name__ == "__main__":
    main()
