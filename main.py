from pathlib import Path
from organiseMyProjects.logUtils import getLogger, setApplication

thisApplication = Path(__file__).parent.name
setApplication(thisApplication)

logger = getLogger(includeConsole=False)

try:
    from ui.mainMenu import mainMenu as tkinterMainMenu
except ModuleNotFoundError as exc:
    if exc.name is None or exc.name != "ui":
        raise
    tkinterMainMenu = None

try:
    from qt.mainMenu import mainMenu as qtMainMenu
except ModuleNotFoundError as exc:
    if exc.name is None or exc.name not in {"qt", "PySide6"}:
        raise
    qtMainMenu = None


def main():
    global logger

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args()

    dryRun = not args.confirm

    logDir = Path.home() / ".local" / "state" / thisApplication
    logDir.mkdir(parents=True, exist_ok=True)

    logger = getLogger(
        logDir=logDir,
        includeConsole=True,
        dryRun=dryRun,
    )

    logger.doing("main")
    if tkinterMainMenu is not None:
        tkinterMainMenu()
    elif qtMainMenu is not None:
        qtMainMenu()
    else:
        logger.info(
            "No UI scaffold installed. Run `createProject --update --ui` "
            "and/or `createProject --update -qt` to add GUI templates."
        )
    logger.done("main")


if __name__ == "__main__":
    main()
