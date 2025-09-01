# Gyoukaku Schema Mapper

## 概要

このプロジェクトは、行政事業レビューシートのデータベースからダウンロードされる、巨大かつ複数年度にわたって列構成（スキーマ）が変動するExcelファイルを分析するための基盤を構築するものです。

手動での開封が困難な巨大Excelを安全にCSVへ変換し、年度ごとに異なる混沌としたヘッダー（列名）の構造を解明・可視化（マッピング）します。最終的には、ETLパイプラインを通じてクリーンなデータを生成し、RAG（Retrieval-Augmented Generation）システムによるAI検索基盤を構築することを目的とします。

## 主な機能

- **堅牢なETLパイプライン**: 巨大Excelを、ストリーミング処理と中間フォーマット（Parquet）を活用して、メモリに依存しない形で、分析可能な構造化データベース（DuckDB）に変換します。
- **データプロファイリング**: 変換過程のデータの特性（列数、セル長分布など）を詳細に分析し、可視化するためのインタラクティブなダッシュボードを提供します。
- **ハイブリッド検索インデックス構築**: キーワード検索（BM25/Pyserini）とベクトル検索（Faiss）の両方のための、高度な検索インデックスを構築します。
- **RAGアプリケーション**: 構築したインデックスを活用し、自然言語での質問応答を可能にするStreamlit製のWebアプリケーションプロトタイプ。

## プロジェクト構成

このリポジトリの主要なファイルとディレクトリ構造は以下の通りです。

```
gyoukaku-schema-mapper/
├── .gitignore
├── LICENSE
├── README.md
├── config.template.json
├── requirements.txt
├── analysis/
│   └── .gitkeep
├── data/
│   ├── csv/
│   │   └── .gitkeep
│   ├── excel/
│   │   └── .gitkeep
│   ├── long_csv/
│   │   └── .gitkeep
│   └── parquet/
│       └── .gitkeep
├── doc/
│   ├── rag_pipeline_guide.md
│   └── windows_setup_guide.md
├── src/
│   ├── analyze_csv_metrics.py
│   ├── analyze_data_distribution.py
│   ├── analyze_header_matrix.py
│   ├── build_faiss_index.py
│   ├── build_header_matrix_db.py
│   ├── build_search_docs.py
│   ├── chunk_preprocessed_docs.py
│   ├── convert_long_csv_to_parquet.py
│   ├── create_header_matrix.py
│   ├── llm_handler.py
│   ├── preprocess_docs.py
│   ├── retriever.py
│   ├── split_excel_to_csv.py
│   ├── transform_parquet_to_load_db.py
│   ├── unpivot_csv_to_long_csv.py
│   ├── verify_and_classify_headers.py
│   └── verify_search_docs.py
└── streamlit_app/
    ├── app.py
    └── report_viewer.py
```

## セットアップ

1. **リポジトリのクローンと移動**
   ```bash
   git clone [リポジトリのURL]
   cd gyoukaku-schema-mapper
   ```

2. **環境構築**
   *   **Windowsユーザーへの注意:** このプロジェクトのAIライブラリ群は、Windows環境で特別なセットアップを必要とします。まず **[Windowsセットアップガイド](doc/windows_setup_guide.md)** を参照して、C++ビルドツール、Java 21、およびConda環境を構築してください。

3. **ライブラリのインストール (Conda環境推奨)**
   ```bash
   # Conda環境の有効化 (例)
   conda activate gyoukaku
   
   # 必要なライブラリのインストール
   pip install -r requirements.txt
   ```

4. **設定ファイルの作成**
   プロジェクトのルートにある`config.template.json`をコピーして、`config.json`という名前でファイルを作成します。現時点では特に編集は不要です。

## 実行ワークフロー

### 1. データ分析 (オプション)

データの特性を理解するために、以下の分析スクリプトを実行できます。

```bash
# CSVの基本メトリクスを集計
python src/analyze_csv_metrics.py

# CSVのデータ分布を詳細に分析
python src/analyze_data_distribution.py
```

### 2. ETLパイプライン (Excel -> 構造化DB)

以下の順番でスクリプトを実行し、データを変換します。

```bash
# Step 1: Excelから生CSVへ変換
python src/split_excel_to_csv.py

# Step 2: 生CSVを縦長CSVに変換 (ストリーミング処理)
python src/unpivot_csv_to_long_csv.py

# Step 3: 縦長CSVをParquet形式に最適化
python src/convert_long_csv_to_parquet.py

# Step 4: Parquetを読み込み、構造化してDBにロード
python src/transform_parquet_to_load_db.py
```

### 3. RAGインデックスの構築

ETLパイプラインが完了した後、検索インデックスを構築します。
詳細な手順は **[RAGパイプライン構築手順書](doc/rag_pipeline_guide.md)** を参照してください。

### 4. アプリケーションの起動

プロジェクトには2つのアプリケーションが含まれています。

#### 4a. データ分布分析ビューアー

ETL過程で生成されたデータの分布をインタラクティブに分析します。

```bash
streamlit run streamlit_app/report_viewer.py
```

#### 4b. RAGシステム本体

構築したインデックスを使い、自然言語での質問応答を行います。

```bash
streamlit run streamlit_app/app.py
```