import os
import glob
import csv
import json
from tqdm import tqdm
from collections import defaultdict
import re

# --- プロファイリングルールの定義 ---

# ルール1: これらの単語が含まれていたら、それは金額データではない可能性が高い
EXCLUSION_KEYWORDS = [
    "評価", "説明", "理由", "概要", "有無", "法人番号", "契約方式", 
    "落札率", "入札者数", "応募者数", "チェック欄", "部局"
]

# ルール2: これらのキーワードに完全一致するものを最優先で探す
INCLUSION_KEYWORDS_PRIORITY = {
    "expenditure_final": ["支出済額", "執行額"],
    "expenditure_itemized": ["支出額"] # 「支出額」は項目別で多用されるため別カテゴリ
}

# ルール3: 質問文のパターン (正規表現)
QUESTION_PATTERN = re.compile(r'か。?$')

def profile_and_rank_headers(csv_dir: str) -> dict:
    """
    プロファイリングルールに基づき、全CSVのヘッダーを分析・ランク付けする。
    """
    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    if not csv_files: return {}

    # { header_name: { "score": float, "found_in_files": set() } }
    header_profiles = defaultdict(lambda: {"score": 0.0, "found_in_files": set()})

    for csv_path in tqdm(csv_files, desc="Profiling all headers"):
        filename = os.path.basename(csv_path)
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header: continue

                for col_name in header:
                    # 初期スコア
                    score = 0.0
                    is_candidate = False

                    # --- Inclusionルール (加点) ---
                    # 最優先キーワードにマッチすれば高得点
                    for keywords in INCLUSION_KEYWORDS_PRIORITY.values():
                        for keyword in keywords:
                            if keyword in col_name:
                                score += 2.0
                                is_candidate = True
                                break
                    
                    # スコアが低くても「支出」が含まれていれば最低点を与える
                    if "支出" in col_name and not is_candidate:
                        score += 0.1
                        is_candidate = True

                    # 候補でなければここで処理終了
                    if not is_candidate:
                        continue
                    
                    # --- Exclusionルール (減点) ---
                    # 除外キーワードが含まれていたら大幅減点
                    for keyword in EXCLUSION_KEYWORDS:
                        if keyword in col_name:
                            score -= 1.5
                    
                    # 質問文形式なら減点
                    if QUESTION_PATTERN.search(col_name):
                        score -= 1.5

                    # --- 構造ルール (加点) ---
                    # キーワードが列名の末尾部分にあると、より重要度が高い
                    parts = col_name.split('-')
                    if len(parts) > 1:
                        last_part = parts[-1]
                        if "支出額" in last_part or "支出済額" in last_part or "執行額" in last_part:
                            score += 0.5
                    
                    # 最終スコアを更新
                    header_profiles[col_name]["score"] += score
                    header_profiles[col_name]["found_in_files"].add(filename)

        except Exception as e:
            print(f"\nファイル処理中にエラーが発生しました {filename}: {e}")
    
    # スコアが0より大きいものだけをフィルタリングし、ランキング付け
    ranked_results = []
    for name, profile in header_profiles.items():
        if profile["score"] > 0:
            ranked_results.append({
                "header_name": name,
                "score": round(profile["score"], 2),
                "found_in_files_count": len(profile["found_in_files"]),
            })
    
    # スコアの高い順にソート
    ranked_results.sort(key=lambda x: x["score"], reverse=True)
    
    return {"ranked_candidates": ranked_results}

def main():
    print("--- 高度なプロファイリングによるヘッダー候補の探索を開始 ---")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_input_dir = os.path.join(project_root, 'data', 'csv')
    analysis_dir = os.path.join(project_root, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)
    output_path = os.path.join(analysis_dir, 'header_profiling_results.json')
    
    results = profile_and_rank_headers(csv_input_dir)
    
    if not results.get("ranked_candidates"):
        print("有効な候補が見つかりませんでした。")
        return

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nプロファイリング結果が出力されました: {output_path}")
    print("上位の候補をレビューし、最終的なキーワードを決定してください。")

    # 上位20件をコンソールに表示
    print("\n--- 上位20候補 ---")
    for item in results["ranked_candidates"][:20]:
        print(f"Score: {item['score']:.2f}, Header: {item['header_name']}")

if __name__ == "__main__":
    main()