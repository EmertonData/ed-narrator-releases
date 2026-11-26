"""MCP server for a running ED Narrator. Talks to its /api only; never to /api/settings (the Azure key stays in the app). It may start installs
of catalog voices and engines through /api/models and /api/engines, with explicit confirm and licence flags."""
from __future__ import annotations

import argparse
import asyncio
import base64
import hmac
import logging
import os
import re
import shutil
import subprocess
import time
from contextlib import ExitStack
from pathlib import Path
from typing import Literal

import httpx
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.types import Icon
from mcp.server.transport_security import TransportSecuritySettings

from .core import FILM_EXTS, MUSIC_EXTS, SCRIPT_EXTS, Config, GuardError, load_config, output_path, safe_input, safe_job_id

DOWNLOADS = {"video": "voiced.mp4", "audio": "voiceover.mp3", "wav": "voiceover.wav", "script": "script.srt",
             "flac": "voiceover.flac", "video_hires": "voiced_hires_flac.mp4"}
DONE = ("done", "error", "cancelled")
INSTALL_HINT = ("Call list_installable, then install_voice_model (a Piper voice is small); or open ED Narrator > Models. "
                "Azure voices need a key added in the app's Settings.")
INSTRUCTIONS = ("Adds timed voice-over to a film through a running ED Narrator app. Typical order: check_status, list_voices, preview_script, "
                "create_voiceover, wait_for_job (repeat until finished), download_result. Files are read only from the allow-listed input folders.")


def _detail(r: httpx.Response) -> str:
    try:
        d = r.json().get("detail", "")
    except Exception:
        d = ""
    if isinstance(d, list):
        d = "; ".join(f"{'.'.join(str(x) for x in e.get('loc', [])[1:])}: {e.get('msg', '')}" for e in d if isinstance(e, dict))
    return str(d) or r.reason_phrase or f"HTTP {r.status_code}"


def _fail(r: httpx.Response) -> ToolError:
    d = _detail(r)
    if r.status_code == 503:
        d += f" {INSTALL_HINT}"
    elif r.status_code == 400 and "host" in d.lower():
        d += " Use ED_NARRATOR_URL with 127.0.0.1 or localhost."
    elif r.status_code == 403:
        d += " (the app refused a cross-site request; this server sends no Origin header, so check for a proxy in between)"
    return ToolError(f"ED Narrator answered {r.status_code}: {d}")


# 128 px logo shown next to the connector in Claude (self-contained data URI: works from uvx, the desktop bundle and HTTP alike)
ICON = Icon(src="data:image/png;base64," + base64.b64encode((Path(__file__).parent / "icon.png").read_bytes()).decode(),
            mimeType="image/png", sizes=["128x128"])


