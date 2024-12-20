import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import plotly.express as px

# データの読み込み
df = pd.read_csv("Book1.csv", encoding="utf-8-sig")
df.columns = ["問番号", "設問内容の要約", "全体 (%)", "造血器腫瘍 (%)", "固形腫瘍 (脳腫瘍を除く) (%)", "脳腫瘍 (%)"]

# 表示用に問番号と設問内容を結合
df["表示用"] = df["問番号"] + " - " + df["設問内容の要約"]

# アプリの作成
app = dash.Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootswatch@5.2.3/dist/flatly/bootstrap.min.css"])
app.title = "R1小児調査報告書データ"

# 項目の順序を固定
metric_order = ["全体 (%)", "造血器腫瘍 (%)", "固形腫瘍 (脳腫瘍を除く) (%)", "脳腫瘍 (%)"]

# アプリのレイアウト
app.layout = html.Div([
    html.Div([
        html.H1("R1小児調査報告書データ", className="text-center text-primary mb-4"),
    ], className="bg-light p-3"),

    html.Div([
        html.Div([
            html.Label("問番号を選択:", className="form-label"),
            dcc.Dropdown(
                id="selected_page",
                options=[{"label": row["表示用"], "value": row["問番号"]} for _, row in df.iterrows()],
                multi=True,
                className="form-select"
            ),
        ], className="mb-3"),

        html.Div([
            html.Label("比較する指標:", className="form-label"),
            dcc.Checklist(
                id="selected_metrics",
                options=[
                    {"label": "全体 (%)", "value": "全体 (%)"},
                    {"label": "造血器腫瘍 (%)", "value": "造血器腫瘍 (%)"},
                    {"label": "固形腫瘍 (脳腫瘍を除く) (%)", "value": "固形腫瘍 (脳腫瘍を除く) (%)"},
                    {"label": "脳腫瘍 (%)", "value": "脳腫瘍 (%)"}
                ],
                value=["全体 (%)", "造血器腫瘍 (%)"],
                className="form-check-inline"
            ),
        ], className="mb-3"),

        html.Button("フィルタリング", id="filter_btn", className="btn btn-primary"),

    ], className="p-3 border rounded shadow-sm mb-4"),

    html.Div([
        html.H2("項目比較", className="text-secondary"),
        dcc.Graph(id="comparison_plot"),
    ], className="mb-4"),

    html.Div([
        html.H2("データテーブル", className="text-secondary"),
        html.Div(id="data_table", className="table-responsive"),
    ], className="mb-4"),

    html.Div([
        html.H2("統計情報", className="text-secondary"),
        dash_table.DataTable(
            id="stats_table",
            columns=[{"name": col, "id": col} for col in df.describe().reset_index().columns],
            data=df.describe().reset_index().to_dict("records"),
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "center",
                "minWidth": "150px",
                "maxWidth": "150px",
                "whiteSpace": "normal",
            },
            style_header={
                "backgroundColor": "lightgrey",
                "fontWeight": "bold",
            }
        )
    ]),
], className="container mt-4")

# コールバックの定義
@app.callback(
    [Output("data_table", "children"),
     Output("comparison_plot", "figure"),
     Output("stats_table", "data")],
    [Input("filter_btn", "n_clicks")],
    [State("selected_page", "value"),
     State("selected_metrics", "value")]
)
def update_dashboard(n_clicks, selected_page, selected_metrics):
    if not selected_page:
        filtered_df = df
    else:
        filtered_df = df[df["問番号"].isin(selected_page)]
    
    # データテーブルから「表示用」列を除外
    filtered_df_without_display = filtered_df.drop(columns=["表示用"])

    # データテーブル
    table = html.Table([
        html.Thead(html.Tr([html.Th(col) for col in filtered_df_without_display.columns])),
        html.Tbody([
            html.Tr([html.Td(filtered_df_without_display.iloc[i][col]) for col in filtered_df_without_display.columns])
            for i in range(len(filtered_df_without_display))
        ])
    ], className="table table-striped")
    
    # 項目比較プロット
    if selected_metrics:
        long_data = filtered_df.melt(
            id_vars=["問番号"], value_vars=selected_metrics,
            var_name="項目", value_name="値"
        )
        # 順序を固定
        long_data["項目"] = pd.Categorical(long_data["項目"], categories=metric_order, ordered=True)
        long_data = long_data.sort_values(by=["問番号", "項目"])  # ソートして順序を保持

        # 色を指定
        color_map = {
            "全体 (%)": "skyblue",
            "造血器腫瘍 (%)": "pink",
            "固形腫瘍 (脳腫瘍を除く) (%)": "lightgreen",
            "脳腫瘍 (%)": "lavender"
        }
        fig = px.bar(
            long_data, x="問番号", y="値", color="項目",
            barmode="group", title="指標の比較",
            color_discrete_map=color_map
        )
        # 背景色をグレーに設定
        fig.update_layout(
            yaxis=dict(range=[0, 100]),
            plot_bgcolor="#f9f9f9",  # グラフ背景色
            paper_bgcolor="#f9f9f9",  # 外側背景色
            dragmode="zoom",  # ズームモードをデフォルトに設定
        )
    else:
        fig = px.bar(title="データが選択されていません")
    
    # 統計情報
    stats_data = filtered_df[selected_metrics].describe().round(1).reset_index().to_dict("records") if selected_metrics else []
    
    return table, fig, stats_data

server = app.server

# アプリの起動
if __name__ == "__main__":
    app.run_server(debug=True)
