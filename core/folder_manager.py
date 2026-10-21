from core.paths import FOLDERS, path


class FolderManager:

    @staticmethod
    def create():

        for folder in FOLDERS:
            folder.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def exists(folder):

        return path(folder).exists()
