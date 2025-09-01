import streamlit as st
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.retriever import HybridRetriever
from src.llm_handler import generate_answer # ★★★ LLMハンドラーをインポート ★★★

st.set_page_config(page_title="Gyoukaku RAG System", layout="wide")

@st.cache_resource
def load_retriever(pyserini_index_name):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analysis_dir = os.path.join(project_root, 'analysis')
    return HybridRetriever(analysis_dir, pyserini_index_name)

st.title(" Gyoukaku RAG System")
st.write("行政事業レビューシートの内容について、自然言語で質問してください。")

with st.sidebar:
    st.header("設定")
    index_version = st.radio(
        "使用するBM25インデックスを選択:",
        ('75件 (テスト用)', '完全版'),
        index=1 # ★★★ デフォルトを「完全版」にしておく ★★★
    )

pyserini_index_folder = "pyserini_index_75" if index_version == '75件 (テスト用)' else "pyserini_index"

try:
    retriever = load_retriever(pyserini_index_folder)

    user_query = st.text_input("質問を入力してください:", "随意契約の割合が高い事業について教えて")

    if st.button("検索を実行"):
        if user_query:
            retrieved_docs = []
            with st.spinner("関連情報を検索中..."):
                retrieved_docs = retriever.search(user_query, k=5)
            
            st.success(f"検索が完了しました。（使用インデックス: {index_version}）")

            # --- LLMへの連携と回答表示 ---
            st.subheader("AIによる回答:")
            if retrieved_docs:
                with st.spinner("AIが回答を生成中です..."):
                    # ★★★ ここでLLMを呼び出す ★★★
                    answer = generate_answer(user_query, retrieved_docs)
                    
                    if answer:
                        st.write(answer)
                    else:
                        st.error("AIからの回答がありませんでした。")

                # --- 検索結果（根拠）の表示 ---
                st.subheader("回答の根拠となった参考情報:")
                for i, doc_contents in enumerate(retrieved_docs, 1):
                    with st.expander(f"参考情報 {i}"):
                        st.write(doc_contents[:1000] + "...") # プレビューを少し長めに
            else:
                st.warning("関連する情報が見つかりませんでした。")

except Exception as e:
    st.error(f"アプリケーションの初期化/実行中にエラーが発生しました: {e}")