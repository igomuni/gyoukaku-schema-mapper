import streamlit as st
import duckdb
import os

st.set_page_config(page_title="ヘッダー分析アプリ", layout="wide")

# ★★★ パス更新 ★★★
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILEPATH = os.path.join(PROJECT_ROOT, 'data', 'header_matrix.duckdb')

st.title("📊 行政事業レビューシート ヘッダー分析アプリ")
st.write("`header_matrix.duckdb` データベースに対して、直接SQLクエリを実行できます。")

if not os.path.exists(DB_FILEPATH):
    st.error(f"データベースファイルが見つかりません: {DB_FILEPATH}\n`python src/build_db.py` を実行してDBを構築してください。")
else:
    with st.sidebar:
        st.header("データベース情報")
        try:
            con = duckdb.connect(database=DB_FILEPATH, read_only=True)
            st.success("データベースに接続しました。")
            table_info = con.execute("DESCRIBE header_matrix;").fetchdf()
            st.write("`header_matrix` テーブルの構造:")
            st.dataframe(table_info, use_container_width=True)
            con.close()
        except Exception as e:
            st.error(f"DB情報取得エラー: {e}")

    st.header("SQL実行")
    sample_query = """-- 各列名がいくつのファイルに登場するかを集計
SELECT
    column_name,
    SUM(value::INTEGER) AS appearance_count
FROM (
    UNPIVOT header_matrix
    ON * EXCLUDE (column_name)
    INTO
        NAME filename
        VALUE value
)
GROUP BY column_name
ORDER BY appearance_count DESC, column_name ASC;"""
    query = st.text_area("実行したいSQLクエリを入力してください", value=sample_query, height=250)

    if st.button("クエリを実行"):
        with st.spinner("クエリ実行中..."):
            try:
                con = duckdb.connect(database=DB_FILEPATH, read_only=True)
                result_df = con.execute(query).fetchdf()
                con.close()
                st.success(f"クエリが成功しました。{len(result_df)}行の結果が見つかりました。")
                st.dataframe(result_df)
            except Exception as e:
                st.error(f"SQLの実行中にエラーが発生しました:\n\n{e}")