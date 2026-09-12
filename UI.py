import streamlit as st
import pandas as pd
import os
import time

# 导入你现有的核心模块
from backtest_engine import run_single_backtest
from result_saver import BatchResultSaver

# --- 页面基础配置 ---
st.set_page_config(
    page_title="RDIG回测评价",
    page_icon="RDIG.png",
    layout="wide"
)

st.title("双均线量化回测与风险评价系统")
st.caption("RDIG出品 | Powered by Streamlit & Python")

# --- 侧边栏：全局参数 ---
with st.sidebar:
    st.header("⚙️ 回测参数")
    start_date = st.date_input("开始日期", value=pd.to_datetime("2023-01-01"))
    end_date = st.date_input("结束日期", value=pd.to_datetime("2026-08-19"))
    
    # 转换为引擎需要的字符串格式 YYYYMMDD
    start_str = start_date.strftime("%Y%m%d")
    end_str = end_date.strftime("%Y%m%d")
    
    st.divider()
    st.info("💡 提示：系统已内置交易成本(买0.05%, 卖0.15%)与日期安全修复机制。")

# --- 主界面：功能选项卡 ---
tab1, tab2 = st.tabs(["🔍 单股回测评价", "📲 智慧策略选股"])

# ==========================================
# Tab 1: 单股深度回测
# ==========================================
with tab1:
    col_input, col_btn = st.columns([3, 1])
    with col_input:
        symbol = st.text_input("输入股票代码 (例如: sh600001)", "sh600001").strip()
    with col_btn:
        st.write("") # 占位对齐
        st.write("")
        run_single_btn = st.button("开始单股回测", use_container_width=True, type="primary")

    if run_single_btn:
        if not symbol:
            st.error("请输入有效的股票代码")
        else:
            with st.spinner(f"正在获取 {symbol} 数据并计算风险指标..."):
                # 直接调用你写好的引擎
                result = run_single_backtest(symbol, start_date=start_str, end_date=end_str)
            
            if result:
                st.success(f"✅ {symbol} 回测完成！")
                
                # 1. 展示核心风险收益指标 (响应汪老师要求)
                st.subheader("📊 风险收益评价指标")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("策略净值", result['strategy_nav'])
                m2.metric("年化收益", result['annual_return'])
                m3.metric("最大回撤", result['max_drawdown'])
                m4.metric("夏普比率", result['sharpe_ratio'])
                
                st.divider()
                
                # 2. 展示净值曲线图
                st.subheader("📈 净值曲线对比")
                chart_path = f"backtest_results/charts/{symbol}.png"
                if os.path.exists(chart_path):
                    st.image(chart_path, use_column_width=True)
                else:
                    st.warning("未找到生成的图表文件，请检查 backtest_engine.py 的保存路径。")
            else:
                st.error(f"❌ {symbol} 回测失败，可能是无数据或网络问题，请查看终端报错。")

# ==========================================
# Tab 2: 批量扫描优选
# ==========================================
# ==========================================
# Tab 2: 批量扫描优选 (修正版)
# ==========================================
with tab2:
    st.text("请选择扫描市场范围:")
  

# --- 布局开始 ---

# 1. 第一行：上海A股 和 深圳A股 并列
# [1, 1] 表示两列宽度相等
    col_sh, col_sz = st.columns([1, 1])

    with col_sh:
        # 使用 use_container_width=True 让按钮填满这一列的宽度
        run_batch_btn_SH = st.button("上海A股", key="btn_sh", use_container_width=True)
            
    with col_sz:
        run_batch_btn_SZ = st.button("深圳A股", key="btn_sz", use_container_width=True)

    # 2. 第二行：全市场 (默认占满整行)
    run_batch_btn_ALL = st.button("全市场", key="btn_all", use_container_width=True)

    # 3. 第三行：输入框 + 导入自选股按钮
    # [3, 1] 表示左边输入框宽一些(占3份)，右边按钮窄一些(占1份)，可根据需要调整比例
    col_input1, col_input2, col_btn = st.columns([2, 2, 1])

    with col_input1:
        startcode = st.text_input(
            label="请输入股票代码范围", 
            placeholder="例如: sh600001-sh600100",
            label_visibility="collapsed",
            key="startcode_input" # 隐藏标签让界面更紧凑
        )
    with col_input2:
        endcode = st.text_input(
            label="请输入股票代码范围", 
            placeholder="例如: sh600001-sh600100",
            label_visibility="collapsed",
            key="endcode_input" # 隐藏标签让界面更紧凑
        )

    with col_btn:
        # 设置 min_height=42 是为了让按钮高度和输入框大致对齐（Streamlit默认对齐有时会有偏差）
        run_batch_btn_IMPORT = st.button("导入自选股", key="btn_import", use_container_width=True)

    # --- 布局结束 ---
