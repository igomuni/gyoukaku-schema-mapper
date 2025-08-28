import os
import glob
import csv
from collections import defaultdict

def classify_csv_headers(directory, output_filepath):
    """
    指定されたディレクトリ内のCSVファイルをヘッダーで分類し、結果をテキストファイルに出力する。
    """
    # with open... as report_file: ブロックを使い、ファイルへの書き込みを安全に行う
    with open(output_filepath, 'w', encoding='utf-8') as report_file:
        
        # --- ヘルパー関数を定義 ---
        # コンソールに表示し、同時にファイルにも書き込む
        def log(message):
            print(message)
            report_file.write(message + '\n')

        log(f"--- '{directory}' 内のCSVヘッダー分類を開始します ---")
        
        csv_files = glob.glob(os.path.join(directory, '*.csv'))
        if not csv_files:
            log("検証対象のCSVファイルが見つかりません。")
            return

        # --- ステップ1: フィンガープリントでファイルをグループ化 ---
        header_signatures = defaultdict(list)
        for file_path in csv_files:
            filename = os.path.basename(file_path)
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    header = next(reader)
                
                column_count = len(header)
                total_length = sum(len(col) for col in header)
                signature = (column_count, total_length)
                
                header_signatures[signature].append({
                    "filename": filename,
                    "header_content": header
                })
            except StopIteration:
                log(f"[警告] ファイル '{filename}' は空かヘッダーがありません。スキップします。")
            except Exception as e:
                log(f"[エラー] ファイル '{filename}' の読み込み中にエラーが発生: {e}")

        # --- ステップ2: 各グループを検証し、タイプ分けして報告 ---
        if not header_signatures:
            log("有効なヘッダーを持つファイルがありませんでした。")
            return

        log("\n--- 分類結果 ---")
        type_index = 1
        
        # フィンガープリントでソートし、毎回同じ順序で出力されるようにする
        for signature, file_group in sorted(header_signatures.items()):
            column_count, total_length = signature
            
            log(f"\n▼ タイプ {type_index} (フィンガープリント)")
            log(f"  - 列数          : {column_count}")
            log(f"  - ヘッダー合計長: {total_length}")
            
            reference_header = file_group[0]["header_content"]
            is_consistent = True
            
            for file_info in file_group[1:]:
                if file_info["header_content"] != reference_header:
                    is_consistent = False
                    log(f"  [警告] このグループ内でヘッダー内容の不一致が見つかりました。")
                    log(f"    - 基準ファイル '{file_group[0]['filename']}' と")
                    log(f"    - 比較ファイル '{file_info['filename']}' の内容が異なります。")
            
            if is_consistent:
                log(f"  - 検証結果      : このタイプのヘッダーはすべて完全に一致します。")

            log(f"  - 該当ファイル ({len(file_group)}件):")
            for file_info in file_group:
                log(f"    - {file_info['filename']}")
                
            type_index += 1

        log("\n★★★ ヘッダーの分類が完了しました ★★★")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(project_root, 'data', 'processed')
    
    # ★★★ 変更点: 出力ファイルパスを定義 ★★★
    report_output_path = os.path.join(project_root, 'header_classification_report.txt')
    
    if not os.path.exists(processed_dir):
        print(f"エラー: 検証対象のフォルダ '{processed_dir}' が見つかりません。")
    else:
        # ★★★ 変更点: 関数に出力パスを渡す ★★★
        classify_csv_headers(processed_dir, report_output_path)
        
        # 最後にレポートの場所をユーザーに通知
        print(f"\nレポートがファイルに出力されました: {report_output_path}")