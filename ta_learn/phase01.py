import ccxt
import os
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor
import threading

"""
phase 1
爬取市场数据，保存到csv文件中
"""

############## config ##############
DATA_DIR = "../data/kline"
TIMEFRAME = "1w"
MAX_THREADS = 5
############## config ##############

exchange = ccxt.binance(
    {
        "proxies": {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        },
    }
)


def get_all_symbols(exchange):
    exchange.load_markets()
    return exchange.symbols


def get_markets(exchange, symbol, timeframe, fromTimestamp=0):
    limit = 1000
    result = []
    len_result = limit
    while len_result == limit:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit, params={"startTime": fromTimestamp})
        result += ohlcv
        start = ohlcv[0]
        end = ohlcv[-1]
        len_result = len(ohlcv)
        fromTimestamp = end[0] + 1
        print(f">>>> get {len_result} market for {symbol} from {start[0]}({format_time(start[0])}) to {end[0]}({format_time(end[0])})")

    return result


def format_time(timestamp):
    if len(str(timestamp)) > 10:
        timestamp = timestamp / 1000
    return datetime.fromtimestamp(
        timestamp, tz=ZoneInfo("Asia/Shanghai")
    ).strftime('%Y-%m-%d %H:%M:%S')


def save_markets(dir_name, symbol, markets):
    symbol_name: str = symbol.replace("/", "-")

    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    with open(os.path.join(dir_name, f"{symbol_name}_{TIMEFRAME}.csv"), "w") as f:
        f.write("timestamp,time,open,high,low,close,volume")
        f.write("\n")
        for row in markets:
            line = (
                f"{row[0]},{format_time(row[0])},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}"
            )
            f.write(line)
            f.write("\n")
    print(f">>>> save {symbol_name} markets success")


def job(exchange, symbol):
    markets = get_markets(exchange, symbol, TIMEFRAME)
    len_m = len(markets)
    start = markets[0]
    end = markets[-1]
    print(f">>>> [{threading.current_thread().name}] get {len_m} market for {symbol} from {start[0]}({format_time(start[0])}) to {end[0]}({format_time(end[0])})")
    save_markets(DATA_DIR, symbol, markets)


def main():
    try:
        # all_symbols = get_all_symbols(exchange)
        # print(">>>> get {} symbols".format(len(all_symbols)))

        # target_symbols = list(filter(lambda x: x.endswith("USDT") or x.endswith("BUSD"), all_symbols))
        target_symbols = [
            "BTC/USDT",
        ]
        print(">>>> target symbols: {}".format(len(target_symbols)))

        pool = ThreadPoolExecutor(MAX_THREADS, "markets_fetch_thread")

        for symbol in target_symbols:
            pool.submit(job, exchange, symbol)

    except Exception as e:
        print(e)


main()
