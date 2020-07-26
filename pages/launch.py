import re

from locals import *
from pages.download import DownloadFrame


class LaunchPage(Page):
    def __init__(self, parent):
        super().__init__(parent)
        self.image_container = Panel(self)
        self.image_container.SetBackgroundColour(Colour(0, 0, 0))
        self.img_earth = StaticBitmap(self.image_container, bitmap=get.scaled(get.image("assets/earth.png"), 0.6))
        self.pressed = False
        self.launchable = False

        self.title = StaticBitmap(self, bitmap=get.scaled(get.image("assets/tx_space_craft.png"), 0.32))
        self.tx_name = TextCtrl(self, size=(200, 32), style=TE_CENTER | TE_PROCESS_ENTER)
        self.tx_name.SetForegroundColour(Colour(255, 255, 255))
        self.tx_name.SetBackgroundColour(Colour(0, 0, 0))
        self.tx_name.SetFont(
            wx.Font(16, MODERN, NORMAL, NORMAL, False, u'Verdana')
        )
        self.tx_name.Bind(EVT_TEXT, self.on_text)
        self.tx_name.Bind(EVT_TEXT_ENTER, lambda evt: self.btn_play.SetFocus())

        self.btn_play = Button(
            parent=self,
            size=(180, 50),
            style=NO_BORDER,
            label="Launch",
        )
        self.btn_play.SetFont(
            wx.Font(16, MODERN, NORMAL, BOLD, False, u'Verdana')
        )
        self.btn_play.SetBackgroundColour(Colour(128, 128, 128))
        self.btn_play.SetForegroundColour(Colour(255, 255, 255))

        self.btn_play.Bind(
            EVT_BUTTON, lambda evt: self.on_press() if not self.pressed else None
        )
        self.btn_play.Bind(
            EVT_ENTER_WINDOW,
            self.on_enter_btn
        )
        self.btn_play.Bind(
            EVT_LEAVE_WINDOW, self.on_leave_btn
        )

        self.label_name = StaticText(self, label="Player Name: ")
        self.label_name.SetForegroundColour(Colour(255, 255, 255))
        self.label_name.SetFont(
            wx.Font(14, MODERN, NORMAL, NORMAL, False, u'Verdana')
        )

        self.on_resize(*self.GetSize())

        self._last_name = self.tx_name.GetValue()

    def on_text(self, evt: CommandEvent):
        value = evt.GetString()
        if len(value) > 16:
            cursor = self.tx_name.GetInsertionPoint()
            CallAfter(self.tx_name.SetValue, self._last_name)
            CallAfter(self.tx_name.SetInsertionPoint, (cursor - 1))
            CallAfter(self.btn_play.SetBackgroundColour, Colour(45, 202, 100))
            value = self.tx_name.GetValue()
        if re.fullmatch("^[a-zA-Z0-9_\-]{2,16}$", value):
            self._last_name = value
            self.launchable = True
            CallAfter(self.btn_play.SetBackgroundColour, Colour(45, 202, 100))
        else:
            CallAfter(self.btn_play.SetBackgroundColour, Colour(128, 128, 128))
            self.launchable = False

    def on_enter_btn(self, evt):
        if self.launchable:
            CallAfter(self.btn_play.SetBackgroundColour, (Colour(75, 232, 130) if not self.pressed else Colour(45, 202, 100)))
        else:
            CallAfter(self.btn_play.SetBackgroundColour, Colour(128, 128, 128))

    def on_leave_btn(self, evt):
        if self.launchable:
            CallAfter(self.btn_play.SetBackgroundColour, (Colour(45, 215, 100) if not self.pressed else Colour(45, 202, 100)))
        else:
            CallAfter(self.btn_play.SetBackgroundColour, Colour(128, 128, 128))

    def on_press(self):
        if self.launchable:
            self.pressed = True
            CallAfter(self.btn_play.SetBackgroundColour, Colour(45, 202, 100))
            frame = DownloadFrame(self, self.tx_name.GetValue(), self.GetParent().GetParent())
            self.btn_play.Disable()
            self.tx_name.Disable()
            self.pressed = False
            CallAfter(self.btn_play.SetBackgroundColour, Colour(45, 215, 100))
        else:
            CallAfter(self.btn_play.SetBackgroundColour, Colour(128, 128, 128))

    def on_resize(self, width, height):
        CallAfter(self.image_container.SetSize, (width * (4 / 7), height))
        w, h = self.img_earth.GetSize()
        w /= 2
        h /= 2
        CallAfter(self.img_earth.SetPosition,(
            width * (2 / 7) - w, height * (23 / 48) - h
        ))

        w, h = self.title.GetSize()
        w /= 2
        h /= 2
        CallAfter(self.title.SetPosition, (
            width * (7 / 9) - w, height * (1 / 5) - h
        ))

        w, h = self.tx_name.GetSize()
        w /= 2
        h /= 2
        CallAfter(self.tx_name.SetPosition, (
            width * (7 / 9) - w, height * (1 / 2) - h
        ))
        self.label_name.SetPosition((
            width * (7 / 9) - w - 16, height * (1 / 2) - h - 32
        ))

        w, h = self.btn_play.GetSize()
        w /= 2
        h /= 2
        CallAfter(self.btn_play.SetPosition,(
            width * (7 / 9) - w, height * (7 / 9) - h
        ))
