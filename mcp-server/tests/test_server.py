"""Offline tests: a fake ED Narrator behind httpx.MockTransport, temp folders, no network."""
import json
import re
from pathlib import Path

import httpx
import pytest
from mcp.server.fastmcp.exceptions import ToolError

from ed_narrator_mcp import core
from ed_narrator_mcp.core import Config, GuardError, check_url, load_config, safe_input
from ed_narrator_mcp.server import build_server

JOB = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"
SRT = "1\n00:00:00,000 --> 00:00:02,000\nHello there.\n\n2\n00:00:03,000 --> 00:00:05,000\nSecond cue.\n"
VOICES = [{"id": "en_GB-alba-medium", "name": "Alba", "gender": "female", "lang": "en-GB", "licence": "MIT", "commercial": True},
          {"id": "fr_FR-siwis-medium", "name": "Siwis", "gender": "female", "lang": "fr-FR"}]


class FakeApp:
    def __init__(self):
        self.calls, self.status, self.providers, self.down = [], "queued", [{"id": "piper", "voices": VOICES}], False
        self.polls, self.installs = 0, []
        self.piper = [{"id": "en_GB-alba-medium", "name": "Alba", "gender": "female", "lang": "en-GB", "size_mb": 65, "installed": False, "state": "", "error": "", "progress": None},
                      {"id": "fr_FR-siwis-medium", "name": "Siwis", "gender": "female", "lang": "fr-FR", "size_mb": 65, "installed": True, "state": "installed", "error": "", "progress": None}]
        eng = {"installed": False, "state": "", "error": "", "fits": True, "reason": "", "progress": None, "blurb": "b"}
        self.engines = [{**eng, "id": "kokoro", "label": "Kokoro", "size_mb": 2400, "ram_mb": 1500, "needs_accept": False},
                        {**eng, "id": "pocket", "label": "Pocket TTS", "size_mb": 3500, "ram_mb": 1100, "needs_accept": False, "fits": False, "reason": "Not enough free disk."},
                        {**eng, "id": "chatterbox", "label": "Chatterbox", "size_mb": 5500, "ram_mb": 4500, "needs_accept": False}]
        self.system = {"machine": {"cpu": "Test", "cores": 8, "ram_mb": 16000, "free_disk_mb": 100000, "accelerator": "mps"},
                       "engines": [{"id": "kokoro", "verdict": "smooth", "reason": ""}, {"id": "pocket", "verdict": "no", "reason": "disk"},
                                   {"id": "chatterbox", "verdict": "slow", "reason": "no_gpu"}]}

    def __call__(self, req: httpx.Request) -> httpx.Response:
        self.calls.append(req)
        assert "origin" not in req.headers, "the MCP server must not send an Origin header"
        if self.down:
            raise httpx.ConnectError("refused")
        p, m = req.url.path, req.method
        if p == "/api/health":
            return httpx.Response(200, json={"ok": True, "ffmpeg": True, "version": "1.4.0"})
        if p == "/api/providers":
            return httpx.Response(200, json=self.providers)
        if p == "/api/models" and m == "GET":
            return httpx.Response(200, json=self.piper)
        if p == "/api/engines" and m == "GET":
            return httpx.Response(200, json=self.engines)
        if p == "/api/system" and m == "GET":
            return httpx.Response(200, json=self.system) if self.system else httpx.Response(404, json={"detail": "Not Found"})
        if (mm := re.fullmatch(r"/api/models/piper/([\w.-]+)", p)) and m == "POST":
            self.installs.append(("piper", mm[1], None))
            return httpx.Response(202, json={"ok": True})
        if (mm := re.fullmatch(r"/api/engines/(\w+)", p)) and m == "POST":
            self.installs.append((mm[1], "", json.loads(req.content)))
            return httpx.Response(202, json={"ok": True})
        if p == "/api/script/preview":
            return httpx.Response(200, json={"kind": "srt", "words": 4, "cues": [
                {"i": 1, "start": 0, "end": 2, "text": "Hello there.", "tight": False}, {"i": 2, "start": 3, "end": 5, "text": "Second cue.", "tight": True}]})
        if p == "/api/jobs" and m == "POST":
            return httpx.Response(201, json=self.job())
        if p == "/api/jobs":
            return httpx.Response(200, json=[self.job()])
        if p == f"/api/jobs/{JOB}" and m == "GET":
            self.polls += 1
            if self.polls >= 2 and self.status == "running":
                self.status = "done"
            return httpx.Response(200, json=self.job())
        if p == f"/api/jobs/{JOB}" and m == "DELETE":
            return httpx.Response(202 if self.status == "running" else 200, json=self.job())
        if p == f"/api/jobs/{JOB}/video":
            if self.status != "done":
                return httpx.Response(409, json={"detail": "This file is not ready yet."})
            return httpx.Response(200, content=b"MP4DATA")
        return httpx.Response(404, json={"detail": "Unknown job."})

    def job(self):
        done = 2 if self.status == "done" else 1
        return {"id": JOB, "status": self.status, "stage": "voicing", "done": done, "total": 2, "error": "", "log": [], "provider": "piper",
                "voices": ["en_GB-alba-medium"], "duration": 6.0, "overflow": 1, "elapsed": 3.0, "music": False, "azure_key": "SECRET-KEY"}


