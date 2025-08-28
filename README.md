# Gyoukaku Schema Mapper

## 概要

このプロジェクトは、行政事業レビューシートのデータベースからダウンロードされる、巨大かつ複数年度にわたって列構成（スキーマ）が大きく変動するExcelファイルを分析するための基盤を構築するものです。

手動での開封が困難な巨大Excelを安全にCSVへ変換し、年度ごとに異なる混沌としたヘッダー（列名）の構造を解明・可視化（マッピング）します。最終的には、インタラクティブなWebアプリケーションを通じて、SQLによる深いデータ探索を可能にすることを目的とします。

## 主な機能

- **巨大Excelの安全なCSV変換**: `openpyxl`を利用し、メモリを大量に消費するPandasを介さずに巨大ExcelをシートごとにCSVへ変換します。(`src/split_excel_to_csv.py`)
- **ヘッダー構造の比較・可視化**: 全CSVファイルのヘッダーを比較し、どの列がどのファイルに存在するかを示す巨大なマトリクスを生成します。(`src/create_header_matrix.py`)
- **高速な分析データベースの構築**: 生成したマトリクスを元に、インメモリ分析DBであるDuckDBのデータベースファイルを構築します。(`src/build_header_matrix_db.py`)
- **インタラクティブなSQL実行環境**: Streamlit製のWebアプリを起動し、構築したデータベースに対して直接SQLクエリを実行し、分析結果を動的に確認できます。(`streamlit_app/app.py`)

## プロジェクト構成

```
gyoukaku-schema-mapper/
├── src/                      # 各種処理を実行するスクリプト群
│   ├── split_excel_to_csv.py       # Excel -> CSV 変換
│   ├── create_header_matrix.py   # ヘッダー比較マトリクス作成
│   └── build_header_matrix_db.py # 比較マトリクス -> DB構築
├── streamlit_app/            # Streamlit Webアプリ
│   └── app.py
├── data/                       # 生データおよび中間データ
│   ├── excel/                  # 元のExcelファイルを配置 (.xlsx)
│   ├── csv/                    # 変換後のCSVファイルが格納される
│   └── header_matrix.duckdb    # 分析用データベース
├── analysis/                   # 分析結果の成果物
│   └── header_comparison_matrix.csv
├── .gitignore                  # Git管理対象外のファイルを指定
├── README.md                   # このファイル
└── requirements.txt            # 必要なPythonライブラリ
```

## セットアップ

1. **リポジトリのクローン**
   ```bash
   git clone [リポジトリのURL]
   cd gyoukaku-schema-mapper
   ```

2. **Python仮想環境の作成と有効化**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **必要なライブラリのインストール**
   ```bash
   pip install -r requirements.txt
   ```

## 実行ワークフロー

以下の順番でスクリプトを実行してください。

1. **Excelファイルの配置**: `data/excel/` フォルダに、分析したい `.xlsx` ファイルを配置します。

2. **Excel -> CSV 変換**:
   ```bash
   python src/split_excel_to_csv.py
   ```
   *結果: `data/csv/` にCSVファイルが生成されます。*

3. **ヘッダー比較マトリクス作成**:
   ```bash
   python src/create_header_matrix.py
   ```
   *結果: `analysis/header_comparison_matrix.csv` が生成されます。*

4. **データベース構築**:
   ```bash
   python src/build_header_matrix_db.py
   ```
   *結果: `data/header_matrix.duckdb` が生成されます。*

5. **分析Webアプリの起動**:
   ```bash
   streamlit run streamlit_app/app.py
   ```
   *ブラウザが起動し、SQL実行画面が表示されます。*

## 次のステップ

このプロジェクトでデータのスキーマ（構造）とその変遷を完全に明らかにしました。次のフェーズでは、この知見を元に**ETL (Extract, Transform, Load)** プロセスを設計・実装し、複数年度にわたるデータをクレンジングし、分析しやすい「ロングフォーマット」のデータベースを構築することを目指します。