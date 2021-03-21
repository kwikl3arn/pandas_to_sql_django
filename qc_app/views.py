from django.shortcuts import render
import pandas as pd
from django.http import HttpResponse
from django.conf import settings
import sqlalchemy
from django.db import connection


def db_connection():
    user = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    database_name = settings.DATABASES['default']['NAME']

    database_url = 'mysql://{user}:{password}@localhost:3306/{database_name}'.format(
        user=user,
        password=password,
        database_name=database_name,
    )

    return database_url


def pandas_tabelcreate(df, tableName):
    print(db_connection())
    try:
        df.to_sql(tableName, db_connection(), if_exists='fail')
        print('created')
    except Exception as ex:
        print('unable to create table=', ex)
    else:
        print(f"Table {tableName} created successfully.")


# Create your views here.
def qc_title(request):
    if request.method == 'POST':
        file = request.FILES['file']
        filename = request.FILES['file'].name
        df = pd.read_excel(file, engine='openpyxl')
        df = df.reset_index()
        df.columns.values[0] = 'id'
        df['id'] = df.index + 1
        tableName = 'df_data'
        pandas_tabelcreate(df, tableName)
        # frame = pd.read_sql("select * from {}".format(tableName), db_connection())
        # pd.set_option('display.expand_frame_repr', False)
        # print(type(frame))
        with connection.cursor() as cursor:
            cursor.execute("select * from {}".format(tableName))
            # print('-------->query=', connection.queries)
            file_data = cursor.fetchall()
        return render(request, 'qc_title1.html', {'file_data': file_data, 'tableName': tableName})
    else:
        return render(request, 'qc_title.html')


def qc_title_update(request):
    if request.method == 'GET':
        tableName = request.GET.get('tabelname')
        Referenceid = request.GET.get('Referenceid')
        marketplace_id = request.GET.get('marketplace_id')
        product_title_id = request.GET.get('product_title_id')
        product_title = str(product_title_id).replace("'", "\\'")
        # print(tableName, product_title)
        with connection.cursor() as cursor:
            cursor.execute(
                f"update {tableName} set product_title='{product_title}',marketplace='{marketplace_id}' where id={Referenceid}")
            # print('-------->query=', connection.queries)
        return HttpResponse('updated')
