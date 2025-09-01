import os
import glob
import csv
import json
from tqdm import tqdm

# ★★★ 最終版のバケツ定義 ★★★
LENGTH_BINS = [0, 1, 10, 50, 100, 250, 500, 1000, 5000] 

def analyze_file_distribution(csv_path):
    """単一のCSVファイルをストリーミング処理し、分布を分析する"""
    header_lengths = []
    cell_lengths = []
    max_cell_len = 0
    total_cell_count = 0
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return None
        header_lengths = [len(h) for h in header]
        
        # データ行の分析
        for row in reader:
            # 各セルの長さをリストに追加
            row_lengths = [len(cell) for cell in row]
            cell_lengths.extend(row_lengths)
            
            # メモリを節約するため、チャンクごとに最大値を更新
            current_max = max(row_lengths) if row_lengths else 0
            if current_max > max_cell_len:
                max_cell_len = current_max
            total_cell_count += len(row)

    def calculate_bins(lengths):
        """
        与えられた長さのリストを、LENGTH_BINSに基づいて集計する。
        """
        last_bin_threshold = LENGTH_BINS[-1]
        last_bin_key = f"{last_bin_threshold}+"
        
        # バケツを0で初期化
        bins = {b: 0 for b in LENGTH_BINS}
        bins[last_bin_key] = 0

        for length in lengths:
            if length > last_bin_threshold:
                bins[last_bin_key] += 1
                continue

            # 該当する最小の上限バケツを見つけてカウント
            binned = False
            for b in LENGTH_BINS:
                if length <= b:
                    bins[b] += 1
                    binned = True
                    break
            
            # このロジックではLENGTH_BINSに0が含まれていれば、
            # length=0はbins[0]に正しくカウントされる
        
        # 最終的な出力形式を整える (0件のバケツは出力しない)
        final_bins = {str(k): v for k, v in bins.items() if v > 0}
        
        return final_bins

    header_dist = calculate_bins(header_lengths)
    cell_dist = calculate_bins(cell_lengths)

    # このファイルに関する全てのメトリクスを返す
    return {
        "filename": os.path.basename(csv_path),
        "column_count": len(header),
        "cell_count": total_cell_count,
        "max_header_len": max(header_lengths) if header_lengths else 0,
        "avg_header_len": round(sum(header_lengths) / len(header_lengths), 1) if header_lengths else 0,
        "max_cell_len": max_cell_len,
        "avg_cell_len": round(sum(cell_lengths) / total_cell_count, 1) if total_cell_count > 0 else 0,
        "header_len_distribution": header_dist,
        "cell_len_distribution": cell_dist
    }

def main(csv_dir, output_filepath):
    """メインの実行関数"""
    print(f"--- '{csv_dir}' 内のCSVデータ分布分析を開始 ---")
    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    if not csv_files:
        print("分析対象のCSVファイルが見つかりません。")
        return

    all_results = []
    for csv_path in tqdm(csv_files, desc="Analyzing distributions"):
        result = analyze_file_distribution(csv_path)
        if result:
            all_results.append(result)

    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    if all_results:
        max_cell_len_overall = max(r['max_cell_len'] for r in all_results)
        max_header_len_overall = max(r['max_header_len'] for r in all_results)
        print("\n--- サマリー ---")
        print(f"全ファイル中の最大セル長: {max_cell_len_overall:,} 文字")
        print(f"全ファイル中の最大ヘッダー長: {max_header_len_overall:,} 文字")
    
    print(f"分析結果が出力されました: {output_filepath}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_input_dir = os.path.join(project_root, 'data', 'csv')
    analysis_dir = os.path.join(project_root, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)
    dist_output_path = os.path.join(analysis_dir, 'data_distribution_summary.json')
    main(csv_input_dir, dist_output_path)
    print("\n★★★ 分布分析が完了しました ★★★")