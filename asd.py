from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql+psycopg2://postgres:123123@localhost/postgres')
connection = engine.connect()
series = "'DD-MM-YYYY'"
serial = "'MM-YYYY'"
start_date = "'01.01.2022'"
end_date = "'31.01.2022'"
payments_by_time = pd.read_sql_query('select "Время сервера" as "Дата", sum("Принятая сумма") as "Общая сумма" from '
                                     'test_board1.payment_data group by "Дата" order by "Дата" desc',
                                     connection)

for key in payments_by_time['Общая сумма']:

    print(type(key))