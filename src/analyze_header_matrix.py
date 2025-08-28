import os
import csv

def analyze_matrix_file(matrix_filepath, output_filepath):
    """
    ヘッダー比較マトリクスファイルを読み込み、各列名の登場回数を集計して
    サマリーレポートCSVを生成する。
    """
    print(f"--- '{os.path.basename(matrix_filepath)}' の分析を開始します ---")

    try:
        # --- マトリクスファイルからデータを読み込む ---
        with open(matrix_filepath, 'r', encoding='utf-8-sig') as f_in:
            reader = csv.reader(f_in)
            
            # ヘッダー行をスキップ
            header = next(reader)
            
            # --- 集計結果を新しいCSVファイルに書き込む ---
            with open(output_filepath, 'w', newline='', encoding='utf-8-sig') as f_out:
                writer = csv.writer(f_out)
                
                # サマリーレポートのヘッダーを書き込む
                writer.writerow(['column_name', 'appearance_count'])
                
                print("各列名の登場回数を集計中...")
                
                # データ行を1行ずつ処理
                for row in reader:
                    column_name = row[0]
                    # row[1:] には '1' か '0' が入っている
                    # '1' の数を数えることで登場回数を計算
                    appearance_count = sum(1 for value in row[1:] if value == '1')
                    
                    # 結果を書き込む
                    writer.writerow([column_name, appearance_count])

        print("\n★★★ サマリーレポートの生成が完了しました ★★★")

    except FileNotFoundError:
        print(f"[エラー] 分析対象のマトリクスファイルが見つかりません: {matrix_filepath}")
    except StopIteration:
        print(f"[エラー] マトリクスファイル '{os.path.basename(matrix_filepath)}' が空か、ヘッダー行しかありません。")
    except Exception as e:
        print(f"[エラー] 処理中に問題が発生しました: {e}")


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    result_dir = os.path.join(project_root, 'result')
    
    # 分析対象の入力ファイルパス
    matrix_input_path = os.path.join(result_dir, 'header_comparison_matrix.csv')
    
    # サマリーレポートの出力ファイルパス
    summary_output_path = os.path.join(result_dir, 'header_summary_report.csv')
    
    analyze_matrix_file(matrix_input_path, summary_output_path)
    
    print(f"\n分析結果がCSVファイルに出力されました: {summary_output_path}")