import os, glob, duckdb
from tqdm import tqdm

def convert_all_csv_to_parquet(csv_dir, parquet_dir):
    print(f"\n--- {os.path.basename(csv_dir)} -> Parquet 変換開始 ---")
    os.makedirs(parquet_dir, exist_ok=True)
    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    if not csv_files:
        print("変換対象のCSVファイルが見つかりません。")
        return
        
    con = duckdb.connect()
    # 全ての列をVARCHARとして読み込む設定
    read_csv_options = "auto_detect=false, columns={'original_column_name': 'VARCHAR', 'value': 'VARCHAR'}"

    for csv_path in tqdm(csv_files, desc="CSV to Parquet"):
        basename, _ = os.path.splitext(os.path.basename(csv_path))
        parquet_path = os.path.join(parquet_dir, f"{basename}.parquet")
        
        # read_csv_autoで型推測をさせつつ、Parquetに変換
        con.execute(f"""
            COPY (SELECT * FROM read_csv_auto('{csv_path.replace(os.sep, '/')}', header=true))
            TO '{parquet_path.replace(os.sep, '/')}'
            (FORMAT PARQUET, OVERWRITE_OR_IGNORE);
        """)
    print("\n★★★ Parquetへの変換が完了しました ★★★")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # ★★★ 入力元を long_csv に変更 ★★★
    csv_input_dir = os.path.join(project_root, 'data', 'long_csv')
    parquet_output_dir = os.path.join(project_root, 'data', 'parquet')
    convert_all_csv_to_parquet(csv_input_dir, parquet_output_dir)