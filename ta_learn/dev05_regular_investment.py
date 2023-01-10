import os.path
import time
import common
import pandas as pd

# 展示所有列
pd.set_option('display.max_columns', None)

"""
定额仓位定投实盘
"""


def get_next_record(price, df_records, amount, time_str):
    if len(df_records) == 0:
        last_record = {
            "after_amount": 0,
            "target_position": 0
        }
    else:
        last_record = df_records.to_dict("records")[-1]

    current_record = {
        "time": common.now_time_str() if time_str is None else time_str,
        "price": price,
        "before_invest_amount": last_record["after_amount"],
        "before_invest_value": last_record["after_amount"] * price,
        "target_position": last_record["target_position"] + amount
    }
    current_record["estimated_trade_amount"] = (current_record["target_position"] - current_record["before_invest_value"]) / price
    current_record["estimated_trade_value"] = (current_record["target_position"] - current_record["before_invest_value"])
    # current_record["after_amount"] = current_record["before_invest_amount"] + current_record["estimated_trade_amount"]
    # current_record["after_value"] = current_record["after_amount"] * price
    # current_record["cash"] = - current_record["estimated_trade_amount"]
    return current_record


def do_invest(exchange, symbol, amount, record_path="./records.csv"):
    """
    定投入口
    :param exchange: ccxt exchange 对象
    :param symbol: 交易对
    :param amount: 定投数量
    :param record_path: 定投记录文件
    :return:
    """
    ticker = exchange.fetch_tickers(symbols=[symbol])[symbol]
    print(ticker)
    print(f"""
    {symbol}
    报价时间  {common.format_time(ticker['timestamp'])}
    当前时间  {common.now_time_str()}
    报价时差  {time.time() * 1000 - ticker['timestamp']} ms
    bid      {ticker["bid"]}
    ask      {ticker["ask"]}
    """)
    if os.path.exists(record_path):
        df_records = pd.read_csv(record_path)
    else:
        df_records = pd.DataFrame()
    invest_record = get_next_record(ticker["bid"], df_records, amount, common.format_time(ticker['timestamp']))
    print(invest_record)

    side = "BUY" if invest_record['estimated_trade_amount'] > 0 else "SELL"

    print(f"""
    价格          {ticker["bid"]}
    交易方向       {side}
    预估交易数量    {invest_record["estimated_trade_amount"]} BTC ({invest_record["estimated_trade_value"]} USDT)
    """)

    if "BUY" == side:
        order_result = exchange.create_market_buy_order(symbol, invest_record["estimated_trade_amount"])
        common.print_json(order_result)
        invest_record['trade_amount'] = order_result['amount']
        invest_record['trade_value'] = order_result['cost']
        invest_record['trade_price'] = order_result['average']
        invest_record["after_amount"] = invest_record["before_invest_amount"] + invest_record['trade_amount']
        invest_record["after_value"] = invest_record["after_amount"] * invest_record['trade_price']
        invest_record["cash"] = - order_result['cost']
    else:
        # todo
        order_result = exchange.create_market_sell_order(symbol, invest_record["estimated_trade_amount"])
        common.print_json(order_result)
        invest_record['trade_amount'] = - order_result['amount']
        invest_record['trade_value'] = - order_result['amount']
    df_records = df_records.append(invest_record, ignore_index=True)
    df_records.to_csv(record_path, index=False)

    total_cash = df_records['cash'].sum()
    print(f"""
    总投入现金       {total_cash}
    当前仓位价值     {invest_record["after_value"]}
    利润            {total_cash + invest_record["after_value"]}
    """)


def main():
    exchange = common.get_binance_exchange()
    symbol = "BTC/USDT"
    amount = 20

    do_invest(exchange, symbol, amount=amount, record_path="./records3.csv")

    ############# 测试代码保证余额全部卖出 #############
    balance = exchange.fetch_balance()
    balance_btc = balance['BTC']['total']
    # balance_usdt = balance['USDT']['total']
    # price = (100 - balance_usdt) / balance_btc
    price = exchange.fetch_tickers(symbols=[symbol])[symbol]['ask']
    print(f"价格 {price} 挂单 {balance_btc} BTC")
    exchange.create_limit_sell_order(symbol, balance_btc, price)
    ############# 测试代码保证余额全部卖出 #############


if __name__ == '__main__':
    main()
