import psycopg2
from pymongo import MongoClient


# Тест PostgreSQL
# try:
#     conn = psycopg2.connect(
#         host="ваш_хост_elephant",
#         database="ваша_бд",
#         user="ваш_юзер",
#         password="ваш_пароль"
#     )
#     print("✅ PostgreSQL подключен успешно!")
#     conn.close()
# except Exception as e:
#     print(f"❌ PostgreSQL ошибка: {e}")
    
# Тест MongoDB    
try:
    client = MongoClient("mongodb+srv://admin:qwerty123@cluster0.4jhoran.mongodb.net/?retryWrites=true&w=majority")
    client.server_info()
    print("✅ MongoDB подключен успешно!")
except Exception as e:
    print(f"❌ MongoDB ошибка: {e}")