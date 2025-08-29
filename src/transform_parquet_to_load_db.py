import os
import duckdb

def transform_and_load_pipeline(parquet_dir, db_filepath):
    """
    Parquetデータレイクからデータを読み込み、変換・クレンジング処理を実行し、
    最終的な正規化済みテーブルとしてDuckDBにロードする。
    """
    print(f"\n--- データ変換＆ロードパイDプライン開始 (最終版) ---")
    
    parquet_files_path = os.path.join(parquet_dir, '*.parquet').replace(os.sep, '/')
    
    try:
        con = duckdb.connect(database=db_filepath, read_only=False)
        print(f"データベースに接続しました: {db_filepath}")

        schema_query = f"""
            SELECT column_name
            FROM (DESCRIBE SELECT * FROM read_parquet('{parquet_files_path}', union_by_name=True))
        """
        all_columns = [row[0] for row in con.execute(schema_query).fetchall()]

        biz_id_parts = []
        for i in range(1, 4):
            col_name = f"事業番号-{i}"
            if col_name in all_columns:
                biz_id_parts.append(f'"{col_name}"')
            else:
                biz_id_parts.append("''") 
        
        safe_biz_id_sql = f"COALESCE({biz_id_parts[0]}, '') || '-' || COALESCE({biz_id_parts[1]}, '') || '-' || COALESCE({biz_id_parts[2]}, '')"

        transform_sql_query = f"""
        CREATE OR REPLACE TABLE clean_long_data AS
        WITH raw_data AS (
            SELECT * FROM read_parquet('{parquet_files_path}', union_by_name=True, filename=true)
        ),
        structured_data AS (
            SELECT
                regexp_extract(filename, '([0-9]{{4}})', 1) AS year,
                {safe_biz_id_sql} AS business_id,
                original_column_name, value,
                str_split(original_column_name, '-') AS parts
            FROM raw_data
        ),
        final_structure AS (
            SELECT
                year, business_id, original_column_name, value, parts,
                parts[1] AS concept,
                CASE
                    WHEN parts[2] LIKE '%.支払先' THEN parts[2]
                    WHEN parts[2] = 'グループ' THEN parts[2]
                    ELSE NULL
                END AS block,
                CASE
                    WHEN parts[2] LIKE '%.支払先' AND regexp_matches(parts[3], '^[0-9]+$') THEN parts[3]
                    WHEN parts[2] = 'グループ' AND regexp_matches(parts[4], '^[0-9]+$') THEN parts[4]
                    ELSE NULL
                END AS item_index,
                CASE
                    WHEN parts[2] LIKE '%.支払先' AND regexp_matches(parts[3], '^[0-9]+$') THEN array_to_string(list_slice(parts, 4, len(parts)), '-')
                    WHEN parts[2] = 'グループ' AND regexp_matches(parts[4], '^[0-9]+$') THEN parts[3]
                    ELSE original_column_name
                END AS detail
            FROM structured_data
        )
        SELECT
            year, business_id, concept, block, item_index, detail, value, original_column_name
        FROM final_structure
        WHERE value IS NOT NULL AND trim(value) != '';
        """

        print("変換クエリを実行し、'clean_long_data'テーブルを構築しています...")
        con.execute(transform_sql_query)
        print("'clean_long_data'テーブルの構築が完了しました。")

        print("\n--- 構築されたテーブルの概要 ---")
        # ★★★ 修正点: .show() -> .fetchdf()とprint() ★★★
        table_info_df = con.execute("DESCRIBE clean_long_data;").fetchdf()
        print(table_info_df)
        
        row_count = con.execute("SELECT COUNT(*) FROM clean_long_data;").fetchone()[0]
        print(f"\n総行数: {row_count:,} 件")

    except Exception as e:
        print(f"[エラー] 変換処理中に問題が発生しました: {e}")
    finally:
        if 'con' in locals() and con:
            con.close()

if __name__ == "__main__":
    print("★★★ ステップ4: データ変換＆ロードパイプラインを実行します ★★★")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parquet_input_dir = os.path.join(project_root, 'data', 'parquet')
    db_output_path = os.path.join(project_root, 'data', 'header_matrix.duckdb')

    transform_and_load_pipeline(parquet_input_dir, db_output_path)
    
    print("\n★★★ ETLフェーズが完了しました。分析の準備が整いました！ ★★★")