import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px

# データの読み込み
df = pd.read_csv("Book1.csv", encoding="utf-8-sig")
df.columns = ["問番号", "設問内容の要約", "全体 (%)", "造血器腫瘍 (%)", "固形腫瘍 (脳腫瘍を除く) (%)", "脳腫瘍 (%)"]

# アプリの作成
app = dash.Dash(__name__)

# アプリのレイアウト
app.layout = html.Div([
    html.H1("小児調査データダッシュボード"),
    
    html.Div([
        html.Label("問番号を選択:"),
        dcc.Dropdown(
            id="selected_page",
            options=[{"label": i, "value": i} for i in df["問番号"].unique()],
            multi=True
        ),
        html.Label("比較する指標:"),
        dcc.Checklist(
            id="selected_metrics",
            options=[
                {"label": "全体 (%)", "value": "全体 (%)"},
                {"label": "造血器腫瘍 (%)", "value": "造血器腫瘍 (%)"},
                {"label": "固形腫瘍 (脳腫瘍を除く) (%)", "value": "固形腫瘍 (脳腫瘍を除く) (%)"},
                {"label": "脳腫瘍 (%)", "value": "脳腫瘍 (%)"}
            ],
            value=["全体 (%)", "造血器腫瘍 (%)"]
        ),
        html.Button("フィルタリング", id="filter_btn"),
    ], style={"padding": "10px", "border": "1px solid #ddd", "margin-bottom": "20px"}),
    
    html.Div([
        html.H2("データテーブル"),
        html.Div(id="data_table"),
    ], style={"margin-bottom": "20px"}),
    
    html.Div([
        html.H2("項目比較"),
        dcc.Graph(id="comparison_plot"),
    ], style={"margin-bottom": "20px"}),
    
    html.Div([
        html.H2("統計情報"),
        html.Pre(id="stats"),
    ]),
])

# コールバックの定義
@app.callback(
    [Output("data_table", "children"),
     Output("comparison_plot", "figure"),
     Output("stats", "children")],
    [Input("filter_btn", "n_clicks")],
    [State("selected_page", "value"),
     State("selected_metrics", "value")]
)
def update_dashboard(n_clicks, selected_page, selected_metrics):
    if not selected_page:
        filtered_df = df
    else:
        filtered_df = df[df["問番号"].isin(selected_page)]
    
    # データテーブル
    table = html.Table([
        html.Thead(html.Tr([html.Th(col) for col in filtered_df.columns])),
        html.Tbody([
            html.Tr([html.Td(filtered_df.iloc[i][col]) for col in filtered_df.columns])
            for i in range(len(filtered_df))
        ])
    ])
    
    # 項目比較プロット
    if selected_metrics:
        long_data = filtered_df.melt(
            id_vars=["問番号"], value_vars=selected_metrics,
            var_name="項目", value_name="値"
        )
        fig = px.bar(
            long_data, x="問番号", y="値", color="項目",
            barmode="group", title="指標の比較"
        )
    else:
        fig = px.bar(title="データが選択されていません")
    
    # 統計情報
    stats = filtered_df[selected_metrics].describe().to_string() if selected_metrics else "選択されたデータがありません"
    
    return table, fig, stats

# アプリの起動
if __name__ == "__main__":
    app.run_server(debug=True)
