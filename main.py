# main.py
import os
import pandas as pd
from backtest_engine import run_single_backtest
from result_saver import BatchResultSaver


def find_best_stock(csv_path="backtest_results/results.csv"):
    """从已保存的结果中挑选策略净值最高的股票"""
    if not os.path.exists(csv_path):
        print(f"\n❌ 未找到结果文件: {csv_path}")
        return None

    df = pd.read_csv(csv_path)
    if df.empty:
        print("\n⚠️ 结果文件为空")
        return None

    best = df.sort_values("strategy_nav", ascending=False).iloc[0]

    print("\n" + "=" * 50)
    print("🏆 策略净值最优股票")
    print("=" * 50)
    print(f"  股票代码:   {best['symbol']}")
    print(f"  最后日期:   {best['last_date']}")
    print(f"  基准净值:   {best['market_nav']:.4f}")
    print(f"  策略净值:   {best['strategy_nav']:.4f}")
    print(f"  超额收益:   {best['strategy_nav'] - best['market_nav']:+.4f}")
    print("=" * 50)

    return best.to_dict()


def main():
    # 1. 初始化保存器
    saver = BatchResultSaver()

    # 2. 生成股票代码 sh600001 ~ sh600015
    symbols = [f"sh{str(c).zfill(6)}" for c in range(600001, 600100)]

    # 3. 批量回测 + 收集结果
    for symbol in symbols:
        result = run_single_backtest(symbol)
        saver.add(result)  # 无论成功(None)还是有效结果，add内部会自动过滤

    # 4. 统一保存15个净值
    saver.save_all()

    # 5. ✅ 新增：从保存的结果中挑选最优股票
    # 注意：csv路径需与 BatchResultSaver.save_all() 实际保存路径一致
    # 如果你的 saver 用了自定义路径，请相应修改下面的参数
    csv_path = "backtest_results/results.csv"
    find_best_stock(csv_path)


if __name__ == "__main__":
    main()