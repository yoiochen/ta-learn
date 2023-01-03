import ccxt
import pandas as pd

# 展示所有列
pd.set_option('display.max_columns', None)


def main():
    """
    三角套利
    :return:
    """
    exchange = ccxt.binance(
        {
            "proxies": {
                "http": "http://127.0.0.1:7890",
                "https": "http://127.0.0.1:7890",
            },
        }
    )

    markets = exchange.load_markets()

    market0 = "BTC"
    market1 = "ETH"

    symbols = list(markets.keys())

    df_symbols = pd.DataFrame(data=symbols, columns=["symbol"])

    df_base_quote = df_symbols['symbol'].str.split(pat='/', expand=True)
    df_base_quote.columns = ['base', 'quote']
    df_symbols = pd.concat([df_symbols, df_base_quote], axis=1)

    print(df_symbols)

    base0_list = df_symbols[df_symbols['quote'] == market0]['base'].values.tolist()
    base1_list = df_symbols[df_symbols['quote'] == market1]['base'].values.tolist()

    common_base_list = list(
        set(base0_list).intersection(set(base1_list))
    )

    print(f"{market0}、{market1} 有共同计价币种有 {len(common_base_list)} 个")

    tickers = exchange.fetch_tickers()

    cols = [
        "path",
        "symbol0",
        "price0",
        "symbol1",
        "price1",
        "symbol2",
        "price2",
        "begin",
        "end",
        "profit"
    ]
    list_path = []
    for base in common_base_list:
        path = f"{market0}-{base}-{market1}-{market0}"
        symbol0 = f"{base}/{market0}"
        price0 = tickers[symbol0]['bid']
        symbol1 = f"{base}/{market1}"
        price1 = tickers[symbol1]['ask']
        symbol2 = f"{market1}/{market0}"
        price2 = tickers[symbol2]['ask']
        begin = 1
        end = None
        if not price0 == 0:
            end = 1 / price0 * price1 * price2

        profit = None
        if end is not None:
            profit = end - 1

        list_path.append([
            path,
            symbol0,
            price0,
            symbol1,
            price1,
            symbol2,
            price2,
            begin,
            end,
            profit
        ])

    df_path = pd.DataFrame(list_path, columns=cols)

    df_result = df_path[df_path['profit'] > 0]

    print(df_result)

    df_result.to_csv("./result_arbitrage_triangular.csv")


if __name__ == '__main__':
    main()