def build_server(cfg: Config, transport: httpx.AsyncBaseTransport | None = None, host: str = "127.0.0.1", port: int = 8765) -> FastMCP:
    # Explicit, not the SDK default: a web page in the browser must not reach /mcp (DNS rebinding, cross-site POST).
    security = TransportSecuritySettings(enable_dns_rebinding_protection=True, allowed_hosts=["127.0.0.1:*", "localhost:*", "[::1]:*"],
                                         allowed_origins=["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"])
    mcp = FastMCP("ed-narrator", instructions=INSTRUCTIONS, icons=[ICON], host=host, port=port, transport_security=security)

    def client() -> httpx.AsyncClient:
        # no redirects (one could point off the configured address); long read/write for uploading a big film and for streaming a result
        return httpx.AsyncClient(base_url=cfg.url, transport=transport, timeout=httpx.Timeout(600, connect=10), follow_redirects=False,
                                 trust_env=False)       # HTTP_PROXY / ALL_PROXY must never carry uploads away from the loopback address the guard checked

    async def api(method: str, path: str, **kw) -> httpx.Response:
        try:
            async with client() as c:
                r = await c.request(method, path, **kw)
        except httpx.TransportError as e:
            raise ToolError(f"ED Narrator is not reachable at {cfg.url} ({e.__class__.__name__}). Start the app (Docker: `make up`, or the desktop app) "
                            "and set ED_NARRATOR_URL to its address; the desktop app uses another port than Docker.") from None
        if r.status_code >= 400:
            raise _fail(r)
        return r

    def guarded(fn, *a):
        try:
            return fn(*a)
        except GuardError as e:
            raise ToolError(str(e)) from None

    async def voices() -> list[dict]:
        out = []
        for p in (await api("GET", "/api/providers")).json():
            for v in p.get("voices", []):
                out.append({"id": v["id"], "provider": p["id"], "name": v.get("name", ""), "gender": v.get("gender", ""), "lang": v.get("lang", ""),
                            "commercial_use": v.get("commercial"), "licence": v.get("licence", "")})
        return out

    def view(j: dict) -> dict:
        """A whitelisted, plain-language view of a job (the raw API object has a long log we do not forward)."""
        done, total, status = j.get("done", 0), j.get("total", 0), j.get("status", "")
        out = {"job_id": j.get("id"), "status": status, "stage": j.get("stage"), "progress": f"{done}/{total} cues" if total else "starting",
               "percent": round(100 * done / total) if total else 0, "elapsed_s": j.get("elapsed"), "film_duration_s": j.get("duration"),
               "voices": j.get("voices"), "provider": j.get("provider"), "music": j.get("music"),
               "cues_too_long_for_slot": j.get("overflow", 0)}
        if status in ("queued", "running"):
            out["next"] = "Call wait_for_job, then download_result when status is done."
        elif status == "done":
            out["next"] = "Call download_result."
        elif status == "error":
            out["error"] = (j.get("error") or "The render failed.")[:500]
            out["log_tail"] = [s[:200] for s in (j.get("log") or [])[-3:]]
        else:
            out["next"] = "The job was cancelled."
        return out

    @mcp.tool()
    async def check_status() -> dict:
        """Check that ED Narrator is reachable and ready: app version, whether ffmpeg works, and how many voices can be used right now."""
        try:
            h = (await api("GET", "/api/health")).json()
            vs = await voices()
        except ToolError as e:
            return {"reachable": False, "url": cfg.url, "problem": str(e)}
        out = {"reachable": True, "url": cfg.url, "version": h.get("version"), "ffmpeg_ok": bool(h.get("ffmpeg")), "voices_available": len(vs),
               "engines": sorted({v["provider"] for v in vs}), "input_dirs": [str(d) for d in cfg.input_dirs], "output_dir": str(cfg.output_dir)}
        if not h.get("ffmpeg"):
            out["problem"] = "ffmpeg is missing on the app side, so no render can work."
        elif not vs:
            out["problem"] = f"No voice is available. {INSTALL_HINT}"
        return out

    @mcp.tool()
    async def list_voices(language: str = "", provider: str = "", limit: int = 40) -> dict:
        """List the voices the app can use now. `language` matches a language code prefix ("en", "fr", "en-GB"); `provider` is an engine id
        ("piper", "kokoro", "azure"...). Pass a voice `id` to create_voiceover. At most `limit` (1-200) voices are returned; narrow the filters if truncated."""
        vs = await voices()
        if not vs:
            return {"total": 0, "voices": [], "hint": INSTALL_HINT}
        lang = language.strip().lower().replace("_", "-")
        sel = [v for v in vs if (not lang or v["lang"].lower().replace("_", "-").startswith(lang)) and (not provider or v["provider"] == provider.strip().lower())]
        limit = max(1, min(limit, 200))
        out = {"total": len(sel), "shown": min(len(sel), limit), "voices": sel[:limit]}
        if not sel:
            out["hint"] = f"No voice matches. Available engines: {sorted({v['provider'] for v in vs})}; languages: {sorted({v['lang'] for v in vs})[:30]}."
        elif len(sel) > limit:
            out["hint"] = "Truncated: add a language or provider filter."
        return out

    def duration_for(script_path, film_path, duration_s) -> float:
        if duration_s:
            return float(duration_s)
        if film_path:
            film = guarded(safe_input, film_path, cfg, FILM_EXTS, "film")
            if shutil.which("ffprobe"):
                p = subprocess.run(["ffprobe", "-v", "error", "-protocol_whitelist", "file", "-show_entries", "format=duration", "-of", "csv=p=0", "-f", "mov,mp4,m4a,3gp,3g2,mj2", str(film)],
                                   capture_output=True, text=True, timeout=30)
                try:
                    return float(p.stdout.strip())
                except ValueError:
                    pass
        if script_path.suffix.lower() == ".srt":      # shortcut: last cue end + the app's 2 s tail; a script that needs the real film length must pass duration_s
            ends = re.findall(r"-->\s*(\d+):(\d+):(\d+)[,.](\d+)", script_path.read_text("utf-8-sig", errors="replace"))
            if ends:
                h, m, s, ms = (int(x) for x in ends[-1])
                return h * 3600 + m * 60 + s + ms / 1000 + 2
        raise ToolError("Give duration_s (the film length in seconds): a Markdown/text script is spread over the film, so its length is needed.")

    @mcp.tool()
    async def preview_script(script_path: str, duration_s: float | None = None, film_path: str | None = None) -> dict:
        """Parse a script (.srt, .md or .txt) with the app's own rules, without rendering. Reports cue count, words and the cues too long for their time
        slot (the voice would have to speed up or overlap). Give `duration_s` (film length in seconds) or `film_path`; for .srt it is optional."""
        sp = guarded(safe_input, script_path, cfg, SCRIPT_EXTS, "script")
        dur = duration_for(sp, film_path, duration_s)
        r = await api("POST", "/api/script/preview", files={"file": (sp.name, sp.read_bytes())}, data={"duration": str(dur)})
        d = r.json()
        cues, tight = d["cues"], [c for c in d["cues"] if c.get("tight")]
        return {"kind": d["kind"], "cues": len(cues), "words": d["words"], "duration_s": round(dur, 1), "last_cue_end_s": cues[-1]["end"] if cues else 0,
                "too_long_count": len(tight), "too_long_cues": [{"i": c["i"], "start": c["start"], "end": c["end"], "text": c["text"][:120]} for c in tight[:20]],
                "advice": "Shorten the listed cues or lengthen their slots." if tight else "Every cue fits its slot."}

    @mcp.tool()
    async def create_voiceover(film_path: str, script_path: str, voice: str, provider: str = "", second_voice: str = "", music_path: str = "",
                               quality: Literal["standard", "high"] = "standard", pronunciations: dict[str, str] | None = None) -> dict:
        """Upload a film (.mp4/.m4v/.mov) and a script (.srt/.md/.txt) and start the render. Returns at once with a job_id: then call wait_for_job and
        download_result. `voice` must be an id from list_voices (`provider` only if two engines share the id). `second_voice` (same engine) alternates
        voices for a two-voice script. `music_path` adds a background track (.mp3/.wav/.m4a/.aac/.ogg/.flac). `quality` "high" also makes lossless files.
        `pronunciations` maps a word to how it should be said, e.g. {"SQL": "sequel"}."""
        film = guarded(safe_input, film_path, cfg, FILM_EXTS, "film")
        scr = guarded(safe_input, script_path, cfg, SCRIPT_EXTS, "script")
        music = guarded(safe_input, music_path, cfg, MUSIC_EXTS, "music") if music_path else None
        known = await voices()
        if not known:
            raise ToolError(f"No voice is available. {INSTALL_HINT}")
        want = [v for v in (voice, second_voice) if v]
        provs = {p for p in (provider.strip().lower(),) if p} or {v["provider"] for v in known if v["id"] == voice}
        prov = next((p for p in provs if all(any(k["id"] == w and k["provider"] == p for k in known) for w in want)), None)
        if len(provs) > 1 and not provider:
            raise ToolError(f"The voice id {voice!r} exists in several engines ({sorted(provs)}); pass provider.")
        if not voice or prov is None:
            raise ToolError(f"Unknown voice {want or voice!r}{f' for provider {provider!r}' if provider else ''}. Only ids returned by list_voices are accepted (and both voices must use the same engine).")
        prons = "\n".join(f"{k}={v}" for k, v in (pronunciations or {}).items() if k and v and not re.search(r"[=\n]", k + v))
        with ExitStack() as st:
            files = {"video": (film.name, st.enter_context(film.open("rb")), "video/mp4"), "script_file": (scr.name, st.enter_context(scr.open("rb")), "text/plain")}
            if music:
                files["music"] = (music.name, st.enter_context(music.open("rb")), "application/octet-stream")
            r = await api("POST", "/api/jobs", files=files,
                          data={"provider": prov, "voice_a": voice, "voice_b": second_voice, "quality": quality, "pronunciations": prons})
        return view(r.json())

    @mcp.tool()
    async def get_job(job_id: str) -> dict:
        """Status of one job: queued / running / done / error / cancelled, the stage, progress in cues, and the error in plain words if it failed."""
        return view((await api("GET", f"/api/jobs/{guarded(safe_job_id, job_id)}")).json())

    @mcp.tool()
    async def wait_for_job(job_id: str, ctx: Context, timeout_s: int = 120) -> dict:
        """Wait until the job finishes or `timeout_s` (1-600, default 120) passes, whichever is first, then return its status. If it is still running,
        call this again. Sends progress notifications while waiting."""
        path = f"/api/jobs/{guarded(safe_job_id, job_id)}"
        end, last = time.monotonic() + max(1, min(timeout_s, 600)), None
        while True:
            j = (await api("GET", path)).json()
            if (j["done"], j["stage"]) != last:
                last = (j["done"], j["stage"])
                try:
                    await ctx.report_progress(j["done"], j["total"] or None, f"{j['stage']}: {j['done']}/{j['total']} cues")
                except Exception:      # a client without progress support must not break the wait
                    pass
            if j["status"] in DONE or time.monotonic() >= end:
                out = view(j)
                if j["status"] not in DONE:
                    out["next"] = "Still running: call wait_for_job again."
                return out
            await asyncio.sleep(1.5)

    @mcp.tool()
    async def download_result(job_id: str, kind: Literal["video", "audio", "wav", "script", "flac", "video_hires"] = "video") -> dict:
        """Save a finished job's file into the output folder and return its path. kind: video (voiced MP4, default), audio (MP3 narration), wav
        (narration), script (SRT), flac and video_hires (lossless, only for jobs made with quality "high")."""
        dest = guarded(output_path, cfg, job_id, DOWNLOADS[kind])
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_name(dest.name + ".part")
        try:
            async with client() as c, c.stream("GET", f"/api/jobs/{job_id}/{kind}", params={"download": "true"}) as r:
                if r.status_code >= 400:
                    await r.aread()
                    raise _fail(r)
                with tmp.open("wb") as f:
                    async for chunk in r.aiter_bytes(1 << 20):
                        f.write(chunk)
        except httpx.TransportError as e:
            tmp.unlink(missing_ok=True)
            raise ToolError(f"ED Narrator is not reachable at {cfg.url} ({e.__class__.__name__}).") from None
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
        tmp.replace(dest)
        return {"path": str(dest), "bytes": dest.stat().st_size, "kind": kind}

    @mcp.tool()
    async def list_jobs(limit: int = 10) -> dict:
        """The most recent jobs, newest first (1-50). The app keeps jobs for 24 hours."""
        rows = (await api("GET", "/api/jobs", params={"limit": max(1, min(limit, 50))})).json()
        return {"jobs": [{k: v for k, v in view(j).items() if k in ("job_id", "status", "stage", "progress", "film_duration_s", "voices")} for j in rows]}

    @mcp.tool()
    async def delete_job(job_id: str) -> dict:
        """Delete a finished or failed job and its files; a running job is asked to cancel (call delete_job again once it has stopped)."""
        r = await api("DELETE", f"/api/jobs/{guarded(safe_job_id, job_id)}")
        return {"job_id": job_id, "result": "cancellation requested" if r.status_code == 202 else "deleted"}

    async def catalogs() -> tuple[list[dict], list[dict]]:
        return (await api("GET", "/api/models")).json(), (await api("GET", "/api/engines")).json()

    async def verdicts() -> dict[str, dict]:
        """Whether each engine should run smoothly on this computer (the app's /api/system: hardware facts only). An older app has none: the install tools still work."""
        try:
            return {e["id"]: e for e in (await api("GET", "/api/system")).json()["engines"]}
        except (ToolError, KeyError):
            return {}

    @mcp.tool()
    async def list_installable(language: str = "") -> dict:
        """List the voices and engines that can be installed from the app's Models panel, with size, memory need, whether the machine can take them
        and whether they are installed. `language` filters Piper voices by code prefix ("en", "fr-FR"). Use it when check_status says no voice is available."""
        piper, engines = await catalogs()
        runs = await verdicts()
        lang = language.strip().lower().replace("_", "-")
        return {"piper_voices": [{"id": v["id"], "name": v["name"], "gender": v["gender"], "lang": v["lang"], "size_mb": v["size_mb"],
                                  "installed": v["installed"], "state": v["state"]} for v in piper if not lang or v["lang"].lower().replace("_", "-").startswith(lang)],
                "engines": [{"id": e["id"], "label": e["label"], "about": e["blurb"], "size_mb": e["size_mb"], "ram_mb": e["ram_mb"], "installed": e["installed"],
                             "state": e["state"], "fits": e["fits"], "reason": e["reason"], "needs_licence_accept": e["needs_accept"],
                             "on_this_computer": runs.get(e["id"], {}).get("verdict", "unknown"), "why": runs.get(e["id"], {}).get("reason", "")} for e in engines]}

    @mcp.tool()
    async def install_voice_model(name: Literal["piper", "kokoro", "pocket", "chatterbox"], voice_id: str = "", confirm: bool = False) -> dict:
        """Start installing a voice or engine in the app (it downloads in the background: then call wait_for_install). `name` "piper" needs a `voice_id` from
        list_installable (about 65 MB). "kokoro", "pocket" and "chatterbox" are engines of 2.4 to 5.5 GB: they only start with `confirm` true, which you set ONLY
        after telling the user the size and memory need (and, when the answer says `slow` or `no` for this computer, that) and getting a yes. Chatterbox
        needs an NVIDIA GPU: it is far too slow on a laptop."""
        piper, engines = await catalogs()
        if name == "piper":
            v = next((x for x in piper if x["id"] == voice_id), None)      # only an id the app listed ever reaches a URL
            if v is None:
                raise ToolError("Give a voice_id returned by list_installable (piper_voices).")
            if v["installed"]:
                return {"name": name, "voice_id": voice_id, "result": "already installed"}
            await api("POST", f"/api/models/piper/{v['id']}")
            return {"name": name, "voice_id": voice_id, "result": "install started", "next": "Call wait_for_install."}
        e = next(x for x in engines if x["id"] == name)
        if e["installed"]:
            return {"name": name, "result": "already installed"}
        if not e["fits"]:
            raise ToolError(f"{e['label']} cannot be installed on this machine: {e['reason']}")
        if not confirm:
            run = (await verdicts()).get(name, {})
            slow = run.get("verdict") in ("slow", "no")
            return {"name": name, "needs_confirmation": True, "size_mb": e["size_mb"], "ram_mb": e["ram_mb"], "on_this_computer": run.get("verdict", "unknown"), "why": run.get("reason", ""),
                    "message": f"{e['label']} adds about {e['size_mb']} MB on disk and needs about {e['ram_mb']} MB of memory."
                               + (" It will be slow on this computer: tell the user." if slow else "") + " Ask the user, then call again with confirm true."}
        if e["needs_accept"]:       # no engine has a licence today; if one does, only the person accepts it, in the app: never through a tool argument
            raise ToolError(f"{e['label']} has a licence only you can accept: open ED Narrator > Models and install it there.")
        await api("POST", f"/api/engines/{name}", json={"accept": False})
        return {"name": name, "result": "install started", "next": "Call wait_for_install."}

    @mcp.tool()
    async def wait_for_install(name: Literal["piper", "kokoro", "pocket", "chatterbox"], ctx: Context, voice_id: str = "", timeout_s: int = 300) -> dict:
        """Wait until an install started by install_voice_model finishes or `timeout_s` (1-600) passes. For "piper" pass the same `voice_id`."""
        end = time.monotonic() + max(1, min(timeout_s, 600))
        while True:
            piper, engines = await catalogs()
            item = next((x for x in (piper if name == "piper" else engines) if x["id"] == (voice_id if name == "piper" else name)), None)
            if item is None:
                raise ToolError("Unknown voice_id: use one returned by list_installable.")
            out = {"name": name, "installed": item["installed"], "state": item["state"], "progress": item.get("progress")}
            if item["installed"] or item["error"] or time.monotonic() >= end:
                out["error"] = item["error"][:300]
                out["next"] = ("Installed: call list_voices." if item["installed"] else "The install failed: tell the user why." if item["error"] else "Still installing: call wait_for_install again.")
                return out
            try:
                await ctx.report_progress(0, None, f"{name}: {item['state']}")
            except Exception:      # a client without progress support must not break the wait
                pass
            await asyncio.sleep(2)

    @mcp.prompt()
    def voice_over_a_film(film_path: str, script_path: str, language: str = "") -> str:
        """Guide for adding narration to a film."""
        return (f"Add a voice-over to the film {film_path} using the script {script_path}.\n"
                "1. check_status: stop and tell the user how to fix it if the app is unreachable or no voice is available.\n"
                f"2. list_voices{f' with language {language!r}' if language else ''}: pick a voice that matches the script language; ask the user if unsure.\n"
                "3. preview_script: if cues are too long for their slot, show them and offer to shorten the text before rendering.\n"
                "4. create_voiceover with the chosen voice id; keep the job_id.\n"
                "5. wait_for_job repeatedly (each call waits up to 2 minutes) until the status is done; report errors in plain words.\n"
                "6. download_result (video), then tell the user the saved path. Offer delete_job to clean up.")

    return mcp


