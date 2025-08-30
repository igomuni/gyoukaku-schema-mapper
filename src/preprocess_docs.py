# src/preprocess_docs.py
import os, json, argparse # ★★★ argparseをインポート ★★★
from tqdm import tqdm
from sudachipy import tokenizer, dictionary

# ... (tokenize_large_text関数は変更なし) ...
def tokenize_large_text(tokenizer_obj, text, mode):
    text_bytes = text.encode('utf-8'); tokens, start = [], 0
    while start < len(text_bytes):
        end = start + 40000; chunk_str = text_bytes[start:end].decode('utf-8', errors='ignore')
        tokens.extend([m.surface() for m in tokenizer_obj.tokenize(chunk_str, mode)])
        start += len(chunk_str.encode('utf-8'))
    return tokens

def main(docs_filepath, output_filepath):
    print(f"--- SudachiPyによる前処理を開始 ---")
    print(f"入力: {docs_filepath}")
    print(f"出力: {output_filepath}")
    # ... (以降の処理は変更なし) ...
    # (ファイルが存在したら中断するロジックもそのまま)
    if os.path.exists(output_filepath): print("-> 出力ファイルが既に存在するため中断。"); return
    tokenizer_obj = dictionary.Dictionary().create(); mode = tokenizer.Tokenizer.SplitMode.C
    with open(docs_filepath, 'r', encoding='utf-8') as f_in, open(output_filepath, 'w', encoding='utf-8') as f_out:
        for line in tqdm(f_in, desc="Preprocessing"):
            original_doc = json.loads(line); tokens = tokenize_large_text(tokenizer_obj, original_doc['contents'], mode)
            preprocessed_doc = { "id": original_doc['id'], "contents": ' '.join(tokens) }
            f_out.write(json.dumps(preprocessed_doc, ensure_ascii=False) + '\n')
    print("-> 前処理完了。")

if __name__ == "__main__":
    # ★★★ コマンドライン引数を解釈する部分を追加 ★★★
    parser = argparse.ArgumentParser(description="SudachiPyでドキュメントを前処理する")
    parser.add_argument("--input", default="analysis/search_documents.jsonl", help="入力JSONLファイルパス")
    parser.add_argument("--output", default="analysis/preprocessed_for_pyserini.jsonl", help="出力JSONLファイルパス")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(project_root, args.input)
    output_path = os.path.join(project_root, args.output)
    
    main(input_path, output_path)