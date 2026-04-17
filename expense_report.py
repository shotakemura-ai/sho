#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
経費精算書 自動生成スクリプト
三幸商事株式会社 営業部 竹村 翔

使い方:
    python expense_report.py

対応種別:
    1. 交際費（接待交際費申請書）
    2. 旅費交通費（旅費交通費精算書）
    3. 金銭受領書（立替経費精算）
    4. 仮払申請書
"""

import os
import sys
import io
from datetime import datetime, date

# 文字化け対策
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from template_builder import (
    build_kosaihi, build_kotsu, build_kinsen, build_karibarai
)

# ---------- 設定 ----------
OUTPUT_DIR  = r"\\192.168.1.126\本社\営業\営業2部\個人フォルダ\竹村\カーソル\三幸商事株式会社\財務・経理部\経費精算"
DEFAULT_NAME = "竹村　翔"


# ---------- 入力ヘルパー ----------
def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    val = input(f"  {prompt}{suffix}: ").strip()
    return val if val else default


def ask_date(prompt, default_today=True):
    default = date.today().strftime("%Y/%m/%d") if default_today else None
    while True:
        val = ask(prompt, default)
        try:
            return datetime.strptime(val, "%Y/%m/%d").date()
        except Exception:
            print("    ※ 日付は YYYY/MM/DD 形式で入力してください")


def ask_int(prompt, default=None):
    while True:
        val = ask(prompt, str(default) if default is not None else None)
        try:
            return int(val)
        except Exception:
            print("    ※ 整数で入力してください")


def ask_amount(prompt, default=0):
    while True:
        val = ask(prompt, str(default) if default else None)
        try:
            return int(str(val).replace(",", "").replace("円", ""))
        except Exception:
            print("    ※ 金額を数値で入力してください（例: 5000）")


def ask_yn(prompt):
    val = ask(f"{prompt} (y/n)", "n").lower()
    return val in ("y", "yes", "はい")


# ---------- 保存 ----------
def save_wb(wb, ref_date, label, extra=""):
    name = f"{ref_date.strftime('%Y%m%d')}_{label}"
    if extra:
        name += f"_{extra}"
    name += ".xlsx"
    out_path = os.path.join(OUTPUT_DIR, name)
    base, ext = os.path.splitext(out_path)
    n = 1
    while os.path.exists(out_path):
        out_path = f"{base}_{n}{ext}"
        n += 1
    wb.save(out_path)
    return out_path


# ---------- 各フォーム ----------

def create_kosaihi():
    print("\n【接待交際費申請書 入力】")
    申請日       = date.today()          # 申請日・領収日は作成日を自動セット
    申請者       = ask("申請者氏名", DEFAULT_NAME)
    相手先会社   = ask("相手先 会社名")
    相手先出席者 = ask("相手先 出席者氏名（複数は「・」区切り）")
    相手先人数   = ask_int("相手先 人数", 1)
    関係         = ask("当社との関係", "得意先")
    自社出席者   = ask("当社出席者", DEFAULT_NAME)
    自社人数     = ask_int("当社 人数", 1)
    実施日       = ask_date("実施日時（日付）")
    実施時間     = ask("実施時間（例: 19:00～21:00）", "")
    場所名       = ask("接待場所 名称")
    場所住所     = ask("接待場所 住所")
    目的         = ask("目的", "会食")

    print("\n  ── 支出明細（最大5行、空白Enterで終了） ──")
    expenses = []
    for i in range(5):
        payee = ask(f"  支払先[{i+1}]（空白で終了）", "")
        if not payee:
            break
        detail = ask(f"  内訳[{i+1}]（支払方法・金額等）", "")
        amount = ask_amount(f"  実績額[{i+1}]（会社カード払い→0）", 0)
        expenses.append((payee, detail, amount))

    仮払金 = ask_amount("仮払金（ある場合）", 0)

    data = {
        "申請日": 申請日, "申請者": 申請者,
        "相手先会社": 相手先会社, "相手先出席者": 相手先出席者, "相手先人数": 相手先人数,
        "関係": 関係, "自社出席者": 自社出席者, "自社人数": 自社人数,
        "実施日": 実施日, "実施時間": 実施時間,
        "場所名": 場所名, "場所住所": 場所住所, "目的": 目的,
        "expenses": expenses, "仮払金": 仮払金,
    }
    wb = build_kosaihi(data)
    extra = 相手先会社.replace("株式会社", "").replace("（株）", "").strip().replace(" ", "")
    return wb, 申請日, "交際費", extra


def create_kotsu():
    print("\n【旅費交通費精算書 入力】")
    精算日 = ask_date("精算日", default_today=True)
    報告者 = ask("報告者氏名", DEFAULT_NAME)
    目的地 = ask("目的地（訪問先）")
    目的   = ask("目的", "商談")

    print("\n  ── 交通費明細（最大12行、空白Enterで終了） ──")
    routes = []
    for i in range(12):
        val = input(f"    月日[{i+1}]（YYYY/MM/DD、空白で終了）: ").strip()
        if not val:
            break
        try:
            d = datetime.strptime(val, "%Y/%m/%d").date()
        except Exception:
            print("      ※ 形式エラー、スキップ"); continue
        route  = ask(f"    行き先[{i+1}]", "")
        payer  = ask(f"    支払先[{i+1}]", "")
        detail = ask(f"    内訳[{i+1}]", "")
        amount = ask_amount(f"    金額[{i+1}]（会社カード→0）", 0)
        routes.append((d, route, payer, detail, amount))

    日当フラグ = ask_yn("日当あり？")
    出張開始   = routes[0][0] if routes else date.today()
    出張終了   = routes[-1][0] if routes else date.today()
    日数       = 0
    日当単価   = 5000
    if 日当フラグ:
        出張開始 = ask_date("出張開始日", default_today=False)
        出張終了 = ask_date("出張終了日", default_today=False)
        日数     = ask_int("日数", (出張終了 - 出張開始).days + 1)
        日当単価 = ask_amount("日当単価", 5000)

    宿泊先 = ""
    宿泊料 = 0
    if ask_yn("宿泊あり？"):
        宿泊先 = ask("宿泊先名")
        宿泊料 = ask_amount("宿泊料（円）", 0)

    print("\n  ── 諸経費（最大5行、空白Enterで終了） ──")
    misc = []
    for i in range(5):
        val = input(f"    月日[{i+1}]（YYYY/MM/DD、空白で終了）: ").strip()
        if not val:
            break
        try:
            md = datetime.strptime(val, "%Y/%m/%d").date()
        except Exception:
            continue
        misc.append((md, ask(f"    支払先[{i+1}]", ""), ask(f"    摘要[{i+1}]", ""), ask_amount(f"    金額[{i+1}]", 0)))

    仮払金 = ask_amount("仮払金（ある場合）", 0)

    data = {
        "精算日": 精算日, "報告者": 報告者, "目的地": 目的地, "目的": 目的,
        "routes": routes,
        "日当フラグ": 日当フラグ, "出張開始": 出張開始, "出張終了": 出張終了,
        "日数": 日数, "日当単価": 日当単価,
        "宿泊先": 宿泊先, "宿泊料": 宿泊料,
        "misc": misc, "仮払金": 仮払金,
    }
    wb = build_kotsu(data)
    return wb, 精算日, "旅費交通費", 目的地.replace(" ", "")


def create_kinsen():
    print("\n【金銭請求書兼領収書 入力】")
    届出日 = ask_date("届出日", default_today=True)
    氏名   = ask("氏名", DEFAULT_NAME)
    目的   = ask("使用目的")

    print("\n  ── 支出明細（最大6行、空白Enterで終了） ──")
    items = []
    for i in range(6):
        val = input(f"    月日[{i+1}]（YYYY/MM/DD、空白で終了）: ").strip()
        if not val:
            break
        try:
            d = datetime.strptime(val, "%Y/%m/%d").date()
        except Exception:
            continue
        items.append((d, ask(f"    支払先[{i+1}]", ""), ask(f"    摘要[{i+1}]", ""), ask_amount(f"    金額[{i+1}]", 0)))

    仮払金 = ask_amount("仮払金（前渡金、ある場合）", 0)

    data = {"届出日": 届出日, "氏名": 氏名, "目的": 目的, "items": items, "仮払金": 仮払金}
    wb = build_kinsen(data)
    return wb, 届出日, "金銭受領書", ""


def create_karibarai():
    print("\n【仮払申請書 入力】")
    届出日 = ask_date("届出日", default_today=True)
    氏名   = ask("申請者氏名", DEFAULT_NAME)
    目的   = ask("使用目的（出張先・用途等）")
    金額   = ask_amount("申請金額（円）")
    使用日 = ask_date("使用日（出張・使用予定日）")

    data = {"届出日": 届出日, "氏名": 氏名, "目的": 目的, "金額": 金額, "使用日": 使用日}
    wb = build_karibarai(data)
    return wb, 届出日, "仮払申請書", ""


# ---------- メイン ----------
def main():
    print("=" * 55)
    print("  三幸商事株式会社 経費精算書 自動生成")
    print("=" * 55)
    print()
    print("  種別を選択してください：")
    print("    1. 交際費（接待交際費申請書）")
    print("    2. 旅費交通費（旅費交通費精算書）")
    print("    3. 金銭受領書（立替経費・駐車料金等）")
    print("    4. 仮払申請書")
    print("    q. 終了")
    print()

    choice = input("  番号を入力 > ").strip()
    if choice == "q":
        print("終了します。")
        return

    try:
        if choice == "1":
            wb, ref_date, label, extra = create_kosaihi()
        elif choice == "2":
            wb, ref_date, label, extra = create_kotsu()
        elif choice == "3":
            wb, ref_date, label, extra = create_kinsen()
        elif choice == "4":
            wb, ref_date, label, extra = create_karibarai()
        else:
            print("無効な選択です。")
            return

        print("\n保存中...")
        out_path = save_wb(wb, ref_date, label, extra)
        print(f"\n  保存完了:")
        print(f"    {out_path}")
        print()

    except Exception as e:
        import traceback; traceback.print_exc()


if __name__ == "__main__":
    main()
