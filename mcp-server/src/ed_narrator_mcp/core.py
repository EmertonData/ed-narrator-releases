"""Configuration and the safety guards: loopback-only URL, input allow-list, sanitised output names. No MCP or HTTP code here."""
from __future__ import annotations

import ipaddress
import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_URL = "http://127.0.0.1:8090"      # the Docker address; the desktop app picks its own local port (see docs/mcp.md)
FILM_EXTS = (".mp4", ".m4v", ".mov")       # same lists as backend/app/main.py
SCRIPT_EXTS = (".srt", ".md", ".markdown", ".txt")
MUSIC_EXTS = (".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac")
JOB_ID = re.compile(r"[0-9a-f]{8,64}")     # the app's ids are hex; anything else never reaches a URL path


class GuardError(ValueError):
    """A refusal with a message fit for the assistant and the user."""


@dataclass(frozen=True)
class Config:
    url: str
    output_dir: Path
    input_dirs: tuple[Path, ...]


def check_url(url: str, allow_remote: bool = False) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise GuardError(f"ED_NARRATOR_URL must look like http://127.0.0.1:8090 (got {url!r}).")
    if parts.username or parts.password:
        raise GuardError("ED_NARRATOR_URL must not contain credentials.")
    host = parts.hostname
    try:
        loopback = ipaddress.ip_address(host).is_loopback
    except ValueError:
        loopback = host.lower() == "localhost"
    if not loopback and not allow_remote:
        raise GuardError(f"Refusing {host}: ED Narrator has no login, so this server only talks to a loopback address. "
                         "Set ED_NARRATOR_ALLOW_REMOTE=1 only if you accept that anyone who can reach that address can use the app.")
    return f"{parts.scheme}://{parts.netloc}"


def too_broad(d: Path, home: Path) -> bool:
    return d == Path(d.anchor) or home == d or home.is_relative_to(d)


def load_config(env=os.environ, cwd: Path | None = None, home: Path | None = None) -> Config:
    home = (home or Path.home()).resolve()
    cwd = (cwd or Path.cwd()).resolve()
    url = check_url(env.get("ED_NARRATOR_URL") or DEFAULT_URL, env.get("ED_NARRATOR_ALLOW_REMOTE") == "1")
    out = Path(env.get("ED_NARRATOR_OUTPUT_DIR") or "ed-narrator-output").expanduser()
    raw = env.get("ED_NARRATOR_INPUT_DIRS")
    if raw:
        dirs = tuple(Path(p).expanduser().resolve() for p in raw.split(os.pathsep) if p.strip())
        for d in dirs:
            if too_broad(d, home):
                raise GuardError(f"ED_NARRATOR_INPUT_DIRS may not contain {d}: it is the filesystem root, your home folder or a parent of it. Use a dedicated folder such as ~/Movies.")
    else:
        # fail closed: a GUI client often starts us in "/" or in the home folder, which would expose ssh keys and the like
        dirs = () if too_broad(cwd, home) else (cwd,)
    return Config(url, (cwd / out).resolve(), dirs)


def safe_input(path: str, cfg: Config, exts: tuple[str, ...], what: str) -> Path:
    """Resolve symlinks and `..` first, then require the real path to sit inside an allowed folder."""
    if not cfg.input_dirs:
        raise GuardError("No input folder is allowed: the working directory is the filesystem root or your home folder, which is too broad. "
                         "Set ED_NARRATOR_INPUT_DIRS to the folder(s) that hold your films and scripts (not your home folder).")
    try:
        real = Path(path).expanduser().resolve(strict=True)
    except (OSError, RuntimeError):
        raise GuardError(f"The {what} file does not exist: {path}") from None
    root = next((d for d in cfg.input_dirs if real.is_relative_to(d)), None)
    if root is None:
        allowed = ", ".join(str(d) for d in cfg.input_dirs)
        raise GuardError(f"The {what} file is outside the folders this server may read ({allowed}). "
                         "Move it there or add its folder to ED_NARRATOR_INPUT_DIRS.")
    if any(part.startswith(".") for part in real.relative_to(root).parts):
        raise GuardError(f"The {what} path has a hidden (dot) folder or file name, which is never read.")
    if not real.is_file():
        raise GuardError(f"The {what} path is not a file: {path}")
    if real.suffix.lower() not in exts:
        raise GuardError(f"The {what} must be one of {', '.join(exts)} (got {real.suffix or 'no extension'}).")
    return real


def safe_job_id(job_id: str) -> str:
    if not JOB_ID.fullmatch(job_id or ""):
        raise GuardError("That is not a job id. Use the id returned by create_voiceover or list_jobs.")
    return job_id


def output_path(cfg: Config, job_id: str, name: str) -> Path:
    """`name` comes from a fixed table in server.py; the check is a second line of defence against traversal."""
    dest = (cfg.output_dir / f"{safe_job_id(job_id)[:8]}-{Path(name).name}").resolve()
    if dest.parent != cfg.output_dir:
        raise GuardError("Refusing to write outside ED_NARRATOR_OUTPUT_DIR.")
    return dest
