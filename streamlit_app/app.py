import streamlit as st
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.retriever import HybridRetriever

st.set_page_config(page_title="Gyoukaku RAG System", layout="wide")

# ★★★ 変更点: キャッシュのキーをインデックス名にする ★★★
# これにより、インデックスを切り替えた際に、キャッシュが再実行される
@st.cache_resource
def load_retriever(pyserini_index_name):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analysis_dir = os.path.join(project_root, 'analysis')
    # ★★★ 変更点: 引数で受け取ったインデックス名を渡す ★★★
    return HybridRetriever(analysis_dir, pyserini_index_name)

st.title(" Gyoukaku RAG System")
st.write("行政事業レビューシートの内容について、自然言語で質問してください。")

# --- サイドバーに設定を追加 ---
with st.sidebar:
    st.header("設定")
    # ★★★ 変更点: インデックス選択用のラジオボタンを追加 ★★★
    index_version = st.radio(
        "使用するBM25インデックスを選択:",
        ('75件 (テスト用)', '完全版'),
        index=0 # デフォルトは'75件'
    )

# 選択に応じてインデックス名を決定
pyserini_index_folder = "pyserini_index_75" if index_version == '75件 (テスト用)' else "pyserini_index"

try:
    # 選択されたインデックス名を渡してリトリーバーをロード
    retriever = load_retriever(pyserini_index_folder)

    # --- ユーザー入力 ---
    user_query = st.text_input("質問を入力してください:", "随意契約の割合が高い事業について教えて")

    if st.button("検索を実行"):
        if user_query:
            with st.spinner("関連情報を検索中..."):
                retrieved_docs = retriever.search(user_query, k=5)
            
            st.success(f"検索が完了しました。（使用インデックス: {index_version}）")

            st.subheader("検索された参考情報:")
            for i, doc_contents in enumerate(retrieved_docs, 1):
                with st.expander(f"参考情報 {i}"):
                    st.write(doc_contents[:500] + "...")
            
            # (LLM連携部分は変更なし)

except Exception as e:
    st.error(f"アプリケーションの初期化/実行中にエラーが発生しました: {e}")