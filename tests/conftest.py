"""Import the Windows app against isolated settings, without acquiring its mutex."""
import importlib
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(scope="session")
def vox0_app(tmp_path_factory):
    if sys.platform != "win32":
        pytest.skip("Vox0 app integration requires Windows")
    import ctypes

    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("LOCALAPPDATA", str(tmp_path_factory.mktemp("vox0-settings")))
        patch.setenv("HF_HUB_OFFLINE", "1")
        patch.setattr(ctypes.windll.kernel32, "CreateMutexW", lambda *args: 0)
        patch.setattr(ctypes.windll.kernel32, "GetLastError", lambda: 0)
        app = importlib.import_module("vox0")
    yield app


@pytest.fixture
def vox0(vox0_app, monkeypatch, tmp_path):
    import queue
    from unittest.mock import Mock

    app = vox0_app
    monkeypatch.setattr(app, "SETTINGS_FILE", str(tmp_path / "settings.json"))
    monkeypatch.setattr(app, "app_settings", dict(app.DEFAULT_SETTINGS))
    monkeypatch.setattr(app, "ui_queue", queue.Queue())
    monkeypatch.setattr(app, "trace", Mock())
    monkeypatch.setattr(app, "_CAPTURE_DEMO_PATH", None)
    app.vox0i18n.set_language("es")
    yield app


@pytest.fixture
def pipeline(vox0, monkeypatch):
    """Exercise real _transcribe; only the model and external paste are mocked."""
    from contextlib import nullcontext
    from types import SimpleNamespace
    from unittest.mock import Mock

    vox0.trace.span.side_effect = lambda name: nullcontext()
    monkeypatch.setattr(vox0, "model_device", "cpu")
    monkeypatch.setattr(vox0, "model_threads", 4)
    monkeypatch.setattr(vox0, "_clipboard_has_text", lambda: True)
    monkeypatch.setattr(vox0.pyperclip, "paste", Mock(return_value="previous clipboard"))
    monkeypatch.setattr(vox0.pyperclip, "copy", Mock())
    monkeypatch.setattr(vox0.pyautogui, "hotkey", Mock())
    monkeypatch.setattr(vox0.time, "sleep", lambda seconds: None)
    model = Mock()
    monkeypatch.setattr(vox0, "model_obj", model)

    def run(text, detected="es", duration=4, fail=None):
        model.transcribe.side_effect = fail
        model.transcribe.return_value = (
            iter([SimpleNamespace(text=text)]),
            SimpleNamespace(language=detected, language_probability=0.91),
        )
        # A voiced-level waveform, with the actual preprocessing and text path.
        audio = vox0.np.full(int(duration * vox0.SAMPLE_RATE), 0.1, dtype="float32")
        vox0._transcribe(audio, vox0.SAMPLE_RATE)
        events = []
        while not vox0.ui_queue.empty():
            events.append(vox0.ui_queue.get_nowait())
        return events

    return SimpleNamespace(app=vox0, model=model, run=run)
