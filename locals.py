
from wx.core import *
import get

VERSION = 'pre1.0'

WIN_WIDTH = 960
WIN_HEIGHT = 600


class Page(Panel):
    def __init__(self, parent):
        super(Page, self).__init__(
            parent,
        )
        self.SetSize(parent.GetSize())

    def on_resize(self, width, height):
        pass
