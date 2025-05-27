# @Author  : Kurt
# @Time    : 27/05/2025 16:45
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from typing import Dict, List, Tuple


class FundDataManager:
    def __init__(self, data_file='data.json'):
        """初始化基金数据管理器"""
        self.data_file = data_file
        self.data = self.load_data()

    def load_data(self) -> Dict:
        """加载现有数据，如果文件不存在则创建默认数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self.create_default_data()

    def create_default_data(self) -> Dict:
        """创建默认数据结构"""
        return {
            "lastUpdate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nav": {
                "current": 1.0000,
                "change": 0.0000,
                "changePercent": 0.00,
                "totalReturn": 0.00
            },
            "fund": {
                "totalAssets": 100.0,
                "totalShares": 100.0,
                "investors": 1
            },
            "navHistory": [],
            "positions": {
                "aStock": 0,
                "hkStock": 0,
                "usStock": 0,
                "cash": 100
            },
            "holdings": [],
            "monthly": {
                "monthlyReturn": 0.00,
                "annualReturn": 0.00,
                "maxDrawdown": 0.00,
                "sharpeRatio": 0.00
            },
            "monthlyReturns": [],
            "trades": []
        }

    def save_data(self):
        """保存数据到JSON文件"""
        self.data["lastUpdate"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 {self.data_file}")

    def add_daily_nav(self, nav_value: float, total_assets: float = None):
        """添加每日净值数据"""
        today = datetime.now().strftime("%Y-%m-%d")

        # 计算涨跌幅
        if self.data["navHistory"]:
            prev_nav = self.data["navHistory"][-1]["nav"]
            change = nav_value - prev_nav
            change_percent = (change / prev_nav) * 100
        else:
            change = 0.0
            change_percent = 0.0

        # 更新当前净值
        self.data["nav"]["current"] = nav_value
        self.data["nav"]["change"] = change
        self.data["nav"]["changePercent"] = change_percent

        # 计算累计收益率
        if self.data["navHistory"]:
            initial_nav = self.data["navHistory"][0]["nav"]
        else:
            initial_nav = 1.0000
        self.data["nav"]["totalReturn"] = ((nav_value - initial_nav) / initial_nav) * 100

        # 添加到历史记录（避免重复）
        if not self.data["navHistory"] or self.data["navHistory"][-1]["date"] != today:
            self.data["navHistory"].append({
                "date": today,
                "nav": nav_value
            })
        else:
            # 更新当天的净值
            self.data["navHistory"][-1]["nav"] = nav_value

        # 更新总资产
        if total_assets:
            self.data["fund"]["totalAssets"] = total_assets
            self.data["fund"]["totalShares"] = total_assets / nav_value

        print(f"已添加 {today} 净值数据: {nav_value:.4f} ({change_percent:+.2f}%)")

    def calculate_performance_metrics(self):
        """计算各种业绩指标"""
        if len(self.data["navHistory"]) < 2:
            return

        # 转换为DataFrame便于计算
        df = pd.DataFrame(self.data["navHistory"])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['returns'] = df['nav'].pct_change()

        # 计算月度收益率
        current_month = datetime.now().strftime("%Y-%m")
        month_start = datetime.now().replace(day=1)

        current_month_data = df[df['date'] >= month_start.strftime("%Y-%m-%d")]
        if len(current_month_data) > 0:
            month_return = ((current_month_data['nav'].iloc[-1] / current_month_data['nav'].iloc[0]) - 1) * 100
            self.data["monthly"]["monthlyReturn"] = round(month_return, 2)

        # 计算年化收益率
        if len(df) > 30:  # 至少30天数据
            days = (df['date'].iloc[-1] - df['date'].iloc[0]).days
            if days > 0:
                total_return = (df['nav'].iloc[-1] / df['nav'].iloc[0]) - 1
                annual_return = ((1 + total_return) ** (365.25 / days) - 1) * 100
                self.data["monthly"]["annualReturn"] = round(annual_return, 2)

        # 计算最大回撤
        df['cummax'] = df['nav'].expanding().max()
        df['drawdown'] = (df['nav'] / df['cummax'] - 1) * 100
        max_drawdown = df['drawdown'].min()
        self.data["monthly"]["maxDrawdown"] = round(max_drawdown, 2)

        # 计算夏普比率（假设无风险利率为3%）
        if len(df) > 30 and df['returns'].std() > 0:
            daily_returns = df['returns'].dropna()
            excess_returns = daily_returns.mean() * 252 - 0.03  # 年化超额收益
            volatility = daily_returns.std() * np.sqrt(252)  # 年化波动率
            sharpe_ratio = excess_returns / volatility if volatility > 0 else 0
            self.data["monthly"]["sharpeRatio"] = round(sharpe_ratio, 2)

        print("业绩指标已更新")

    def update_positions(self, a_stock: float = None, hk_stock: float = None,
                         us_stock: float = None, cash: float = None):
        """更新仓位配置（百分比）"""
        if a_stock is not None:
            self.data["positions"]["aStock"] = a_stock
        if hk_stock is not None:
            self.data["positions"]["hkStock"] = hk_stock
        if us_stock is not None:
            self.data["positions"]["usStock"] = us_stock
        if cash is not None:
            self.data["positions"]["cash"] = cash

        # 检查总和是否为100%
        total = sum(self.data["positions"].values())
        if abs(total - 100) > 0.1:
            print(f"警告：仓位总和为 {total:.1f}%，不等于100%")

        print("仓位配置已更新")

    def update_holdings(self, holdings_list: List[Dict]):
        """更新重仓股信息
        holdings_list: [{"code": "000001", "name": "平安银行", "percentage": 15.2, "weeklyChange": 3.45}]
        """
        self.data["holdings"] = holdings_list
        print(f"已更新 {len(holdings_list)} 只重仓股信息")

    def add_trade_record(self, date: str, code: str, action: str, quantity: str, price: str):
        """添加交易记录"""
        trade = {
            "date": date,
            "code": code,
            "action": action,
            "quantity": quantity,
            "price": price
        }
        self.data["trades"].append(trade)
        print(f"已添加交易记录: {date} {action} {code}")

    def update_monthly_returns(self):
        """更新月度收益率数据"""
        if len(self.data["navHistory"]) < 2:
            return

        df = pd.DataFrame(self.data["navHistory"])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # 按月分组计算收益率
        df['year_month'] = df['date'].dt.strftime('%Y-%m')
        monthly_data = []

        for year_month, group in df.groupby('year_month'):
            if len(group) > 1:
                month_return = ((group['nav'].iloc[-1] / group['nav'].iloc[0]) - 1) * 100
                month_name = datetime.strptime(year_month, '%Y-%m').strftime('%m月')
                monthly_data.append({
                    "month": month_name,
                    "return": round(month_return, 2)
                })

        self.data["monthlyReturns"] = monthly_data[-12:]  # 只保留最近12个月
        print("月度收益率数据已更新")

    def get_summary(self) -> str:
        """获取基金概况摘要"""
        current_nav = self.data["nav"]["current"]
        total_return = self.data["nav"]["totalReturn"]
        total_assets = self.data["fund"]["totalAssets"]
        investors = self.data["fund"]["investors"]

        summary = f"""
