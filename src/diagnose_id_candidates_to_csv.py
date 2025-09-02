import os
import glob
import pandas as pd
from tqdm import tqdm

# --- 診断対象のキーワード ---
ID_KEYWORDS = ["事業番号", "整理番号", "番号", "ID", "コード"]

# --- 絶対に除外するキーワード ---
# ここに人間の判断で「違う」と確定したキーワードを追加する
HARD_EXCLUSION_KEYWORDS = ["法人番号"]

# --- サンプル設定 ---
SAMPLE_ROWS = 500
SAMPLE_VALUES_COUNT = 5

def diagnose_id_candidates_in_file(csv_path: str) -> list:
    """
    単一ファイル内のID候補を、除外ルールを適用して診断する。
    """
    try:
        header = pd.read_csv(csv_path, nrows=0, dtype=str).columns.tolist()
        
        # --- ここが改良点 ---
        # 1. まずキーワードにマッチする候補をリストアップ
        pre_candidates = [col for col in header if any(kw in col for kw in ID_KEYWORDS)]
        
        # 2. 次に、絶対除外キーワードを含むものをフィルタリングで除去
        candidate_names = [
            col for col in pre_candidates 
            if not any(ex_kw in col for ex_kw in HARD_EXCLUSION_KEYWORDS)
        ]
        
        if not candidate_names:
            return []

        # 候補列のデータだけをサンプルとして読み込む
        df_sample = pd.read_csv(csv_path, usecols=candidate_names, nrows=SAMPLE_ROWS, dtype=str)
        
        report_list = []
        for col_name in candidate_names:
            series = df_sample[col_name].dropna()
            
            if series.empty:
                uniqueness = 0.0
                sample_values = []
                non_empty_count = 0
            else:
                uniqueness = series.nunique() / len(series)
                sample_values = series.unique()[:SAMPLE_VALUES_COUNT].tolist()
                non_empty_count = len(series)
            
            report_list.append({
                "column_name": col_name,
                "uniqueness_rate": round(uniqueness, 4),
                "non_empty_count (in sample)": non_empty_count,
                "sample_values": sample_values
            })
            
        report_list.sort(key=lambda x: x["uniqueness_rate"], reverse=True)
        
        return report_list

    except Exception as e:
        tqdm.write(f"エラー: ファイル処理中に失敗 {os.path.basename(csv_path)}: {e}")
        return []

def main():
    print("--- 事業ID候補の診断レポート(フィルタリング版)作成を開始 ---")
    print(f"NOTE: {HARD_EXCLUSION_KEYWORDS} を含む列名は候補から除外されます。")
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_input_dir = os.path.join(project_root, 'data', 'csv')
    analysis_dir = os.path.join(project_root, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)
    output_path = os.path.join(analysis_dir, 'id_candidates_diagnostics_filtered.csv')

    all_diagnostics = []
    csv_files = glob.glob(os.path.join(csv_input_dir, 'database*.csv'))
    
    for csv_path in tqdm(csv_files, desc="Diagnosing ID candidates (filtered)"):
        filename = os.path.basename(csv_path)
        file_diagnostics = diagnose_id_candidates_in_file(csv_path)
        
        for report in file_diagnostics:
            report['filename'] = filename
            all_diagnostics.append(report)
    
    if not all_diagnostics:
        print("診断対象が見つかりませんでした。")
        return
        
    df = pd.DataFrame(all_diagnostics)
    df['sample_values_str'] = df['sample_values'].apply(lambda x: ' | '.join(map(str, x)))
    df = df.drop(columns=['sample_values'])
    df = df[['filename', 'column_name', 'uniqueness_rate', 'non_empty_count (in sample)', 'sample_values_str']]
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"\nフィルタリングされたID候補の診断レポート(CSV)が出力されました: {output_path}")

if __name__ == "__main__":
    main()