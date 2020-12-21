It works enough to output a website (include OBS.Ninja streams) into an NDI Video output. It can do this headlessly.

This Code is me tinkering around with ideas; it is unfinished. Audio isn't yet supported.

It is based on the chromicast repo I made. https://github.com/steveseguin/chromicam 

# macOS Build
python3 build chromicast.py pack

# Windows Build
pyinstaller --onefile --hidden-import='pkg_resources.py2_warn' --icon=chromicast.ico chromicast.py

# find the location of CEF on macOS
sudo find / | grep "Chromium Embedded Framework"

