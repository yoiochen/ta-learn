from common import timer_start, now_time_str
import ccxt
import pandas as pd
import time
from dotenv import dotenv_values

config = {
    **dotenv_values("../.env")
}
api_key = config['BINANCE_API_KEY']
secret_key = config['BINANCE_SECRET_KEY']

# 展示所有列
pd.set_option('display.max_columns', None)

current_milli_time = lambda: int(round(time.time() * 1000))

exchange = ccxt.binance(
    {
        "proxies": {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        },
        "apiKey": config['BINANCE_API_KEY'],
        "secret": config['BINANCE_SECRET_KEY']
    }
)

markets = exchange.load_markets()
fees = exchange.fetch_trading_fees()


def get_common_base_list(markets, market_a, market_b):
    symbols = list(filter(lambda x: markets[x]['active'], markets.keys()))
    df_symbols = pd.DataFrame(data=symbols, columns=["symbol"])
    df_base_quote = df_symbols['symbol'].str.split(pat='/', expand=True)
    df_base_quote.columns = ['base', 'quote']
    df_symbols = pd.concat([df_symbols, df_base_quote], axis=1)
    base0_list = df_symbols[df_symbols['quote'] == market_a]['base'].values.tolist()
    base1_list = df_symbols[df_symbols['quote'] == market_b]['base'].values.tolist()

    common_base_list = list(
        set(base0_list).intersection(set(base1_list))
    )
    print(f"{market_a}、{market_b} 有共同计价币种有 {len(common_base_list)} 个")
    return common_base_list


def build_path(common_base_list, market_a, market_b):
    return list(map(
        lambda base: {
            "path": f"{market_a}-{base}-{market_b}-{market_a}",
            "symbol0": f"{base}/{market_a}",
            "symbol1": f"{base}/{market_b}",
            "symbol2": f"{market_b}/{market_a}"
        },
        common_base_list
    ))


# def do_arbitrage():


def main():
    """
    三角套利
    :return:
    """

    market_a = "BTC"
    market_b = "ETH"

    # 获取同时存在a、b作为计价币种交易对的基础币种列表
    common_base_list = get_common_base_list(markets, market_a, market_b)

    # 构建path list
    path_list = build_path(common_base_list, market_a, market_b)

    # 获取所有的symbol set
    symbol_set = set([])
    for item in path_list:
        symbol_set.add(item['symbol0'])
        symbol_set.add(item['symbol1'])
        symbol_set.add(item['symbol2'])

    def do_path():
        tickers = exchange.fetch_tickers(list(symbol_set))
        print(f"get {len(tickers.keys())} tickers")
        result_list = []
        for item in path_list:
            path = item['path']
            symbol0 = item['symbol0']
            symbol1 = item['symbol1']
            symbol2 = item['symbol2']
            # 判断交易对是否关闭
            if not markets[symbol0]['active']:
                print(f">>>> {symbol0} not active")
                continue
            if not markets[symbol1]['active']:
                print(f">>>> {symbol1} not active")
                continue
            if not markets[symbol2]['active']:
                print(f">>>> {symbol2} not active")
                continue

            price0 = tickers[symbol0]['ask']
            price1 = tickers[symbol1]['bid']
            price2 = tickers[symbol2]['bid']

            fee0 = fees[symbol0]['taker']
            fee1 = fees[symbol0]['taker']
            fee2 = fees[symbol0]['taker']

            timestamp0 = tickers[symbol0]['timestamp']
            timestamp1 = tickers[symbol1]['timestamp']
            timestamp2 = tickers[symbol2]['timestamp']
            begin = 1
            end = None
            if price0 > 0 and price1 > 0 and price2 > 0:
                end = (1 / price0) * price1 * price2 * (1 - fee0) * (1 - fee1) * (1 - fee2)
            profit = None
            if end is not None:
                profit = end - 1

            result_list.append(
                dict(item, **{
                    "price0": price0,
                    "fee0": fee0,
                    "timestamp0": f"{timestamp0}({current_milli_time() - timestamp0})",

                    "price1": price1,
                    "fee1": fee1,
                    "timestamp1": f"{timestamp1}({current_milli_time() - timestamp0})",

                    "symbol2": symbol2,
                    "price2": price2,
                    "fee2": fee2,
                    "timestamp2": f"{timestamp2}({current_milli_time() - timestamp0})",

                    "begin": begin,
                    "end": end,
                    "profit": profit,

                })
            )

        df_result = pd.DataFrame(result_list).sort_values("profit", ascending=False)

        first = df_result.iloc[0]
        last = df_result.iloc[-1]
        print(f"{first['path']} max profit {first['profit']}")
        print(f"{last['path']} min profit {last['profit']}")

        if len(df_result[df_result['profit'] > 0]) > 0:
            df_result.to_csv(f"../data/result/result_arbitrage_triangular_{now_time_str()}.csv")

    timer_start(do_path, 3)


if __name__ == '__main__':
    main()
