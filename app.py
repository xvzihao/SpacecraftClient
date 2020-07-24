import wx
from wx.core import *

from pages.login import *
from locals import *


class MainFrame(Frame):
    def __init__(self):
        super(MainFrame, self).__init__(
            parent=None,
            title="AMCL " + VERSION,
            size=(WIN_WIDTH, WIN_HEIGHT),
            style=CAPTION|MINIMIZE_BOX|CLOSE_BOX
        )
        self.screen = Panel(
            parent=self,
            pos=(0, 0),
            size=(WIN_WIDTH, WIN_HEIGHT),
        )
        self.SetIcon(Icon("assets/icon.ico"))
        self._page = LoginPage(self.screen)
        Panel(parent=self, size=(0, 0))
        self.SetMinSize((WIN_WIDTH, WIN_HEIGHT))
        self.screen.SetBackgroundColour(Colour(38, 38, 38))

        self.Bind(EVT_SIZING, self.on_resize)
        self.Bind(EVT_SIZE, self.on_resize)

    def on_resize(self, event: SizeEvent):
        w, h = event.GetSize()
        self.screen.SetSize(w - 16, h - 39)
        self._page.SetSize(w, h)
        self._page.on_resize(w, h)


if __name__ == '__main__':
    app = App()
    mainFrame = MainFrame()
    mainFrame.Show(True)
    app.MainLoop()