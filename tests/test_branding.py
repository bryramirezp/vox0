"""Compatibility with Kara users after the Vox0 rename."""
import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from unittest.mock import Mock

import pytest


def test_existing_kara_settings_load_without_resetting_preferences(vox0_app, monkeypatch):
    assert Path(vox0_app.APP_DIR).name == "Kara"
    settings = Path(vox0_app.APP_DIR) / "settings.json"
    settings.write_text(json.dumps({"language": "en", "hotkey": "key:f9",
                                   "model": "small", "ui_language": "fr"}))
    monkeypatch.setattr(vox0_app, "SETTINGS_FILE", str(settings))
    loaded = vox0_app.load_settings()
    assert (loaded["language"], loaded["hotkey"], loaded["model"], loaded["ui_language"]) == (
        "en", "key:f9", "small", "fr")


@pytest.mark.parametrize("already_open", [False, True])
def test_vox0_and_kara_share_the_single_instance_lock(vox0_app, monkeypatch, already_open):
    create, message = Mock(), Mock()
    monkeypatch.setattr(ctypes.windll.kernel32, "CreateMutexW", create)
    monkeypatch.setattr(ctypes.windll.kernel32, "GetLastError", lambda: 183 if already_open else 0)
    monkeypatch.setattr(ctypes.windll.user32, "MessageBoxW", message)
    if already_open:
        with pytest.raises(SystemExit):
            vox0_app.ensure_single_instance()
        assert message.call_args.args[2] == "Vox0"
    else:
        vox0_app.ensure_single_instance()
        message.assert_not_called()
    create.assert_called_once_with(None, False, "Kara_SingleInstance")


@pytest.mark.parametrize("current", [None, "new-machine"])
def test_machine_environment_keeps_legacy_fallback(vox0_app, monkeypatch, current):
    monkeypatch.setenv("KARA_MACHINE", "legacy-machine")
    monkeypatch.delenv("VOX0_MACHINE", raising=False)
    if current:
        monkeypatch.setenv("VOX0_MACHINE", current)
    assert vox0_app._Trace().machine == (current or "legacy-machine")


def test_ui_languages_use_vox0(vox0_app):
    for strings in vox0_app.vox0i18n.STRINGS.values():
        for key in ("tray_title", "tray_title_recording", "tray_title_ready"):
            assert strings[key].startswith("Vox0")
        assert all("Kara" not in text for text in strings.values())


@pytest.mark.parametrize("variable", ["VOX0_PYTHON", "KARA_PYTHON", "DICTATION_PYTHON"])
def test_capture_tool_accepts_existing_interpreter_preferences(monkeypatch, tmp_path, variable):
    from tools import capture_demo

    executable = tmp_path / "pythonw.exe"
    executable.touch()
    for name in ("VOX0_PYTHON", "KARA_PYTHON", "DICTATION_PYTHON"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv(variable, str(executable))
    assert capture_demo._vox0_python() == str(executable)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows launchers")
@pytest.mark.parametrize("launcher", ["launch.bat", "launch.vbs"])
@pytest.mark.parametrize("variable", ["VOX0_PYTHON", "KARA_PYTHON", "DICTATION_PYTHON"])
def test_launchers_run_vox0_from_paths_with_spaces(tmp_path, launcher, variable):
    project = tmp_path / "project with spaces"
    project.mkdir()
    script = project / "vox0.py"
    script.write_text("from pathlib import Path\nPath(__file__).with_suffix('.ok').touch()\n")
    shutil.copyfile(Path(__file__).resolve().parents[1] / launcher, project / launcher)
    env = dict(os.environ)
    for name in ("VOX0_PYTHON", "KARA_PYTHON", "DICTATION_PYTHON"):
        env.pop(name, None)
    env[variable] = sys.executable
    if launcher.endswith(".bat"):
        command = [os.environ["COMSPEC"], "/d", "/c", str(project / launcher)]
    else:
        command = ["cscript.exe", "//Nologo", str(project / launcher)]
    result = subprocess.run(command, cwd=project, env=env, capture_output=True,
                            text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
    assert result.returncode == 0, result.stdout + result.stderr
    deadline = time.monotonic() + 5
    while not script.with_suffix(".ok").exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    assert script.with_suffix(".ok").exists(), result.stdout + result.stderr
