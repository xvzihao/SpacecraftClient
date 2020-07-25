import ssl
from socket import timeout
from urllib.error import URLError
from urllib.request import urlopen, Request
from zipfile import ZipFile

from launcher import launch
from locals import *
from loader import *
from wx.core import *


class Task:

    @staticmethod
    def get_missing():
        missing = []

        try:
            with urlopen(
                url=server_url+'/mods/planned',
                timeout=5,
            ) as browser:
                content = json.loads(browser.read().decode('utf8'))
                for name in content:
                    link = content[name]['link']
                    with urlopen(
                        url=Request(
                            url=link,
                            headers={"User-Agent": "SpaceCraft-Client"}
                        ),
                        context=ssl.create_default_context()
                    ) as b:
                        size = int(b.headers.get("Content-Length"))
                        path = os.path.join(ROOT_PATH, ".minecraft/mods/", name)
                        if not Path(path).exists():
                            missing.append(
                                Task(link, path, size)
                            )
                        elif os.path.getsize(path) != size:
                            missing.append(
                                Task(link, path, size)
                            )

        except URLError as e:
            print(e)
        with File('assets/1.12.json', 'r') as f:
            objs = json.load(f)["objects"]
        for name in objs:
            obj = Objects(name, objs[name])
            if not obj.done:
                missing.append(Task(obj.url, obj.path, obj.size))

        for patch in libraries["patches"]:
            lib = patch["libraries"]
            for item in lib:
                l = Library(item)
                if not l.done:
                    missing.append(
                        Task(l.url, l.path, l.size)
                    )

        return missing

    def __init__(self, url, file, size):
        self.path = file
        self.url = url
        self.file = None
        self.size = size

    def run(self):
        file = self.file = File(str(self.path))
        browser = urlopen(
            url=Request(
                url=self.url,
                headers={
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/80.0.3987.106 Safari/537.36 "
                },
            ),
            context=ssl.create_default_context()
        )
        try:
            data = None
            while data != b'':
                data = browser.read(1024)
                file.write(data)
        except Exception as e:
            file.close()
            browser.close()
            raise e
        file.close()
        browser.close()

    @property
    def progress(self):
        if self.file:
            return os.path.getsize(self.path) / self.size
        return 0


class TaskBar(Panel):

    def __init__(self, parent, pos):
        super(TaskBar, self).__init__(
            parent=parent,
            size=(325, 30),
            pos=pos
        )
        self.SetBackgroundColour(Colour(100, 100, 100))
        w, h = self.GetSize()
        self.bar = ProgressBar(self, size=(w, 5), pos=(0, 0))
        self.bar.child.SetBackgroundColour(Colour(0, 200, 200))
        self.label = StaticText(self, pos=(5, 12), size=(w - 10, h - 20))
        self.label.SetForegroundColour(Colour(255, 255, 255))
        self.label.SetLabel("*")
        self.pos = self.GetPosition()

    def set_state(self, task):
        self.label.SetLabel(f"[{str(int(task.progress * 100)).rjust(3)}%] {task.path}")
        self.bar.slideTo(task.progress)

    def hide(self):
        self.SetPosition((0, -100))

    def show(self):
        self.SetPosition(self.pos)


