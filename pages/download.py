import re
import shutil
import ssl
from gzip import GzipFile
from tarfile import TarFile
import tarfile
from urllib.error import URLError
from urllib.request import urlopen, Request
from zipfile import ZipFile

from wx.core import *

from launcher import launch
from libraries import jre32, jre64
from loader import *


def is_mod(name):
    return name.endswith('.jar') or name.endswith('.litemod')


class Task:

    @staticmethod
    def get_missing():
        missing = []

        # Update Mods

        try:
            with urlopen(
                    url=server_url + '/mods/planned',
                    timeout=5,
            ) as browser:
                content = json.loads(browser.read().decode('utf8'))
                for name in content:
                    if content[name]['client']:
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

        except Exception as e:
            print("Unable to get module list. [%s]" % e)

        # Add Tasks
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

        # Jre Part
        if OS == "Linux":
            if not Path(JAVA_PATH).exists():
                missing.append(JreTask())
        else:
            res = jre64['files'] if MACHINE.endswith('64') else jre32['files']

            for name in res:
                details = res[name]
                if details['type'] == 'file':
                    size = details['downloads']['raw']['size']
                    url = details['downloads']['raw']['url']
                    path = os.path.join('runtime', jre, name)
                    if need_load(path, size):
                        missing.append(
                            Task(url, str(Path(path)), size)
                        )

        return missing

    @staticmethod
    def get_non_used():
        non_used = []
        try:
            with urlopen(
                    url=server_url + '/mods/planned',
                    timeout=5,
            ) as browser:
                content = json.loads(browser.read().decode('utf8'))
                names = [
                    name
                    for name in content
                    if content[name]['client']
                ]

                for name in os.listdir(ROOT_PATH + "/.minecraft/mods"):
                    if is_mod(name) and name not in names:
                        non_used.append(str(Path(os.path.join(ROOT_PATH, '.minecraft/mods', name))))

        except URLError as e:
            print(e)
        return non_used

    def __init__(self, url, file, size):
        self.path = file
        self.url = url
        self.file = None
        self.size = size
        self._cancel = False
        self.browser = None

    @property
    def cancel(self):
        return self._cancel

    @cancel.setter
    def cancel(self, value):
        if value and self.browser:
            self.browser.close()
        self._cancel = value

    def run(self, downloadFrame):
        while True:
            try:
                file = self.file = File(str(self.path))
                self.browser = browser = urlopen(
                    url=Request(
                        url=self.url,
                        headers={
                            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                          "Chrome/80.0.3987.106 Safari/537.36 "
                        },
                    ),
                    timeout=5,
                    context=ssl.create_default_context()
                )
                try:
                    if self.cancel:
                        print("Cancelled Download Task: %s" % self.path)
                        file.close()
                        self.browser.close()
                        return
                    if self.size is None:
                        self.size = int(self.browser.headers.get("Content-Length"))
                    data = None
                    while data != b'':
                        data = browser.read(1024)
                        file.write(data)
                        downloadFrame.stream_size += len(data)
                        if self.cancel:
                            file.close()
                            browser.close()
                            print("Cancelled Download Task: %s" % self.path)
                            return
                except Exception as e:
                    file.close()
                    browser.close()
                    raise e
                file.close()
                browser.close()
                return True
            except Exception as e:
                print("Error Courred when trying to download %s from %s" % (self.file, self.url))
                print("Exception: ", e)
                print("Retry in 2 seconds")
                raise(e)
                time.sleep(2)

    @property
    def progress(self):
        if self.file:
            if self.size:
                return os.path.getsize(self.path) / self.size
            return 0
        return 0


class JreTask(Task):
    def __init__(self):
        link = "https://javadl.oracle.com/webapps/download/AutoDL?BundleId=242980_a4634525489241b9a9e1aa73d9e118e6" \
            if MACHINE.endswith('64') else \
            "https://javadl.oracle.com/webapps/download/AutoDL?BundleId=242978_a4634525489241b9a9e1aa73d9e118e6"
        super().__init__(
            url=link,
            file="./%s.tar.gz" % jre,
            size=None
        )

    def run(self):
        if not Path(self.path).exists():
            super(JreTask, self).run()
        if not re.match("jre[0-9]\.[0-9]\.[0-9]_[0-9]{1,5}", '\n'.join(os.listdir('runtime'))):
            with tarfile.open(self.path, 'r:gz') as obj:
                obj.extractall('runtime')
        os.rename(
            os.path.join('runtime', re.match("jre[0-9]\.[0-9]\.[0-9]_[0-9]{1,5}", '\n'.join(os.listdir('runtime')))[0] ),
            os.path.join('runtime', jre)
        )



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
        CallAfter(self.label.SetLabel, f"[{str(int(task.progress * 100)).rjust(3)}%] {str(Path(task.path))}")
        self.bar.slideTo(task.progress)

    def hide(self):
        CallAfter(self.SetPosition, (0, -100))

    def show(self):
        CallAfter(self.SetPosition, self.pos)


