import json
import os
from pathlib import Path
from libraries import content as libraries

from locals import *


server_url = "http://localhost:2005/"


class Objects:
    root = ROOT_PATH + "/.minecraft/assets/objects/"

    def __init__(self, name, details):
        self.hash = details["hash"]
        self.size = details["size"]
        self.name = name

    @property
    def done(self):
        if not Path(self.path).exists():
            return False
        return os.path.getsize(Path(self.path)) >= self.size

    @property
    def url(self):
        return f"http://resources.download.minecraft.net/{self.hash[:2]}/{self.hash}"

    @property
    def path(self):
        return f"{self.root}/{self.hash[:2]}/{self.hash}"


class Library:
    root = ROOT_PATH + '/.minecraft/libraries'

    def __init__(self, content):
        self.name = content["name"]
        self.downloads = content["downloads"]
        self.useless = False
        if self.downloads:
            if "artifact" in self.downloads:
                self.artifact = self.downloads["artifact"]
            else:
                self.artifact = self.downloads["classifiers"]["natives-windows"]
            self._path = self.artifact["path"]
            self.url = self.artifact["url"]
            self.sha1 = self.artifact["sha1"]
            self.size = self.artifact["size"]
        else:
            self.useless = True


    @property
    def done(self):
        if self.useless:
            return True
        path = Path(self.path)
        if path.exists():
            if os.path.getsize(path) == self.size:
                return True
        return False

    @property
    def path(self):
        return self.root + '/' + self._path


if __name__ == '__main__':
    content = {
                    "name": "com.mojang:patchy:1.1",
                    "downloads": {
                        "artifact": {
                            "path": "com/mojang/patchy/1.1/patchy-1.1.jar",
                            "url": "https://libraries.minecraft.net/com/mojang/patchy/1.1/patchy-1.1.jar",
                            "sha1": "aef610b34a1be37fa851825f12372b78424d8903",
                            "size": 15817
                        }
                    }
                }
