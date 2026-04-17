"""
Google API 認証モジュール
全 Google サービス共通の OAuth 2.0 認証を管理する
"""

import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 使用するスコープ（必要に応じて追加）
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
]

# 認証ファイルのパス（このスクリプトと同じフォルダ）
BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / 'credentials.json'
TOKEN_FILE = BASE_DIR / 'token.pickle'


def get_credentials():
    """認証情報を取得（初回はブラウザで認証）"""
    creds = None

    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"credentials.json が見つかりません: {CREDENTIALS_FILE}\n"
                    "Google Cloud Console からダウンロードして同じフォルダに置いてください。"
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'wb') as f:
            pickle.dump(creds, f)
        print("認証成功。token.pickle を保存しました。")

    return creds


def get_drive_service():
    return build('drive', 'v3', credentials=get_credentials())


def get_gmail_service():
    return build('gmail', 'v1', credentials=get_credentials())


def get_calendar_service():
    return build('calendar', 'v3', credentials=get_credentials())


def get_sheets_service():
    return build('sheets', 'v4', credentials=get_credentials())


if __name__ == '__main__':
    print("Google API 認証テスト")
    creds = get_credentials()
    print(f"認証OK: {creds.token[:20]}...")
    print("Drive / Gmail / Calendar / Sheets に接続できます。")
