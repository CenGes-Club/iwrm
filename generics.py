import csv
import os
from datetime import datetime, timedelta


DATA_LOG_PATH = 'data/logs.csv'


def write_to_csv(filepath: str, data: list):
    with open(filepath, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(data)


def rename_log_file(now: datetime) -> None:
    previous_day: str = (now - timedelta(days=1)).strftime("%m-%d-%y")  # format should be 'mm-dd'
    os.rename(DATA_LOG_PATH, DATA_LOG_PATH[:-4] + '_' + previous_day + DATA_LOG_PATH[-4:])


def get_next_midnight(now: datetime) -> datetime:
    """get next midnight
    Args:
        now:
        datetime when the data was retrieved
    Returns:
        `datetime` next midnight on 00h 00m 00s
    """
    return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
