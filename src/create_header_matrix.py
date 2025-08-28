import os
import glob
import csv

def generate_comparison_matrix(directory, output_filepath):
    print(f"--- '{directory}' 内のCSVヘッダー比較マトリクスの生成を開始します ---")
    csv_files = sorted(glob.glob(os.path.join(directory, '*.csv')))
    if not csv_files:
        print("分析対象のCSVファイルが見つかりません。")
        return

    headers_by_file, all_unique_columns = {}, set()
    print(f"発見したCSVファイル数: {len(csv_files)}件。ヘッダーを読み込んでいます...")
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                header = next(csv.reader(f))
                header_set = set(header)
                headers_by_file[filename] = header_set
                all_unique_columns.update(header_set)
        except Exception as e:
            print(f"[警告] ファイル '{filename}' の処理中にエラー: {e}")

    if not all_unique_columns:
        print("有効なヘッダーを持つファイルがありませんでした。")
        return

    sorted_unique_columns = sorted(list(all_unique_columns))
    sorted_filenames = [os.path.basename(f) for f in csv_files if os.path.basename(f) in headers_by_file]
    print(f"ユニークな列名の総数: {len(sorted_unique_columns)}件")
    print("比較マトリクスをCSVファイルに書き込んでいます...")
    try:
        with open(output_filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['column_name'] + sorted_filenames)
            for column_name in sorted_unique_columns:
                row = [column_name] + ['1' if column_name in headers_by_file[fn] else '0' for fn in sorted_filenames]
                writer.writerow(row)
        print("\n★★★ 比較マトリクスの生成が完了しました ★★★")
    except Exception as e:
        print(f"\n[エラー] CSV書き込み中にエラー: {e}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # ★★★ パス更新 ★★★
    csv_dir = os.path.join(project_root, 'data', 'csv')
    analysis_dir = os.path.join(project_root, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)
    output_csv_path = os.path.join(analysis_dir, 'header_comparison_matrix.csv')
    
    if not os.path.exists(csv_dir):
        print(f"エラー: 分析対象のフォルダ '{csv_dir}' が見つかりません。")
    else:
        generate_comparison_matrix(csv_dir, output_csv_path)
        print(f"\nレポートがCSVファイルに出力されました: {output_csv_path}")