# Windows環境におけるセットアップガイド

このプロジェクトのRAG機能（特にPyserini）は、Windows環境で動作させるためにいくつかの特別な設定を必要とします。このガイドの手順に従って、開発環境を構築してください。

## 1. Microsoft C++ Build Toolsのインストール

**目的:** Pythonライブラリ（`pyjnius`や`nmslib`の依存関係）をソースコードからビルド（コンパイル）するために必要です。

1.  **ダウンロード**: [Visual Studio Build Tools](https://visualstudio.microsoft.com/ja/visual-cpp-build-tools/)にアクセスし、インストーラーをダウンロードします。
2.  **インストール**: インストーラーを実行し、「ワークロード」タブで**「C++によるデスクトップ開発」**にチェックを入れます。
3.  **確認**: インストールの詳細で「MSVC C++ビルドツール」と「Windows SDK」が含まれていることを確認し、インストールを実行します。

## 2. Java 21 (JDK) のインストール

**目的:** Pyseriniの最新バージョンは、Java 21の実行環境を要求します。

1.  **ダウンロード**: [Adoptium Temurin 21 (LTS)](https://adoptium.net/ja/temurin/releases/?version=21)にアクセスし、Windows x64版のJDKの`.msi`インストーラーをダウンロードします。
2.  **インストール**: インストーラーを実行します。
3.  **最重要設定**: インストール中に`Set JAVA_HOME variable`（JAVA_HOME変数を設定する）というオプションが表示されたら、必ず**「Will be installed on local hard drive」**を選択して、環境変数を自動で設定するようにしてください。

## 3. CondaによるPython環境の構築

**目的:** 複雑なライブラリの依存関係とPythonのバージョンを管理するため、`conda`を使用してプロジェクト専用の独立した環境を構築します。

1.  **Minicondaのインストール**:
    *   [Miniconda](https://docs.conda.io/en/latest/miniconda.html)のインストーラーをダウンロードします。
    *   インストール実行時、**「Install for: Just Me (recommended)」**を選択します。これにより、権限の問題を回避できます。

2.  **環境の作成とライブラリのインストール**:
    *   スタートメニューから「Anaconda Prompt」を起動します。
    *   以下のコマンドを順番に実行します。

    ```bash
    # 1. Python 3.11の環境を作成 (ライブラリの互換性が高いため)
    conda create --name gyoukaku python=3.11

    # 2. 作成した環境を有効化
    conda activate gyoukaku

    # 3. condaでインストールすべきライブラリをインストール (conda-forgeチャネルから)
    conda install -c conda-forge faiss-cpu pandas openpyxl streamlit tqdm

    # 4. pipでインストールすべきライブラリをインストール
    pip install pyserini sentence-transformers sudachipy sudachidict_core
    ```

## 4. VSCodeとの連携設定 (オプション)

VSCodeのターミナルで`conda`環境を快適に使用するための設定です。

1.  **Anaconda Prompt**を起動します。
2.  `conda init powershell` コマンドを実行します。
3.  VSCodeを完全に再起動します。
4.  VSCodeで新しいターミナルを開くと、自動的に`(base)`環境で起動するようになります。`conda activate gyoukaku`で環境を切り替えてください。