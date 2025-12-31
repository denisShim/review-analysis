from pymongo import MongoClient
from datetime import datetime

def setup_mongodb():
    # Замените эту строку на свою из MongoDB Atlas
    # Формат: mongodb+srv://username:password@cluster.mongodb.net/
    connection_string = "mongodb+srv://admin:qwerty123@cluster0.4jhoran.mongodb.net/"
    
    client = MongoClient(connection_string)
    
    # Создаем/получаем базу данных
    db = client["review_analysis_nosql"]
    
    # Создаем коллекции
    products = db["products"]
    reviews = db["reviews"]
    
    # Очищаем коллекции (опционально)
    products.delete_many({})
    reviews.delete_many({})
    
    # Добавляем тестовые данные
    # 1. Продукты
    product1 = {
        "_id": "p001",
        "name": "iPhone 14",
        "category": "Смартфоны",
        "price": 799.99,
        "release_year": 2022
    }
    
    product2 = {
        "_id": "p002",
        "name": "Samsung Galaxy S23",
        "category": "Смартфоны",
        "price": 899.99,
        "release_year": 2023
    }
    
    products.insert_many([product1, product2])
    
    # 2. Отзывы (обратите внимание на структуру!)
    review1 = {
        "review_id": "r001",
        "product": {
            "product_id": "p001",
            "name": "iPhone 14"
        },
        "user": {
            "user_id": "u001",
            "username": "alex_ivanov",
            "region": "Москва"
        },
        "rating": 5,
        "review_text": "Отличный телефон! Камера просто супер.",
        "review_date": datetime.now(),
        "media": [
            {"type": "image", "url": "https://example.com/photo1.jpg"},
            {"type": "image", "url": "https://example.com/photo2.jpg"}
        ],
        "tags": ["позитивный", "камера", "качество"],
        "helpful_count": 24
    }
    
    review2 = {
        "review_id": "r002",
        "product": {
            "product_id": "p002",
            "name": "Samsung Galaxy S23"
        },
        "user": {
            "user_id": "u002",
            "username": "maria_smith",
            "region": "Санкт-Петербург"
        },
        "rating": 4,
        "review_text": "Хороший телефон, но батарея держит недолго.",
        "review_date": datetime.now(),
        "media": [],
        "tags": ["нейтральный", "батарея", "производительность"],
        "helpful_count": 12
    }
    
    reviews.insert_many([review1, review2])
    
    print("Данные успешно добавлены в MongoDB!")
    print(f"Продуктов: {products.count_documents({})}")
    print(f"Отзывов: {reviews.count_documents({})}")
    
    client.close()

if __name__ == "__main__":
    setup_mongodb()