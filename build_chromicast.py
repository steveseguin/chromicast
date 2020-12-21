from PyInstaller.utils.hooks import get_package_paths
import subprocess

subprocess.Popen([
      "pyinstaller", "--clean", "-F", "src/chromicast.py",
      "--onefile",
      "--icon","images/chromicast.ico",
      "--add-data", f"{get_package_paths('cefpython3')[1]}:cefpython3",
      "--hidden-import", "pkg_resources.py2_warn", "-n", "Chromicast"
])
