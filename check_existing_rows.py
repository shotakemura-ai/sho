#!/usr/bin/env python3
import sys
sys.stdout.reconfigure(encoding='utf-8')
from google_auth import get_sheets_service

SPREADSHEET_ID = '1qZbzvN8goWp1P_ORZuTxeQWnFQblE7B5Xq7k7V4RQY8'

service = get_sheets_service()
result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range='シート1!A80:I95'
).execute()
rows = result.get('values', [])
for i, row in enumerate(rows):
    print(f'行{80+i}: {row}')
