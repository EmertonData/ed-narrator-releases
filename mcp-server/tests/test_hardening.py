"""Fail-closed input folders and the hardened HTTP transport."""
import os
from pathlib import Path

import httpx
import pytest
from starlette.testclient import TestClient

from ed_narrator_mcp import core
from ed_narrator_mcp.core import Config, GuardError, load_config, safe_input
from ed_narrator_mcp.server import build_server, http_app


def test_default_input_dir_refuses_root_home_and_ancestors(tmp_path):
    home = tmp_path / "home" / "me"
    (home / "Movies").mkdir(parents=True)
    for cwd in (Path("/"), home, home.parent, tmp_path):
        assert load_config({}, cwd=cwd, home=home).input_dirs == (), cwd
    assert load_config({}, cwd=home / "Movies", home=home).input_dirs == ((home / "Movies").resolve(),)


def test_explicit_input_dirs_refuse_root_home_and_ancestors(tmp_path):
    home = tmp_path / "home" / "me"
    (home / "Movies").mkdir(parents=True)
    for bad in ("/", str(home), str(home.parent)):
        with pytest.raises(GuardError, match="may not contain"):
            load_config({"ED_NARRATOR_INPUT_DIRS": bad}, cwd=tmp_path, home=home)
    ok = load_config({"ED_NARRATOR_INPUT_DIRS": os.pathsep.join([str(home / "Movies"), str(tmp_path / "x")])}, cwd=tmp_path, home=home)
    assert len(ok.input_dirs) == 2


def test_hidden_components_are_refused(tmp_path):
    inp = tmp_path / "in"
    (inp / ".ssh").mkdir(parents=True)
    (inp / ".ssh" / "film.mp4").write_bytes(b"x")
    (inp / ".hidden.mp4").write_bytes(b"x")
    (inp / "film.mp4").write_bytes(b"x")
    cfg = Config("http://127.0.0.1:8090", tmp_path / "o", (inp.resolve(),))
    for p in (inp / ".ssh" / "film.mp4", inp / ".hidden.mp4"):
        with pytest.raises(GuardError, match="hidden"):
            safe_input(str(p), cfg, core.FILM_EXTS, "film")
    assert safe_input(str(inp / "film.mp4"), cfg, core.FILM_EXTS, "film")


def test_empty_allow_list_error_mentions_the_variable():
    with pytest.raises(GuardError, match="ED_NARRATOR_INPUT_DIRS"):
        safe_input("/tmp/x.mp4", Config("http://127.0.0.1:8090", Path("/tmp/o"), ()), core.FILM_EXTS, "film")


INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}}
HDRS = {"content-type": "application/json", "accept": "application/json, text/event-stream"}


def post(token, headers):
    mcp = build_server(Config("http://127.0.0.1:8090", Path("/tmp/o"), ()), transport=httpx.MockTransport(lambda r: httpx.Response(404)))
    with TestClient(http_app(mcp, token), base_url="http://127.0.0.1:8765") as c:
        return c.post("/mcp", json=INIT, headers={**HDRS, **headers})


def test_http_refuses_foreign_host_and_origin():
    assert post("", {}).status_code == 200
    assert post("", {"origin": "http://localhost:3000"}).status_code == 200
    assert post("", {"host": "evil.example:8765"}).status_code in (421, 403)
    assert post("", {"origin": "https://evil.example"}).status_code in (421, 403)


async def test_the_client_ignores_proxy_environment_variables(monkeypatch):
    for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
        monkeypatch.setenv(k, "http://proxy.example:3128")
    made = []

    class Spy(httpx.AsyncClient):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            made.append(self)
    monkeypatch.setattr(httpx, "AsyncClient", Spy)
    mcp = build_server(Config("http://127.0.0.1:8090", Path("/tmp/o"), ()), transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"ok": True, "ffmpeg": True} if r.url.path == "/api/health" else [])))
    await mcp.call_tool("check_status", {})
    assert made and all(c.trust_env is False for c in made)


def test_http_bearer_token():
    assert post("s3cret", {}).status_code == 401
    assert post("s3cret", {"authorization": "Bearer wrong"}).status_code == 401
    assert post("s3cret", {"authorization": "s3cret"}).status_code == 401
    assert post("s3cret", {"authorization": "Bearer s3cret"}).status_code == 200


def test_server_advertises_its_icon(tmp_path):
    server = build_server(Config(url="http://127.0.0.1:1", output_dir=tmp_path / "out", input_dirs=(tmp_path,)))
    icons = server._mcp_server.icons
    assert icons and icons[0].src.startswith("data:image/png;base64,") and icons[0].mimeType == "image/png"
