import random

import yadisk

from src.bottoken import yadisk_token


async def get_pictures(total_cup_num: int, black_in: bool):
    """
    Connects to Yandex.Disk via token, randomly chooses
    total_cup_num cup-pics and returns us
    download-links.
    :param total_cup_num: int, number of cups,
    :param black_in: bool, whether to include
                     the black cup or not,
    :return: list of download-links.
    """

    y = yadisk.YaDisk(token=yadisk_token)
    files_A = [f.file for f in y.listdir("/cupbot/A")]
    # randomize which cups to send
    if not black_in:
        chosen_files = random.sample(files_A, k=total_cup_num)
    else:
        files_black = [f.file for f in y.listdir("/cupbot/black")]
        chosen_files = random.sample(files_A, k=total_cup_num - 1)
        chosen_files.extend(random.sample(files_black, k=1))
    return chosen_files
