import google.generativeai as genai
import streamlit as st

# StreamlitのSecretsからAPIキーを読み込んで設定
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except (FileNotFoundError, KeyError):
    st.error("APIキーが設定されていません。.streamlit/secrets.toml を作成してください。")
    st.stop()

def generate_answer(query, context_docs):
    """
    検索されたコンテキストを元に、Geminiを使って回答を生成する。
    """
    
    # LLMに渡すための、整形されたコンテキストを作成
    context = "\n\n---\n\n".join(context_docs)
    
    # Geminiに渡すプロンプトのテンプレート
    prompt = f"""
あなたは非常に優秀で、誠実な行政アナリストです。
以下の参考情報に厳密に基づいて、ユーザーの質問に日本語で回答してください。
参考情報に答えがない場合、または情報が不十分な場合は、「参考情報からは分かりませんでした」と正直に回答してください。
あなた自身の知識や意見を付け加えてはいけません。

---
【参考情報】
{context}
---

【ユーザーの質問】
{query}
---

【回答】
"""
    
    try:
        # 使用するモデルを定義 (gemini-1.5-flashは高速で安価)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 回答を生成
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        st.error(f"AIによる回答生成中にエラーが発生しました: {e}")
        return None