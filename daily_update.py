# @Author  : Kurt
# @Time    : 27/05/2025 16:46
from FundManager import create_fund_manager


def daily_update():
    """每日更新脚本"""
    fm = create_fund_manager()

    print("=== 阔盈基金每日数据更新 ===")
    print(fm.get_summary())
    print()

    # 获取用户输入
    try:
        nav = float(input("请输入今日净值: "))
        assets = input("请输入总资产(万元，留空则自动计算): ")

        if assets.strip():
            assets = float(assets)
        else:
            assets = None

        # 更新数据
        fm.add_daily_nav(nav, assets)
        fm.calculate_performance_metrics()
        fm.update_monthly_returns()

        # 询问是否更新其他数据
        update_positions = input("是否需要更新仓位配置？(y/n): ").lower() == 'y'
        if update_positions:
            a_stock = float(input("A股仓位百分比: ") or "0")
            hk_stock = float(input("港股仓位百分比: ") or "0")
            us_stock = float(input("美股仓位百分比: ") or "0")
            cash = float(input("现金仓位百分比: ") or "0")
            fm.update_positions(a_stock, hk_stock, us_stock, cash)

        # 保存数据
        fm.save_data()
        print("\n✅ 数据更新完成！")
        print(fm.get_summary())

    except KeyboardInterrupt:
        print("\n❌ 用户取消操作")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    daily_update()