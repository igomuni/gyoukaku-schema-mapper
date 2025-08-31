# RAGインデックス構築パイプライン手順書

このドキュメントは、ETLパイプラインによって生成された`clean_long_data`テーブルを元に、BM25（キーワード検索）とFaiss（ベクトル検索）の2種類の検索インデックスを構築するための手順を詳述します。

## パイプラインの全体像

1.  **検索ドキュメントの作成**: `clean_long_data`テーブルから、事業ごとの自然言語ドキュメント（コーパス）を`search_documents.jsonl`として生成します。
2.  **BM25向け前処理**:
    1.  まず、コーパス全体を`SudachiPy`で形態素解析（分かち書き）します。
    2.  次に、分かち書き済みのコーパスの中に存在する、Pyserini/Anseriniの制約を超える巨大なドキュメントを、小さなチャンクに分割します。
3.  **BM25インデックス構築**: チャンク化された、前処理済みのコーパスを元に、`Pyserini`を使ってBM25インデックスを構築します。
4.  **Faissインデックス構築**: 元の（チャンク化されていない）コーパスを`SentenceTransformer`でベクトル化し、`Faiss`を使ってベクトルインデックスを構築します。

## 実行手順

以下のコマンドを、プロジェクトのルートディレクトリで、`conda`の`gyoukaku`環境を有効化した状態で実行してください。

### 1. 検索ドキュメントの作成 (RAG Step 1)

**スクリプト:** `src/build_search_docs.py`
**入力:** `data/header_matrix.duckdb`
**出力:** `analysis/search_documents.jsonl`

```bash
python src/build_search_docs.py
```

### 2. BM25インデックス構築 (RAG Step 2a & 2b)

#### ステップ 2a: 前処理 (形態素解析とチャンク化)

このステップは2段階の処理からなります。

**1. 形態素解析**
**スクリプト:** `src/preprocess_docs.py`
**入力:** `analysis/search_documents.jsonl`
**出力:** `analysis/preprocessed_for_pyserini.jsonl`

```bash
# まず、SudachiPyでコーパス全体を分かち書きします (時間がかかります)
python src/preprocess_docs.py
```

**2. 巨大ドキュメントのチャンク化**
**スクリプト:** `src/chunk_preprocessed_docs.py`
**入力:** `analysis/preprocessed_for_pyserini.jsonl`
**出力:** `analysis/preprocessed_chunked.jsonl`

```bash
# 次に、分かち書き済みの巨大ドキュメントを安全なサイズのチャンクに分割します
python src/chunk_preprocessed_docs.py
```

#### ステップ 2b: BM25インデックスの構築

**入力:** `analysis/preprocessed_chunked.jsonl` (チャンク化されたコーパス)
**出力:** `analysis/pyserini_index/`

このステップは、ターミナルから直接コマンドを実行するのが最も確実です。

1.  **一時フォルダとコーパスの準備**:
    ```powershell
    # 一時フォルダを作成
    mkdir -Force .\analysis\pyserini_corpus_temp
    # チャンク化された前処理済みファイルをコピー
    cp .\analysis\preprocessed_chunked.jsonl .\analysis\pyserini_corpus_temp\
    ```

2.  **Pyseriniコマンドの実行**:
    ```powershell
    # JVMオプションは不要
    python -m pyserini.index.lucene `
      -collection JsonCollection `
      -input '.\analysis\pyserini_corpus_temp' `
      -index '.\analysis\pyserini_index' `
      -generator DefaultLuceneDocumentGenerator `
      -threads 8 `
      -storePositions -storeDocvectors -storeRaw `
      -pretokenized
    ```

3.  **クリーンアップ (成功後)**:
    ```powershell
    rm -Recurse -Force .\analysis\pyserini_corpus_temp
    ```

### 3. Faissインデックス構築 (RAG Step 2c)

**スクリプト:** `src/build_faiss_index.py`
**入力:** `analysis/search_documents.jsonl` (元の、チャンク化されていないコーパス)
**出力:** `analysis/faiss_index.bin` および `analysis/faiss_id_mapping.json`

```bash
python src/build_faiss_index.py
```

この手順により、RAGアプリケーションに必要な全ての検索インデックスが構築されます。