import os
import duckdb

def build_database_from_csv(matrix_filepath, db_filepath):
    """
    ヘッダー比較マトリクスCSVからDuckDBデータベースファイルを構築する。
    """
    print("--- DuckDBデータベースの構築を開始します ---")
    if not os.path.exists(matrix_filepath):
        print(f"[エラー] 入力ファイルが見つかりません: {matrix_filepath}")
        return
    try:
        con = duckdb.connect(database=db_filepath, read_only=False)
        print(f"データベースに接続しました: {db_filepath}")
        
        table_name = "header_matrix"
        sql_create_table = f"""
            CREATE OR REPLACE TABLE {table_name} AS
            SELECT * FROM read_csv_auto('{matrix_filepath.replace(os.sep, '/')}');
        """
        print(f"テーブル '{table_name}' をCSVから作成しています...")
        con.execute(sql_create_table)
        
        print("\n--- テーブル情報 ---")
        
        # ★★★ 修正点 ★★★
        # .print() は使わず、結果をDataFrameとして取得(fetchdf)してからprintする
        table_info_df = con.execute(f"DESCRIBE {table_name};").fetchdf()
        print(table_info_df)
        
        print("\n★★★ データベースの構築が完了しました ★★★")

    except Exception as e:
        print(f"[エラー] 処理中に問題が発生しました: {e}")
    finally:
        # 接続オブジェクトが存在すれば、最後に必ず閉じる
        if 'con' in locals() and con:
            con.close()

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    analysis_dir = os.path.join(project_root, 'analysis')
    data_dir = os.path.join(project_root, 'data')
    
    matrix_input_path = os.path.join(analysis_dir, 'header_comparison_matrix.csv')
    db_output_path = os.path.join(data_dir, 'header_matrix.duckdb')
    
    build_database_from_csv(matrix_input_path, db_output_path)