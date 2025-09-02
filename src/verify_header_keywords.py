import os
import glob
import csv
import json
from collections import defaultdict
from tqdm import tqdm
import typing

# --- 検証したいメタデータの「仮説」をここに定義 ---
# この辞書を編集して、様々なキーワードを試すことができる
METADATA_HYPOTHESIS = {
    "project_id": ["事業番号", "事業№", "通し番号", "事業No", "整理番号"],
    "project_name": ["事業名", "件名", "事業・施策名"],
    "year": ["年度"],
    "budget_amount": ["予算", "要求額", "決定額", "当初予算", "補正予算"],
    "expenditure_amount": ["支出", "執行額", "支出済額", "支出額"],
    "governing_agency": ["府省庁", "府省", "実施機関", "所管"]
}

def verify_keywords_in_headers(csv_dir: str, hypothesis: dict) -> dict:
    """
    指定されたディレクトリ内の全CSVのヘッダーをスキャンし、
    仮説キーワードの出現頻度と場所を集計する。
    """
    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    if not csv_files:
        print("分析対象のCSVファイルが見つかりません。")
        return {}

    # {target_key: {keyword: {"count": 0, "found_in_files": set()}}}
    # found_in_filesはsetを使い、ファイル名の重複を防ぐ
    findings = defaultdict(lambda: defaultdict(lambda: {"count": 0, "found_in_files": set()}))

    for csv_path in tqdm(csv_files, desc="Verifying header keywords"):
        filename = os.path.basename(csv_path)
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header:
                    continue

                # ヘッダー内の各列名に対して、仮説キーワードをチェック
                for col_name in header:
                    for target_key, keywords in hypothesis.items():
                        for keyword in keywords:
                            if keyword in col_name:
                                # キーワードが見つかったらカウントとファイル名を記録
                                findings[target_key][keyword]["count"] += 1
                                findings[target_key][keyword]["found_in_files"].add(filename)
        except Exception as e:
            print(f"\nファイル処理中にエラーが発生しました {filename}: {e}")

    # 最終的な出力のために、setをソート済みリストに変換
    final_report = {}
    for target_key, keyword_data in findings.items():
        final_report[target_key] = {}
        for keyword, stats in keyword_data.items():
            final_report[target_key][keyword] = {
                "total_occurrences": stats["count"],
                "found_in_files_count": len(stats["found_in_files"]),
                "found_in_files": sorted(list(stats["found_in_files"]))
            }
            
    return final_report

def main():
    """メインの実行関数"""
    print("--- CSVヘッダーに含まれるキーワードの検証を開始 ---")
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_input_dir = os.path.join(project_root, 'data', 'csv')
    analysis_dir = os.path.join(project_root, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)
    output_path = os.path.join(analysis_dir, 'header_keyword_verification.json')
    
    report = verify_keywords_in_headers(csv_input_dir, METADATA_HYPOTHESIS)

    if not report:
        print("検証結果は空です。")
        return

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n検証レポートが出力されました: {output_path}")
    print("レポートを基に `METADATA_TARGETS` の精度を高めてください。")


if __name__ == "__main__":
    main()
    print("\n★★★ キーワード検証が完了しました ★★★")