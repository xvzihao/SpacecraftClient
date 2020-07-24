import time
from pathlib import Path
from threading import Thread

from wx.core import *
import get

VERSION = 'pre1.0'

WIN_WIDTH = 960
WIN_HEIGHT = 600
ROOT_PATH = '.'


def File(filename, mode='wb'):
    path = Path(ROOT_PATH+'/'+filename)
    parent = str(path.parent).replace('\\', '/').split('/')
    current = ''
    while parent:
        current += parent.pop(0) + '/'
        if not Path(current).exists():
            try:
                Path(current).mkdir()
            except FileExistsError:
                pass
    return open(filename, mode)


class BaseFrame(Frame):
    def centerThread(self):
        sw, sh = DisplaySize()
        sw /= 2
        sh /= 2

        w, h = self.GetSize()
        w /= 2
        h /= 2

        target_x = sw - w
        target_y = sh - h

        start = time.time()
        while time.time() - start < 0.7:
            x, y = self.GetPosition()
            self.SetPosition((
                x - (x - target_x) / 5, y - (y - target_y) / 5
            ))
            time.sleep(1/60)


class ProgressBar(Panel):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        w, h = self.GetSize()
        self.SetBackgroundColour(Colour(50, 50, 50))
        self.SetForegroundColour(Colour(255, 255, 255))
        self.child = Panel(self, size=(1, h))
        self.child.SetBackgroundColour(Colour(0, 200, 0))
        self.child.SetPosition((0, 0))
        self.target = 0
        Thread(target=self._slideTo).start()

    def slideTo(self, value):
        self.target = value

    def _slideTo(self):
        width, height = self.GetSize()
        w, h = self.child.GetSize()
        try:
            while True:
                w, h = self.child.GetSize()
                self.child.SetSize((w - (w - (width * (self.target + 0.05))) / 20, height))
                time.sleep(1/60)
        except Exception as e:
            print(e)

    def update(self):
        pass

    def SetSize(self, size):
        super(ProgressBar, self).SetSize(size)
        self.child.SetPosition((0, 0))


class Page(Panel):
    def __init__(self, parent):
        super(Page, self).__init__(
            parent,
        )
        self.SetSize(parent.GetSize())

    def on_resize(self, width, height):
        pass
