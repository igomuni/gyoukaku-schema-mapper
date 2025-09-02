import os
import glob
import pandas as pd
from tqdm import tqdm
import re
from collections import defaultdict
import json # <<<--- JSONをインポート

# (正規表現や定数の定義は変更なし)
EXPENDITURE_PATTERN = re.compile(r'支出先上位.*?リスト-([A-Z\d]+)\..*?-(\d+)-(.+)')
ATTRIBUTE_MAP = {
    "支出額（百万円）": "expenditure_amount_jpy_million",
    "支出先": "supplier_name",
    "法人番号": "supplier_corporate_id",
    "業務概要": "contract_summary"
}

# <<<--- process_csv_separation関数を修正 ---
def process_csv_separation(csv_path: str, output_dir: str, id_map: dict): # id_mapを引数に追加
    filename = os.path.basename(csv_path)
    
    # マップから事業ID列名を取得
    project_id_col = id_map.get(filename)
    if not project_id_col:
        tqdm.write(f"警告: IDマップに '{filename}' の事業ID列が定義されていません。スキップします。")
        return

    # (以降の処理はほぼ同じだが、ID特定ロジックは不要になる)
    # ... (前回のスクリプトの main_output_path, exp_output_path, chunk_iter, is_first_chunk, ファイル削除部分などをそのまま流用)
    main_output_path = os.path.join(output_dir, filename.replace('.csv', '_main.csv'))
    exp_output_path = os.path.join(output_dir, filename.replace('.csv', '_expenditures.csv'))
    
    try:
        chunk_iter = pd.read_csv(csv_path, chunksize=100, low_memory=False, dtype=str)
    except Exception as e:
        tqdm.write(f"エラー: ファイルの読み込みに失敗しました {filename}: {e}")
        return
        
    is_first_chunk = True
    if os.path.exists(main_output_path): os.remove(main_output_path)
    if os.path.exists(exp_output_path): os.remove(exp_output_path)
        
    for chunk in tqdm(chunk_iter, desc=f"Processing {filename}", unit=" chunks", leave=False):
        if project_id_col not in chunk.columns:
            tqdm.write(f"エラー: '{filename}' 内に指定されたID列 '{project_id_col}' が見つかりません。")
            return # チャンク内にID列がなければ処理を中断
            
        # (支出データの抽出と分離ロジックは前回と同じ)
        expenditure_columns = [col for col in chunk.columns if EXPENDITURE_PATTERN.match(col)]
        expenditures_data = []
        for index, row in chunk.iterrows():
            project_id = row[project_id_col]
            if pd.isna(project_id) or str(project_id).strip() == "": continue
            parsed_items = defaultdict(dict)
            for col in expenditure_columns:
                match = EXPENDITURE_PATTERN.match(col)
                if match:
                    item_index, attribute_raw = match.group(2), match.group(3)
                    if attribute_raw in ATTRIBUTE_MAP:
                        new_attribute_name = ATTRIBUTE_MAP[attribute_raw]
                        value = row[col]
                        if pd.notna(value) and str(value).strip():
                            parsed_items[item_index][new_attribute_name] = value
            for item_index, attributes in parsed_items.items():
                if attributes:
                    exp_record = {"project_id": project_id, "expenditure_index": int(item_index), **attributes}
                    expenditures_data.append(exp_record)
        if expenditures_data:
            exp_df = pd.DataFrame(expenditures_data)
            exp_df.to_csv(exp_output_path, mode='a', header=is_first_chunk, index=False, encoding='utf-8-sig')
        main_df = chunk.drop(columns=expenditure_columns, errors='ignore')
        main_df.to_csv(main_output_path, mode='a', header=is_first_chunk, index=False, encoding='utf-8-sig')
        is_first_chunk = False

# <<<--- main関数を修正 ---
def main():
    print("--- 事業データと支出先データの分離ETL処理を開始 ---")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_input_dir = os.path.join(project_root, 'data', 'csv')
    separated_dir = os.path.join(project_root, 'data', 'separated')
    analysis_dir = os.path.join(project_root, 'analysis')
    os.makedirs(separated_dir, exist_ok=True)
    
    # 事前に生成したIDマップを読み込む
    id_map_path = os.path.join(analysis_dir, 'project_id_map.json')
    if not os.path.exists(id_map_path):
        print(f"エラー: 事業IDの対応表 '{id_map_path}' が見つかりません。")
        print("先に 'map_project_id_columns.py' を実行してください。")
        return
    with open(id_map_path, 'r', encoding='utf-8') as f:
        id_map = json.load(f)
    
    csv_files = glob.glob(os.path.join(csv_input_dir, '*.csv'))
    for csv_path in tqdm(csv_files, desc="All Files"):
        process_csv_separation(csv_path, separated_dir, id_map)

if __name__ == "__main__":
    main()
    print("\n★★★ データ分離処理が完了しました ★★★")