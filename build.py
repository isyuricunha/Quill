"""
Bragi build script.

Builds the Windows onedir application with PyInstaller and prepares a
classic ICO for Inno Setup from the application's selected icon artwork.
"""

import io
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path


def clean_build_files():
    print("Cleaning previous build files...")

    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")

    if os.path.exists("Bragi.spec"):
        os.remove("Bragi.spec")
        print("  Removed Bragi.spec")

    if os.path.exists("Quill.spec"):
        os.remove("Quill.spec")
        print("  Removed legacy Quill.spec")


def check_requirements():
    print("\nChecking build requirements...")

    requirements = [
        ("PyInstaller", "pyinstaller"),
        ("PIL", "pillow"),
    ]

    for import_name, package_name in requirements:
        try:
            __import__(import_name)
            print(f"  {package_name}: OK")
        except ImportError:
            print(f"  {package_name}: NOT FOUND")
            print(f"\nInstalling {package_name}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name]
            )
            print(f"  {package_name} installed successfully!")


def build_exe():
    print("\nBuilding Bragi.exe...")

    cmd = [
        "pyinstaller",
        "--onedir",
        "--windowed",
        "--name=Bragi",
        "--clean",
        "--icon=resources/icon.ico",
        "--add-data=resources/default_prompts.json;resources",
        "--add-data=resources/version.txt;resources",
        "--add-data=resources/icon.ico;resources",
        "--add-data=resources/icon_alpha.ico;resources",
        "--collect-submodules=core",
        "--collect-submodules=app",
        "--collect-submodules=ui",
        "--hidden-import=core.prompt_manager",
        "--collect-submodules=PySide6.QtCore",
        "--collect-submodules=PySide6.QtGui",
        "--collect-submodules=PySide6.QtWidgets",
        "--hidden-import=PySide6",
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "--exclude-module=pandas",
        "--exclude-module=scipy",
        "--exclude-module=PIL",
        "--exclude-module=PyQt5",
        "--exclude-module=tkinter",
        "main.py",
    ]

    print("\nRunning PyInstaller...")
    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print("\n" + "=" * 50)
        print("Build FAILED!")
        print("=" * 50)
        return False

    print("\n" + "=" * 50)
    print("Build completed successfully!")
    print("=" * 50)

    dist_folder = Path("dist") / "Bragi"
    exe_path = dist_folder / "Bragi.exe"
    if exe_path.exists():
        total_size = sum(
            f.stat().st_size for f in dist_folder.rglob("*") if f.is_file()
        )
        size_mb = total_size / (1024 * 1024)
        print(f"\nApplication folder: {dist_folder}")
        print(f"Total size: {size_mb:.2f} MB")

        print("\n" + "-" * 50)
        print("How to use:")
        print("  1. Copy the entire 'dist/Bragi' folder to your desired location")
        print("  2. Run Bragi.exe inside the folder")
        print("  3. Configure API settings on first run")
        print("  4. Press Ctrl+Space to activate!")
        print("-" * 50)

    return True


def _encode_classic_icon_frame(image):
    """Encode one RGBA image as a classic 32-bit Windows ICO DIB frame."""
    image = image.convert("RGBA")
    width, height = image.size
    pixels = image.load()

    xor_bitmap = bytearray()
    for y in range(height - 1, -1, -1):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            xor_bitmap.extend((blue, green, red, alpha))

    mask_stride = ((width + 31) // 32) * 4
    and_mask = bytearray(mask_stride * height)
    for row, y in enumerate(range(height - 1, -1, -1)):
        row_offset = row * mask_stride
        for x in range(width):
            if pixels[x, y][3] < 128:
                and_mask[row_offset + (x // 8)] |= 0x80 >> (x % 8)

    bitmap_header = struct.pack(
        "<IIIHHIIIIII",
        40,
        width,
        height * 2,
        1,
        32,
        0,
        len(xor_bitmap),
        0,
        0,
        0,
        0,
    )
    return bitmap_header + bytes(xor_bitmap) + bytes(and_mask)


def _load_largest_png_icon_frame(icon_path):
    """Extract the largest PNG-backed frame from an ICO without Pillow's ICO parser."""
    from PIL import Image

    data = Path(icon_path).read_bytes()
    if len(data) < 6:
        raise ValueError(f"Icon file is too small: {icon_path}")

    reserved, icon_type, count = struct.unpack_from("<HHH", data, 0)
    if reserved != 0 or icon_type != 1 or count < 1:
        raise ValueError(f"Invalid ICO header: {icon_path}")

    best = None
    for index in range(count):
        entry_offset = 6 + (index * 16)
        if entry_offset + 16 > len(data):
            raise ValueError(f"Truncated ICO directory: {icon_path}")

        width_byte, height_byte, _, _, _, _, size, offset = struct.unpack_from(
            "<BBBBHHII", data, entry_offset
        )
        width = width_byte or 256
        height = height_byte or 256
        end = offset + size
        if offset < 0 or size <= 0 or end > len(data):
            continue

        payload = data[offset:end]
        if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
            continue

        score = width * height
        if best is None or score > best[0]:
            best = (score, width, height, payload)

    if best is None:
        raise ValueError(f"No PNG-backed frame found in icon: {icon_path}")

    _, width, height, payload = best
    with Image.open(io.BytesIO(payload)) as frame:
        image = frame.convert("RGBA")
        image.load()

    print(f"  Extracted source icon frame: {width}x{height}")
    return image


def prepare_installer_icon():
    """Create an Inno-compatible ICO without changing the app's icon artwork."""
    from PIL import Image

    source_path = Path("resources") / "icon.ico"
    output_path = Path("build") / "setup_icon.ico"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    source = _load_largest_png_icon_frame(source_path)
    sizes = (16, 32, 48, 64, 128, 256)
    frames = []
    for size in sizes:
        resized = source.resize((size, size), Image.Resampling.LANCZOS)
        frames.append((size, _encode_classic_icon_frame(resized)))

    offset = 6 + (16 * len(frames))
    directory_entries = []
    for size, payload in frames:
        dimension = 0 if size == 256 else size
        directory_entries.append(
            struct.pack(
                "<BBBBHHII",
                dimension,
                dimension,
                0,
                0,
                1,
                32,
                len(payload),
                offset,
            )
        )
        offset += len(payload)

    icon_data = (
        struct.pack("<HHH", 0, 1, len(frames))
        + b"".join(directory_entries)
        + b"".join(payload for _, payload in frames)
    )
    output_path.write_bytes(icon_data)
    print(f"\nPrepared Inno Setup icon: {output_path} ({len(icon_data)} bytes)")


def main():
    print("=" * 50)
    print("Bragi Build Script")
    print("=" * 50)

    if not Path("main.py").exists():
        print("\nError: main.py not found!")
        print("Please run this script from the Bragi root directory.")
        sys.exit(1)

    version_file = Path("resources/version.txt")
    if not version_file.exists():
        print("\nError: resources/version.txt not found!")
        sys.exit(1)

    clean_build_files()
    check_requirements()
    success = build_exe()

    if success:
        prepare_installer_icon()
        print("\nBuild completed successfully!")
        sys.exit(0)

    print("\nBuild failed. Please check the error messages above.")
    sys.exit(1)


if __name__ == "__main__":
    main()
