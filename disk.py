import yadisk
from bottoken import yadisk_token


def get_pictures():
    """bla bla.
    Returns:
        list: urls to pics
    """
    y = yadisk.YaDisk(token=yadisk_token)
    files = [f.file for f in y.listdir("/cupbot/A")]
    print(files)
    return files
