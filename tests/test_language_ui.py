"""Opt-in real Tk widget checks: set VOX0_TEST_UI=1 on an interactive desktop."""
import os
from pathlib import Path
import subprocess
import sys

import pytest

pytestmark = pytest.mark.skipif(os.environ.get("VOX0_TEST_UI") != "1",
                                reason="Opt-in Windows UI tests")


def state(segmented):
    # CTk 5.2 supports configure(state=...), but not cget('state') on the
    # container. Verify the actual clickable buttons instead.
    states = {button.cget("state") for button in segmented._buttons_dict.values()}
    assert len(states) == 1
    return states.pop()


def assert_header_drag(app, frame):
    header = frame.winfo_children()[0]
    x, y = app.winfo_x(), app.winfo_y()
    header._canvas.event_generate("<ButtonPress-1>", x=150, y=20)
    header._canvas.event_generate("<B1-Motion>", x=130, y=10)
    app.update()
    assert (app.winfo_x(), app.winfo_y()) == (x - 20, y - 10)
    header._canvas.event_generate("<ButtonRelease-1>", x=130, y=10)


def test_settings_widgets_save_reload_and_localize(vox0, monkeypatch):
    # No microphone, global listeners, tray, real model or user settings.
    monkeypatch.setattr(vox0, "list_input_devices", lambda: [])
    monkeypatch.setattr(vox0, "current_mic_name", lambda: "Test microphone")
    monkeypatch.setattr(vox0.Vox0App, "_fill_hw_info", lambda self: None)
    monkeypatch.setattr(vox0.Vox0App, "_reload_model", lambda self: None)
    vox0.save_settings(dict(vox0.DEFAULT_SETTINGS, numbers="words", commands="all"))
    windows = []
    try:
        app = vox0.Vox0App()
        windows.append(app)
        app.update()
        assert app.title() == "Vox0"
        assert_header_drag(app, app._main_frame)
        logo = app._dot.cget("image")
        assert logo.cget("light_image").getpixel((48, 48))[:3] == (232, 232, 232)
        assert app._stage_mark.cget("fg_color") == "#abdb25"
        app._set_recording(True)
        assert app._stage_mark.cget("fg_color") == "#e74c3c"
        assert app._dot.cget("image") is logo
        app._set_recording(False)
        assert app._stage_mark.cget("fg_color") == "#abdb25"
        assert app._dot.cget("image") is logo
        app._show_settings()
        app.update()
        assert_header_drag(app, app._settings_frame)
        assert app._lang_var.get() == "Automático"
        assert not hasattr(app, "_numbers_seg")
        assert not hasattr(app, "_commands_seg")
        for seg, variable in ((app._theme_seg, app._theme_var),
                              (app._device_seg, app._device_var)):
            for value, button in seg._buttons_dict.items():
                expected = app.theme["text_on_accent" if value == variable.get()
                                     else "text_on_button"]
                assert button.cget("text_color") == expected
        assert "Automático" not in app._ui_lang_menu.cget("values")

        app._lang_var.set("Spanish")
        app.update()
        assert state(app._device_seg) == "normal"
        app._lang_var.set("Automático")
        app._apply_settings()
        assert vox0.load_settings()["language"] == "auto"
        assert vox0.load_settings()["numbers"] == "words"
        assert vox0.load_settings()["commands"] == "all"

        app._on_ui_language_change("English")
        app.update()
        assert app._lang_var.get() == "Automatic"
        assert not hasattr(app, "_numbers_seg")
        assert not hasattr(app, "_commands_seg")
        app._on_theme_change("light")
        app.update()
        assert app._lang_var.get() == "Automatic"

        for ui in vox0.LANGUAGE_CODES:
            app._on_ui_language_change(vox0.LANGUAGE_NAMES[ui])
            app.update()
            assert app._lang_var.get() == vox0.vox0i18n.STRINGS[ui]["language_auto"]
            assert app._lang_var.get() not in app._ui_lang_menu.cget("values")
            assert not hasattr(app, "_numbers_seg")
            assert not hasattr(app, "_commands_seg")

        app._lang_var.set("English")
        assert state(app._device_seg) == "normal"
        assert app._settings["numbers"] == "words"
        assert app._settings["commands"] == "all"
        app._apply_settings()
        assert vox0.load_settings()["language"] == "en"
        # Reload from disk and rebuild the settings widgets in the same Tcl
        # interpreter. Tk image objects cannot cross interpreter lifetimes.
        app._settings = vox0.load_settings()
        app._rebuild_ui()
        app.update()
        app._show_settings()
        app.update()
        assert_header_drag(app, app._settings_frame)
        assert app._lang_var.get() == "English"
        assert app._settings["numbers"] == "words"
        assert app._settings["commands"] == "all"
        assert not hasattr(app, "_numbers_seg")
        assert not hasattr(app, "_commands_seg")
    finally:
        for window in windows:
            window.destroy()
        vox0._mark_cache.clear()
        vox0.vox0i18n.set_language("es")


@pytest.mark.parametrize("language", ["auto", "en"])
def test_settings_in_fresh_app_process(vox0, language, tmp_path):
    vox0.save_settings(dict(vox0.DEFAULT_SETTINGS, language=language,
                            ui_language="en", numbers="words", commands="all"))
    env = dict(os.environ, LOCALAPPDATA=str(tmp_path / "appdata"), HF_HUB_OFFLINE="1",
               VOX0_TEST_SETTINGS=vox0.SETTINGS_FILE, VOX0_TEST_LANGUAGE=language)
    code = '''
import ctypes, os
from unittest.mock import patch
with patch.object(ctypes.windll.kernel32, "CreateMutexW", return_value=0), \\
     patch.object(ctypes.windll.kernel32, "GetLastError", return_value=0):
    import vox0
vox0.SETTINGS_FILE = os.environ["VOX0_TEST_SETTINGS"]
vox0.vox0i18n.set_language("en")
vox0.list_input_devices = lambda: []
vox0.Vox0App._fill_hw_info = lambda self: None
app = vox0.Vox0App()
try:
    app.update()
    automatic = os.environ["VOX0_TEST_LANGUAGE"] == "auto"
    assert app._lang_var.get() == ("Automatic" if automatic else "English")
    assert app._settings["numbers"] == "words"
    assert app._settings["commands"] == "all"
    assert app._ui_lang_var.get() == "English"
    assert not hasattr(app, "_numbers_seg")
    assert not hasattr(app, "_commands_seg")
finally:
    app.destroy()
'''
    result = subprocess.run([sys.executable, "-c", code], env=env,
                            cwd=Path(__file__).resolve().parents[1],
                            capture_output=True, text=True, timeout=30,
                            creationflags=subprocess.CREATE_NO_WINDOW)
    assert result.returncode == 0, result.stdout + result.stderr
