"""
Bragi build script.

Builds the Windows onedir application with PyInstaller.
"""

import os
import shutil
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
    print("\nChecking requirements...")

    try:
        import PyInstaller  # noqa: F401
        print("  PyInstaller: OK")
    except ImportError:
        print("  PyInstaller: NOT FOUND")
        print("\nInstalling PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("  PyInstaller installed successfully!")


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
        print("\nBuild completed successfully!")
        sys.exit(0)

    print("\nBuild failed. Please check the error messages above.")
    sys.exit(1)


if __name__ == "__main__":
    main()
