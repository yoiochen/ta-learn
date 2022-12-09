import os
import pandas as pd
from decimal import Decimal

"""
phase 2
实现 轮替策略，并回测
"""

############## config ##############
DATA_KLINE_DIR = "../data/kline"
DATA_RESULT_DIR = "../data/result"
TOKEN0 = "BTC"
TOKEN1 = "ETH"
TOKEN_STABLE = "BUSD"
SYMBOL0 = f"{TOKEN0}-{TOKEN_STABLE}"
SYMBOL1 = f"{TOKEN1}-{TOKEN_STABLE}"
# 投入稳定币U数量
INVEST_STABLE_AMOUNT = 10000
N = 10
############## config ##############


def read_symbol_markets(symbol):
    df = pd.read_csv(f'{DATA_KLINE_DIR}/{symbol}.csv')
    markets = df.to_dict('records')
    result = []
    for item in markets:
        item['change'] = (Decimal(item['close']) - Decimal(item['open'])) / Decimal(item['open']) * 100
        result.append(item)
    return markets


def read_symbol_markets_with_n(symbol, n):
    markets = read_symbol_markets(symbol)
    lst_sliced = [markets[i:i + n] for i in range(0, len(markets), n)]
    result = []
    for item in lst_sliced:
        ll = len(item)
        if ll < n:
            continue
        begin = item[0]
        end = item[ll - 1]
        result.append(
            {
                "time": f"{begin['time']} - {end['time']}",
                "open": begin['open'],
                "high": max(map(lambda x: x['high'], item)),
                "low": min(map(lambda x: x['low'], item)),
                "close": end['close'],
                "volume": sum(map(lambda x: x['volume'], item)),
                "change": (Decimal(end['close']) - Decimal(begin['open'])) / Decimal(begin['open']) * 100
            }
        )
    return result


def get_market_by_time(markets, time):
    filter_market = list(filter(lambda x: x["time"] == time, markets))
    if len(filter_market) == 0:
        return None
    return filter_market[0]


def main():
    # markets0 = read_symbol_markets(SYMBOL0)
    # markets1 = read_symbol_markets(SYMBOL1)

    markets0 = read_symbol_markets_with_n(SYMBOL0, N)
    markets1 = read_symbol_markets_with_n(SYMBOL1, N)

    time_list = map(lambda x: x["time"], markets0)

    # 期初金额
    initial_amount0 = Decimal(0)
    initial_amount1 = Decimal(0)
    # 期末金额
    final_amount0 = Decimal(0)
    final_amount1 = Decimal(0)

    results = []

    for i, time in enumerate(time_list):
        market0 = get_market_by_time(markets0, time)
        if market0 is None:
            print(f">>>> can not find [{time}] market for {SYMBOL0}")
            continue
        market1 = get_market_by_time(markets1, time)
        if market1 is None:
            print(f">>>> can not find [{time}] market for {SYMBOL1}")
            continue
        change0 = market0['change']
        change1 = market1['change']
        choose = SYMBOL0 if change0 < change1 else SYMBOL1

        # 模拟投资
        if i == 0:
            initial_amount0 = Decimal(0) if choose == SYMBOL0 else INVEST_STABLE_AMOUNT / market0['close']
            initial_amount1 = INVEST_STABLE_AMOUNT / market1['close'] if choose == SYMBOL0 else Decimal(0)
        else:
            initial_amount0 = final_amount0
            initial_amount1 = final_amount1

        if choose == SYMBOL0 and initial_amount1 > 0:
            final_amount0 = Decimal(initial_amount1) * Decimal(market1['close']) / Decimal(market0['close'])
            final_amount1 = Decimal(0)

        if choose == SYMBOL1 and initial_amount0 > 0:
            final_amount1 = Decimal(initial_amount0) * Decimal(market0['close']) / Decimal(market1['close'])
            final_amount0 = Decimal(0)

        results.append(
            {
                'time': time,
                f'{TOKEN0} open': market0['open'],
                f'{TOKEN0} close': str(market0['close']),
                f'{TOKEN0} change': f"{round(change0, 4)}%",
                f'{TOKEN1} open': market1['open'],
                f'{TOKEN1} close': str(market1['close']),
                f'{TOKEN1} change': f"{round(change1, 4)}%",
                'invest symbol': choose.split('-')[0],
                'initial': f"{round(initial_amount0, 4)} {TOKEN0} + {round(initial_amount1, 4)} {TOKEN1}",
                'final': f"{round(final_amount0, 4)} {TOKEN0} + {round(final_amount1, 4)} {TOKEN1}",
                f"value ({TOKEN_STABLE})": round(
                    final_amount0 * Decimal(market0['close']) + final_amount1 * Decimal(market1['close']), 4)
            }
        )
        # print( f"{time} {SYMBOL0} change {change0}, {SYMBOL1} change {change1}, result: {choose.split('-')[0]}, initial: {initial_amount0} {SYMBOL0} + {initial_amount1} {SYMBOL1}, final: {final_amount0} {SYMBOL0} + {final_amount1} {SYMBOL1}")

    print(list(results[0].keys()))

    df = pd.DataFrame(results)
    print(df)
    df.to_csv(os.path.join(DATA_RESULT_DIR, f"result_across_{INVEST_STABLE_AMOUNT}_{TOKEN_STABLE}_every_{N}_day.csv"))


main()
