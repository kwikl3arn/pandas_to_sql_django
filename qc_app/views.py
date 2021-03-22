from django.shortcuts import render
import pandas as pd
from django.http import HttpResponse
from django.conf import settings
import sqlalchemy
from django.db import connection
from django.http import JsonResponse
import json

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

def json_tabel(request,tableName):
    print('tableName=',tableName)
    with connection.cursor() as cursor:
        cursor.execute("select * from {}".format(tableName))
        # print('-------->query=', connection.queries)
        file_data = cursor.fetchall()
    json_data = []
    for obj in file_data:
        json_data.append({"ReferenceID": obj[1], "Marketplace": obj[2], "Customer_id": obj[3], "Review_id": obj[4],
                        "Product_id": obj[5], "Product_parent": obj[6], "Product_title": obj[7]})
    # print(json_data)                    
    return JsonResponse(json_data, safe=False)                    

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
        customer_id = request.GET.get('customer_id')
        product_id = request.GET.get('product_id')
        review_id = request.GET.get('review_id')
        product_parent_id = request.GET.get('product_parent_id')
        product_title_id = request.GET.get('product_title_id')
        product_title = str(product_title_id).replace("'", "\\'")
        # print(tableName, product_title)
        with connection.cursor() as cursor:
            cursor.execute(
                f"update {tableName} set product_title='{product_title}',marketplace='{marketplace_id}' where id={Referenceid}")
            # print('-------->query=', connection.queries)
            # return JsonResponse(json_data, safe=False)
        file_data = {'ReferenceID': Referenceid, 'Marketplace': marketplace_id, 'Customer_id': customer_id,
                     'Review_id': review_id, 'Product_id': product_id, "Product_parent": product_parent_id,
                     "Product_title": product_title_id}
        data = {
            'file_data': file_data
        }
        # print(data)
        return JsonResponse(data)
