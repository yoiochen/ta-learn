import time
from datetime import datetime
from zoneinfo import ZoneInfo
from threading import Timer



def timer_start(function, interval=0.001):
    """
    执行轮询任务
    :param function:
    :param interval:
    :return:
    """
    begin = time.time()
    function()
    print(f">>>> timer start run: {time.time() - begin} s")
    Timer(interval, function=timer_start, args=[function, interval]).start()


def now_timestamp():
    return int(time.time() * 1000)


def now_timestamp_10():
    return int(time.time())


def now_time_str():
    return format_time(now_timestamp())


def format_time(timestamp):
    if len(str(timestamp)) > 10:
        timestamp = timestamp / 1000
    return datetime.fromtimestamp(
        timestamp, tz=ZoneInfo("Asia/Shanghai")
    ).strftime('%Y-%m-%d %H:%M:%S')


def job():
    print(f"do job {time.time()}")


if __name__ == '__main__':
    # timer_start(job)
    print(now_timestamp())
    print(now_timestamp_10())


