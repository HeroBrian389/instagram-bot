import pymysql.cursors


sql = 'select id, filename from images_new'


# connect to db
mydb = pymysql.connect(
    host="34.89.55.66",
    user="root",
    password="Mintylucky9",
    database="instagram",
    cursorclass=pymysql.cursors.DictCursor
)

mycursor = mydb.cursor()

mycursor.execute(sql)
results = list(mycursor.fetchall())

for result in results:
    if ('instagram_webserver/static/' in result['filename']):
        filename = result['filename'].replace('instagram_webserver/static/', '')

        sql = f'update images_new set filename="{filename}" where id={result["id"]}'
        mycursor.execute(sql)

        mydb.commit()