# Gyoukaku Schema Mapper

## 概要

このプロジェクトは、行政事業レビューシートのデータベースからダウンロードされる、巨大かつ複数年度にわたって列構成（スキーマ）が変動するExcelファイルを分析するための基盤を構築するものです。

手動での開封が困難な巨大Excelを安全にCSVへ変換し、年度ごとに異なる混沌としたヘッダー（列名）の構造を解明・可視化（マッピング）します。最終的には、ETLパイプラインを通じてクリーンなデータを生成し、RAG（Retrieval-Augmented Generation）システムによるAI検索基盤を構築することを目的とします。

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
│   ├── analyze_header_matrix.py
│   ├── build_faiss_index.py
│   ├── build_header_matrix_db.py
│   ├── build_search_docs.py
│   ├── chunk_preprocessed_docs.py
│   ├── convert_long_csv_to_parquet.py
│   ├── create_header_matrix.py
│   ├── preprocess_docs.py
│   ├── retriever.py
│   ├── split_excel_to_csv.py
│   ├── transform_parquet_to_load_db.py
│   ├── unpivot_csv_to_long_csv.py
│   ├── verify_and_classify_headers.py
│   └── verify_search_docs.py
└── streamlit_app/
    └── app.py
```

#### 各ディレクトリの役割

- **`src/`**: 全てのPythonスクリプトを格納するメインのソースコードディレクトリ。
- **`streamlit_app/`**: Streamlit製のWebアプリケーション本体。
- **`data/`**: ETLプロセスにおける各段階のデータを格納する場所 (Git管理外)。
  - `excel/`: 入力となる元のExcelファイル。
  - `csv/`: Excelから変換された生CSV。
  - `long_csv/`: 縦長に変換された中間CSV。
  - `parquet/`: 最適化されたParquet形式の中間データ。
- **`analysis/`**: RAGインデックスや分析結果など、最終的な成果物を格納する場所 (Git管理外)。
- **`doc/`**: セットアップ手順やパイプラインの実行手順など、プロジェクトに関するドキュメント。

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

### 1. ETLパイプライン (Excel -> 構造化DB)

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

### 2. RAGインデックスの構築

ETLパイプラインが完了した後、検索インデックスを構築します。
詳細な手順は **[RAGパイプライン構築手順書](doc/rag_pipeline_guide.md)** を参照してください。

### 3. 分析Webアプリの起動

```bash
streamlit run streamlit_app/app.py
```