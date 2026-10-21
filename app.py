import sys

from core.application import Application


def main():

    headless = any(
        flag in sys.argv
        for flag in ("--headless", "-h")
    )

    app = Application(headless=headless)

    if headless:

        app.run()

    else:

        from gui import run_gui

        run_gui(app)


if __name__ == "__main__":

    main()