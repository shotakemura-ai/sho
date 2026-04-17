#!/usr/bin/env python3
"""
三幸プロダクツの欠員13名をスプレッドシートに追加するスクリプト
挿入位置: 行89（松本真奈美）の直後 = 行90から
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google_auth import get_sheets_service

SPREADSHEET_ID = '1qZbzvN8goWp1P_ORZuTxeQWnFQblE7B5Xq7k7V4RQY8'
SHEET_ID = 0
INSERT_AFTER_ROW = 89   # 松本真奈美の行（1-based）

# 年齢列: H=85期(end_year=2023) から 31列
AGE_COL_START = 7  # 0-based index of column H
AGE_NUM_COLS = 31
AGE_START_YEAR = 2023  # H列=85期の終了年


def calc_age(birth_year, birth_month, end_year):
    """年齢計算: 6月以降生まれは end_year - birth_year - 1"""
    return end_year - birth_year - (1 if birth_month >= 6 else 0)


def fmt_join(year, month, day):
    """入社日エントリ文字列を生成"""
    if day:
        return f'{year}/{month}/{day}→入社'
    else:
        return f'{year}/{month}→入社'


# 追加する13名のデータ
# (氏名, 所属工場, 役職, 生年, 生月, 生日, 入社年, 入社月, 入社日)
NEW_EMPLOYEES = [
    # 東大阪工場
    ('西村\u3000健二',   '東大阪工場', '',      1988,  1, 27, 2024,  4,  1),
    ('灰塚\u3000直樹',   '東大阪工場', '',      1996,  9, 18, 2024,  8,  1),
    # 松原工場（正社員）
    ('齋藤\u3000太一',   '松原工場',   '',      1989,  7, 30, 2023, 12,  4),
    ('山本\u3000雪乃',   '松原工場',   '',      2002,  1,  2, 2024,  6,  1),
    ('赤井\u3000正',     '松原工場',   '',      1982,  2, 19, 2024, 10, 15),
    ('川西\u3000美紀',   '松原工場',   '',      1990,  5, 14, 2024, 11,  1),
    # 松原工場（パート）
    ('有田\u3000怜奈',   '松原工場',   'パート', 2001,  5, 22, 2024,  2, 13),
    ('岩永\u3000歩',     '松原工場',   'パート', 2004,  7, 19, 2024,  2, 26),
    ('石丸\u3000智美',   '松原工場',   'パート', 1993, 11,  2, 2024,  6,  1),
    ('奥谷\u3000珠里',   '松原工場',   'パート', 1993, 10, 24, 2024,  9,  2),
    ('島田\u3000苑果',   '松原工場',   'パート', 2003,  4, 25, 2026,  2,  9),
    ('國重\u3000亜寿佳', '松原工場',   'パート', 1992,  2,  4, 2026,  2, 19),
    ('中谷\u3000宏子',   '松原工場',   'パート', 1982,  8, 27, 2026,  4,  1),
]


def build_row(name, factory, role, birth_year, birth_month, birth_day,
              join_year, join_month, join_day):
    """スプレッドシート1行分のデータを構築"""
    join_str = fmt_join(join_year, join_month, join_day)

    # 月日: M/D 形式（ゼロ埋めなし）
    birth_md = f'{birth_month}/{birth_day}'
    birth_y_str = str(birth_year)

    # 年齢列（31列）
    ages = []
    for i in range(AGE_NUM_COLS):
        end_year = AGE_START_YEAR + i
        age = calc_age(birth_year, birth_month, end_year)
        ages.append(str(age))

    row = [name, 'プロダクツ', factory, role, join_str,
           birth_y_str, birth_md] + ages
    return row


def main():
    service = get_sheets_service()

    # ---------- 1. 行を挿入（13行、行89の直後） ----------
    insert_start = INSERT_AFTER_ROW   # 0-based: 行89 = index 89（次の行に挿入）
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            'requests': [{
                'insertDimension': {
                    'range': {
                        'sheetId': SHEET_ID,
                        'dimension': 'ROWS',
                        'startIndex': INSERT_AFTER_ROW,  # 0-based, 行90の位置
                        'endIndex': INSERT_AFTER_ROW + len(NEW_EMPLOYEES),
                    },
                    'inheritFromBefore': True
                }
            }]
        }
    ).execute()
    print(f'行90〜{89 + len(NEW_EMPLOYEES)} を挿入しました（13行）')

    # ---------- 2. データ書き込み ----------
    data_updates = []
    for idx, emp in enumerate(NEW_EMPLOYEES):
        row_num = INSERT_AFTER_ROW + 1 + idx  # 1-based: 90, 91, ...
        row_data = build_row(*emp)
        data_updates.append({
            'range': f'シート1!A{row_num}',
            'values': [row_data]
        })
        name = emp[0]
        join_str = fmt_join(emp[6], emp[7], emp[8])
        print(f'  行{row_num}: {name} ({emp[2] or "正社員"}) | {join_str} | 生年{emp[3]}/{emp[4]}/{emp[5]}')

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            'valueInputOption': 'USER_ENTERED',
            'data': data_updates
        }
    ).execute()

    print(f'\n=== 完了 ===')
    print(f'三幸プロダクツ 欠員 {len(NEW_EMPLOYEES)} 名を追加しました')


if __name__ == '__main__':
    main()