#     col_SH, col_SZ = st.columns([1,1])
#     # st.text(" 1. 上海A股 (sh600001-sh600100):")
#     # st.text(" 2. 深圳A股 (sz000001-sz000100):")
#     # st.text(" 3. 全市场")
#     # st.text(" 4.导入自选股")
#    with col_SH:
#     if st.button("上海A股", use_container_width=True, type="primary"):
#     run_batch_btn_SH = st.button("上海A股", use_container_width=True, type="primary")
#     run_batch_btn_SZ = st.button("深圳A股", use_container_width=True, type="primary")
#     run_batch_btn_ALL = st.button("全市场", use_container_width=True, type="primary")
#     run_batch_btn_IMPORT = st.button("导入自选股", use_container_width=True, type="primary")
#     fw = st.text_input("请选择扫描市场范围 \n 1. 上海A股 (sh600001-sh600100)\n 2. 深圳A股 (sz000001-sz000100)\n 3. 全市场\n 4.导入自选股", "sh600001-sh600100").strip()
#     st.markdown("一键扫描 `sh600001` 至 `sh600100`，并基于**夏普比率**自动筛选最优标的。")
#     run_batch_btn = st.button("🚀 启动批量扫描", use_container_width=True, type="primary")
    
    # 用于显示进度的容器
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 【关键修改】：用一个变量来标记是否刚刚完成了批量回测
    batch_finished = False
    
    def run_batch(symbols):
        saver = BatchResultSaver()
        total = len(symbols)

        for i, sym in enumerate(symbols):
            status_text.text(f"正在回测: {sym} ({i + 1}/{total})")
            result = run_single_backtest(sym, start_date=start_str, end_date=end_str)
            saver.add(result)
            progress_bar.progress((i + 1) / total)
            time.sleep(0.5)

        status_text.text("✅ 批量回测完成！正在保存并分析结果...")
        saver.save_all()
        csv_path = saver.save_all() 
        return csv_path  # 获取保存的 CSV 文件路径

    if run_batch_btn_SH:
        symbols = [f"sh{str(c).zfill(6)}" for c in range(600001, 600010)]
        csv_path = run_batch(symbols)
        batch_finished = True
    elif run_batch_btn_SZ:
        symbols = [f"sz{str(c).zfill(6)}" for c in range(1, 10)]
        csv_path = run_batch(symbols)
        batch_finished = True
    elif run_batch_btn_ALL:
        symbols = [f"sh{str(c).zfill(6)}" for c in range(600001, 600010)]
        csv_path = run_batch(symbols)
        batch_finished = True
    elif run_batch_btn_IMPORT:
        if startcode[0] == "6":
            symbols = [f"sh{str(c).zfill(6)}" for c in range(int(startcode), int(endcode))]
        else:
            symbols = [f"sz{str(c).zfill(6)}" for c in range(int(startcode), int(endcode))]  # 这里你可以根据实际需求修改
        csv_path = run_batch(symbols)
        batch_finished = True
    # 【关键修改】：只有当 batch_finished 为 True 时，才去读取和展示 CSV
    # 这样就不会在刚点击按钮、还没跑完的时候就报错了
    if batch_finished:

        # csv_path = "backtest_results/results.csv"  # 这里你可以动态获取最新的 CSV 文件路径
        if os.path.exists(csv_path):
            df_results = pd.read_csv(csv_path)
            
            if not df_results.empty:
                st.success("🎉 批量扫描完成！")
                
                # 找出夏普比率最高的
                best_stock = df_results.sort_values("sharpe_ratio", ascending=False).iloc[0]
                
                st.subheader("🏆 综合评分最优股票 (基于夏普比率)")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("股票代码", best_stock['symbol'])
                c2.metric("年化收益", best_stock['annual_return'])
                c3.metric("最大回撤", best_stock['max_drawdown'])
                c4.metric("夏普比率", best_stock['sharpe_ratio'])
                
                st.divider()
                st.subheader("📋 全部股票回测明细")
                # 使用 Streamlit 原生表格展示，支持排序
                st.dataframe(df_results.sort_values("sharpe_ratio", ascending=False), use_container_width=True)
            else:
                st.warning("所有股票均无有效数据。")
        else:
            st.error("未找到 results.csv 文件，请检查 result_saver.py 的保存路径。")