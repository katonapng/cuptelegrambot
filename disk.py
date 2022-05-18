import yadisk
from bottoken import yadisk_token


def get_pictures(total_cup_num: int, black_in: bool):
    """bla bla.
    Returns:
        list: urls to pics
    """
    # TODO ALL
    y = yadisk.YaDisk(token=yadisk_token)
    files = [f.file for f in y.listdir("/cupbot/A")]
    print(files)
    return files
