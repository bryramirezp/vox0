"""Release naming and the removal of the dynamic NVIDIA downloader."""
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("kara_build", ROOT / "packaging" / "build.py")
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)


def test_setup_names_are_versioned_and_distinct():
    assert Path(build.setup_path("0.3.4", False)).name == "Kara-Setup-0.3.4.exe"
    assert Path(build.setup_path("0.3.4", True)).name == "Kara-Setup-GPU-0.3.4.exe"


def test_distributed_icon_uses_full_logo_at_every_size():
    from PIL import Image

    icon = Image.open(ROOT / "assets" / "icon.ico")
    assert icon.ico.sizes() == {(n, n) for n in (16, 32, 48, 64, 128, 256)}
    for size in icon.ico.sizes():
        frame = icon.ico.getimage(size)
        centre = frame.getpixel((size[0] // 2, size[1] // 2))
        assert all(channel > 180 for channel in centre[:3]), size


def test_runtime_has_no_dynamic_gpu_downloader():
    source = (ROOT / "kara.py").read_text(encoding="utf-8")
    assert "gpu_component" not in source
    assert "GPU_MANIFEST_FILE" not in source
    assert not (ROOT / "gpu_component.py").exists()


def test_docs_stamp_updates_download_labels_and_urls(monkeypatch):
    import re
    from tools import stamp_docs

    monkeypatch.setattr(stamp_docs, "last_commit_date", lambda path: "2026-10-11")
    text = ('[Kara-Setup-0.3.4.exe](https://github.com/bryramirezp/kara/releases/download/v0.3.4/Kara-Setup-0.3.4.exe) '
            '[Kara-Setup-GPU-0.3.4.exe](https://github.com/bryramirezp/kara/releases/download/v0.3.4/Kara-Setup-GPU-0.3.4.exe)')
    for rel, pattern, replacement in stamp_docs.rules("0.3.5", None):
        if rel == "README.md":
            text = re.sub(pattern, replacement, text)
    assert "0.3.4" not in text
    assert text.count("Kara-Setup-0.3.5.exe") == 2
    assert text.count("Kara-Setup-GPU-0.3.5.exe") == 2


def test_build_cleans_intermediates_and_excludes_gpu_environment(monkeypatch):
    from unittest.mock import Mock

    run = Mock()
    monkeypatch.setattr(build, "run", run)
    monkeypatch.setattr(build.shutil, "rmtree", Mock())
    monkeypatch.setattr(build.os.path, "exists", lambda path: True)
    monkeypatch.setattr(build.os.path, "isdir", lambda path: False)
    monkeypatch.setenv("KARA_GPU", "1")
    build.build_exe(False)
    args, kwargs = run.call_args
    assert "--clean" in args[0]
    assert "KARA_GPU" not in kwargs["env"]
