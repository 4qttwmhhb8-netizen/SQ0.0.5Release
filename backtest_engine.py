# backtest_engine.py
import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import random
import os
from datetime import datetime, timedelta

plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def calculate_metrics(df, risk_free_rate=0.03):
    """
    【新增】计算风险收益评价指标 (响应汪老师建议)
    """
    total_days = len(df)
    # 假设一年约252个交易日
    years = total_days / 252.0 if total_days > 0 else 1.0

    # 1. 年化收益率
    # 防止净值小于等于0导致数学错误
    final_nav = df['Strategy_NAV'].iloc[-1] if not df.empty else 1.0
    if final_nav > 0 and years > 0:
        strategy_annual = (final_nav ** (1 / years)) - 1
    else:
        strategy_annual = 0.0
        
    market_final_nav = df['Market_NAV'].iloc[-1] if not df.empty else 1.0
    if market_final_nav > 0 and years > 0:
        market_annual = (market_final_nav ** (1 / years)) - 1
    else:
        market_annual = 0.0

    # 2. 最大回撤 (Max Drawdown)
    def get_max_dd(nav_series):
        if nav_series.empty: return 0.0
        cummax = nav_series.cummax()
        drawdown = (nav_series - cummax) / cummax
        return drawdown.min()

    strategy_dd = get_max_dd(df['Strategy_NAV'])

    # 3. 夏普比率 (Sharpe Ratio)
    daily_rf = risk_free_rate / 252
    if 'Strategy_Return' in df.columns and df['Strategy_Return'].std() != 0:
        excess_returns = df['Strategy_Return'] - daily_rf
        sharpe = np.sqrt(252) * (excess_returns.mean() / df['Strategy_Return'].std())
    else:
        sharpe = 0.0

    return {
        "market_annual": market_annual,
        "strategy_annual": strategy_annual,
        "max_drawdown": strategy_dd,
        "sharpe_ratio": sharpe
    }


