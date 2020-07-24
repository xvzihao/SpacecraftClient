import time
from threading import Thread

from wx.core import *
from locals import *


class LoginPage(Page):
    def __init__(self, parent):
        super().__init__(parent)
        self.image_container = Panel(self)
        self.image_container.SetBackgroundColour(Colour(0, 0, 0))
        self.img_earth = StaticBitmap(self.image_container, bitmap=get.scaled(get.image("assets/earth.png"), 0.6))
        self.pressed = False

        self.title = StaticBitmap(self, bitmap=get.scaled(get.image("assets/tx_space_craft.png"), 0.32))
        self.tx_name = TextCtrl(self, size=(200, 32), style=TE_CENTER)
        self.tx_name.SetForegroundColour(Colour(255, 255, 255))
        self.tx_name.SetBackgroundColour(Colour(0, 0, 0))
        self.tx_name.SetFont(
            wx.Font(16, MODERN, NORMAL, NORMAL, False, u'Verdana')
        )

        self.btn_play = Button(
            parent=self,
            size=(180, 50),
            style=NO_BORDER,
            label="Launch",
        )
        self.btn_play.SetFont(
            wx.Font(16, MODERN, NORMAL, BOLD, False, u'Verdana')
        )
        self.btn_play.SetBackgroundColour(Colour(45, 215, 100))
        self.btn_play.SetForegroundColour(Colour(255, 255, 255))

        self.btn_play.Bind(
            EVT_BUTTON, lambda evt: Thread(target=self.on_press).start() if not self.pressed else None
        )
        self.btn_play.Bind(
            EVT_ENTER_WINDOW,
            lambda evt: self.btn_play.SetBackgroundColour(Colour(75, 232, 130) if not self.pressed else Colour(45, 202, 100))
        )
        self.btn_play.Bind(
            EVT_LEAVE_WINDOW, lambda evt: self.btn_play.SetBackgroundColour(
                Colour(45, 215, 100) if not self.pressed else Colour(45, 202, 100))
        )

        self.label_name = StaticText(self, label="Player Name: ")
        self.label_name.SetForegroundColour(Colour(255, 255, 255))
        self.label_name.SetFont(
            wx.Font(14, MODERN, NORMAL, NORMAL, False, u'Verdana')
        )

        self.on_resize(*self.GetSize())

    def on_press(self):
        self.pressed = True
        self.btn_play.SetBackgroundColour(Colour(45, 202, 100))
        time.sleep(1)
        self.pressed = False
        self.btn_play.SetBackgroundColour(Colour(45, 215, 100))

    def on_resize(self, width, height):
        self.image_container.SetSize((width * (4 / 7), height))
        w, h = self.img_earth.GetSize()
        w /= 2
        h /= 2
        self.img_earth.SetPosition((
            width * (2 / 7) - w, height * (23 / 48) - h
        ))

        w, h = self.title.GetSize()
        w /= 2
        h /= 2
        self.title.SetPosition((
            width * (7 / 9) - w, height * (1 / 5) - h
        ))

        w, h = self.tx_name.GetSize()
        w /= 2
        h /= 2
        self.tx_name.SetPosition((
            width * (7 / 9) - w, height * (1 / 2) - h
        ))
        self.label_name.SetPosition((
            width * (7 / 9) - w - 16, height * (1 / 2) - h - 32
        ))

        w, h = self.btn_play.GetSize()
        w /= 2
        h /= 2
        self.btn_play.SetPosition((
            width * (7 / 9) - w, height * (7 / 9) - h
        ))
