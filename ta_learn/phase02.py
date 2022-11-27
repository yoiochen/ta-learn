import os
from decimal import Decimal



def read_symbol_markets(symbol):
    if not os.path.exists(os.path.join("./data", f"{symbol}.csv")):
        raise Exception(f"can not markets data file for {symbol}")
        
    markets: list = []
    with open(os.path.join("./data", f"{symbol}.csv")) as f:
        text = f.read()
        # rm title row and blank row
        rows = list(filter(lambda x: x.find("time") == -1 and len(x) > 0, text.split("\n")))
        for row_str in rows:
            row = row_str.split(",")
            # time,open,high,low,close,volume
            markets.append({
                "time": row[0],
                "open": row[1],
                "high": row[2],
                "low": row[3],
                "close": row[4],
                "volume": row[5],
                "change": (Decimal(row[4]) - Decimal(row[1])) / Decimal(row[1]) * 100
            })
    return markets

def get_market_by_time(markets, time):
    filter_market = list(filter(lambda x: x["time"] == time, markets))
    if len(filter_market) == 0:
        return None
    return filter_market[0]

def main():
    SYMBOL1 = "BTC-BUSD"
    SYMBOL2= "ETH-BUSD"
    markets1 = read_symbol_markets(SYMBOL1)
    markets2 = read_symbol_markets(SYMBOL2)
    time_list = map(lambda x: x["time"], markets1)

    for time in time_list:
        market1 = get_market_by_time(markets1, time)
        if market1 is None:
            print(f">>>> can not find [{time}] market for {SYMBOL1}")
            continue
        market2 = get_market_by_time(markets2, time)
        if market2 is None:
            print(f">>>> can not find [{time}] market for {SYMBOL2}")
            continue
        change1 = market1['change']
        change2 = market2['change']
        choose = SYMBOL1 if change1 < change2 else SYMBOL2
        print(f"{time} {SYMBOL1} change {change1}, {SYMBOL2} change {change2}, result: {choose}")

main()

