#!/usr/bin/env python

import os
import subprocess

DEFAULT_FRAME = 9
DEFAULT_EXECUTABLE_PATH = os.environ["NATRON_PATH"]
DEFAULT_PROJECT_PATH = os.environ["NATRON_PROJECT_PATH"]

current = os.path.dirname(os.path.realpath(__file__))


class BoxRenderer:
    """Render Boxes"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, frame):
        subprocess.check_call(
            [
                f"{executable_path}/NatronRenderer",
                "-l",
                f"{current}/box.py",
                f"{project_path}/box.ntp",
                f"{frame}",
            ]
        )


class PaperRenderer:
    """Render Paper"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, frame):
        subprocess.check_call(
            [
                f"{executable_path}/NatronRenderer",
                "-l",
                f"{current}/paper.py",
                f"{project_path}/waxpaper.ntp",
                f"{frame}",
            ]
        )


class CrustRenderer:
    """Render Crust"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, frame):
        subprocess.check_call(
            [
                f"{executable_path}/NatronRenderer",
                "-l",
                f"{current}/crust.py",
                f"{project_path}/crust.ntp",
                f"{frame}",
            ]
        )


class SauceRenderer:
    """Render sauces"""

    def __init__(self):
        pass

    def render(self, executable_path, project_path, frame):
        subprocess.check_call(
            [
                f"{executable_path}/NatronRenderer",
                "-l",
                f"{current}/sauce.py",
                f"{project_path}/sauce.ntp",
                f"{frame}",
            ]
        )


if __name__ == "__main__":
    """invoke the rendering steps via the command line"""
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

    parser.add_argument(
        "-r",
        "--recipe-path",
        metavar="<project>",
        default=DEFAULT_PROJECT_PATH,
        type=str,
        help="The folder where project files exist",
    )

    args = parser.parse_args()

    BoxRenderer().render(args.natron_path, args.project_path, args.frame)
    PaperRenderer().render(args.natron_path, args.project_path, args.frame)
    CrustRenderer().render(args.natron_path, args.project_path, args.frame)
    SauceRenderer().render(args.natron_path, args.project_path, args.frame)
