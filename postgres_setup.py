import psycopg2
from psycopg2 import sql


def create_tables():
    # Подключение к базе данных
    conn = psycopg2.connect(
        host="localhost",
        database="review_analysis",
        user="denisimac27",  # ваше имя пользователя
        password="123456"  # ваш пароль
    )
    
    cursor = conn.cursor()
    
    # Создание таблиц
    tables = [
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            price DECIMAL(10,2)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            region VARCHAR(100)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS reviews (
            review_id SERIAL PRIMARY KEY,
            product_id INT REFERENCES products(product_id),
            user_id INT REFERENCES users(user_id),
            rating INT CHECK (rating >= 1 AND rating <= 5),
            review_text TEXT,
            review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    for table in tables:
        cursor.execute(table)
    
    conn.commit()
    print("Таблицы успешно созданы!")
    
    # Добавим немного тестовых данных
    test_data = [
        "INSERT INTO products (name, category, price) VALUES ('iPhone 14', 'Смартфоны', 799.99)",
        "INSERT INTO products (name, category, price) VALUES ('Samsung Galaxy S23', 'Смартфоны', 899.99)",
        "INSERT INTO users (username, region) VALUES ('alex_ivanov', 'Москва')",
        "INSERT INTO users (username, region) VALUES ('maria_smith', 'Санкт-Петербург')"
    ]
    
    for data in test_data:
        try:
            cursor.execute(data)
        except:
            pass
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()