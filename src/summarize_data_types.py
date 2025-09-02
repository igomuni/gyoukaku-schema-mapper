import os
import glob
import csv
import json
from tqdm import tqdm
from collections import defaultdict
import typing

# 定数: 列の支配的な型を判断するための閾値
DOMINANCE_THRESHOLD = 0.95

def get_value_type(value: str) -> str:
    """単一のセルの値（文字列）からデータ型を判定する。"""
    if not value or value.isspace():
        return "empty"
    if value.lower() in ('true', 'false'):
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    return "text"

def classify_column(type_counts: dict, total_rows: int) -> str:
    """列の型カウント情報から、その列の「支配的な型」を分類する。"""
    if total_rows == 0:
        return "empty_column"
    if type_counts.get("empty", 0) == total_rows:
        return "fully_empty"

    non_empty_rows = total_rows - type_counts.get("empty", 0)
    if non_empty_rows == 0:
         return "fully_empty" # 理論上は上のifでキャッチされるはず

    if type_counts.get("empty", 0) / total_rows >= DOMINANCE_THRESHOLD:
        return "mostly_empty"
    if type_counts.get("int", 0) / non_empty_rows >= DOMINANCE_THRESHOLD:
        return "mostly_int"
    if type_counts.get("float", 0) / non_empty_rows >= DOMINANCE_THRESHOLD:
        return "mostly_float"
    if type_counts.get("bool", 0) / non_empty_rows >= DOMINANCE_THRESHOLD:
        return "mostly_bool"
    if type_counts.get("text", 0) / non_empty_rows >= DOMINANCE_THRESHOLD:
        return "mostly_text"
    return "mixed"

def analyze_column_properties(csv_path: str) -> typing.Optional[dict]:
    """
    単一CSVをストリーミング処理し、列のプロパティを集計・分析する。
    """
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return None

            num_columns = len(header)
            # 各列の詳細な統計情報を保持するリスト
            column_details = [
                {
                    "type_counts": defaultdict(int),
                    "max_len": 0,
                    "total_len": 0,
                    "non_empty_len": 0,
                    "non_empty_count": 0,
                } for _ in range(num_columns)
            ]
            total_rows = 0

            # Pass 1: 各列の詳細なメトリクスを収集
            for row in reader:
                total_rows += 1
                for i in range(num_columns):
                    cell_value = row[i] if i < len(row) else ""
                    cell_type = get_value_type(cell_value)
                    cell_len = len(cell_value)

                    details = column_details[i]
                    details["type_counts"][cell_type] += 1
                    details["max_len"] = max(details["max_len"], cell_len)
                    details["total_len"] += cell_len
                    if cell_type != "empty":
                        details["non_empty_len"] += cell_len
                        details["non_empty_count"] += 1
            
            if total_rows == 0:
                return {
                    "filename": os.path.basename(csv_path),
                    "total_data_rows": 0,
                    "column_count": num_columns,
                    "column_property_summary": {}
                }

            # Pass 2: 収集したメトリクスをカテゴリ別に集計
            summary_agg = defaultdict(lambda: {
                "column_count": 0, "total_empty_cells": 0, "total_max_cell_len": 0,
                "total_len_sum": 0, "total_non_empty_len_sum": 0, "total_non_empty_count_sum": 0
            })

            for details in column_details:
                dominant_type = classify_column(details["type_counts"], total_rows)
                agg = summary_agg[dominant_type]
                agg["column_count"] += 1
                agg["total_empty_cells"] += details["type_counts"]["empty"]
                agg["total_max_cell_len"] = max(agg["total_max_cell_len"], details["max_len"])
                agg["total_len_sum"] += details["total_len"]
                agg["total_non_empty_len_sum"] += details["non_empty_len"]
                agg["total_non_empty_count_sum"] += details["non_empty_count"]

            # Pass 3: 集計結果から最終的なサマリーを計算
            final_summary = {}
            for dtype, agg in summary_agg.items():
                count = agg["column_count"]
                total_cells = count * total_rows
                
                final_summary[dtype] = {
                    "column_count": count,
                    "avg_empty_rate": round(agg["total_empty_cells"] / total_cells, 3) if total_cells > 0 else 0,
                    "overall_max_cell_len": agg["total_max_cell_len"],
                    "avg_cell_len": round(agg["total_len_sum"] / total_cells, 2) if total_cells > 0 else 0,
                    "avg_non_empty_cell_len": round(agg["total_non_empty_len_sum"] / agg["total_non_empty_count_sum"], 2) if agg["total_non_empty_count_sum"] > 0 else 0,
                }

            return {
                "filename": os.path.basename(csv_path),
                "total_data_rows": total_rows,
                "column_count": num_columns,
                "column_property_summary": final_summary
            }
    except Exception as e:
        print(f"\nファイル処理中にエラーが発生しました {os.path.basename(csv_path)}: {e}")
        return None

def main(csv_dir: str, output_filepath: str):
    """メインの実行関数"""
    print(f"--- '{csv_dir}' 内のCSV列プロパティ分析を開始 ---")
    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    if not csv_files:
        print("分析対象のCSVファイルが見つかりません。")
        return

    all_analyses = []
    for csv_path in tqdm(csv_files, desc="Analyzing column properties"):
        analysis = analyze_column_properties(csv_path)
        if analysis:
            all_analyses.append(analysis)

    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(all_analyses, f, ensure_ascii=False, indent=2)

    print(f"\n分析結果が出力されました: {output_filepath}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_input_dir = os.path.join(project_root, 'data', 'csv')
    analysis_dir = os.path.join(project_root, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)
    summary_output_path = os.path.join(analysis_dir, 'column_property_summary.json')
    
    main(csv_input_dir, summary_output_path)
    
    print("\n★★★ 列プロパティ分析が完了しました ★★★")