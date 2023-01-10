import common
import pandas as pd

description = "查询余额"


def run(**args):
    exchange = common.get_binance_exchange()
    dict_balance = exchange.fetch_balance()
    # common.print_json(dict_balance['info']['balances'])
    df_balance = pd.DataFrame(dict_balance['info']['balances'])
    df_balance['free'] = pd.to_numeric(df_balance['free'])
    df_balance['locked'] = pd.to_numeric(df_balance['locked'])
    df_balance['total'] = df_balance['free'] + df_balance['locked']

    print(f"update at: {common.format_time(dict_balance['timestamp'])}")
    print(df_balance[df_balance['free'] + df_balance['locked'] > 0])
