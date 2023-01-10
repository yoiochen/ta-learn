import common
import pandas as pd
import plotly.express as px
import numpy as np


# 展示所有列
pd.set_option('display.max_columns', None)

"""
准备数据
处理数据
计算因子、信号
风控
交易
"""

VALUE_PER_TIMES = 100


def get_record(price, df_records, time):
    last_record = None
    if len(df_records) == 0:
        last_record = {
            "index": 0,
            "after_amount": 0,
            "target_position": 0
        }
    else:
        last_record = df_records.to_dict("records")[-1]

    current_record = {
        "index": last_record['index'] + 1,
        "time": common.now_time_str() if time is None else time,
        "price": price,
        "before_invest_amount": last_record["after_amount"],
        "before_invest_value": last_record["after_amount"] * price,
        "target_position": last_record["target_position"] + VALUE_PER_TIMES
    }
    current_record["trade_amount"] = (current_record["target_position"] - current_record["before_invest_value"]) / price
    current_record["trade_value"] = (current_record["target_position"] - current_record["before_invest_value"])
    current_record["after_amount"] = current_record["before_invest_amount"] + current_record["trade_amount"]
    current_record["after_value"] = current_record["after_amount"] * price
    current_record["cash"] = - current_record["trade_value"]
    return current_record


def get_kline(symbol, timeframe, start_time="1970-01-01 00:00:00", end_time=common.now_time_str()):
    df_kline = pd.read_csv(f"../data/kline/{symbol}_{timeframe}.csv")
    df_kline['time'] = pd.to_datetime(df_kline['time'])
    df_kline.set_index("time")
    return df_kline[df_kline['time'] >= start_time][df_kline['time'] < end_time]


def do_invest(symbol, timeframe, start_time, end_time=common.now_time_str()):
    df_kline = get_kline(symbol, timeframe=timeframe, start_time=start_time, end_time=end_time)
    df_records = pd.read_csv("./records.csv")
    for item in df_kline.to_dict('records'):
        record = get_record(item['close'], df_records, time=item['time'])
        # print(record)
        df_records.loc[len(df_records)] = record.values()

    df_records.to_csv(f"../data/result/result_automatic_invest_{symbol}_{timeframe}_{start_time}_{end_time}.csv")

    invest_cash = abs(df_records['cash'].sum())
    first_record = df_records.values[1]
    last_record = df_records.values[-1]
    print(last_record)
    position_value = last_record[5]

    # 投资天数
    invest_days = (last_record[1] - first_record[1]).days

    result = {
        "定投开始": first_record[1],
        "定投结束": last_record[1],
        "首期价格": first_record[2],
        "末期价格": last_record[2],
        "投入期数": last_record[0],
        "每期新增仓位": VALUE_PER_TIMES,
        "买期数": df_records[df_records['trade_amount'] > 0]['index'].count(),
        "卖期数": df_records[df_records['trade_amount'] < 0]['index'].count(),
        "投入价值": invest_cash,
        "仓位价值": position_value,
        "利润": position_value - invest_cash,
        "收益比": f"{round((position_value - invest_cash) / invest_cash * 100, 4)}",
        "投资天数": invest_days,
        "APY": f"{round((position_value - invest_cash) / invest_cash * 100 / invest_days * 365, 4) if invest_days > 0 else 0}",
    }

    for key in result.keys():
        print(key, result[key])

    # print("定投开始", first_record[1])
    # print("定投结束", last_record[1])
    # print("首期价格", first_record[2])
    # print("末期价格", last_record[2])
    # print("投入期数", last_record[0])
    # print("每期新增仓位", VALUE_PER_TIMES)
    # print("买期数", df_records[df_records['trade_amount'] > 0]['index'].count())
    # print("卖期数", df_records[df_records['trade_amount'] < 0]['index'].count())
    # print("投入价值", invest_cash)
    # print("仓位价值", position_value)
    # print("利润", position_value - invest_cash)
    return result


def main():

    """
    对比从2019年2月份起每月开始定投的情况
    """
    """
    symbol = "BTC-USDT"
    start_time="2019-2-01 08:00:00"
    end_time="2021-04-01 08:00:00"
    timeframe = "1M"
    df_kline_all = get_kline(symbol, timeframe=timeframe, start_time=start_time, end_time=end_time)
    result = []
    for time in list(df_kline_all['time'].values):
        result.append(do_invest(symbol, timeframe=timeframe, start_time=time, end_time=end_time))
    df_result = pd.DataFrame(result)
    df_result.to_csv(f"./result_{symbol}_{timeframe}_{start_time}_{end_time}.csv")
    """
    """
    对比从2019年2月份起每周开始定投的情况
    """
    """
    symbol = "BTC-USDT"
    start_time="2019-2-01 08:00:00"
    end_time="2021-04-01 08:00:00"
    timeframe = "1w"
    df_kline_all = get_kline(symbol, timeframe=timeframe, start_time=start_time, end_time=end_time)
    result = []
    for time in list(df_kline_all['time'].values):
        result.append(do_invest(symbol, timeframe=timeframe, start_time=time, end_time=end_time))
    df_result = pd.DataFrame(result)
    df_result.to_csv(f"./result_{symbol}_{timeframe}_{start_time}_{end_time}.csv")
    """

    """
    对比从2017年8月份起开始定投半年的情况
    """
    symbol = "BTC-USDT"
    timeframe = "1d"
    days = 365

    df_kline_all = get_kline(symbol, timeframe=timeframe)
    result = []
    time_list = list(df_kline_all['time'].values)
    for time in time_list:
        end_time = time + np.timedelta64(days, 'D')
        if end_time > time_list[-1]:
            break
        result.append(do_invest(symbol, timeframe=timeframe, start_time=time, end_time=end_time))

    df_result = pd.DataFrame(result)
    df_result.to_csv(f"./result_invest_{symbol}_{timeframe}_{days}days.csv")

    # 绘制折线图
    fig = px.line(df_result, x='定投开始', y=['首期价格', '利润'])
    # fig.write_html('first_figure.html', auto_open=True)
    fig.show()


if __name__ == '__main__':
    main()
