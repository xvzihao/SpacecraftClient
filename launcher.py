import os
import random
import subprocess

from locals import *


def launch(
        root=str(Path(ROOT_PATH).absolute()),
        java=JAVA_PATH,
        player="steve",
        memory=DEFAULT_MEMORY,
        width=1200,
        height=800,
        uuid=None,
        access_token=None,
):

    def rand_token():
        return "".join(
            str(
                chr(random.randint(97, 122))
                if random.randint(0, 1) else
                chr(random.randint(48, 57))
            )
            for i in range(32)
        )

    script = LAUNCH_TEMPLATE.replace("{ROOT}", root). \
        replace("{PLAYER}", player). \
        replace("{MEMORY}", str(memory)).\
        replace("{WIDTH}", str(width)). \
        replace("{HEIGHT}", str(height)). \
        replace("{VERSION}", VERSION). \
        replace("{UUID}", uuid if uuid else rand_token()). \
        replace("{ACCESS_TOKEN}", access_token if access_token else rand_token())

    if OS == "Linux":
        launch_script = Path("./launch.sh")
        launch_script.write_text(str(Path(java).absolute()) + ' ' + script)
        subprocess.Popen(['bash', 'launch.sh'])

    else:
        subprocess.Popen(java+' '+script)


if __name__ == '__main__':
    launch()
