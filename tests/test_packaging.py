"""Release naming and the removal of the dynamic NVIDIA downloader."""
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vox0_build", ROOT / "packaging" / "build.py")
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)


def test_setup_names_are_versioned_and_distinct():
    assert Path(build.setup_path("0.3.6", False)).name == "Vox0-Setup-0.3.6.exe"
    assert Path(build.setup_path("0.3.6", True)).name == "Vox0-Setup-GPU-0.3.6.exe"


def test_distributed_icon_uses_full_logo_at_every_size():
    from PIL import Image

    icon = Image.open(ROOT / "assets" / "icon.ico")
    assert icon.ico.sizes() == {(n, n) for n in (16, 32, 48, 64, 128, 256)}
    for size in icon.ico.sizes():
        frame = icon.ico.getimage(size)
        centre = frame.getpixel((size[0] // 2, size[1] // 2))
        assert all(channel > 180 for channel in centre[:3]), size


def test_runtime_has_no_dynamic_gpu_downloader():
    source = (ROOT / "vox0.py").read_text(encoding="utf-8")
    assert "gpu_component" not in source
    assert "GPU_MANIFEST_FILE" not in source
    assert not (ROOT / "gpu_component.py").exists()


@pytest.mark.parametrize("repository", ["kara", "vox0"])
def test_docs_stamp_updates_download_labels_and_urls(monkeypatch, repository):
    import re
    from tools import stamp_docs

    monkeypatch.setattr(stamp_docs, "last_commit_date", lambda path: "2026-10-11")
    text = (f'[Kara-Setup-0.3.5.exe](https://github.com/bryramirezp/{repository}/releases/download/v0.3.5/Kara-Setup-0.3.5.exe) '
            f'[Kara-Setup-GPU-0.3.5.exe](https://github.com/bryramirezp/{repository}/releases/download/v0.3.5/Kara-Setup-GPU-0.3.5.exe)')
    for rel, pattern, replacement in stamp_docs.rules("0.3.6", None):
        if rel == "README.md":
            text = re.sub(pattern, replacement, text)
    assert "0.3.5" not in text
    assert text.count("Vox0-Setup-0.3.6.exe") == 2
    assert text.count("Vox0-Setup-GPU-0.3.6.exe") == 2
    assert text.count("https://github.com/bryramirezp/vox0/releases/download/v0.3.6/") == 2


def test_build_cleans_intermediates_and_excludes_gpu_environment(monkeypatch):
    from unittest.mock import Mock

    run = Mock()
    monkeypatch.setattr(build, "run", run)
    monkeypatch.setattr(build.shutil, "rmtree", Mock())
    monkeypatch.setattr(build.os.path, "exists", lambda path: True)
    monkeypatch.setattr(build.os.path, "isdir", lambda path: False)
    monkeypatch.setenv("VOX0_GPU", "1")
    monkeypatch.setenv("KARA_GPU", "1")
    build.build_exe(False)
    args, kwargs = run.call_args
    assert "--clean" in args[0]
    assert "VOX0_GPU" not in kwargs["env"]
    assert "KARA_GPU" not in kwargs["env"]


def test_installer_preserves_identity_and_replaces_legacy_launchers():
    source = (ROOT / "packaging" / "installer.iss").read_text(encoding="utf-8")
    assert 'AppId={{7C1B4E62-9A3D-4F58-B0E7-2D6A5F8C1E90}' in source
    assert 'UsePreviousAppDir=yes' in source
    assert 'UsePreviousGroup=no' in source
    assert '"Vox0.exe"' in source
    assert "SettingsDir := GetEnv('LOCALAPPDATA') + '\\Kara';" in source
    assert 'Type: files; Name: "{app}\\Kara.exe"' in source
    assert 'ValueName: "Kara"; Flags: deletevalue' in source
    assert 'ValueName: "Vox0"; ValueData:' in source


def test_release_notes_keep_only_the_changelog_summary(monkeypatch, capsys):
    from tools import release_notes

    monkeypatch.setattr(release_notes, "section", lambda tag: "Product changes.")
    for version in ("0.3.5", "0.3.6"):
        monkeypatch.setattr(release_notes.sys, "argv", ["release_notes.py", "v" + version])
        assert release_notes.main() == 0
        assert capsys.readouterr().out == "Product changes."


@pytest.mark.parametrize("current", [False, True])
def test_signing_accepts_legacy_environment_and_prefers_vox0(monkeypatch, current):
    from unittest.mock import Mock

    run = Mock()
    monkeypatch.setattr(build, "run", run)
    monkeypatch.setattr(build.os.path, "exists", lambda path: True)
    monkeypatch.setenv("KARA_SIGN_COMMAND", "legacy-sign {file}")
    monkeypatch.delenv("VOX0_SIGN_COMMAND", raising=False)
    if current:
        monkeypatch.setenv("VOX0_SIGN_COMMAND", "vox0-sign {file}")
    signer = "vox0-sign" if current else "legacy-sign"
    assert build.sign_artifact("Vox0.exe")
    run.assert_called_once_with([signer, "Vox0.exe"])
    build.build_installer("0.3.6", True, False)
    assert "/DSignVox0=1" in run.call_args.args[0]
    assert f"/Svox0={signer} $f" in run.call_args.args[0]


def test_docs_release_label_matches_the_new_artifact_brand(monkeypatch):
    import re
    from tools import stamp_docs

    monkeypatch.setattr(stamp_docs, "last_commit_date", lambda path: "2026-10-11")
    text = '<!--app-name-->Kara<!--/app-name--> <!--app-version-->0.3.5<!--/app-version-->'
    for rel, pattern, replacement in stamp_docs.rules("0.3.6", None):
        if rel == "docs/index.html":
            text = re.sub(pattern, replacement, text)
    assert 'Kara' not in text
    assert '<!--app-name-->Vox0<!--/app-name-->' in text
    assert '0.3.6' in text
