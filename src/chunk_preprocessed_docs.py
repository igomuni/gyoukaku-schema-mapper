import os
import json
from tqdm import tqdm

# Anserini/Jacksonのデフォルト上限(20MB)より安全な値を設定
MAX_CONTENTS_BYTES = 10 * 1024 * 1024  # 10MB

def chunk_preprocessed_documents(input_filepath, output_filepath):
    print("--- 前処理済み巨大ドキュメントの分割処理を開始 ---")
    
    if not os.path.exists(input_filepath):
        print(f"[エラー] 入力ファイルが見つかりません: {input_filepath}")
        return

    total_lines = sum(1 for _ in open(input_filepath, 'r', encoding='utf-8'))
    
    with open(input_filepath, 'r', encoding='utf-8') as f_in, \
         open(output_filepath, 'w', encoding='utf-8') as f_out:
        
        for line in tqdm(f_in, total=total_lines, desc="Chunking Preprocessed Docs"):
            doc = json.loads(line)
            doc_id = doc["id"]
            contents = doc["contents"] # これは既にスペース区切りの単語列
            
            contents_bytes = contents.encode('utf-8')
            
            # コンテンツが上限を超えていなければ、そのまま書き出す
            if len(contents_bytes) <= MAX_CONTENTS_BYTES:
                f_out.write(json.dumps(doc, ensure_ascii=False) + '\n')
                continue
            
            # 上限を超えている場合は、チャンクに分割
            tqdm.write(f"\n[情報] 巨大ドキュメントを分割中: ID={doc_id}, Size={len(contents_bytes):,} bytes")
            chunk_num = 0
            start = 0
            while start < len(contents_bytes):
                end = start + MAX_CONTENTS_BYTES
                chunk_str = contents_bytes[start:end].decode('utf-8', errors='ignore')
                
                # チャンクの切れ目が単語の途中にならないように、最後のスペースで区切る
                # (もしチャンクの末尾にスペースがあれば、そのままでOK)
                if end < len(contents_bytes) and ' ' in chunk_str:
                    last_space_index = chunk_str.rfind(' ')
                    if last_space_index != -1:
                        chunk_str = chunk_str[:last_space_index]
                
                chunk_doc = {
                    "id": f"{doc_id}_chunk_{chunk_num}",
                    "contents": chunk_str.strip()
                }
                f_out.write(json.dumps(chunk_doc, ensure_ascii=False) + '\n')
                
                # 次のチャンクの開始位置を、実際に処理したバイト数で更新
                start += len(chunk_str.encode('utf-8'))
                chunk_num += 1

    print("\n★★★ ドキュメントの分割が完了しました ★★★")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analysis_dir = os.path.join(project_root, 'analysis')
    
    # ★★★ 入力と出力を明確化 ★★★
    preprocessed_input_path = os.path.join(analysis_dir, 'preprocessed_for_pyserini.jsonl')
    chunked_output_path = os.path.join(analysis_dir, 'preprocessed_chunked.jsonl')
    
    chunk_preprocessed_documents(preprocessed_input_path, chunked_output_path)
    print(f"\n成果物が作成されました: {chunked_output_path}")