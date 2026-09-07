"""
Google Drive 操作スクリプト
ファイル一覧の取得・整理案の出力
"""

import json
from google_auth import get_drive_service


def list_all_files(service, folder_id='root', path='', depth=0, max_depth=5):
    """ドライブ内の全ファイル・フォルダを再帰的に取得"""
    if depth > max_depth:
        return []

    results = []
    page_token = None

    query = f"'{folder_id}' in parents and trashed = false"

    while True:
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='nextPageToken, files(id, name, mimeType, modifiedTime, size)',
            pageToken=page_token,
            pageSize=100,
            orderBy='folder,name'
        ).execute()

        files = response.get('files', [])
        for f in files:
            is_folder = f['mimeType'] == 'application/vnd.google-apps.folder'
            current_path = f"{path}/{f['name']}" if path else f['name']
            results.append({
                'id': f['id'],
                'name': f['name'],
                'path': current_path,
                'type': 'folder' if is_folder else 'file',
                'mimeType': f['mimeType'],
                'modifiedTime': f.get('modifiedTime', ''),
                'size': f.get('size', ''),
                'depth': depth,
            })
            if is_folder:
                children = list_all_files(service, f['id'], current_path, depth + 1, max_depth)
                results.extend(children)

        page_token = response.get('nextPageToken')
        if not page_token:
            break

    return results


def print_tree(files):
    """ツリー形式で表示"""
    for f in files:
        indent = '  ' * f['depth']
        icon = '📁' if f['type'] == 'folder' else '📄'
        print(f"{indent}{icon} {f['name']}")


def save_file_list(files, output_path='drive_contents.json'):
    """ファイル一覧をJSONに保存"""
    with open(output_path, 'w', encoding='utf-8') as fp:
        json.dump(files, fp, ensure_ascii=False, indent=2)
    print(f"\nファイル一覧を保存: {output_path}")


def get_storage_info(service):
    """ストレージ使用量を取得"""
    about = service.about().get(fields='storageQuota, user').execute()
    user = about.get('user', {})
    quota = about.get('storageQuota', {})

    used = int(quota.get('usage', 0))
    limit = int(quota.get('limit', 0)) if quota.get('limit') else None
    used_in_drive = int(quota.get('usageInDrive', 0))

    print(f"\n=== Google Drive 情報 ===")
    print(f"ユーザー: {user.get('displayName')} ({user.get('emailAddress')})")
    print(f"使用量: {used / 1024**3:.2f} GB")
    if limit:
        print(f"上限: {limit / 1024**3:.2f} GB")
    print(f"Drive使用量: {used_in_drive / 1024**3:.2f} GB")


if __name__ == '__main__':
    print("Google Drive に接続中...")
    service = get_drive_service()

    # ストレージ情報
    get_storage_info(service)

    # ファイル一覧取得
    print("\nファイル一覧を取得中（しばらくお待ちください）...")
    files = list_all_files(service)

    print(f"\n合計: {len([f for f in files if f['type'] == 'folder'])} フォルダ / "
          f"{len([f for f in files if f['type'] == 'file'])} ファイル\n")

    # ツリー表示
    print_tree(files)

    # JSON保存
    save_file_list(files)
    print("\n次のステップ: drive_contents.json を Claude に見せて整理案を作成できます。")
