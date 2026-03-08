import flet as ft
from datetime import datetime
import json
import os
import traceback

# 定义本地数据文件路径
DATA_FILE = "ledger_data.json"

def load_data():
    """从本地加载数据，如果文件不存在则返回空列表"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 将字符串日期转换回 datetime 对象
                for item in data:
                    item['date'] = datetime.fromisoformat(item['date'])
                return data
        except Exception:
            return []
    return []

def save_data(records):
    """将数据序列化并保存到本地"""
    # 转换 datetime 为字符串以便 JSON 序列化
    serializable_data = []
    for r in records:
        serializable_data.append({
            "amount": r["amount"],
            "type": r["type"],
            "date": r["date"].isoformat()
        })
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable_data, f, ensure_ascii=False, indent=2)

def main(page: ft.Page):
    try:
        page.title = "极简记账"
        page.theme_mode = "light" 
        page.horizontal_alignment = "center" 

        # 启动时加载历史数据
        records = load_data()

        amount_input = ft.TextField(label="金额", width=150)
        type_dropdown = ft.Dropdown(
            label="类型",
            options=[ft.dropdown.Option("支出"), ft.dropdown.Option("收入")],
            value="支出",
            width=100
        )
        summary_text = ft.Text("本月总结: 收入 0.00 | 支出 0.00 | 结余 0.00", size=16, weight="bold")
        record_list = ft.ListView(expand=True, spacing=5)

        def update_ui():
            current_month = datetime.now().month
            monthly_records = [r for r in records if r['date'].month == current_month]
            income = sum(r['amount'] for r in monthly_records if r['type'] == '收入')
            expense = sum(r['amount'] for r in monthly_records if r['type'] == '支出')
            
            summary_text.value = f"本月总结: 收入 {income:.2f} | 支出 {expense:.2f} | 结余 {(income - expense):.2f}"
            
            record_list.controls.clear()
            for r in reversed(records):
                text_color = "red" if r['type'] == '支出' else "green"
                record_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{r['type']}: {r['amount']:.2f}", color=text_color, weight="bold"),
                        subtitle=ft.Text(r['date'].strftime("%Y-%m-%d %H:%M")),
                    )
                )
            page.update()

        def add_record(e):
            if not amount_input.value:
                return
            try:
                amount = float(amount_input.value)
            except ValueError:
                return
                
            records.append({
                "amount": amount,
                "type": type_dropdown.value,
                "date": datetime.now()
            })
            amount_input.value = "" 
            
            # 每次记账后，强制写入本地硬盘
            save_data(records)
            update_ui()

        page.add(
            summary_text,
            ft.Divider(),
            ft.Row([amount_input, type_dropdown], alignment="center"),
            ft.ElevatedButton("记一笔", on_click=add_record, width=260),
            ft.Divider(),
            record_list
        )
        
        # 初始启动时渲染一次 UI
        update_ui()
        
    except Exception as e:
        page.add(ft.Text(f"UI 初始化失败:\n{traceback.format_exc()}", color="red", selectable=True))

if __name__ == "__main__":
    try:
        ft.app(target=main)
    except Exception as e:
        print("程序运行崩溃，错误日志如下：")
        print(traceback.format_exc())
        input("\n按回车键退出...")
