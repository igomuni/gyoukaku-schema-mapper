import os
import glob
import pandas as pd
import json
from tqdm import tqdm

# --- 事業ID特定のヒューリスティック定義 (v5) ---
ID_KEYWORDS = ["事業番号", "整理番号", "番号", "ID"]
CONTEXT_BONUS_KEYWORDS = ["事業"]
CONTEXT_EXCLUSION_KEYWORDS = ["関連", "過去", "点検", "改善", "レビューシート", "法人", "郵便", "支出先"]
SAMPLE_ROWS = 500

def find_best_id_column_v5(csv_path: str) -> str:
    """
    v5の優先順位付きトランプカードルールに基づき、最適な事業ID列名を特定する。
    """
    try:
        header = pd.read_csv(csv_path, nrows=0, dtype=str).columns.tolist()
        
        # --- ここからが優先順位付きトランプカードロジック ---

        # 1. 最優先トランプ: "事業番号"
        if "事業番号" in header:
            df_sample = pd.read_csv(csv_path, usecols=["事業番号"], nrows=SAMPLE_ROWS, dtype=str)
            series = df_sample["事業番号"].dropna()
            if not series.empty and (series.nunique() / len(series) > 0.3):
                return "事業番号"

        # 2. 次世代トランプ: "事業番号-1"
        if "事業番号-1" in header:
            df_sample = pd.read_csv(csv_path, usecols=["事業番号-1"], nrows=SAMPLE_ROWS, dtype=str)
            series = df_sample["事業番号-1"].dropna()
            if not series.empty and (series.nunique() / len(series) > 0.3):
                return "事業番号-1"

        # --- トランプが使えなかった場合、通常のプロファイリングを開始 ---
        candidates = []
        for col_name in header:
            for keyword in ID_KEYWORDS:
                if keyword in col_name:
                    score = 100.0
                    for bonus in CONTEXT_BONUS_KEYWORDS:
                        if bonus in col_name: score += 100
                    for penalty in CONTEXT_EXCLUSION_KEYWORDS:
                        if penalty in col_name: score -= 1000
                    score -= col_name.count('-') * 50
                    score -= len(col_name)
                    
                    if score > -500:
                        candidates.append({"name": col_name, "score": score})
                    break
        
        if not candidates: return None

        # --- ユニーク率の検証 ---
        candidate_names = list(set([c["name"] for c in candidates]))
        df_sample = pd.read_csv(csv_path, usecols=candidate_names, nrows=SAMPLE_ROWS, dtype=str)

        max_final_score = -float('inf')
        best_column = None

        for cand in candidates:
            col_name = cand["name"]
            series = df_sample[col_name].dropna()
            if series.empty or (series.nunique() / len(series) < 0.3):
                continue

            final_score = cand["score"] * (series.nunique() / len(series))
            
            if final_score > max_final_score:
                max_final_score = final_score
                best_column = col_name
                
        return best_column

    except Exception as e:
        tqdm.write(f"エラー: ファイル処理中に失敗 {os.path.basename(csv_path)}: {e}")
        return None

def main():
    print("--- 各CSVファイルの事業ID列の特定とマッピングを開始 (v5) ---")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_input_dir = os.path.join(project_root, 'data', 'csv')
    analysis_dir = os.path.join(project_root, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)
    output_path = os.path.join(analysis_dir, 'project_id_map_v5.json')

    id_map = {}
    csv_files = glob.glob(os.path.join(csv_input_dir, 'database*.csv'))
    
    for csv_path in tqdm(csv_files, desc="Mapping Project ID columns (v5)"):
        filename = os.path.basename(csv_path)
        best_id_col = find_best_id_column_v5(csv_path)
        id_map[filename] = best_id_col
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(id_map, f, ensure_ascii=False, indent=2)

    print(f"\n事業IDの対応表 (v5) が出力されました: {output_path}")

if __name__ == "__main__":
    main()