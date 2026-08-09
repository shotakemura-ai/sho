"""
MJS e-ドキュメントCloud 領収書自動登録スクリプト
使い方:
  python edoc_register.py          # 今月の領収書を登録
  python edoc_register.py 202604   # 指定月の領収書を登録
"""

import asyncio
import json
import re
import sys
from pathlib import Path
from datetime import datetime

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# ============================================================
# パス設定
# ============================================================
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "edoc_config.json"
RECEIPTS_DIR = BASE_DIR / "財務・経理部" / "経費精算" / "領収書"
BASE_URL = "https://www.edoc.cloud369.com"


# ============================================================
# 設定・データ読み込み
# ============================================================
def load_config():
    if not CONFIG_FILE.exists():
        print("❌ edoc_config.json が見つかりません。")
        print("   edoc_config.json.example をコピーして edoc_config.json を作成してください。")
        sys.exit(1)
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_receipts(month_str=None):
    if month_str is None:
        month_str = datetime.now().strftime("%Y%m")
    receipts_file = RECEIPTS_DIR / month_str / f"receipts_{month_str}.json"
    if not receipts_file.exists():
        print(f"❌ 領収書リストが見つかりません: {receipts_file}")
        print(f"   {receipts_file} を作成してください（receipts_template.json を参考に）。")
        sys.exit(1)
    with open(receipts_file, encoding="utf-8") as f:
        receipts = json.load(f)
    return receipts, receipts_file.parent


# ============================================================
# ログイン
# ============================================================
async def login(page, config):
    print("🔑 ログイン中...")
    await page.goto(f"{BASE_URL}/users/sign_in", wait_until="networkidle")

    # メールアドレス／ID
    email_field = page.locator('input[type="email"], input[name="email"], input[name="login"]').first
    await email_field.fill(config["username"])

    # パスワード
    await page.locator('input[type="password"]').fill(config["password"])

    # ログインボタン
    await page.locator('input[type="submit"], button[type="submit"]').click()

    try:
        await page.wait_for_url(f"{BASE_URL}/users/dashboard", timeout=15000)
        print("✅ ログイン成功")
    except PlaywrightTimeoutError:
        print("❌ ログインに失敗しました。ID/パスワードを確認してください。")
        sys.exit(1)


# ============================================================
# 書類登録（1件）
# ============================================================
async def register_receipt(page, receipt, pdf_path, config):
    book_name = receipt["書類名"]
    print(f"  📄 登録中: {book_name}")

    # 新規作成ページへ
    # まずメニューから新規作成をクリック（URLが不明のため）
    await page.goto(f"{BASE_URL}/users/dashboard", wait_until="networkidle")
    new_btn = page.get_by_role("link", name=re.compile("新規作成")).first
    await new_btn.click()
    await page.wait_for_load_state("networkidle")

    # --- 書類分類（領収書）---
    await page.get_by_label("書類分類").select_option(label="領収書")

    # --- 書類名 ---
    await page.get_by_label("書類名").fill(book_name)

    # --- 書類年月日（YYYY-MM-DD → 年/月/日 の日付入力に対応）---
    date_input = page.get_by_label("書類年月日")
    await date_input.fill(receipt["書類年月日"])

    # --- 取引先名 ---
    vendor_field = page.get_by_label("取引先名")
    await vendor_field.fill(receipt["取引先名"])

    # --- 金額 ---
    await page.get_by_label("金額").fill(str(receipt["金額"]))

    # --- 通貨（円：デフォルトのまま）---

    # --- 保存先（領収書（受領））---
    await page.get_by_label("保存先").select_option(label="領収書（受領）")

    # --- 備考（任意）---
    if receipt.get("備考"):
        await page.get_by_label("備考").fill(receipt["備考"])

    # --- PDF アップロード ---
    await page.set_input_files('input[type="file"]', str(pdf_path))
    await page.wait_for_timeout(3000)  # アップロード完了待ち

    # --- 承認者選択へ ---
    await page.get_by_role("button", name=re.compile("承認者選択")).click()
    await page.wait_for_load_state("networkidle")

    # --- 承認者選択画面 ---
    await select_approver(page, config["approver_name"])

    print(f"  ✅ 登録完了: {book_name}")


# ============================================================
# 承認者選択（承認者選択画面）
# ============================================================
async def select_approver(page, approver_name):
    """
    承認者選択画面で指定の承認者を選択して登録を確定する。
    画面の仕様によって調整が必要な場合があります。
    """
    try:
        # 承認者名で行を探してクリック（テーブル行やチェックボックスを想定）
        approver_row = page.get_by_text(approver_name).first
        await approver_row.wait_for(timeout=5000)
        await approver_row.click()

        # 登録確定ボタン（「登録」「確定」「完了」「申請」などを試みる）
        submit_btn = page.get_by_role("button", name=re.compile("登録|確定|完了|申請")).first
        await submit_btn.click()
        await page.wait_for_load_state("networkidle")

    except PlaywrightTimeoutError:
        print(f"  ⚠️  承認者「{approver_name}」が見つかりません。手動で選択してください。")
        print("     ブラウザで承認者を選択して登録を完了後、Enterキーを押してください...")
        input()


# ============================================================
# メイン処理
# ============================================================
async def main():
    config = load_config()

    month_str = sys.argv[1] if len(sys.argv) > 1 else None
    receipts, pdf_dir = load_receipts(month_str)

    print(f"\n📋 登録件数: {len(receipts)} 件")
    print(f"📁 PDFフォルダ: {pdf_dir}\n")

    # PDF存在確認
    missing = [r for r in receipts if not (pdf_dir / r["pdf_file"]).exists()]
    if missing:
        print("⚠️  以下のPDFが見つかりません:")
        for r in missing:
            print(f"   - {r['pdf_file']}")
        answer = input("見つからないファイルをスキップして続行しますか？ (y/N): ")
        if answer.lower() != "y":
            sys.exit(0)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context()
        page = await context.new_page()

        success_list = []
        error_list = []

        try:
            await login(page, config)

            for receipt in receipts:
                pdf_path = pdf_dir / receipt["pdf_file"]
                if not pdf_path.exists():
                    error_list.append(f"{receipt['書類名']} (PDFなし)")
                    continue
                try:
                    await register_receipt(page, receipt, pdf_path, config)
                    success_list.append(receipt["書類名"])
                except Exception as e:
                    print(f"  ❌ エラー: {receipt['書類名']} — {e}")
                    error_list.append(receipt["書類名"])

        finally:
            print(f"\n{'='*50}")
            print(f"📊 結果: 成功 {len(success_list)} 件 / エラー {len(error_list)} 件")
            if error_list:
                print("エラー一覧:")
                for name in error_list:
                    print(f"  ❌ {name}")
            print("='*50")

            input("\nブラウザを閉じるには Enter を押してください...")
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
