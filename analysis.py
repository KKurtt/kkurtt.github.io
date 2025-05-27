# @Author  : Kurt
# @Time    : 27/05/2025 16:47
import matplotlib.pyplot as plt
import pandas as pd
from FundManager import create_fund_manager

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def generate_charts():
    """生成图表分析"""
    fm = create_fund_manager()

    if len(fm.data["navHistory"]) < 2:
        print("数据不足，无法生成图表")
        return

    # 净值走势图
    df = pd.DataFrame(fm.data["navHistory"])
    df['date'] = pd.to_datetime(df['date'])

    plt.figure(figsize=(12, 8))

    # 净值走势
    plt.subplot(2, 2, 1)
    plt.plot(df['date'], df['nav'], linewidth=2, color='#4facfe')
    plt.title('净值走势图')
    plt.xlabel('日期')
    plt.ylabel('净值')
    plt.grid(True, alpha=0.3)

    # 收益率分布
    plt.subplot(2, 2, 2)
    returns = df['nav'].pct_change().dropna() * 100
    plt.hist(returns, bins=20, alpha=0.7, color='#667eea')
    plt.title('日收益率分布')
    plt.xlabel('收益率(%)')
    plt.ylabel('频次')

    # 回撤分析
    plt.subplot(2, 2, 3)
    df['cummax'] = df['nav'].expanding().max()
    df['drawdown'] = (df['nav'] / df['cummax'] - 1) * 100
    plt.fill_between(df['date'], df['drawdown'], 0, alpha=0.3, color='red')
    plt.plot(df['date'], df['drawdown'], color='red')
    plt.title('回撤分析')
    plt.xlabel('日期')
    plt.ylabel('回撤(%)')

    # 月度收益
    plt.subplot(2, 2, 4)
    if fm.data["monthlyReturns"]:
        months = [item["month"] for item in fm.data["monthlyReturns"]]
        returns = [item["return"] for item in fm.data["monthlyReturns"]]
        colors = ['green' if r >= 0 else 'red' for r in returns]
        plt.bar(months, returns, color=colors, alpha=0.7)
        plt.title('月度收益率')
        plt.xlabel('月份')
        plt.ylabel('收益率(%)')

    plt.tight_layout()
    plt.savefig('fund_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

    print("✅ 图表已生成并保存为 fund_analysis.png")


if __name__ == "__main__":
    generate_charts()