# Gyoukaku Schema Mapper

## 概要

このプロジェクトは、行政事業レビューシートのデータベースからダウンロードされる、巨大かつ複数年度にわたって列構成（スキーマ）が変動するExcelファイルを分析するための基盤を構築するものです。

手動での開封が困難な巨大Excelを安全にCSVへ変換し、年度ごとに異なる混沌としたヘッダー（列名）の構造を解明・可視化（マッピング）します。最終的には、ETLパイプラインを通じてクリーンなデータを生成し、RAG（Retrieval-Augmented Generation）システムによるAI検索基盤を構築することを目的とします。

## プロジェクト構成

このリポジトリの主要なスクリプトとデータ構造は以下の通りです。

```
gyoukaku-schema-mapper/
├── src/                          # ETLおよび分析スクリプト群
│   ├── split_excel_to_csv.py       # Step 1: Excel -> 生CSV
│   ├── unpivot_csv_to_long_csv.py  # Step 2: 生CSV -> 縦長CSV (Streaming)
│   ├── convert_long_csv_to_parquet.py # Step 3: 縦長CSV -> Parquet
│   ├── transform_parquet_to_load_db.py # Step 4: Parquet -> 構造化DBテーブル
│   │
│   ├── build_search_docs.py        # RAG Step 1: 検索ドキュメント作成
│   ├── preprocess_docs.py          # RAG Step 2a: SudachiPy前処理
│   ├── build_pyserini_index.py     # RAG Step 2b: BM25インデックス構築
│   └── build_faiss_index.py        # RAG Step 2c: Faissベクトルインデックス構築
│
├── streamlit_app/                # Streamlit Webアプリ
│   └── app.py
├── data/                           # データ格納庫 (Git管理外)
│   ├── excel/                      # 入力: 元のExcelファイル
│   ├── csv/                        # 中間: 生CSVファイル
│   ├── long_csv/                   # 中間: 縦長CSVファイル
│   ├── parquet/                    # 中間: 最適化済みParquetファイル
│   └── header_matrix.duckdb        # 出力: 最終分析用データベース
│
├── analysis/                       # 分析成果物 (インデックス等)
│   ├── header_comparison_matrix.csv
│   └── ...
└── doc/                            # ドキュメント
    └── windows_setup_guide.md      # Windows環境構築ガイド
```

## セットアップ

1. **リポジトリのクローン**
   ```bash
   git clone [リポジトリのURL]
   cd gyoukaku-schema-mapper
   ```

2. **環境構築**
   *   **Windowsユーザーへの注意:** このプロジェクトのAIライブラリ群は、Windows環境で特別なセットアップを必要とします。まず **[Windowsセットアップガイド](doc/windows_setup_guide.md)** を参照して、C++ビルドツール、Java 21、およびConda環境を構築してください。
   *   **macOS / Linuxユーザー:** `requirements.txt`に基づく標準的なPython環境構築で動作する可能性が高いですが、必要に応じてJavaのバージョン等を調整してください。

3. **ライブラリのインストール (Conda環境推奨)**
   ```bash
   # Conda環境の有効化 (例)
   conda activate gyoukaku
   
   # 必要なライブラリのインストール
   pip install -r requirements.txt
   ```

4. **設定ファイルの作成**
   プロジェクトのルートにある`config.template.json`をコピーして、`config.json`という名前でファイルを作成します。
   作成した`config.json`を開き、`anserini_jar_path`の値を、あなたのPC環境におけるAnseriniの`.jar`ファイルへの正しいフルパスに書き換えてください。

## 実行ワークフロー

以下の順番でスクリプトを実行し、データを変換します。

1. **Excelファイルの配置**: `data/excel/` フォルダに、分析したい `.xlsx` ファイルを配置します。

2. **ETLパイプラインの実行**:
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

3. **RAGインデックスの構築**:
   ```bash
   # Step 5: 検索ドキュメントの作成
   python src/build_search_docs.py

   # Step 6a: BM25用前処理
   python src/preprocess_docs.py

   # Step 6b: BM25インデックス構築
   python src/build_pyserini_index.py
   
   # Step 6c: Faissインデックス構築
   python src/build_faiss_index.py
   ```

4. **分析Webアプリの起動**:
   ```bash
   streamlit run streamlit_app/app.py
   ```