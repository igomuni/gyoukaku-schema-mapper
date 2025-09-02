import os
import glob
import csv
import json
from tqdm import tqdm
import sys

# --- ここに探索したいキーワードを設定 ---
TARGET_KEYWORD = "支出"

def explore_headers_for_keyword(csv_dir: str, keyword: str) -> list:
    """
    指定されたキーワードを含む、全てのユニークなヘッダー名を探索してリストアップする。
    """
    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    if not csv_files:
        print("分析対象のCSVファイルが見つかりません。")
        return []

    found_headers = set() # 重複を自動的に排除するためにセットを使用

    for csv_path in tqdm(csv_files, desc=f"Exploring headers with '{keyword}'"):
        try:
            # ヘッダーの文字化けに対処するため、複数のエンコーディングを試行
            encodings_to_try = ['utf-8-sig', 'cp932', 'shift_jis']
            header = None
            for enc in encodings_to_try:
                try:
                    with open(csv_path, 'r', encoding=enc) as f:
                        reader = csv.reader(f)
                        header = next(reader, None)
                    break # 読み込めたらループを抜ける
                except (UnicodeDecodeError, csv.Error):
                    continue
            
            if not header:
                tqdm.write(f"警告: ファイルのヘッダーが読み込めませんでした: {os.path.basename(csv_path)}")
                continue

            for col_name in header:
                if keyword in col_name:
                    found_headers.add(col_name)
        except Exception as e:
            tqdm.write(f"\nファイル処理中に予期せぬエラーが発生しました {os.path.basename(csv_path)}: {e}")

    return sorted(list(found_headers))

def main():
    """メインの実行関数"""
    print(f"--- キーワード '{TARGET_KEYWORD}' を含む列名の探索を開始 ---")

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_input_dir = os.path.join(project_root, 'data', 'csv')
    analysis_dir = os.path.join(project_root, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)
    output_path = os.path.join(analysis_dir, f'explore_headers_{TARGET_KEYWORD}.json')

    unique_headers = explore_headers_for_keyword(csv_input_dir, TARGET_KEYWORD)

    if not unique_headers:
        print("指定されたキーワードを含む列名は見つかりませんでした。")
        return

    # --- コンソールへの出力 ---
    print("\n--- 探索結果 ---")
    print(f"'{TARGET_KEYWORD}' を含むユニークな列名が {len(unique_headers)} 件見つかりました:")
    for header_name in unique_headers:
        print(f"  - {header_name}")
    
    # --- ファイルへの出力 ---
    report = {
        "target_keyword": TARGET_KEYWORD,
        "unique_header_count": len(unique_headers),
        "header_list": unique_headers
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n詳細なリストが出力されました: {output_path}")

if __name__ == "__main__":
    main()
    print(f"\n★★★ '{TARGET_KEYWORD}' の探索が完了しました ★★★")