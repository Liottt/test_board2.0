from datetime import date

from sqlalchemy import create_engine

import pandas as pd

import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

from func import *

engine = create_engine('postgresql+psycopg2://postgres:123123@localhost/postgres')
connection = engine.connect()
payment = pd.read_sql_table(table_name='payment_data', con=connection, schema='test_board1')

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP])
date_selector_day = dcc.DatePickerRange(
    id='date-picker-range',
    min_date_allowed=min(payment['Время сервера']),
    max_date_allowed=max(payment['Время сервера']),
    initial_visible_month=max(payment['Время сервера']),
    end_date=date(2022, 1, 31),
    start_date=date(2022, 1, 1),
    display_format='DD-MM-YYYY')

TEMPLATE_CHART = go.layout.Template(
    layout=dict(
        font=dict(family='Roboto', size=11),
        legend=dict()
    )
)

app.layout = html.Div([
    html.Div([
        dbc.Row([dbc.Navbar(
            dbc.Container(
                [
                    html.A(
                        dbc.Row(
                            [
                                dbc.Col(html.Img(src=app.get_asset_url('images\halyk_logo.png'))),
                                dbc.Col(dbc.NavbarBrand("Статистический отчет", className="ms-2")),
                            ],
                            align="center",
                            className="g-0",
                        ),
                        style={"textDecoration": "none"},
                    )
                ]
            )
        )], style={"color": "white"}),
        dbc.Row([
            dbc.Col(html.H4("Выберите даты"), style={"margin-top": '40px'}),

        ]),
        dbc.Row([
            dbc.Col(html.Div(date_selector_day)),
            dbc.Col(dbc.Button("Применить", id='submit-val', n_clicks=0, className='mr-2'))
        ]),
        dbc.Row([
            dbc.Col(html.Div(id='payments_by_month'), md=6, ),
            dbc.Col(html.Div(id='payments_info'), md=6, )
        ]),
        dbc.Row([
            html.Div(id='top10_transactions_trans')]),
        dbc.Row([
            html.Div(id='top10_transactions')]),
        dbc.Row([
            html.Div(id='user_info_selector')])
    ]
    )
], style={"margin-top": '40px', 'margin-left': '40px', 'margin-right': '40px'}
)


@app.callback([
    Output(component_id='payments_by_month', component_property='children'),
    Output(component_id='payments_info', component_property='children'),
    Output(component_id='top10_transactions_trans', component_property='children'),
    Output(component_id='top10_transactions', component_property='children'),
    Output(component_id='user_info_selector', component_property='children')],
    [Input(component_id='submit-val', component_property='n_clicks')],
    [State(component_id='date-picker-range', component_property='start_date'),
     State(component_id='date-picker-range', component_property='end_date')])
def update_date_payments(n, start_date, end_date):
    payments_by_time = pd.read_sql_query(
        'select "Время сервера" as "Дата", sum("Принятая сумма") as "Общая сумма" from '
        'test_board1.payment_data group by "Дата" order by "Дата" desc',
        connection)
    fig2 = px.bar(payments_by_time, x="Дата", y="Общая сумма")
    fig2.update_layout(xaxis_range=[start_date, end_date], title_text="Транзакции по фильтру",
                       template=TEMPLATE_CHART)
    fig2.update_traces(hovertemplate='Дата: %{x|%d/%m/%Y год} <br>Сумма: %{y:,.0f} сом')
    html2 = [dcc.Graph(figure=fig2)]
    series = "'DD-MM-YYYY'"
    serial = "'YYYY-MM'"
    start_date = f"'{start_date}'"
    end_date = f"'{end_date}'"
    payments_by_month = pd.read_sql_query(f'select * from(select to_char("Время сервера", {serial})  as "Дата", sum('
                                          f'"Принятая сумма") as "Сумма"  from test_board1.payment_data pd group by '
                                          f'"Дата" order by "Сумма" desc) as foo order by foo."Дата";', connection)
    fig1 = px.line(payments_by_month, x="Дата", y="Сумма", markers=True)
    fig1.update_layout(title_text="Обьем транзакций", template=TEMPLATE_CHART)
    fig1.update_traces(hovertemplate="Дата: %{x|%m/%Y год} <br>Сумма: %{y:,.0f} сом")
    html1 = [dcc.Graph(figure=fig1)]
    payments_info_trans = pd.read_sql_query(
        f'select foo.Сервис, sum(foo."Количество транзакций") as "Количество транзакций" from(select '
        f'to_char("Время сервера", {series})  as "Дата", "Сервис", count(*) as '
        f'"Количество транзакций"  from test_board1.payment_data pd where "Время '
        f'сервера" between {start_date} and {end_date} group by "Сервис", '
        f'"Дата" order by "Количество транзакций" desc) as foo group by  foo.Сервис '
        f'order by "Количество транзакций" desc  limit 10;', connection)
    str_dataframe_servis(payments_info_trans, "Сервис")
    fig3 = px.bar(payments_info_trans, x='Количество транзакций', y='Сервис')
    fig3.update_layout(title_text="Top 10 по количеству транзакций",
                       template=TEMPLATE_CHART, margin_l=200)
    fig3.update_traces(hovertemplate='Количество транзакций: %{x} <br>Сервис: %{y}')
    html3 = [dcc.Graph(figure=fig3)]
    payments_info_cash = pd.read_sql_query(
        f'select foo.Сервис, sum(foo."Сумма" ) as "Сумма" from(select to_char("Время '
        f'сервера", {series})  as "Дата", "Сервис", sum("Принятая сумма")as "Сумма"  '
        f'from test_board1.payment_data pd  where "Время сервера"  between {start_date} and {end_date} group '
        f'by "Сервис", "Дата" order by "Сервис" desc ) as foo group by foo.Сервис order '
        f'by "Сумма" desc limit 10', connection)
    str_dataframe_servis(payments_info_cash, "Сервис")
    fig4 = px.bar(payments_info_cash, x='Сумма', y='Сервис')
    fig4.update_layout(title_text="Top 10 по сумме транзакций", template=TEMPLATE_CHART, margin_l=200)
    fig4.update_traces(hovertemplate='Сумма: %{x:,.0f} сом <br>Сервис: %{y}')
    html4 = [dcc.Graph(figure=fig4)]
    user_info_selector = pd.read_sql_query(
        'select foo."Подразделение исполнителя", sum(foo."Количество Заявок") as '
        '"Количество Заявок" from(select "Дата создания", "Подразделение исполнителя", '
        'count(*) as "Количество Заявок" from test_board1.users where "Дата создания" '
        f'between {start_date} and {end_date} group by "Дата создания", '
        '"Подразделение исполнителя" order by "Количество Заявок" desc) as foo '
        'group by "Подразделение исполнителя" order by "Количество Заявок" desc', connection)
    str_dataframe_fil(user_info_selector, "Подразделение исполнителя")
    fig5 = px.bar(user_info_selector, x='Количество Заявок', y='Подразделение исполнителя')
    fig5.update_layout(title_text="Зарегистрированно пользователей по филиалам", template=TEMPLATE_CHART, margin_l=200)
    fig5.update_traces(hovertemplate='Зарегистрированно: %{x} <br>Исполнитель: %{y}')
    html5 = [dcc.Graph(figure=fig5)]
    return html1, html2, html3, html4, html5


if __name__ == '__main__':
    app.run_server(debug=True, port=8000)
