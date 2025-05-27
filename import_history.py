# @Author  : Kurt
# @Time    : 27/05/2025 16:47
from FundManager import create_fund_manager
import pandas as pd


def import_from_excel(excel_file):
    """从Excel文件导入历史数据"""
    fm = create_fund_manager()

    # 读取Excel文件
    df = pd.read_excel(excel_file)
    # 假设Excel格式：日期 | 净值 | 总资产

    for _, row in df.iterrows():
        date = row['日期'].strftime('%Y-%m-%d')
        nav = float(row['净值'])
        assets = float(row['总资产']) if pd.notna(row['总资产']) else None

        # 临时修改日期用于历史数据
        fm.data["navHistory"].append({
            "date": date,
            "nav": nav
        })

        if assets:
            fm.data["fund"]["totalAssets"] = assets

    # 更新最新净值
    if len(fm.data["navHistory"]) > 0:
        latest = fm.data["navHistory"][-1]
        fm.data["nav"]["current"] = latest["nav"]

    fm.calculate_performance_metrics()
    fm.update_monthly_returns()
    fm.save_data()

    print(f"✅ 已导入 {len(df)} 条历史数据")

# 使用示例
# import_from_excel('fund_history.xlsx')