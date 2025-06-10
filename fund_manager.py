import csv
import os
from datetime import datetime

def ensure_csv(filename, headers):
    """自动创建csv文件和表头"""
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

def append_csv(filename, row):
    """在csv文件末尾增加一行"""
    with open(filename, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def overwrite_csv(filename, headers, rows):
    """覆盖写入整个csv（如仓位、基金信息）"""
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

# 1. 确保所有csv存在
ensure_csv('fund_info.csv', [
    'key','value'
])
ensure_csv('nav_history.csv', [
    'date','nav','change','changePercent'
])
ensure_csv('positions.csv', [
    'aStock','hkStock','usStock','cash'
])
ensure_csv('holdings.csv', [
    'code','name','ratio','change'
])
ensure_csv('monthly_returns.csv', [
    'month','return'
])

def update_fund_info():
    print("------ 更新基金信息 ------")
    totalAssets = input("基金规模(万元): ")
    totalShares = input("总份额(万份): ")
    investors = input("投资人数: ")
    totalReturn = input("累计收益率(%): ")
    monthlyReturn = input("月度收益率(%): ")
    annualReturn = input("年化收益率(%): ")
    maxDrawdown = input("最大回撤(%): ")
    sharpeRatio = input("夏普比率: ")
    lastUpdate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    items = [
        ['totalAssets', totalAssets],
        ['totalShares', totalShares],
        ['investors', investors],
        ['totalReturn', totalReturn],
        ['monthlyReturn', monthlyReturn],
        ['annualReturn', annualReturn],
        ['maxDrawdown', maxDrawdown],
        ['sharpeRatio', sharpeRatio],
        ['lastUpdate', lastUpdate],
    ]
    overwrite_csv('fund_info.csv', ['key','value'], items)
    print("基金信息已更新。")

def add_nav_history():
    print("------ 添加每日净值 ------")
    date = input("日期(YYYY-MM-DD, 默认为今天): ").strip()
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    nav = input("单位净值: ")
    change = input("净值变动: ")
    changePercent = input("涨跌幅(%): ")
    append_csv('nav_history.csv', [date, nav, change, changePercent])
    print("净值记录已添加。")

def update_positions():
    print("------ 更新仓位 ------")
    aStock = input("A股仓位(%): ")
    hkStock = input("港股仓位(%): ")
    usStock = input("美股仓位(%): ")
    cash = input("现金(%): ")
    overwrite_csv('positions.csv', ['aStock','hkStock','usStock','cash'], [[aStock, hkStock, usStock, cash]])
    print("仓位已更新。")

def update_holdings():
    print("------ 更新重仓股 ------")
    print("（原有重仓股将被覆盖，请全部输入）")
    holdings = []
    while True:
        code = input("股票代码(留空结束): ").strip()
        if not code:
            break
        name = input("股票名称: ")
        ratio = input("持仓比例(%): ")
        change = input("周涨跌幅(%): ")
        holdings.append([code, name, ratio, change])
    if holdings:
        overwrite_csv('holdings.csv', ['code','name','ratio','change'], holdings)
        print("重仓股已更新。")
    else:
        print("未输入，未更新。")

def add_monthly_return():
    print("------ 添加月度收益 ------")
    month = input("月份（如 6月）: ")
    ret = input("收益率(%): ")
    append_csv('monthly_returns.csv', [month, ret])
    print("月度收益已添加。")

def main():
    while True:
        print("\n=== 阔盈基金管理 ===")
        print("1. 更新基金信息")
        print("2. 添加每日净值")
        print("3. 更新仓位")
        print("4. 更新重仓股")
        print("5. 添加月度收益")
        print("0. 退出")
        choice = input("请选择: ").strip()
        if choice == '1':
            update_fund_info()
        elif choice == '2':
            add_nav_history()
        elif choice == '3':
            update_positions()
        elif choice == '4':
            update_holdings()
        elif choice == '5':
            add_monthly_return()
        elif choice == '0':
            print("再见！")
            break
        else:
            print("无效选择，请重新输入。")

if __name__ == '__main__':
    main()