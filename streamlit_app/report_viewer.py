import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="データ分布レポートビューアー", layout="wide")

@st.cache_data
def load_data(filepath):
    # (load_data関数は変更なし)
    if not os.path.exists(filepath):
        st.error(f"レポートファイルが見つかりません: {filepath}"); return None, None
    with open(filepath, 'r', encoding='utf-8') as f: data = json.load(f)
    if not data: return None, None
    
    for row in data:
        header_dist = {}; cell_dist = {}
        for k, v in row['header_len_distribution'].items(): header_dist[str(k)] = v
        for k, v in row['cell_len_distribution'].items(): cell_dist[str(k)] = v
        row['header_len_distribution'] = header_dist; row['cell_len_distribution'] = cell_dist

    df_metrics = pd.DataFrame(data).drop(columns=['header_len_distribution', 'cell_len_distribution'])
    dist_data = {}
    for row in data:
        fname = row['filename']
        sort_key = lambda item: (item[0].replace('+', '').isdigit(), int(item[0].replace('+', '')) if item[0].replace('+', '').isdigit() else float('inf'))
        dist_data[f"header_{fname}"] = pd.DataFrame(sorted(row['header_len_distribution'].items(), key=sort_key), columns=['Length', 'Count'])
        dist_data[f"cell_{fname}"] = pd.DataFrame(sorted(row['cell_len_distribution'].items(), key=sort_key), columns=['Length', 'Count'])
    return df_metrics, dist_data

def main():
    st.title("📊 データ分布 分析レポートビューアー")
    st.write("`data_distribution_summary.json`の内容を可視化・分析します。")

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_filepath = os.path.join(project_root, 'analysis', 'data_distribution_summary.json')
    df_metrics, dist_data = load_data(report_filepath)

    if df_metrics is not None:
        st.header("📈 総合サマリー")
        col1, col2 = st.columns(2); col1.metric("分析ファイル数", f"{len(df_metrics)} 件"); col2.metric("全ファイル中の最大セル長", f"{df_metrics['max_cell_len'].max():,} 文字")
        
        # --- ★★★ ファイルごと詳細メトリクスにコピーボタンを追加 ★★★ ---
        st.header("📄 ファイルごと詳細メトリクス")
        st.dataframe(df_metrics.style.format(precision=1))
        st.download_button(
           label="📋 表をCSVとしてコピー/ダウンロード",
           data=df_metrics.to_csv(index=False, encoding='utf-8-sig'),
           file_name='metrics_summary.csv',
           mime='text/csv',
        )
        
        if 'selected_file_for_detail' not in st.session_state:
            st.session_state.selected_file_for_detail = df_metrics['filename'][0]

        st.header("🔢 セル文字列長の全体傾向 (マトリクス)")
        st.write("各ファイルにおける、各文字列長の区間ごとのセル出現数です。グラフアイコンをクリックすると、下に詳細な分布が表示されます。")

        matrix_data, all_dist_keys = [], []
        for filename, cell_dist_df in dist_data.items():
            if filename.startswith("cell_"):
                fname = filename.replace("cell_", "")
                row_data = {"filename": fname}
                for _, row in cell_dist_df.iterrows():
                    row_data[row['Length']] = row['Count']
                    if row['Length'] not in all_dist_keys: all_dist_keys.append(row['Length'])
                matrix_data.append(row_data)
        
        sort_key = lambda x: (str(x).replace('+', '').isdigit(), int(str(x).replace('+', '')) if str(x).replace('+', '').isdigit() else float('inf'))
        all_dist_keys.sort(key=sort_key)
        df_matrix = pd.DataFrame(matrix_data).set_index('filename')
        df_matrix = df_matrix.reindex(columns=all_dist_keys).fillna(0)

        header_cols = st.columns((4, 1) + (1,) * len(df_matrix.columns))
        header_cols[0].write("**ファイル名**")
        header_cols[1].write("**詳細**")
        for i, col_name in enumerate(df_matrix.columns):
            header_cols[i+2].write(f"**{col_name}**")

        with st.container(height=400):
            for filename, row in df_matrix.iterrows():
                data_cols = st.columns((4, 1) + (1,) * len(df_matrix.columns))
                data_cols[0].text(filename)
                if data_cols[1].button("📊", key=f"btn_{filename}", help="このファイルの詳細な分布グラフを表示"):
                    st.session_state.selected_file_for_detail = filename
                for i, value in enumerate(row):
                    data_cols[i+2].text(f"{int(value):,}")
        # --- ★★★ 全体傾向マトリクスにコピーボタンを追加 ★★★ ---
        st.download_button(
           label="📋 マトリクスをCSVとしてコピー/ダウンロード",
           data=df_matrix.to_csv(encoding='utf-8-sig'), # index=Trueがデフォルト
           file_name='distribution_matrix.csv',
           mime='text/csv',
        )
        
        st.header("🔬 ファイルごとの詳細分析")
        selected_file = st.session_state.selected_file_for_detail
        if selected_file:
            st.info(f"**'{selected_file}'** の詳細を表示中...")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**ヘッダー列名** の長さ分布:")
                df = dist_data.get(f"header_{selected_file}")
                if df is not None:
                    plot_df = df[df['Count'] > 0]
                    if not plot_df.empty:
                        st.bar_chart(plot_df.set_index('Length'))
            with col2:
                st.write("**セルデータ** の長さ分布:")
                df = dist_data.get(f"cell_{selected_file}")
                if df is not None:
                    plot_df = df[df['Count'] > 0]
                    if not plot_df.empty:
                        st.bar_chart(plot_df.set_index('Length'))

if __name__ == "__main__":
    main()