import os
import sys
import time
import ccxt
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from threading import Timer
from dotenv import dotenv_values
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler


config = {
    **dotenv_values(os.path.join(os.path.dirname(__file__), ".env"))
}


def get_binance_exchange():
    return ccxt.binance(
        {
            "proxies": {
                "http": "http://127.0.0.1:7890",
                "https": "http://127.0.0.1:7890",
            },
            "apiKey": config['BINANCE_API_KEY'],
            "secret": config['BINANCE_SECRET_KEY']
        }
    )


def schedule(function, args=None, minute=None, second=None):
    scheduler = BlockingScheduler()
    scheduler.add_job(function, "cron", args=args, minute=minute, second=second)
    scheduler.start()


def async_schedule(function, minute=None):
    scheduler = BackgroundScheduler()
    scheduler.add_job(function, "cron", minute=minute)
    scheduler.start()


def timer_start(function, interval=0.001):
    """
    执行轮询任务
    :param function:
    :param interval:
    :return:
    """
    try:
        begin = time.time()
        print(f">>>> timer begin: {format_time(begin)}")
        function()
        print(f">>>> timer end {time.time() - begin} s")
    except BaseException:
        print("timer run error")
    finally:
        Timer(interval, function=timer_start, args=[function, interval]).start()


def now_timestamp():
    return int(time.time() * 1000)


def now_timestamp_10():
    return int(time.time())


def now_time_str():
    return format_time(now_timestamp())


def format_time(timestamp):
    timestamp = int(timestamp)
    if len(str(timestamp)) > 10:
        timestamp = timestamp / 1000
    return datetime.fromtimestamp(
        timestamp, tz=ZoneInfo("Asia/Shanghai")
    ).strftime('%Y-%m-%d %H:%M:%S.%f')


def print_json(target):
    """
    打印json
    :param target:
    :return:
    """
    print(json.dumps(target))


def job():
    print(f"do job {now_time_str()}")


def main():
    # timer_start(job)
    # print(now_timestamp())
    # print(now_timestamp_10())
    # schedule(job, minute="*/1")
    pass


if __name__ == '__main__':
    main()