@pytest.fixture
def env(tmp_path):
    inp, out = tmp_path / "in", tmp_path / "out"
    inp.mkdir()
    (inp / "film.mp4").write_bytes(b"film")
    (inp / "script.srt").write_text(SRT)
    (inp / "music.mp3").write_bytes(b"mp3")
    app = FakeApp()
    cfg = Config("http://127.0.0.1:8090", out.resolve(), (inp.resolve(),))
    return build_server(cfg, transport=httpx.MockTransport(app)), app, inp, out, cfg


async def call(mcp, tool, /, **args):
    """The result of a tool as a dict, or the ToolError."""
    res = await mcp.call_tool(tool, args)
    content = res[0] if isinstance(res, tuple) else res      # the SDK returns the content list, plus structured output in some versions
    return json.loads(content[0].text)


# ---------- guards ----------
def test_url_guard():
    assert check_url("http://localhost:18090") and check_url("http://127.0.0.1:8090") and check_url("http://[::1]:8090")
    for bad in ("http://example.com", "http://192.168.1.5:8090", "http://127.0.0.1.evil.com", "ftp://127.0.0.1", "http://user:pw@127.0.0.1"):
        with pytest.raises(GuardError):
            check_url(bad)
    assert check_url("http://192.168.1.5:8090", allow_remote=True)


def test_config_defaults_and_root_cwd(tmp_path):
    cfg = load_config({}, cwd=tmp_path)
    assert cfg.url == core.DEFAULT_URL and cfg.input_dirs == (tmp_path.resolve(),) and cfg.output_dir == (tmp_path / "ed-narrator-output").resolve()
    assert load_config({}, cwd=Path("/")).input_dirs == ()      # a GUI client's "/" must not allow everything
    with pytest.raises(GuardError):
        load_config({"ED_NARRATOR_URL": "http://evil.example"}, cwd=tmp_path)


def test_input_allow_list_and_traversal(env, tmp_path):
    _, _, inp, _, cfg = env
    assert safe_input(str(inp / "film.mp4"), cfg, core.FILM_EXTS, "film")
    (tmp_path / "secret.mp4").write_bytes(b"x")
    with pytest.raises(GuardError, match="outside"):
        safe_input(str(inp / ".." / "secret.mp4"), cfg, core.FILM_EXTS, "film")
    (inp / "link.mp4").symlink_to(tmp_path / "secret.mp4")
    with pytest.raises(GuardError, match="outside"):
        safe_input(str(inp / "link.mp4"), cfg, core.FILM_EXTS, "film")
    with pytest.raises(GuardError, match="outside"):
        safe_input("/etc/hosts", cfg, (".txt", ""), "script")
    with pytest.raises(GuardError, match="must be one of"):
        safe_input(str(inp / "script.srt"), cfg, core.FILM_EXTS, "film")
    with pytest.raises(GuardError, match="does not exist"):
        safe_input(str(inp / "nope.mp4"), cfg, core.FILM_EXTS, "film")


