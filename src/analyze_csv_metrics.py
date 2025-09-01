import os
import glob
import csv
from tqdm import tqdm
import pandas as pd # 結果をDataFrameにまとめるために使用

def analyze_csv_files(csv_dir, output_filepath):
    """
    指定されたディレクトリ内の全CSVファイルの定性的なメトリクスを集計し、
    結果をコンソールに表示し、CSVファイルとして保存する。
    """
    print(f"--- '{csv_dir}' 内のCSVファイルの異常性分析を開始 ---")
    
    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    if not csv_files:
        print("分析対象のCSVファイルが見つかりません。")
        return

    results = []
    for csv_path in tqdm(csv_files, desc="Analyzing CSV files"):
        try:
            # ファイルサイズを取得
            file_size_bytes = os.path.getsize(csv_path)
            
            # ヘッダー行だけを高速に読み込む
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                header = next(reader)
            
            # メトリクスを計算
            num_columns = len(header)
            if num_columns > 0:
                max_col_name_len = max(len(col) for col in header)
            else:
                max_col_name_len = 0
                
            results.append({
                "filename": os.path.basename(csv_path),
                "file_size_mb": round(file_size_bytes / (1024 * 1024), 2),
                "column_count": num_columns,
                "max_col_name_length": max_col_name_len
            })
        except Exception as e:
            tqdm.write(f"[警告] ファイル '{os.path.basename(csv_path)}' の処理中にエラー: {e}")

    if not results:
        print("分析できるファイルがありませんでした。")
        return

    # --- 結果をDataFrameに変換し、サマリーと詳細を表示 ---
    df = pd.DataFrame(results)

    # --- サマリー統計 ---
    print("\n" + "="*50)
    print("【総合サマリー】")
    print("="*50)
    print(f"分析ファイル数: {len(df)} 件")
    print(f"合計ファイルサイズ: {df['file_size_mb'].sum():.2f} MB")
    print("\n--- 列数に関する統計 ---")
    print(f"最大列数: {df['column_count'].max():,} 列")
    print(f"最小列数: {df['column_count'].min():,} 列")
    print(f"平均列数: {df['column_count'].mean():,.0f} 列")
    print("\n--- 列名長に関する統計 ---")
    print(f"最大の列名長: {df['max_col_name_length'].max():,} 文字")
    print("="*50)

    # --- 詳細な結果 ---
    print("\n【ファイルごとの詳細】")
    print(df.to_string())
    
    # --- 結果をCSVに保存 ---
    df.to_csv(output_filepath, index=False, encoding='utf-8-sig')
    print(f"\n分析結果がCSVファイルに出力されました: {output_filepath}")


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # ★★★ 分析対象は、変換直後の「生」の横長CSV ★★★
    csv_input_dir = os.path.join(project_root, 'data', 'csv')
    
    analysis_dir = os.path.join(project_root, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)
    metrics_output_path = os.path.join(analysis_dir, 'csv_metrics_summary.csv')
    
    analyze_csv_files(csv_input_dir, metrics_output_path)
    print("\n★★★ 分析が完了しました ★★★")