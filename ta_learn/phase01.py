import ccxt
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

############## config ##############
DATA_DIR = "./data"
MARKET_INTERVAL = "1d"
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

def get_markets(exchange, symbol, intervalTag):
    return exchange.fetch_ohlcv(symbol, intervalTag)

def save_markets(dir_name, symbol, markets):
    symbol_name: str = symbol.replace("/", "-")
    
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    with open(os.path.join(dir_name, f"{symbol_name}.csv"), "w") as f:
        f.write("time,open,high,low,close,volume")
        f.write("\n")
        for row in markets:
            formated_time = datetime.fromtimestamp(
                row[0] / 1000, tz=ZoneInfo("Asia/Shanghai")
            )
            line = (
                f"{formated_time},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}"
            )
            f.write(line)
            f.write("\n")
    print(f">>>> save {symbol_name} markets success")

def main():
    try:
        all_symbols = get_all_symbols(exchange)
        print(">>>> get {} symbols".format(len(all_symbols)))

        target_symbols = list(filter(lambda x: x.endswith("USDT") or x.endswith("BUSD"), all_symbols))
        print(">>>> target symbols: {}".format(len(target_symbols)))

        for symbol in target_symbols:
            markets = get_markets(exchange, symbol, MARKET_INTERVAL)
            print(">>>> get {} market for {}".format(len(markets), symbol))
            save_markets(DATA_DIR, symbol, markets)
    except Exception as e:
        print(e)