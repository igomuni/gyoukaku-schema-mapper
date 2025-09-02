import os
import glob
import csv
import json
import re
from tqdm import tqdm
from collections import defaultdict
import typing

# --- 磨き込み後のターゲット定義 ---
METADATA_TARGETS = {
    "project_id": ["事業番号"],
    "project_name": ["事業名"],
    "governing_agency": ["府省名", "府省庁", "府省"],
    "year": ["年度"],
    "budget_initial": ["当初予算"],
    "budget_supplementary": ["補正予算"],
    "expenditure_final": ["執行額", "支出済額"]
}

def extract_year_from_filename(filename: str) -> typing.Optional[int]:
    """ファイル名から西暦年を抽出する"""
    match = re.search(r'(20\d{2})', filename)
    if match: return int(match.group(1))
    return None

# --- ここからが新しいスコアリングロジック ---
def calculate_score(column_name: str, target_key: str, all_targets: dict) -> float:
    """排他性を考慮したスコアを計算する"""
    # 1. 探しているターゲットのキーワードが含まれているか？
    base_score = 0.0
    for keyword in all_targets[target_key]:
        if keyword in column_name:
            base_score = 1.0
            break
    
    if base_score == 0.0:
        return 0.0 # そもそも候補ですらない

    # 2. 他のターゲットのキーワードが含まれているか？ (ペナルティ計算)
    penalty = 0.0
    for other_key, other_keywords in all_targets.items():
        if other_key == target_key:
            continue # 自分自身のカテゴリはスキップ
        for keyword in other_keywords:
            if keyword in column_name:
                penalty += 0.5
                break # 1つのカテゴリから1回だけペナルティ
    
    return base_score - penalty

def identify_key_metadata_candidates(csv_path: str) -> typing.Optional[dict]:
    """主要なメタデータ列の候補を、排他性スコアリングを用いて特定する。"""
    try:
        filename = os.path.basename(csv_path)
        file_year = extract_year_from_filename(filename)

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header: return None

            # --- Pass 1: ヘッダーから全ての列のスコアを計算 ---
            candidates = defaultdict(list)
            for i, col_name in enumerate(header):
                for target_key in METADATA_TARGETS.keys():
                    score = calculate_score(col_name, target_key, METADATA_TARGETS)
                    if score > 0: # スコアが0より大きいものだけを候補とする
                        candidates[target_key].append({"index": i, "name": col_name, "score": score})
            
            if not any(candidates.values()):
                return {"filename": filename, "identified_metadata": {"status": "No candidates found."}}

            # --- Pass 2: データ特性を収集 (候補列のみ) ---
            candidate_indices = {cand["index"] for c_list in candidates.values() for cand in c_list}
            stats = {idx: {"unique_values": set(), "non_empty_count": 0, "year_match_count": 0} for idx in candidate_indices}
            total_rows = 0
            f.seek(0); next(reader) # Reset pointer and skip header

            for row in reader:
                total_rows += 1
                for idx in candidate_indices:
                    value = row[idx] if idx < len(row) else ""
                    if value and not value.isspace():
                        stats[idx]["non_empty_count"] += 1
                        stats[idx]["unique_values"].add(value)
                        if file_year and value == str(file_year):
                            stats[idx]["year_match_count"] += 1
            
            # --- Pass 3: 最適な候補を選択 ---
            final_mapping = {}
            for target_key, cands_list in candidates.items():
                best_candidate = None
                max_final_score = -1

                for cand in cands_list:
                    idx = cand["index"]
                    stat = stats[idx]
                    non_empty_count = stat["non_empty_count"]
                    if non_empty_count == 0: continue

                    # データ特性を加味した最終スコアを計算
                    final_score = cand["score"] # 排他性スコアをベースにする
                    if target_key in ["project_id", "project_name"]:
                        uniqueness = len(stat["unique_values"]) / non_empty_count
                        final_score += uniqueness # ユニーク率をスコアに加算
                    elif target_key == "year":
                        match_rate = stat["year_match_count"] / non_empty_count if non_empty_count > 0 else 0
                        final_score += match_rate # 年の一致率をスコアに加算

                    if final_score > max_final_score:
                        max_final_score = final_score
                        best_candidate = {
                            "column_name": cand["name"],
                            "column_index": idx,
                            "exclusivity_score": cand["score"], # 排他性スコアも記録
                            "uniqueness_rate": round(len(stat["unique_values"]) / non_empty_count, 3),
                            "non_empty_rate": round(non_empty_count / total_rows, 3) if total_rows > 0 else 0
                        }

                if best_candidate:
                    final_mapping[target_key] = best_candidate

            return {"filename": filename, "identified_metadata": final_mapping}

    except Exception as e:
        print(f"\nファイル処理中にエラーが発生しました {filename}: {e}")
        return None

# (main関数は前回から変更なし)
def main(csv_dir: str, output_filepath: str):
    print(f"--- '{csv_dir}' 内のCSVから主要メタデータの特定を開始 (改良版) ---")
    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    if not csv_files:
        print("分析対象のCSVファイルが見つかりません。")
        return

    all_results = []
    for csv_path in tqdm(csv_files, desc="Identifying key metadata (advanced)"):
        result = identify_key_metadata_candidates(csv_path)
        if result:
            all_results.append(result)

    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\n特定結果が出力されました: {output_filepath}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_input_dir = os.path.join(project_root, 'data', 'csv')
    analysis_dir = os.path.join(project_root, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)
    output_path = os.path.join(analysis_dir, 'key_metadata_candidates_v2.json')
    
    main(csv_input_dir, output_path)
    
    print("\n★★★ 主要メタデータの特定が完了しました ★★★")