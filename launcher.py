import os
import random
import subprocess

from locals import *


def launch(
        root=ROOT_PATH,
        java=JAVA_PATH,
        player="steve",
        memory=DEFAULT_MEMORY,
        width=1200,
        height=800,
        uuid=None,
        access_token=None,
):
    with open("assets/launch_template", 'r') as f:
        script = f.read()

    def rand_token():
        return "".join(
            str(
                chr(random.randint(97, 122))
                if random.randint(0, 1) else
                chr(random.randint(48, 57))
            )
            for i in range(32)
        )

    script = script.replace("{ROOT}", root). \
        replace("{JAVA}", java). \
        replace("{PLAYER}", player). \
        replace("{MEMORY}", str(memory)).\
        replace("{WIDTH}", str(width)). \
        replace("{HEIGHT}", str(height)). \
        replace("{VERSION}", VERSION). \
        replace("{UUID}", uuid if uuid else rand_token()). \
        replace("{ACCESS_TOKEN}", access_token if access_token else rand_token())

    subprocess.call(script)


if __name__ == '__main__':
    launch()
