# src/build_pyserini_index.py
import os, subprocess, shutil, argparse # ★★★ argparseをインポート ★★★

def main(preprocessed_filepath, output_dir):
    print(f"--- Pyseriniインデックス構築を開始 ---")
    print(f"入力: {preprocessed_filepath}")
    print(f"出力: {output_dir}")
    # ... (以降の処理はほぼ変更なし) ...
    if not os.path.exists(preprocessed_filepath): print(f"[エラー] 入力ファイルが見つかりません: {preprocessed_filepath}"); return
    pyserini_input_dir = os.path.join(os.path.dirname(output_dir), "pyserini_corpus_temp")
    os.makedirs(pyserini_input_dir, exist_ok=True); shutil.copy(preprocessed_filepath, pyserini_input_dir)
    try:
        env = os.environ.copy(); env["ANSERINI_JVM_ARGS"] = "-Dcom.fasterxml.jackson.core.StreamReadConstraints.maxStringLength=50000000"
        cmd = [ "python", "-m", "pyserini.index.lucene", "-collection", "JsonCollection", "-input", pyserini_input_dir,
            "-index", output_dir, "-generator", "DefaultLuceneDocumentGenerator", "-threads", "8", 
            "-storePositions", "-storeDocvectors", "-storeRaw", "-pretokenized" ]
        print(f"実行コマンド: {' '.join(cmd)}"); subprocess.run(cmd, check=True, env=env)
        print(f"-> Pyseriniインデックスが '{output_dir}' に構築されました。")
    except Exception as e: print(f"[エラー] Pyseriniインデックスの構築に失敗: {e}")
    finally:
        if os.path.exists(pyserini_input_dir): shutil.rmtree(pyserini_input_dir)

if __name__ == "__main__":
    # ★★★ コマンドライン引数を解釈する部分を追加 ★★★
    parser = argparse.ArgumentParser(description="PyseriniでBM25インデックスを構築する")
    parser.add_argument("--input", default="analysis/preprocessed_for_pyserini.jsonl", help="入力JSONLファイルパス")
    parser.add_argument("--output", default="analysis/pyserini_index", help="出力インデックスディレクトリパス")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_path = os.path.join(project_root, args.input)
    output_path = os.path.join(project_root, args.output)
    main(input_path, output_path)