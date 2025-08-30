# src/build_faiss_index.py
import os, json, faiss, numpy as np
from sentence_transformers import SentenceTransformer

ST_MODEL_NAME = 'sonoisa/sentence-luke-japanese-base-lite'

def main(docs_filepath, output_dir):
    print("--- Faiss (ベクトル) インデックスの構築を開始 ---")
    
    faiss_index_path = os.path.join(output_dir, "faiss_index.bin")
    id_mapping_path = os.path.join(output_dir, "faiss_id_mapping.json")

    if os.path.exists(faiss_index_path):
        print("-> Faissインデックスが既に存在するため、処理を中断します。")
        return
        
    print(f"'{ST_MODEL_NAME}' モデルをロード中...")
    model = SentenceTransformer(ST_MODEL_NAME)
    
    docs_for_faiss, doc_ids = [], []
    with open(docs_filepath, 'r', encoding='utf-8') as f:
        for line in f:
            doc = json.loads(line)
            docs_for_faiss.append(doc['contents'])
            doc_ids.append(doc['id'])
    
    print("ドキュメントをベクトルにエンコード中...")
    embeddings = model.encode(docs_for_faiss, show_progress_bar=True)
    
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    ids_np = np.array(range(len(doc_ids))).astype('int64')
    index_mapped = faiss.IndexIDMap(index)
    index_mapped.add_with_ids(embeddings.astype('float32'), ids_np)

    os.makedirs(output_dir, exist_ok=True)
    faiss.write_index(index_mapped, faiss_index_path)
    with open(id_mapping_path, 'w', encoding='utf-8') as f:
        json.dump(doc_ids, f)

    print(f"-> FaissインデックスとIDマッピングが構築されました。")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    analysis_dir = os.path.join(project_root, 'analysis')
    docs_input_path = os.path.join(analysis_dir, 'search_documents.jsonl')
    main(docs_input_path, analysis_dir) # 出力先はanalysisフォルダ