def test_output_names_cannot_traverse(env):
    *_, cfg = env
    assert core.output_path(cfg, JOB, "voiced.mp4").parent == cfg.output_dir
    assert core.output_path(cfg, JOB, "../../x.mp4").parent == cfg.output_dir
    with pytest.raises(GuardError):
        core.output_path(cfg, "../../etc", "voiced.mp4")


# ---------- tools ----------
async def test_check_status_ok_down_and_no_voice(env):
    mcp, app, *_ = env
    s = await call(mcp, "check_status")
    assert s["reachable"] and s["version"] == "1.4.0" and s["ffmpeg_ok"] and s["voices_available"] == 2
    app.providers = []
    assert "Models" in (await call(mcp, "check_status"))["problem"]
    app.down = True
    s = await call(mcp, "check_status")
    assert s["reachable"] is False and "not reachable" in s["problem"]
    with pytest.raises(ToolError, match="not reachable"):
        await mcp.call_tool("list_voices", {})


async def test_list_voices_filters_and_empty_hint(env):
    mcp, app, *_ = env
    assert [v["id"] for v in (await call(mcp, "list_voices", language="fr"))["voices"]] == ["fr_FR-siwis-medium"]
    assert (await call(mcp, "list_voices", language="en_gb"))["total"] == 1
    assert "hint" in await call(mcp, "list_voices", provider="azure")
    app.providers = []
    assert "Models" in (await call(mcp, "list_voices"))["hint"]


async def test_preview_script(env):
    mcp, _, inp, *_ = env
    r = await call(mcp, "preview_script", script_path=str(inp / "script.srt"))
    assert r["cues"] == 2 and r["too_long_count"] == 1 and r["too_long_cues"][0]["i"] == 2 and r["duration_s"] == 7.0
    (inp / "s.md").write_text("Hello. World.")
    with pytest.raises(ToolError, match="duration_s"):
        await mcp.call_tool("preview_script", {"script_path": str(inp / "s.md")})


async def test_unknown_voice_is_rejected_before_any_upload(env):
    mcp, app, inp, *_ = env
    for bad in ("nope", "en_GB-alba-medium'; DROP", ""):
        with pytest.raises(ToolError, match="Unknown voice"):
            await mcp.call_tool("create_voiceover", {"film_path": str(inp / "film.mp4"), "script_path": str(inp / "script.srt"), "voice": bad})
    with pytest.raises(ToolError, match="Unknown voice"):      # a real id with the wrong engine
        await mcp.call_tool("create_voiceover", {"film_path": str(inp / "film.mp4"), "script_path": str(inp / "script.srt"),
                                                 "voice": "en_GB-alba-medium", "provider": "azure"})
    assert not [c for c in app.calls if c.method == "POST"]


async def test_create_refuses_files_outside_the_allow_list(env, tmp_path):
    mcp, app, inp, *_ = env
    (tmp_path / "other.mp4").write_bytes(b"x")
    with pytest.raises(ToolError, match="outside"):
        await mcp.call_tool("create_voiceover", {"film_path": str(tmp_path / "other.mp4"), "script_path": str(inp / "script.srt"), "voice": "en_GB-alba-medium"})
    assert not app.calls


async def test_no_voice_installed(env):
    mcp, app, inp, *_ = env
    app.providers = []
    with pytest.raises(ToolError, match="Models"):
        await mcp.call_tool("create_voiceover", {"film_path": str(inp / "film.mp4"), "script_path": str(inp / "script.srt"), "voice": "x"})


