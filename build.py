import PyInstaller.__main__
import os

# Get the absolute path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'src/main.py',  # Your main script
    '--name=JSON2SRT',  # Name of the executable
    '--onefile',  # Create a single executable file
    '--windowed',  # Don't show console window
    f'--icon={os.path.join(current_dir, "icon.ico")}',  # Icon file
    '--add-data=icon.ico;.',  # Include icon file in the executable
    '--add-data=src/ui;ui',  # Include ui module
    '--add-data=src/utils;utils',  # Include utils module
    '--clean',  # Clean PyInstaller cache
    '--noconfirm',  # Replace output directory without asking
    '--paths=src'  # Add src directory to Python path
])