def run_single_backtest(symbol, start_date="20230101", end_date="20260819"):
    print(f"🚀 正在回测: {symbol}...")

    # --- 1. 获取数据 (含日期安全修复) ---
    safe_end = end_date
    try:
        input_end = datetime.strptime(end_date, "%Y%m%d")
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if input_end >= today_start:
            safe_end = (today_start - timedelta(days=1)).strftime("%Y%m%d")
            print(f"   📅 end_date 调整为安全日期: {safe_end}")
    except Exception:
        pass

    df = None
    
   
    try:
        time.sleep(random.uniform(0.01, 0.05))
        df = ak.stock_zh_a_daily(symbol=symbol, start_date=start_date,
                                end_date=safe_end, adjust="hfq")
       
        
    except Exception as e:
        print(f"   ⚠️ {symbol} 请求失败: {e}")
    
    if df is None or df.empty:
        print(f"   🛑 {symbol} 无数据，跳过")
        return None    

   
    # --- 2. 清洗与计算 ---
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df.rename(columns={'close': '收盘'}, inplace=True)

    # 双均线策略
    df['MA5'] = df['收盘'].rolling(5).mean()
    df['MA20'] = df['收盘'].rolling(20).mean()
    df['Signal'] = np.where(df['MA5'] > df['MA20'], 1, 0)
    df['Position'] = df['Signal'].shift(1).fillna(0)

    # 收益计算
    df['Market_Return'] = df['收盘'].pct_change()
    buy_cost, sell_cost = 0.0005, 0.0015
    df['Trade_Cost'] = 0.0
    df.loc[(df['Position'] == 1) & (df['Position'].shift(1) == 0), 'Trade_Cost'] = buy_cost
    df.loc[(df['Position'] == 0) & (df['Position'].shift(1) == 1), 'Trade_Cost'] = sell_cost
    df['Strategy_Return'] = (df['Market_Return'] * df['Position']) - df['Trade_Cost']

    # 净值曲线
    df['Market_NAV'] = (1 + df['Market_Return']).cumprod()
    df['Strategy_NAV'] = (1 + df['Strategy_Return']).cumprod()

    # --- 3. 生成图表 ---
    # chart_dir = "backtest_results/charts"
    # os.makedirs(chart_dir, exist_ok=True)
    # plt.figure(figsize=(10, 4))
    # plt.plot(df['date'], df['Market_NAV'], label='基准(买入持有)', color='gray', alpha=0.6)
    # plt.plot(df['date'], df['Strategy_NAV'], label='双均线策略', color='red')
    # plt.title(f'{symbol} 回测净值曲线')
    # plt.legend()
    # plt.grid(True, alpha=0.3)
    # plt.tight_layout()
    # plt.savefig(os.path.join(chart_dir, f"{symbol}.png"), dpi=100)
    # plt.close()
        # --- 3. 生成图表 ---
    chart_dir = "backtest_results/charts"
    os.makedirs(chart_dir, exist_ok=True)
    
    # 先筛选出所有的买入点（开仓）和卖出点（平仓），和你的手续费计算逻辑完全一致
    buy_mask = (df['Position'] == 1) & (df['Position'].shift(1) == 0)
    sell_mask = (df['Position'] == 0) & (df['Position'].shift(1) == 1)
    # 调试用：打印当前标的找到了几个买卖点，要是这里打印0，说明是均线没交叉，不是代码的问题
    print(f"【{symbol}】找到 {buy_mask.sum()} 个买入点，{sell_mask.sum()} 个卖出点")
    
    plt.figure(figsize=(12, 5))  # 稍微把图调大一点，看得更清楚
    # 画基准和策略净值线
    plt.plot(df['date'], df['Market_NAV'], label='基准(买入持有)', color='gray', alpha=0.6, linewidth=1)
    plt.plot(df['date'], df['Strategy_NAV'], label='双均线策略', color='red', linewidth=1.2)
    
    # 标买入点：红色向上三角，zorder=10保证在最上层，绝对不会被线挡住
    if buy_mask.sum() > 0:
        plt.scatter(df.loc[buy_mask, 'date'], df.loc[buy_mask, 'Strategy_NAV'], 
                    marker='^', color='red', s=100, label='买入点', zorder=10, edgecolors='black', linewidth=0.5)
    # 标卖出点：绿色向下三角
    if sell_mask.sum() > 0:
        plt.scatter(df.loc[sell_mask, 'date'], df.loc[sell_mask, 'Strategy_NAV'], 
                    marker='v', color='green', s=100, label='卖出点', zorder=10, edgecolors='black', linewidth=0.5)
    
    plt.title(f'{symbol} 回测净值曲线（MA5&MA20双均线）')
    plt.xlabel('日期')
    plt.ylabel('净值')
    plt.legend(loc='upper left')  # 图例放左上角，不会挡曲线
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    # 保存图片
    save_path = os.path.join(chart_dir, f"{symbol}.png")
    plt.savefig(save_path, dpi=120)
    print(f"【{symbol}】图表已保存到：{save_path}")  # 告诉你图存到哪了，避免你找错旧图
    plt.close()
    
    # --- 4. 【关键修改】计算风险指标 ---
    metrics = calculate_metrics(df)

    # --- 5. 返回结果 (补齐 UI 需要的字段) ---
    last = df.iloc[-1]
    return {
        "symbol": symbol,
        "last_date": str(last['date'].date()),
        "market_nav": round(float(last['Market_NAV']), 4),
        "strategy_nav": round(float(last['Strategy_NAV']), 4),
        # 下面是 UI.py 需要的字段，现在补上了
        "annual_return": f"{metrics['strategy_annual'] * 100:.2f}%",
        "max_drawdown": f"{metrics['max_drawdown'] * 100:.2f}%",
        "sharpe_ratio": round(metrics['sharpe_ratio'], 2)
    }