class DownloadFrame(BaseFrame):
    def __init__(self, parent, name, final_frame):
        super().__init__(
            parent=parent,
            size=(350, 450),
            style=DEFAULT_FRAME_STYLE ^ RESIZE_BORDER ^ MAXIMIZE_BOX | FRAME_FLOAT_ON_PARENT,
            title="Launch"
        )

        self.name = name
        self.final_frame = final_frame

        w, h = self.GetSize()
        self.SetIcon(Icon("assets/icon.ico"))
        self.SetBackgroundColour(Colour(38, 38, 38))

        self.tx_title = StaticText(self, size=(250, 32), pos=(50, 30), style=TE_CENTER, label="Checking Missing Assets")
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
        self.cancel = False
        self.Show(True)

        self.running_task = 0

        self.Bind(EVT_CLOSE, self.on_close)

        self.stream_size = 0

        Thread(target=self.centerThread).start()
        Thread(target=self.main_thread).start()

    def on_close(self, evt):
        print("Canceling Tasks")
        for task in self.tasks:
            task.cancel = True
        self.cancel = True
        print("Finished Cancel")
        CallAfter(self.GetParent().tx_name.Enable)
        CallAfter(self.GetParent().btn_play.Enable)
        self.Destroy()

    def create_task_thread(self, missing):
        url = 'https://launcher.mojang.com/v1/objects/0f275bc1547d01fa5f56ba34bdc87d981ee12daf/client.jar'
        size = 10180113
        path = Path(ROOT_PATH + "/.minecraft/versions/1.12.2/1.12.2.jar")
        do = True
        if path.exists():
            if os.path.getsize(path) == size:
                do = False
        if do:
            missing.append(Task(url, path, size))

        url = 'https://files.minecraftforge.net/maven/net/minecraftforge/forge/1.12.2-14.23.5.2854/forge-1.12.2-14.23.5.2854-universal.jar'
        size = 4464068
        path = Path(
            ROOT_PATH + "/.minecraft/libraries/net/minecraftforge/forge/1.12.2-14.23.5.2854/forge-1.12.2-14.23.5.2854.jar")
        do = True
        if path.exists():
            if os.path.getsize(path) == size:
                do = False
        if do:
            missing.append(Task(url, path, size))

        if missing:
            CallAfter(self.tx_title.SetLabel, "Loading Assets")

        for task in missing:
            if self.cancel:
                return
            while self.running_task >= 32:
                if self.cancel:
                    return
                time.sleep(0.1)
            self.running_task += 1
            Thread(target=self.download_task_handler, args=(task,)).start()

        for name in Task.get_non_used():
            os.remove(name)

    def main_thread(self):
        try:
            for i in range(7):
                self.tasks_widgets[i].hide()
            missing = Task.get_missing()
            count = len(missing)
            Thread(target=self.create_task_thread, args=(missing,)).start()
            last_count = 0
            last_size = 0
            speed = toSize(0) + '/sec'
            while self.completed != count:
                time.sleep(0.1)
                if self.cancel:
                    return
                count = len(missing)
                self.sum_progress.slideTo(self.completed / count)
                CallAfter(self.tx_sum.SetLabel, f"Tasks [{self.completed}/{count}]  {speed}")

                now = time.time()

                if now - last_count > 0.3:
                    last_count = now
                    speed = toSize((self.stream_size - last_size) / 0.3) + '/sec'
                    last_size = self.stream_size

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
            with File(ROOT_PATH + "/.minecraft/versions/1.12.2/1.12.2.json", 'w') as f:
                json.dump(libraries, f)
            with open("assets/1.12.json", 'r') as f:
                with File(ROOT_PATH + "/.minecraft/assets/indexes/1.12.json", 'w') as d:
                    d.write(f.read())
            natives_path = ROOT_PATH + f'/.minecraft/libraries/org/lwjgl/lwjgl/lwjgl-platform/2.9.2-nightly-20140822/lwjgl-platform-2.9.2-nightly-20140822-natives-{"linux" if OS == "Linux" else "windows"}.jar'
            with ZipFile(natives_path, 'r') as zip_ref:
                try:
                    shutil.rmtree(ROOT_PATH + "/.minecraft/versions/1.12.2/natives/")
                except FileNotFoundError:
                    pass
                zip_ref.extractall(ROOT_PATH + "/.minecraft/versions/1.12.2/natives/")
            CallAfter(self.tx_sum.SetLabel, f"* Completed! * ")
            self.sum_progress.slideTo(1)
            CallAfter(self.tx_title.SetLabel, "Launching Game")
            CallAfter(self.EnableCloseButton, False)
            CallAfter(self.final_frame.EnableCloseButton, False)
            time.sleep(1.5)
            CallAfter(self.final_frame.Destroy)
            Thread(target=launch, kwargs={"player": self.name}).start()
        except RuntimeError:
            CallAfter(self.Destroy)

    def download_task_handler(self, task):
        self.tasks.append(task)
        task.run(self)
        self.tasks.remove(task)
        self.completed += 1
        self.running_task -= 1
