from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql+psycopg2://postgres:123123@localhost/postgres')
connection = engine.connect()
payment = pd.read_sql_table(table_name='payment_data', con=connection, schema='test_board1')
payments_by_time = pd.read_sql_query('select "Время сервера" as "Дата", sum("Принятая сумма") as "Общая сумма" from '
                                     'test_board1.payment_data group by "Дата" order by "Дата" desc',
                                     connection)
total_users = pd.read_sql_query('select count(*) as "Total Users" from test_board1.users group by "Номер Заявки"',
                                connection)
total_cash_payments = pd.read_sql_query('select sum("Принятая сумма") as "Общая сумма" from test_board1.payment_data',
                                        connection)
total_payments = pd.read_sql_query('select count(*) as "Кол-во операций" from test_board1.payment_data pd group  by '
                                   '"Номер"', connection)
