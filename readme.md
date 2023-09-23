# Website (webRTC) to NDI source headlessly

It works enough to output a website (include VDO.Ninja streams) into an NDI Video output. It can do this headlessly.

This Code is me tinkering around with ideas; it is unfinished. Audio isn't yet supported.

It is based on the chromicam repo I made. https://github.com/steveseguin/chromicam 

It requires a couple dependencies

```
cefpython3>=66.0
numpy>=1.14.0
```

and you'll need the NDI SDK and the following, which requires compiling.
```
https://github.com/buresu/ndi-python
```

After that, you can run with just python as a script, or you can compile into an app.  If you want to try building Chromicast, the following is the basic idea, but good luck! Dependencies are a pain to sort out well.

# macOS Build
```
python3 build chromicast.py pack
```
# Windows Build
```
pyinstaller --onefile --hidden-import='pkg_resources.py2_warn' --icon=chromicast.ico chromicast.py
```
# find the location of CEF on macOS
```
sudo find / | grep "Chromium Embedded Framework"
```

