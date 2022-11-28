import os
from decimal import Decimal
from print_table import Table
import csv_utils


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
                "close": Decimal(row[4]),
                "volume": row[5],
                "change": (Decimal(row[4]) - Decimal(row[1])) / Decimal(row[1]) * 100
            })
    return markets

def get_market_by_time(markets, time):
    filter_market = list(filter(lambda x: x["time"] == time, markets))
    if len(filter_market) == 0:
        return None
    return filter_market[0]

def print_t():
    print("")

def main():
    SYMBOL0 = "BTC-BUSD"
    SYMBOL1= "ETH-BUSD"
    # 投入币种
    INVEST_SYMBOL = "ETH-BUSD"
    INVEST_AMOUNT = Decimal(10)

    token0 = SYMBOL0.split('-')[0]
    token1 = SYMBOL1.split('-')[0]
    invest_token = INVEST_SYMBOL.split('-')[0]
    markets0 = read_symbol_markets(SYMBOL0)
    markets1 = read_symbol_markets(SYMBOL1)

    time_list = map(lambda x: x["time"], markets0)

    # 期初金额
    initial_amount0 = Decimal(0)
    initial_amount1 = Decimal(0)
    # 期末金额
    final_amount0 = INVEST_AMOUNT if SYMBOL0 == INVEST_SYMBOL else Decimal(0)
    final_amount1 = INVEST_AMOUNT if SYMBOL1 == INVEST_SYMBOL else Decimal(0)

    results = []

    for time in time_list:
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
        initial_amount0 = final_amount0
        initial_amount1 = final_amount1
        if choose == SYMBOL0 and initial_amount1 > 0:
            final_amount0 = initial_amount1 * market1['close'] / market0['close']
            final_amount1 = Decimal(0)

        if choose == SYMBOL1 and initial_amount0 > 0:
            final_amount1 = initial_amount0 * market0['close'] / market1['close']
            final_amount0 = Decimal(0)
        
        results.append(
            {
                 'time': time, 
                f'{token0} open': market0['open'], 
                f'{token0} close': market0['close'], 
                f'{token0} change': f"{round(change0, 4)}%", 
                f'{token1} open': market1['open'], 
                f'{token1} close': market1['close'], 
                f'{token1} change': f"{round(change1, 4)}%", 
                'invest symbol': choose.split('-')[0], 
                'initial': f"{round(initial_amount0, 4)} {token0} + {round(initial_amount1, 4)} {token1}",
                'final': f"{round(final_amount0, 4)} {token0} + {round(final_amount1, 4)} {token1}"
            }
        )

        # print(f"{time} {SYMBOL0} change {change0}, {SYMBOL1} change {change1}, result: {choose.split('-')[0]}, initial: {initial_amount0} {SYMBOL0} + {initial_amount1} {SYMBOL1}, final: {final_amount0} {SYMBOL0} + {final_amount1} {SYMBOL1}")
    tb_title = [
                'time', 
                f'{token0} open', 
                f'{token0} close', 
                f'{token0} change', 
                f'{token1} open', 
                f'{token1} close', 
                f'{token1} change', 
                'invest symbol', 
                'initial', 
                'final'
            ]

    print(list(results[0].keys()))

    csv_utils.write(
        './result', 
        f'result_{INVEST_AMOUNT}_{invest_token}', 
        list(results[0].keys()), 
        list(map(lambda x: list(x.values()), results))
    )

    # tb = Table(numberOfCols=len(tb_title)).head(tb_title)
    # for item in list(map(lambda x: list(x.values()), results)):
    #     tb.row(item)
    # tb.printTable()

main()

