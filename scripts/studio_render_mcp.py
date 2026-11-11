#!/usr/bin/env python3
"""PHOTON / GEOMETOR Studio Render MCP Server (`studio-render`).

Exposes host-level rendering tools (WebGL headless Chromium capture, Blender 5.3
EEVEE rendering, FreeCAD headless runner, FFmpeg 2560x1440 QHD encoding, and
Media Vault `/home/phi/MEDIA` inspection) over the Model Context Protocol (MCP)
Stdio transport so AI agents can trigger renders outside the terminal sandbox
without manual approval prompts.

Registered in:
  - `/home/phi/.gemini/antigravity/mcp_config.json`
  - `/home/phi/.gemini/config/mcp_config.json`
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

SERVER_NAME = "studio-render"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"

TOOLS: list[dict[str, Any]] = [
    {
        "name": "run_render_script",
        "description": (
            "Execute a Python, Blender, FreeCAD, or shell rendering script directly on the host "
            "outside the sandbox with full GPU (/dev/dri) and PHOTON Media Vault (/home/phi/MEDIA) access."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "script_path": {
                    "type": "string",
                    "description": "Absolute path to the Python (.py) or shell (.sh) render script.",
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional command-line arguments to pass to the script.",
                },
                "cwd": {
                    "type": "string",
                    "description": "Optional working directory (defaults to the script's parent directory).",
                },
                "use_uv_numpy": {
                    "type": "boolean",
                    "description": "If true (default for .py), runs via `uv run --offline --with numpy python3`.",
                },
                "background": {
                    "type": "boolean",
                    "description": "If true, launches the script detached in the background and logs output to log_path.",
                },
                "log_path": {
                    "type": "string",
                    "description": "Optional log file path when background=true.",
                },
            },
            "required": ["script_path"],
        },
    },
    {
        "name": "capture_gor9_webgl",
        "description": (
            "Capture and encode a 30.00 fps 2560x1440 QHD WebGL video from GOR-9 `docs/tower-3d.html` "
            "('cold_open', 'drone_tour', 'satellite_orbit', or 'all') directly on the host."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "enum": ["cold_open", "drone_tour", "satellite_orbit", "tours_both", "all"],
                    "description": "Which GOR-9 WebGL sequence to capture and encode in 2560x1440 QHD.",
                },
                "workers": {
                    "type": "integer",
                    "description": "Number of parallel headless Chromium render workers (default: 4).",
                },
            },
            "required": ["target"],
        },
    },
    {
        "name": "record_model_sequence",
        "description": (
            "Record any 3D WebGL HTML model (e.g., `docs/tower-3d.html`, `docs/dilithium-reactor-3d.html`, "
            "`docs/dilithium-pellets-3d.html`) along a declarative `camera_path.json` sequence in native "
            "2560x1440 QHD (30.00 fps CFR) with automatic tear auditing and repair."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "model_html": {
                    "type": "string",
                    "description": "Path to the 3D HTML model file (optional if specified in camera_path.json).",
                },
                "camera_path": {
                    "type": "string",
                    "description": "Path to the camera_path.json file or video project folder.",
                },
                "workers": {
                    "type": "integer",
                    "description": "Number of parallel headless Chromium render workers (default: 2).",
                },
                "clean": {
                    "type": "boolean",
                    "description": "If true, clean existing frames before rendering.",
                },
                "test_frames": {
                    "type": "boolean",
                    "description": "If true, render only diagnostic test_frames defined in camera_path.json.",
                },
            },
            "required": ["camera_path"],
        },
    },
    {
        "name": "probe_media",
        "description": (
            "Run ffprobe on any media file (including symlinked /home/phi/MEDIA vault files) "
            "and return codec, resolution, frame count, duration, and color space metadata."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "media_path": {
                    "type": "string",
                    "description": "Absolute path to the .mp4, .mov, or .wav file.",
                }
            },
            "required": ["media_path"],
        },
    },
]


def _run_cmd(cmd: list[str], cwd: str | None = None, timeout: int = 160) -> dict[str, Any]:
    import tempfile

    env = os.environ.copy()
    env["PAGER"] = "cat"
    # Write stdout/stderr to a temporary file rather than a pipe so grandchild processes
    # (like Chromium's crashpad_handler) cannot hold the pipe open after the main script exits.
    with tempfile.TemporaryFile(mode="w+b") as tmp_out:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=tmp_out,
            stderr=subprocess.STDOUT,
            close_fds=True,
            start_new_session=True,
        )
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            tmp_out.seek(0)
            partial = tmp_out.read().decode("utf-8", errors="replace")
            return {
                "returncode": -1,
                "output": (
                    f"[Still running in background (PID {proc.pid}) after {timeout}s]\n"
                    + partial.strip()[-10000:]
                ),
            }
        tmp_out.seek(0)
        out = tmp_out.read().decode("utf-8", errors="replace")
        return {
            "returncode": proc.returncode,
            "output": out.strip()[-12000:],
        }


def _handle_tool_call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    try:
        if name == "run_render_script":
            script_path = Path(arguments["script_path"]).resolve()
            if not script_path.exists():
                return {
                    "content": [{"type": "text", "text": f"Error: script not found: {script_path}"}],
                    "isError": True,
                }
            extra_args = [str(a) for a in arguments.get("args", [])]
            cwd = arguments.get("cwd") or str(script_path.parent.parent)
            use_uv_numpy = arguments.get("use_uv_numpy", True)
            background = bool(arguments.get("background", False))
            log_path = arguments.get("log_path")

            if script_path.suffix == ".sh":
                cmd = ["/bin/bash", str(script_path), *extra_args]
            elif use_uv_numpy:
                cmd = [
                    "/home/phi/.local/bin/uv",
                    "run",
                    "--offline",
                    "--with",
                    "numpy",
                    "python3",
                    str(script_path),
                    *extra_args,
                ]
            else:
                cmd = ["/home/phi/.local/bin/python3", str(script_path), *extra_args]

            if background:
                out_log = Path(log_path) if log_path else Path("/tmp/studio_render_bg.log")
                out_log.parent.mkdir(parents=True, exist_ok=True)
                env = os.environ.copy()
                env["PAGER"] = "cat"
                f_out = open(out_log, "w", encoding="utf-8")
                proc = subprocess.Popen(
                    cmd,
                    cwd=cwd,
                    env=env,
                    stdin=subprocess.DEVNULL,
                    stdout=f_out,
                    stderr=subprocess.STDOUT,
                    close_fds=True,
                    start_new_session=True,
                )
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Launched background render PID {proc.pid} -> log: {out_log}",
                        }
                    ],
                    "isError": False,
                }

            res = _run_cmd(cmd, cwd=cwd)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Exit code: {res['returncode']}\n{res['output']}",
                    }
                ],
                "isError": res["returncode"] != 0 and res["returncode"] != -1,
            }

        if name == "capture_gor9_webgl":
            target = arguments["target"]
            workers = int(arguments.get("workers", 4))
            gor9_root = Path("/home/phi/Sessions/GOR-9")
            outputs: list[str] = []

            if target in ("cold_open", "all"):
                cmd = [
                    "/home/phi/.local/bin/uv",
                    "run",
                    "--offline",
                    "--with",
                    "numpy",
                    "python3",
                    str(gor9_root / "scripts" / "capture_tower3d_cold_open.py"),
                    "--workers",
                    str(workers),
                ]
                res = _run_cmd(cmd, cwd=str(gor9_root))
                outputs.append(f"[cold_open exit={res['returncode']}]\n{res['output']}")

            if target in ("drone_tour", "satellite_orbit", "tours_both", "all"):
                cmd = [
                    "/home/phi/.local/bin/uv",
                    "run",
                    "--offline",
                    "--with",
                    "numpy",
                    "python3",
                    str(gor9_root / "scripts" / "capture_tours_webgl.py"),
                    "--workers",
                    str(workers),
                ]
                if target in ("drone_tour", "satellite_orbit"):
                    cmd.extend(["--only", target])
                res = _run_cmd(cmd, cwd=str(gor9_root))
                outputs.append(f"[{target} exit={res['returncode']}]\n{res['output']}")

            return {
                "content": [{"type": "text", "text": "\n\n".join(outputs)}],
                "isError": False,
            }

        if name == "record_model_sequence":
            gor9_root = Path("/home/phi/Sessions/GOR-9")
            cmd = [
                "/home/phi/.local/bin/uv",
                "run",
                "--offline",
                "--with",
                "numpy",
                "python3",
                str(gor9_root / "scripts" / "record_model_sequence.py"),
                "--path",
                str(arguments["camera_path"]),
                "--workers",
                str(int(arguments.get("workers", 2))),
            ]
            if arguments.get("model_html"):
                cmd.extend(["--model", str(arguments["model_html"])])
            if arguments.get("clean"):
                cmd.append("--clean")
            if arguments.get("test_frames"):
                cmd.append("--test-frames")
            res = _run_cmd(cmd, cwd=str(gor9_root), timeout=600)
            return {
                "content": [{"type": "text", "text": f"Exit code: {res['returncode']}\n{res['output']}"}],
                "isError": res["returncode"] != 0 and res["returncode"] != -1,
            }

        if name == "probe_media":
            media_path = str(Path(arguments["media_path"]).resolve())
            cmd = [
                "/usr/bin/ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=codec_name,profile,level,width,height,r_frame_rate,avg_frame_rate,nb_frames,duration,color_space",
                "-show_entries",
                "format=filename,duration,size,bit_rate",
                "-of",
                "default=noprint_wrappers=1",
                media_path,
            ]
            res = _run_cmd(cmd, timeout=30)
            return {
                "content": [{"type": "text", "text": res["output"]}],
                "isError": res["returncode"] != 0,
            }

        return {
            "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
            "isError": True,
        }
    except Exception as exc:
        return {
            "content": [{"type": "text", "text": f"Exception in {name}: {exc}"}],
            "isError": True,
        }


def _read_rpc_message() -> tuple[dict[str, Any] | None, bool]:
    """Read one JSON-RPC message from stdin. Supports both Content-Length framing and line-delimited JSON."""
    first_line = sys.stdin.buffer.readline()
    if not first_line:
        return None, False

    stripped = first_line.strip()
    if stripped.lower().startswith(b"content-length:"):
        content_length = int(stripped.split(b":", 1)[1].strip())
        while True:
            header_line = sys.stdin.buffer.readline()
            if not header_line or header_line in (b"\r\n", b"\n"):
                break
        body = sys.stdin.buffer.read(content_length)
        return json.loads(body.decode("utf-8")), True

    if not stripped:
        return _read_rpc_message()

    return json.loads(stripped.decode("utf-8")), False


def _write_rpc_message(payload: dict[str, Any], use_content_length: bool) -> None:
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    if use_content_length:
        header = f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii")
        sys.stdout.buffer.write(header + raw)
    else:
        sys.stdout.buffer.write(raw + b"\n")
    sys.stdout.buffer.flush()


def main() -> None:
    while True:
        msg, framed = _read_rpc_message()
        if msg is None:
            break

        method = msg.get("method")
        msg_id = msg.get("id")
        params = msg.get("params") or {}

        if method == "initialize":
            client_proto = params.get("protocolVersion", PROTOCOL_VERSION)
            resp = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": client_proto,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                },
            }
            _write_rpc_message(resp, framed)
        elif method in ("notifications/initialized", "initialized"):
            continue
        elif method == "ping":
            _write_rpc_message({"jsonrpc": "2.0", "id": msg_id, "result": {}}, framed)
        elif method == "tools/list":
            _write_rpc_message(
                {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}},
                framed,
            )
        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments") or {}
            result = _handle_tool_call(tool_name, tool_args)
            _write_rpc_message(
                {"jsonrpc": "2.0", "id": msg_id, "result": result},
                framed,
            )
        elif msg_id is not None:
            _write_rpc_message(
                {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                },
                framed,
            )


if __name__ == "__main__":
    main()
