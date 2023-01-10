import pandas as pd
from decimal import Decimal
import plotly.express as px


############## config ##############
DATA_KLINE_DIR = "../data/kline"
DATA_RESULT_DIR = "../data/result"
AMOUNT_INVEST = 10000
SYMBOL_INVEST = "BNB-USDT"
############## config ##############

df = pd.read_csv(f"{DATA_KLINE_DIR}/{SYMBOL_INVEST}_1d.csv")
df['ma3'] = df['close'].rolling(3).mean()
df['ma5'] = df['close'].rolling(5).mean()
df['ma20'] = df['close'].rolling(20).mean()


amount_token = 0
amount_u = AMOUNT_INVEST
for i, row in df.iterrows():
    # print(i)
    action = ""
    ma3 = row['ma3']
    ma5 = row['ma5']
    ma20 = row['ma20']
    if ma3 is not None and ma5 is not None and ma20 is not None:
        if ma3 > ma5 > ma20:
            if amount_u > 0:
                print(f"buy {row.to_json()}")
                action = "buy"
                amount_token = float(Decimal(amount_u) / Decimal(row['close']))
                amount_u = 0
        else:
            if amount_token > 0:
                print(f"sell {row.to_json()}")
                action = "sell"
                amount_u = float(Decimal(amount_token) * Decimal(row['close']))
                amount_token = 0
    df.loc[i, 'action'] = action
    df.loc[i, 'token 持仓'] = amount_token
    df.loc[i, 'u 持仓'] = amount_u
    df.loc[i, '持仓净值'] = float(Decimal(amount_u) + Decimal(amount_token) * Decimal(row['close']))


# print(df)
df.to_csv(f"{DATA_RESULT_DIR}/result_ma_{SYMBOL_INVEST}.csv")

# 绘制折线图
fig = px.line(df, x='time', y=['ma3', 'ma5', 'ma20', '持仓净值'])
# fig.write_html('first_figure.html', auto_open=True)
fig.show()
