import os
import glob
import csv
from tqdm import tqdm
import re

def sanitize_for_filename(name):
    """ファイル名として安全な文字列に変換する"""
    return re.sub(r'[\W\s]+', '_', name).strip('_')

def stream_unpivot_pipeline(csv_dir, long_csv_dir):
    print("--- ストリーミングETLパイプライン開始 ---")
    os.makedirs(long_csv_dir, exist_ok=True)
    
    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    if not csv_files:
        print("CSVファイルが見つかりません。")
        return

    for csv_path in tqdm(csv_files, desc="Streaming ETL"):
        filename = os.path.basename(csv_path)
        output_filepath = os.path.join(long_csv_dir, filename)

        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f_in:
                reader = csv.reader(f_in)
                original_header = next(reader)
                
                # 固定列（事業番号など）のインデックスを特定
                # この例ではシンプルに最初の3列を事業番号と仮定
                fixed_col_indices = list(range(3))
                fixed_col_names = [original_header[i] for i in fixed_col_indices]

                # 新しい縦長データのヘッダー
                new_header = fixed_col_names + ['original_column_name', 'value']

                with open(output_filepath, 'w', newline='', encoding='utf-8-sig') as f_out:
                    writer = csv.writer(f_out)
                    writer.writerow(new_header)

                    # --- ここからがストリーミング処理の核心 ---
                    # データ行を一行ずつループ
                    for row in reader:
                        try:
                            # 固定列の値を取得
                            fixed_values = [row[i] for i in fixed_col_indices]
                            
                            # unpivot対象の列をループ
                            for i, value in enumerate(row):
                                # 固定列はスキップ
                                if i in fixed_col_indices:
                                    continue
                                
                                # 値が空でなければ書き出す
                                if value is not None and value.strip() != '':
                                    col_name = original_header[i]
                                    new_row = fixed_values + [col_name, value]
                                    writer.writerow(new_row)
                        except IndexError:
                            # 行の途中でデータが途切れている場合など
                            continue
        
        except Exception as e:
            tqdm.write(f"\n[エラー] ファイル '{filename}' の処理中にエラー: {e}")
            continue

    print("\n★★★ ストリーミングETLが完了しました ★★★")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_input_dir = os.path.join(project_root, 'data', 'csv')
    long_csv_output_dir = os.path.join(project_root, 'data', 'long_csv')
    
    stream_unpivot_pipeline(csv_input_dir, long_csv_output_dir)