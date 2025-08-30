import os
import json
import random

def verify_jsonl_file(filepath, num_samples=3):
    """
    指定されたJSONLファイルの内容を検証し、サマリーとサンプルを表示する。
    """
    print(f"--- '{os.path.basename(filepath)}' の検証を開始します ---")

    if not os.path.exists(filepath):
        print(f"[エラー] ファイルが見つかりません: {filepath}")
        return

    try:
        # --- ステップ1: 総行数（ドキュメント数）をカウント ---
        print("総ドキュメント数をカウント中...")
        with open(filepath, 'r', encoding='utf-8') as f:
            total_docs = sum(1 for _ in f)
        
        print(f"\n--- 検証サマリー ---")
        print(f"総ドキュメント数: {total_docs:,} 件")

        if total_docs == 0:
            print("ファイルは空です。")
            return
            
        # --- ステップ2: サンプリング ---
        first_samples = []
        last_samples = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            # 先頭N件を取得
            for i, line in enumerate(f):
                if i >= num_samples:
                    break
                first_samples.append(json.loads(line.strip()))
            
            # 末尾N件を取得 (効率的ではないが、検証目的ならOK)
            f.seek(0)
            all_lines = f.readlines()
            if len(all_lines) > num_samples:
                last_samples = [json.loads(line.strip()) for line in all_lines[-num_samples:]]
            else:
                last_samples = [json.loads(line.strip()) for line in all_lines]

        # ランダムN件を取得 (メモリに優しい方法)
        random_samples = []
        if total_docs > num_samples:
            random_indices = set(random.sample(range(total_docs), num_samples))
            with open(filepath, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i in random_indices:
                        random_samples.append(json.loads(line.strip()))

        # --- ステップ3: 結果を表示 ---
        def print_samples(title, samples):
            print(f"\n--- {title} (上位{len(samples)}件) ---")
            for i, doc in enumerate(samples, 1):
                print(f"[{i}] ID: {doc.get('id', 'N/A')}")
                # contentsが長いので、最初の200文字だけ表示
                contents_preview = doc.get('contents', '')[:200]
                print(f"    Contents: {contents_preview}...")
        
        print_samples("先頭のサンプル", first_samples)
        print_samples("末尾のサンプル", last_samples)
        if random_samples:
            print_samples("ランダムサンプル", random_samples)

    except Exception as e:
        print(f"\n[エラー] ファイルの処理中に問題が発生しました: {e}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analysis_dir = os.path.join(project_root, 'analysis')
    jsonl_filepath = os.path.join(analysis_dir, 'search_documents.jsonl')
    
    # 表示するサンプル数を指定
    NUMBER_OF_SAMPLES_TO_SHOW = 3
    
    verify_jsonl_file(jsonl_filepath, NUMBER_OF_SAMPLES_TO_SHOW)
    print("\n★★★ 検証が完了しました ★★★")