class DownloadFrame(BaseFrame):
    def __init__(self, parent, name, final_frame):
        super().__init__(
            parent=parent,
            size=(350, 450),
            style=DEFAULT_FRAME_STYLE ^ RESIZE_BORDER ^ MAXIMIZE_BOX| FRAME_FLOAT_ON_PARENT,
            title="Download Game"
        )

        self.name = name
        self.final_frame = final_frame

        w, h = self.GetSize()
        self.SetIcon(Icon("assets/icon.ico"))
        self.SetBackgroundColour(Colour(38, 38, 38))

        self.tx_title = StaticText(self, size=(200, 32), pos=(70, 30), style=TE_CENTER, label="Loading Resources")
        self.sum_progress = ProgressBar(self, size=(w - 38, 5), pos=(10, h * (1 / 6) + 10))
        self.tx_sum = StaticText(self, size=(w - 80, 15), pos=(30, h * (1 / 6) - 8), style=TE_CENTER)
        self.tx_sum.SetForegroundColour(Colour(255, 255, 255))
        self.tx_sum.SetLabel("*")

        self.tx_title.SetForegroundColour(Colour(255, 255, 255))
        self.tx_title.SetFont(
            wx.Font(16, MODERN, NORMAL, NORMAL, False, u'Verdana')
        )

        self.tasks_widgets = [
            TaskBar(self, (5, 100 + i * 45))
            for i in range(7)
        ]
        self.tasks = []

        self.completed = 0
        self.Show(True)

        self.Bind(EVT_CLOSE, self.on_close)

        Thread(target=self.centerThread).start()
        Thread(target=self.main_thread).start()

    def on_close(self, evt):
        self.GetParent().tx_name.Enable()
        self.GetParent().btn_play.Enable()
        self.Destroy()

    def Destory(self):
        super().Destroy()

    def create_task_thread(self, missing):
        url = 'https://launcher.mojang.com/v1/objects/0f275bc1547d01fa5f56ba34bdc87d981ee12daf/client.jar'
        size = 10180113
        path = Path(ROOT_PATH+"/.minecraft/versions/1.12.2/1.12.2.jar")
        do = True
        if path.exists():
            if os.path.getsize(path) == size:
                do = False
        if do:
            missing.append(Task(url, path, size))

        url = 'https://files.minecraftforge.net/maven/net/minecraftforge/forge/1.12.2-14.23.5.2854/forge-1.12.2-14.23.5.2854-universal.jar'
        size = 4464068
        path = Path(ROOT_PATH+"/.minecraft/libraries/net/minecraftforge/forge/1.12.2-14.23.5.2854/forge-1.12.2-14.23.5.2854.jar")
        do = True
        if path.exists():
            if os.path.getsize(path) == size:
                do = False
        if do:
            missing.append(Task(url, path, size))

        for task in missing:
            Thread(target=self.task_handler, args=(task, )).start()

    def main_thread(self):
        for i in range(7):
            self.tasks_widgets[i].hide()
        missing = Task.get_missing()
        count = len(missing)
        Thread(target=self.create_task_thread, args=(missing, )).start()
        while self.completed != count:
            count = len(missing)
            self.sum_progress.slideTo(self.completed / count)
            self.tx_sum.SetLabel(f"Tasks [{self.completed}/{count}]")

            try:
                non_hide_list = []
                for i in range(min(7, len(self.tasks))):
                    self.tasks_widgets[i].set_state(self.tasks[i])
                    non_hide_list.append(i)
                for i in range(7):
                    if i in non_hide_list:
                        self.tasks_widgets[i].show()
                    else:
                        self.tasks_widgets[i].hide()
            except IndexError:
                pass

            time.sleep(0.2)
        with File(ROOT_PATH+"/.minecraft/versions/1.12.2/1.12.2.json", 'w') as f:
            json.dump(libraries, f)
        with open(ROOT_PATH+"/assets/1.12.json", 'r') as f:
            with File(ROOT_PATH+"/.minecraft/assets/indexes/1.12.json", 'w') as d:
                d.write(f.read())
        natives_path = ROOT_PATH+'/.minecraft/libraries/org/lwjgl/lwjgl/lwjgl-platform/2.9.2-nightly-20140822/lwjgl-platform-2.9.2-nightly-20140822-natives-windows.jar'
        with ZipFile(natives_path, 'r') as zip_ref:
            zip_ref.extractall(ROOT_PATH+"/.minecraft/versions/1.12.2/natives/")
        self.tx_sum.SetLabel(f"* Completed! * ")
        self.sum_progress.slideTo(1)
        time.sleep(1.5)
        self.final_frame.Destroy()
        Thread(target=launch, kwargs={"player": self.name}).start()

    def task_handler(self, task):
        self.tasks.append(task)
        task.run()
        self.tasks.remove(task)
        self.completed += 1