基金概况摘要:
================
当前净值: {current_nav:.4f}
累计收益率: {total_return:+.2f}%
基金规模: {total_assets:.1f}万元
投资人数: {investors}人
最后更新: {self.data["lastUpdate"]}
        """
        return summary.strip()


# 便捷函数
def create_fund_manager(data_file='data.json') -> FundDataManager:
    """创建基金数据管理器实例"""
    return FundDataManager(data_file)


# 使用示例
if __name__ == "__main__":
    # 创建管理器
    fm = create_fund_manager()

    # 示例：添加今日净值
    # fm.add_daily_nav(1.2345, 120.5)  # 净值1.2345，总资产120.5万

    # 示例：更新仓位
    # fm.update_positions(a_stock=60, hk_stock=25, us_stock=10, cash=5)

    # 示例：更新重仓股
    # holdings = [
    #     {"code": "000001", "name": "平安银行", "percentage": 15.2, "weeklyChange": 3.45},
    #     {"code": "000002", "name": "万科A", "percentage": 12.8, "weeklyChange": -1.23}
    # ]
    # fm.update_holdings(holdings)

    # 示例：添加交易记录
    # fm.add_trade_record("2025-05-27", "000001", "买入", "1000股", "12.34元")

    # 计算指标
    # fm.calculate_performance_metrics()
    # fm.update_monthly_returns()

    # 保存数据
    # fm.save_data()

    # 显示概况
    print(fm.get_summary())