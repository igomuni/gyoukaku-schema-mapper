import os
import duckdb
import json
from tqdm import tqdm

def create_search_documents(db_filepath, output_filepath):
    """
    DuckDBのclean_long_dataテーブルから、事業ごとの検索ドキュメントを作成し、
    JSONL形式で出力する。
    """
    print("--- 検索ドキュメントの作成を開始します ---")

    if not os.path.exists(db_filepath):
        print(f"[エラー] データベースファイルが見つかりません: {db_filepath}")
        return

    con = None  # 接続オブジェクトを事前に定義
    try:
        con = duckdb.connect(database=db_filepath, read_only=True)
        print(f"データベースに接続しました: {db_filepath}")

        aggregation_query = """
        SELECT
            year,
            business_id,
            string_agg(detail || ': ' || value, '。 ') AS contents
        FROM
            clean_long_data
        GROUP BY
            year, business_id;
        """

        print("SQLクエリを実行し、事業ごとに情報を集約しています...")
        results = con.execute(aggregation_query).fetchall()
        
        if not results:
            print("[警告] データベースに集約対象のデータがありませんでした。")
            return

        print(f"集約された事業（ドキュメント）数: {len(results)}件")
        print("JSONLファイルに書き込んでいます...")

        with open(output_filepath, 'w', encoding='utf-8') as f:
            for row in tqdm(results, desc="Writing Documents"):
                year, business_id, contents = row
                doc_id = f"{year}-{business_id}"
                doc = {
                    "id": doc_id,
                    "contents": contents
                }
                f.write(json.dumps(doc, ensure_ascii=False) + '\n')
        
        print("\n★★★ 検索ドキュメントの作成が完了しました ★★★")

    except Exception as e:
        print(f"[エラー] 処理中に問題が発生しました: {e}")
    finally:
        # ★★★ 修正点 ★★★
        # conオブジェクトが存在し、まだ閉じられていない場合のみ閉じる
        if con:
            con.close()

if __name__ == "__main__":
    print("★★★ RAGフェーズ ステップ2.1: 検索ドキュメントの作成 ★★★")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_input_path = os.path.join(project_root, 'data', 'header_matrix.duckdb')
    
    analysis_dir = os.path.join(project_root, 'analysis')
    os.makedirs(analysis_dir, exist_ok=True)
    docs_output_path = os.path.join(analysis_dir, 'search_documents.jsonl')
    
    create_search_documents(db_input_path, docs_output_path)
    print(f"\n成果物が作成されました: {docs_output_path}")