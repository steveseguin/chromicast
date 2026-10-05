"""Offline shutdown regressions. Run: python -m unittest discover -s tests -v"""
import pathlib
import subprocess
import sys
import unittest

# Execute each complete entry point in isolation. Only native/browser dependencies
# are stubbed; the application creates and joins real Python worker threads.
HARNESS = r"""
import sys, types, threading, time
source, mode = sys.argv[1:]
RealEvent = threading.Event
waiting, release, started = RealEvent(), RealEvent(), RealEvent()
events = []
class Event(RealEvent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        events.append(self)
    def wait(self, timeout=None):
        if self is events[0] and not self.is_set():
            waiting.set()
        return super().wait(timeout)
    def clear(self):
        super().clear()
        if len(events) > 1 and self is events[1]:
            release.set()
threading.Event = Event
class Browser:
    def GetUserData(self, key): return b"frame"
    def SetClientHandler(self, handler): pass
    def SendFocusEvent(self, focused): pass
    def WasResized(self): pass
    def CloseBrowser(self): print("CLOSED", flush=True)
class Window:
    def SetAsOffscreen(self, handle): pass
class Array:
    def reshape(self, shape): return self
ndi = types.SimpleNamespace(
    initialize=lambda: True, SendCreate=lambda: types.SimpleNamespace(),
    send_create=lambda settings: object(),
    VideoFrameV2=lambda: types.SimpleNamespace(), FOURCC_VIDEO_TYPE_RGBA=1,
    send_send_video_v2=lambda *args: None)
sys.modules["NDIlib"] = ndi
sys.modules["numpy"] = types.SimpleNamespace(
    frombuffer=lambda *args, **kwargs: Array(), uint8=int)
def sleep(seconds):
    if mode == "signaled_interrupt":
        started.set()
        release.wait()
time.sleep = sleep
def loop():
    if mode == "signaled_interrupt":
        assert started.wait(3), "worker did not start"
        assert events[0].is_set(), "camera signal must already be set"
    else:
        assert waiting.wait(3), "worker did not reach empty camera wait"
    print("READY", flush=True)
    if mode == "blocked_error":
        raise RuntimeError("simulated message-loop error")
    if mode != "normal":
        raise KeyboardInterrupt()
cef = types.SimpleNamespace(
    Initialize=lambda **kwargs: None, WindowInfo=Window,
    CreateBrowserSync=lambda **kwargs: Browser(), MessageLoop=loop,
    QuitMessageLoop=lambda: None,
    Shutdown=lambda: print("SHUTDOWN", flush=True))
sys.modules["cefpython3"] = types.SimpleNamespace(cefpython=cef)
sys.argv = [source]
exec(compile(open(source).read(), source, "exec"), {"__name__": "__main__"})
"""

class ShutdownTests(unittest.TestCase):
    def test_shutdown_paths(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        for entry in ("chromicast.py", "src/chromicast.py"):
            for mode in ("normal", "blocked_interrupt", "signaled_interrupt", "blocked_error"):
                with self.subTest(entry=entry, mode=mode):
                    try:
                        result = subprocess.run(
                            [sys.executable, "-u", "-c", HARNESS,
                             str(root / entry), mode],
                            capture_output=True, text=True, timeout=5)
                    except subprocess.TimeoutExpired as exc:
                        self.fail("Shutdown hung: %s %s; output: %r" %
                                  (entry, mode, exc.stdout))
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("READY", result.stdout)
                    self.assertIn("CLOSED", result.stdout)
                    self.assertIn("SHUTDOWN", result.stdout)

if __name__ == "__main__":
    unittest.main()
