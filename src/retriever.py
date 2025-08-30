import os
import json
import faiss
import numpy as np
from pyserini.search.lucene import LuceneSearcher
from sentence_transformers import SentenceTransformer
from sudachipy import tokenizer, dictionary

class HybridRetriever:
    def __init__(self, analysis_dir, pyserini_index_name="pyserini_index_75"):
        print("ハイブリッド検索システムを初期化中...")
        
        pyserini_index_path = os.path.join(analysis_dir, pyserini_index_name)
        faiss_index_path = os.path.join(analysis_dir, "faiss_index.bin")
        id_mapping_path = os.path.join(analysis_dir, "faiss_id_mapping.json")
        docs_path = os.path.join(analysis_dir, "search_documents.jsonl")

        print(f" -> Pyseriniインデックス '{pyserini_index_name}' をロード中...")
        if not os.path.exists(pyserini_index_path):
            raise FileNotFoundError(f"Pyseriniインデックスが見つかりません: {pyserini_index_path}")
        self.searcher = LuceneSearcher(pyserini_index_path)
        
        print(" -> Faissインデックスをロード中...")
        if not os.path.exists(faiss_index_path):
            raise FileNotFoundError(f"Faissインデックスが見つかりません: {faiss_index_path}")
        self.faiss_index = faiss.read_index(faiss_index_path)
        
        print(" -> SentenceTransformerモデルをロード中...")
        self.st_model = SentenceTransformer('sonoisa/sentence-luke-japanese-base-lite')
        
        print(" -> ドキュメントストアとIDマッピングをロード中...")
        with open(id_mapping_path, 'r', encoding='utf-8') as f:
            self.faiss_id_mapping = json.load(f)
        
        self.doc_store = {}
        with open(docs_path, 'r', encoding='utf-8') as f:
            for line in f:
                doc = json.loads(line)
                self.doc_store[doc['id']] = doc['contents']

        print(" -> SudachiPyトークナイザーを初期化中...")
        self.tokenizer_obj = dictionary.Dictionary().create()
        self.tokenizer_mode = tokenizer.Tokenizer.SplitMode.C
        
        print("--- 初期化が完了しました ---")

    # ★★★ 修正点: このメソッド全体を1レベルインデントする ★★★
    def search(self, query, k=5):
        print(f"\nクエリ「{query}」でハイブリッド検索を実行...")

        # --- a. キーワード検索 (BM25) ---
        tokenized_query = ' '.join([m.surface() for m in self.tokenizer_obj.tokenize(query, self.tokenizer_mode)])
        bm25_hits = self.searcher.search(tokenized_query, k=k)
        
        bm25_results = []
        for hit in bm25_hits:
            bm25_results.append({
                "id": hit.docid,
                "score": hit.score,
                "contents": self.doc_store.get(hit.docid, "")
            })
        print(f" -> BM25検索結果: {[res['id'] for res in bm25_results]}")

        # --- b. ベクトル検索 (Faiss) ---
        query_embedding = self.st_model.encode([query], show_progress_bar=False)
        distances, indices = self.faiss_index.search(query_embedding.astype('float32'), k)
        
        faiss_results = []
        for i, dist in zip(indices[0], distances[0]):
            if i != -1:
                doc_id = self.faiss_id_mapping[i]
                faiss_results.append({
                    "id": doc_id,
                    "score": float(dist),
                    "contents": self.doc_store.get(doc_id, "")
                })
        print(f" -> Faiss検索結果: {[res['id'] for res in faiss_results]}")

        # --- c. 結果の統合 ---
        final_results = {}
        for res in bm25_results + faiss_results:
            if res['id'] not in final_results:
                final_results[res['id']] = res['contents']
        
        print(f" -> 統合後のユニークなドキュメント数: {len(final_results)}件")
        return list(final_results.values())