async def test_job_lifecycle_create_wait_download_delete(env):
    mcp, app, inp, out, _ = env
    j = await call(mcp, "create_voiceover", film_path=str(inp / "film.mp4"), script_path=str(inp / "script.srt"), voice="en_GB-alba-medium",
                   music_path=str(inp / "music.mp3"), pronunciations={"SQL": "sequel", "bad=key": "x"})
    assert j["job_id"] == JOB and j["status"] == "queued"
    post = next(c for c in app.calls if c.method == "POST" and c.url.path == "/api/jobs")
    body = post.read().decode("latin-1")
    for part in ('name="provider"', "piper", 'name="voice_a"', "en_GB-alba-medium", 'name="music"', "SQL=sequel"):
        assert part in body
    assert "bad=key" not in body and post.headers["host"] == "127.0.0.1:8090"
    with pytest.raises(ToolError, match="not ready"):
        await mcp.call_tool("download_result", {"job_id": JOB})
    assert not out.exists() or not list(out.iterdir())
    app.status = "running"
    assert (await call(mcp, "get_job", job_id=JOB))["progress"] == "1/2 cues"
    w = await call(mcp, "wait_for_job", job_id=JOB, timeout_s=30)
    assert w["status"] == "done" and w["next"].startswith("Call download_result")
    d = await call(mcp, "download_result", job_id=JOB)
    assert Path(d["path"]).read_bytes() == b"MP4DATA" and Path(d["path"]).parent == out.resolve() and not list(out.glob("*.part"))
    assert (await call(mcp, "list_jobs"))["jobs"][0]["job_id"] == JOB
    assert (await call(mcp, "delete_job", job_id=JOB))["result"] == "deleted"


async def test_wait_returns_current_status_on_timeout(env):
    mcp, app, *_ = env
    app.status, app.polls = "running", -1000
    w = await call(mcp, "wait_for_job", job_id=JOB, timeout_s=1)
    assert w["status"] == "running" and "again" in w["next"]


async def test_failed_job_is_reported_in_plain_words(env):
    mcp, app, *_ = env
    app.status = "error"
    app.job = lambda: {"id": JOB, "status": "error", "stage": "voicing", "done": 0, "total": 2, "error": "The engine failed.", "log": ["a", "b"]}
    j = await call(mcp, "get_job", job_id=JOB)
    assert j["status"] == "error" and j["error"] == "The engine failed."


async def test_http_errors_map_to_messages(env):
    mcp, *_ = env
    with pytest.raises(ToolError, match="404.*Unknown job"):
        await mcp.call_tool("get_job", {"job_id": "ffffffffffff"})
    with pytest.raises(ToolError, match="not a job id"):
        await mcp.call_tool("get_job", {"job_id": "../settings"})
    with pytest.raises(ToolError, match="not a job id"):
        await mcp.call_tool("download_result", {"job_id": "../../x"})


# ---------- no credentials ----------
async def test_no_tool_touches_credentials(env):
    mcp, app, inp, *_ = env
    names = {t.name for t in await mcp.list_tools()}
    assert names == {"check_status", "list_voices", "preview_script", "create_voiceover", "get_job", "wait_for_job", "download_result", "list_jobs", "delete_job",
                     "list_installable", "install_voice_model", "wait_for_install"}
    for t in await mcp.list_tools():
        assert not re.search(r"setting|key|credential|secret", t.name + json.dumps(t.inputSchema), re.I), t.name
    out = json.dumps([await call(mcp, "get_job", job_id=JOB), await call(mcp, "list_jobs"), await call(mcp, "check_status")])
    assert "SECRET-KEY" not in out and "azure_key" not in out
    src = "".join(p.read_text() for p in Path(core.__file__).parent.glob("*.py"))
    assert not re.search(r'"/api/settings', src)
    assert not [c for c in app.calls if c.url.path.startswith("/api/settings")]


