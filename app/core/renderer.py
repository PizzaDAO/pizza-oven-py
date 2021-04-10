#!/usr/bin/env python

import os
import subprocess

DEFAULT_FRAME = 9
DEFAULT_EXECUTABLE_PATH = os.environ["NATRON_PATH"]
DEFAULT_PROJECT_PATH = os.environ["NATRON_PROJECT_PATH"]
# output = "../../output/"
# datastore = "../../ingredients-db/"


current = os.path.dirname(os.path.realpath(__file__))

# os.environ["NATRON_INPUT"] = os.getcwd()


class BoxRenderer:
    def __init__(self):
        pass

    def render(self, executable_path, project_path, frame):
        # filename = "0000-box-cardboard.png"
        # fileout = "rp-#####-box.png"

        print(executable_path)
        print(project_path)

        subprocess.check_call(
            [
                f"{executable_path}/NatronRenderer",
                "-l",
                f"{current}/box.py",
                f"{project_path}/box.ntp",
                f"{frame}",
            ]
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Render components using Natron",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-f",
        "--frame",
        metavar="<fame>",
        default=DEFAULT_FRAME,
        type=int,
        help="The frame to render",
    )

    parser.add_argument(
        "-n",
        "--natron-path",
        metavar="<natron>",
        default=DEFAULT_EXECUTABLE_PATH,
        type=str,
        help="The folder where NatronRenderer exists",
    )

    parser.add_argument(
        "-p",
        "--project-path",
        metavar="<project>",
        default=DEFAULT_PROJECT_PATH,
        type=str,
        help="The folder where project files exist",
    )

    args = parser.parse_args()

    BoxRenderer().render(args.natron_path, args.project_path, args.frame)