class BearerToken:
    """ASGI wrapper: every HTTP request needs `Authorization: Bearer <token>` (constant-time compare)."""

    def __init__(self, app, token: str):
        self.app, self.token = app, token.encode()

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            got = dict(scope["headers"]).get(b"authorization", b"")
            if not (got[:7].lower() == b"bearer " and hmac.compare_digest(got[7:], self.token)):
                await send({"type": "http.response.start", "status": 401, "headers": [(b"content-type", b"text/plain"), (b"www-authenticate", b"Bearer")]})
                await send({"type": "http.response.body", "body": b"Missing or wrong bearer token."})
                return
        await self.app(scope, receive, send)


def http_app(mcp: FastMCP, token: str = ""):
    app = mcp.streamable_http_app()
    return BearerToken(app, token) if token else app


def main() -> None:
    ap = argparse.ArgumentParser(prog="ed-narrator-mcp", description="MCP server for a running ED Narrator (stdio by default).")
    ap.add_argument("--http", action="store_true", help="serve streamable HTTP on 127.0.0.1 instead of stdio (set ED_NARRATOR_MCP_TOKEN to require a bearer token)")
    ap.add_argument("--port", type=int, default=8765, help="port for --http (default 8765)")
    a = ap.parse_args()
    try:
        cfg = load_config()
    except GuardError as e:
        raise SystemExit(f"ed-narrator-mcp: {e}") from None
    mcp = build_server(cfg, port=a.port)
    if not a.http:
        mcp.run("stdio")
        return
    import uvicorn
    token = os.environ.get("ED_NARRATOR_MCP_TOKEN", "")
    if not token:
        logging.getLogger("ed-narrator-mcp").warning("--http without ED_NARRATOR_MCP_TOKEN: any local process can call the tools. Set a token to require a bearer header.")
    uvicorn.run(http_app(mcp, token), host="127.0.0.1", port=a.port, log_level="warning")


if __name__ == "__main__":
    main()
