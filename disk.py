import yadisk
import random
from bottoken import yadisk_token


def get_pictures(total_cup_num: int, black_in: bool):
    """

    :param total_cup_num:
    :param black_in:
    :return: list of download-links
    """
    # TODO ALL
    # randomize what cups to send
    y = yadisk.YaDisk(token=yadisk_token)
    files_A = [f.file for f in y.listdir("/cupbot/A")]
    if not black_in:
        chosen_files = random.sample(files_A, k=total_cup_num)
    else:
        files_black = [f.file for f in y.listdir("/cupbot/black")]
        chosen_files = random.sample(files_A, k=total_cup_num - 1)
        chosen_files.append(random.sample(files_black, k=1))
    return chosen_files
