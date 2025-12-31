import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

engine = create_engine('postgresql://denisimac27:123456@localhost:5432/review_analysis')

try:
    conn = psycopg2.connect(
        host="ваш_хост_elephant",
        database="ваша_бд",
        user="ваш_юзер",
        password="ваш_пароль"
    )
    print("✅ PostgreSQL подключен успешно!")
    conn.close()
except Exception as e:
    print(f"❌ PostgreSQL ошибка: {e}")

# Настройка страницы
st.set_page_config(page_title="Анализ отзывов (PostgreSQL)", layout="wide")
st.title("📊 Анализ отзывов - PostgreSQL версия")

# Функция для подключения к базе данных
def get_connection():
    return psycopg2.connect(
        host=st.secrets["POSTGRES_HOST"],
        database=st.secrets["POSTGRES_DB"],
        user=st.secrets["POSTGRES_USER"],
        password=st.secrets["POSTGRES_PASSWORD"],
        port=5432
    )

# Вкладка 1: Добавление данных
tab1, tab2, tab3 = st.tabs(["📝 Добавить данные", "🔍 Просмотр отзывов", "📈 Аналитика"])

with tab1:
    st.header("Добавить новые данные")
    
    # Выбор типа данных для добавления
    data_type = st.selectbox("Что вы хотите добавить?", 
                           ["Продукт", "Пользователь", "Отзыв"])
    
    if data_type == "Продукт":
        with st.form("product_form"):
            name = st.text_input("Название продукта")
            category = st.text_input("Категория")
            price = st.number_input("Цена", min_value=0.0, step=0.01)
            
            if st.form_submit_button("Добавить продукт"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO products (name, category, price) VALUES (%s, %s, %s)",
                    (name, category, price)
                )
                conn.commit()
                conn.close()
                st.success("Продукт успешно добавлен!")
    
    elif data_type == "Пользователь":
        with st.form("user_form"):
            username = st.text_input("Имя пользователя")
            region = st.text_input("Регион")
            
            if st.form_submit_button("Добавить пользователя"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, region) VALUES (%s, %s)",
                    (username, region)
                )
                conn.commit()
                conn.close()
                st.success("Пользователь успешно добавлен!")
    
    elif data_type == "Отзыв":
        conn = get_connection()
        # Получаем списки продуктов и пользователей для выбора
        products = pd.read_sql("SELECT product_id, name FROM products", engine)
        users = pd.read_sql("SELECT user_id, username FROM users", engine)
        conn.close()
        
        with st.form("review_form"):
            product_id = st.selectbox(
                "Выберите продукт",
                options=products['product_id'],
                format_func=lambda x: products[products['product_id']==x]['name'].values[0]
            )
            user_id = st.selectbox(
                "Выберите пользователя",
                options=users['user_id'],
                format_func=lambda x: users[users['user_id']==x]['username'].values[0]
            )
            rating = st.slider("Рейтинг", 1, 5, 5)
            review_text = st.text_area("Текст отзыва")
            
            if st.form_submit_button("Добавить отзыв"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO reviews (product_id, user_id, rating, review_text) 
                       VALUES (%s, %s, %s, %s)""",
                    (product_id, user_id, rating, review_text)
                )
                conn.commit()
                conn.close()
                st.success("Отзыв успешно добавлен!")

with tab2:
    st.header("Просмотр отзывов")
    
    conn = get_connection()
    
    # Получаем все отзывы с JOIN
    query = """
    SELECT r.review_id, p.name as product_name, u.username, r.rating, 
           r.review_text, r.review_date
    FROM reviews r
    JOIN products p ON r.product_id = p.product_id
    JOIN users u ON r.user_id = u.user_id
    ORDER BY r.review_date DESC
    """
    
    reviews_df = pd.read_sql(query, engine)
    conn.close()
    
    if not reviews_df.empty:
        st.dataframe(reviews_df)
        
        # Фильтрация
        st.subheader("Фильтры")
        col1, col2 = st.columns(2)
        with col1:
            min_rating = st.slider("Минимальный рейтинг", 1, 5, 1)
        with col2:
            selected_product = st.selectbox(
                "Фильтр по продукту",
                ["Все"] + list(reviews_df['product_name'].unique())
            )
        
        filtered_df = reviews_df[reviews_df['rating'] >= min_rating]
        if selected_product != "Все":
            filtered_df = filtered_df[filtered_df['product_name'] == selected_product]
        
        st.write(f"Найдено отзывов: {len(filtered_df)}")
        st.dataframe(filtered_df)
    else:
        st.info("Пока нет отзывов. Добавьте первый отзыв во вкладке 'Добавить данные'.")

with tab3:
    st.header("Аналитика отзывов")
    
    conn = get_connection()
    
    # 1. Средний рейтинг по продуктам
    st.subheader("Средний рейтинг по продуктам")
    avg_query = """
    SELECT p.name, AVG(r.rating) as avg_rating, COUNT(r.review_id) as review_count
    FROM products p
    LEFT JOIN reviews r ON p.product_id = r.product_id
    GROUP BY p.product_id, p.name
    HAVING COUNT(r.review_id) > 0
    """
    
    avg_df = pd.read_sql(avg_query, engine)
    
    if not avg_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(avg_df)
        with col2:
            fig, ax = plt.subplots()
            ax.bar(avg_df['name'], avg_df['avg_rating'])
            ax.set_ylabel('Средний рейтинг')
            ax.set_title('Рейтинг продуктов')
            plt.xticks(rotation=45)
            st.pyplot(fig)
    
    # 2. Распределение оценок
    st.subheader("Распределение оценок")
    dist_query = """
    SELECT rating, COUNT(*) as count
    FROM reviews
    GROUP BY rating
    ORDER BY rating
    """
    
    dist_df = pd.read_sql(dist_query, engine)
    
    if not dist_df.empty:
        fig2, ax2 = plt.subplots()
        ax2.pie(dist_df['count'], labels=dist_df['rating'], autopct='%1.1f%%')
        ax2.set_title('Распределение оценок')
        st.pyplot(fig2)
    
    conn.close()