import streamlit as st
import os
import sys
# 親ディレクトリをPythonのパスに追加して、srcモジュールをインポートできるようにする
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.retriever import HybridRetriever
# from src.llm_handler import ask_llm # 将来的にLLM連携を別ファイルに分離

# --- ページ設定 ---
st.set_page_config(page_title="Gyoukaku RAG System", layout="wide")

# --- グローバルなリソースのキャッシュ ---
# Streamlitのキャッシュ機能を使って、重いモデルやインデックスのロードを
# アプリケーションの初回起動時のみに限定する
@st.cache_resource
def load_retriever():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analysis_dir = os.path.join(project_root, 'analysis')
    return HybridRetriever(analysis_dir)

# --- メインアプリケーション ---
st.title(" Gyoukaku RAG System")
st.write("行政事業レビューシートの内容について、自然言語で質問してください。")

# リトリーバーのロード（キャッシュが効く）
try:
    retriever = load_retriever()

    # --- ユーザー入力 ---
    user_query = st.text_input("質問を入力してください:", "随意契約の割合が高い事業について教えて")

    if st.button("検索を実行"):
        if user_query:
            with st.spinner("関連情報を検索中..."):
                # 検索の実行
                retrieved_docs = retriever.search(user_query, k=5)
            
            st.success("検索が完了しました。")

            # --- 検索結果の表示 ---
            st.subheader("検索された参考情報:")
            for i, doc_contents in enumerate(retrieved_docs, 1):
                with st.expander(f"参考情報 {i}"):
                    # ★★★ 変更点: 全文ではなく、最初の500文字だけを表示 ★★★
                    st.write(doc_contents[:500] + "...") 
                                
            # --- LLMへの連携 (この部分はまだダミー) ---
            st.subheader("AIによる回答生成:")
            with st.spinner("AIが回答を生成中です..."):
                # TODO: ここでretrieved_docsをコンテキストとしてLLMに渡し、回答を生成する
                # context = "。 ".join(retrieved_docs)
                # answer = ask_llm(user_query, context) # ask_llmは別途実装が必要
                st.info("現在、LLM連携機能は開発中です。上記の参考情報を元に回答を生成します。")
                st.write("（ここに将来、GeminiやChatGPTからの回答が表示されます）")

        else:
            st.warning("質問を入力してください。")

except Exception as e:
    st.error(f"アプリケーションの初期化中にエラーが発生しました: {e}")
    st.error("必要なインデックスファイルが `analysis` フォルダに存在するか確認してください。")