# ---------- installing voices and engines ----------
async def test_list_installable_filters_by_language(env):
    mcp, *_ = env
    d = await call(mcp, "list_installable", language="en")
    assert [v["id"] for v in d["piper_voices"]] == ["en_GB-alba-medium"] and {e["id"] for e in d["engines"]} == {"kokoro", "pocket", "chatterbox"}
    assert "azure" not in json.dumps(d).lower()
    by = {e["id"]: e for e in d["engines"]}
    assert (by["kokoro"]["on_this_computer"], by["chatterbox"]["on_this_computer"], by["chatterbox"]["why"]) == ("smooth", "slow", "no_gpu")


async def test_an_engine_that_will_be_slow_here_says_so_before_the_install(env):
    mcp, app, *_ = env
    d = await call(mcp, "install_voice_model", name="chatterbox")
    assert d["needs_confirmation"] and d["on_this_computer"] == "slow" and "slow on this computer" in d["message"] and not app.installs
    assert "slow" not in (await call(mcp, "install_voice_model", name="kokoro"))["message"]


async def test_an_older_app_without_system_info_still_installs(env):
    mcp, app, *_ = env
    app.system = None                                                              # /api/system answers 404 in an older app
    d = await call(mcp, "list_installable")
    assert {e["on_this_computer"] for e in d["engines"]} == {"unknown"}
    assert (await call(mcp, "install_voice_model", name="kokoro", confirm=True))["result"] == "install started" and len(app.installs) == 1


async def test_piper_install_only_for_listed_ids(env):
    mcp, app, *_ = env
    assert (await call(mcp, "install_voice_model", name="piper", voice_id="en_GB-alba-medium"))["result"] == "install started"
    assert app.installs == [("piper", "en_GB-alba-medium", None)]
    assert (await call(mcp, "install_voice_model", name="piper", voice_id="fr_FR-siwis-medium"))["result"] == "already installed"
    for bad in ("../settings", "nope", ""):
        with pytest.raises(ToolError, match="list_installable"):
            await mcp.call_tool("install_voice_model", {"name": "piper", "voice_id": bad})
    assert len(app.installs) == 1


async def test_heavy_engines_need_confirm_and_a_licence_is_never_accepted_by_a_tool(env):
    mcp, app, *_ = env
    d = await call(mcp, "install_voice_model", name="kokoro")
    assert d["needs_confirmation"] and d["size_mb"] == 2400 and not app.installs
    assert (await call(mcp, "install_voice_model", name="kokoro", confirm=True))["result"] == "install started"
    assert app.installs[-1] == ("kokoro", "", {"accept": False})
    await call(mcp, "install_voice_model", name="kokoro", confirm=True, accept_licence=True)     # no such argument: it is ignored, the app is told accept=false
    assert app.installs[-1] == ("kokoro", "", {"accept": False}) and len(app.installs) == 2
    with pytest.raises(ToolError):                                       # a removed engine is refused
        await mcp.call_tool("install_voice_model", {"name": "linnet", "confirm": True})
    app.engines[0].update(installed=False, needs_accept=True)            # an engine with a licence: only the person accepts it, in the app
    with pytest.raises(ToolError, match="only you can accept"):
        await mcp.call_tool("install_voice_model", {"name": "kokoro", "confirm": True})
    assert len(app.installs) == 2
    with pytest.raises(ToolError, match="free disk"):
        await mcp.call_tool("install_voice_model", {"name": "pocket", "confirm": True})


async def test_wait_for_install_reports_done_and_failure(env):
    mcp, app, *_ = env
    app.piper[0].update(installed=True, state="installed")
    assert (await call(mcp, "wait_for_install", name="piper", voice_id="en_GB-alba-medium"))["installed"] is True
    app.engines[0].update(state="error", error="Not enough disk.")
    d = await call(mcp, "wait_for_install", name="kokoro")
    assert not d["installed"] and "Not enough disk" in d["error"] and "failed" in d["next"]
    app.engines[1].update(state="running")
    d = await call(mcp, "wait_for_install", name="pocket", timeout_s=1)
    assert d["state"] == "running" and "again" in d["next"]


async def test_prompt_is_listed(env):
    mcp, *_ = env
    assert [p.name for p in await mcp.list_prompts()] == ["voice_over_a_film"]
