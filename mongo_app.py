import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

try:
    client = MongoClient("ваша_строка_mongodb")
    client.server_info()
    print("✅ MongoDB подключен успешно!")
except Exception as e:
    print(f"❌ MongoDB ошибка: {e}")

# Настройка страницы
st.set_page_config(page_title="Анализ отзывов (MongoDB)", layout="wide")
st.title("📊 Анализ отзывов - MongoDB версия")

# Функция для подключения к MongoDB
@st.cache_resource
def get_mongo_client():
    # connection_string = "mongodb+srv://admin:qwerty123@cluster0.4jhoran.mongodb.net/"
    return MongoClient(st.secrets["MONGO_URI"])

client = get_mongo_client()
db = client["review_analysis_nosql"]
products_col = db["products"]
reviews_col = db["reviews"]

# Вкладки приложения
tab1, tab2, tab3 = st.tabs(["📝 Добавить данные", "🔍 Просмотр отзывов", "📈 Аналитика"])

with tab1:
    st.header("Добавить новые данные (MongoDB)")
    
    data_type = st.selectbox("Что вы хотите добавить?", 
                           ["Продукт", "Отзыв"])
    
    if data_type == "Продукт":
        with st.form("product_form_mongo"):
            product_id = st.text_input("ID продукта")
            name = st.text_input("Название продукта")
            category = st.text_input("Категория")
            price = st.number_input("Цена", min_value=0.0, step=0.01)
            
            if st.form_submit_button("Добавить продукт"):
                product_data = {
                    "_id": product_id,
                    "name": name,
                    "category": category,
                    "price": price,
                    "created_at": datetime.now()
                }
                
                try:
                    products_col.insert_one(product_data)
                    st.success("Продукт успешно добавлен в MongoDB!")
                except Exception as e:
                    st.error(f"Ошибка: {e}")
    
    elif data_type == "Отзыв":
        # Получаем список продуктов для выбора
        product_list = list(products_col.find({}, {"_id": 1, "name": 1}))
        product_options = {p["_id"]: p["name"] for p in product_list}
        
        with st.form("review_form_mongo"):
            col1, col2 = st.columns(2)
            
            with col1:
                review_id = st.text_input("ID отзыва")
                selected_product = st.selectbox(
                    "Выберите продукт",
                    options=list(product_options.keys()),
                    format_func=lambda x: product_options[x]
                )
                rating = st.slider("Рейтинг", 1, 5, 5)
            
            with col2:
                username = st.text_input("Имя пользователя")
                user_region = st.text_input("Регион пользователя")
            
            review_text = st.text_area("Текст отзыва")
            
            # Дополнительные поля для демонстрации гибкости MongoDB
            st.subheader("Дополнительные данные (опционально)")
            tags = st.text_input("Теги (через запятую)", "")
            has_media = st.checkbox("Есть медиа-файлы?")
            
            if st.form_submit_button("Добавить отзыв"):
                # Собираем данные в один документ
                review_data = {
                    "review_id": review_id,
                    "product": {
                        "product_id": selected_product,
                        "name": product_options[selected_product]
                    },
                    "user": {
                        "user_id": f"u{review_id}",
                        "username": username,
                        "region": user_region
                    },
                    "rating": rating,
                    "review_text": review_text,
                    "review_date": datetime.now(),
                    "tags": [tag.strip() for tag in tags.split(",")] if tags else [],
                    "metadata": {
                        "chars_count": len(review_text),
                        "processed": False
                    }
                }
                
                # Добавляем медиа, если есть
                if has_media:
                    review_data["media"] = [
                        {"type": "image", "url": "https://example.com/temp.jpg"}
                    ]
                
                try:
                    reviews_col.insert_one(review_data)
                    st.success("Отзыв успешно добавлен в MongoDB!")
                    st.json(review_data)  # Показываем, как выглядит документ
                except Exception as e:
                    st.error(f"Ошибка: {e}")

with tab2:
    st.header("Просмотр отзывов (MongoDB)")
    
    # Получаем все отзывы
    all_reviews = list(reviews_col.find({}))
    
    if all_reviews:
        # Преобразуем в DataFrame для отображения
        review_list = []
        for review in all_reviews:
            review_list.append({
                "ID": review.get("review_id"),
                "Продукт": review.get("product", {}).get("name", ""),
                "Пользователь": review.get("user", {}).get("username", ""),
                "Рейтинг": review.get("rating"),
                "Текст": review.get("review_text", "")[:100] + "...",  # Показываем только начало
                "Дата": review.get("review_date"),
                "Теги": ", ".join(review.get("tags", [])),
                "Медиа": len(review.get("media", []))
            })
        
        reviews_df = pd.DataFrame(review_list)
        st.dataframe(reviews_df)
        
        # Фильтрация
        st.subheader("Фильтры")
        col1, col2 = st.columns(2)
        
        with col1:
            min_rating = st.slider("Минимальный рейтинг", 1, 5, 1, key="mongo_filter")
        
        with col2:
            # Динамические теги из существующих отзывов
            all_tags = set()
            for review in all_reviews:
                all_tags.update(review.get("tags", []))
            selected_tag = st.selectbox("Фильтр по тегу", ["Все"] + list(all_tags))
        
        # Применяем фильтры
        filtered_reviews = [r for r in all_reviews if r.get("rating", 0) >= min_rating]
        
        if selected_tag != "Все":
            filtered_reviews = [r for r in filtered_reviews 
                              if selected_tag in r.get("tags", [])]
        
        st.write(f"Найдено отзывов: {len(filtered_reviews)}")
        
        # Показать детали выбранного отзыва
        if filtered_reviews:
            selected_idx = st.selectbox(
                "Выберите отзыв для детального просмотра",
                range(len(filtered_reviews)),
                format_func=lambda i: f"{filtered_reviews[i].get('product',{}).get('name','')} - {filtered_reviews[i].get('review_id','')}"
            )
            
            selected_review = filtered_reviews[selected_idx]
            st.subheader("Детали отзыва")
            st.json(selected_review)  # Показываем весь документ JSON
            
    else:
        st.info("Пока нет отзывов в MongoDB.")

with tab3:
    st.header("Аналитика (MongoDB)")
    
    # 1. Агрегация: средний рейтинг по продуктам
    st.subheader("Анализ через Aggregation Pipeline")
    
    pipeline = [
        {
            "$group": {
                "_id": "$product.name",
                "avg_rating": {"$avg": "$rating"},
                "total_reviews": {"$sum": 1},
                "min_rating": {"$min": "$rating"},
                "max_rating": {"$max": "$rating"}
            }
        },
        {"$sort": {"avg_rating": -1}}
    ]
    
    result = list(reviews_col.aggregate(pipeline))
    
    if result:
        # Преобразуем результат в DataFrame
        analytics_df = pd.DataFrame([
            {
                "Продукт": item["_id"],
                "Средний рейтинг": round(item["avg_rating"], 2),
                "Всего отзывов": item["total_reviews"],
                "Минимальный": item["min_rating"],
                "Максимальный": item["max_rating"]
            }
            for item in result
        ])
        
        st.dataframe(analytics_df)
        
        # Визуализация
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # График 1: Средний рейтинг
        ax1.bar(analytics_df["Продукт"], analytics_df["Средний рейтинг"])
        ax1.set_title("Средний рейтинг по продуктам")
        ax1.set_ylabel("Рейтинг")
        ax1.tick_params(axis='x', rotation=45)
        
        # График 2: Количество отзывов
        ax2.bar(analytics_df["Продукт"], analytics_df["Всего отзывов"])
        ax2.set_title("Количество отзывов")
        ax2.set_ylabel("Количество")
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        st.pyplot(fig)
    
    # 2. Распределение тегов
    st.subheader("Популярные теги")
    
    # Используем оператор $unwind для работы с массивами
    tag_pipeline = [
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    
    tag_result = list(reviews_col.aggregate(tag_pipeline))
    
    if tag_result:
        tags_df = pd.DataFrame([
            {"Тег": item["_id"], "Количество": item["count"]}
            for item in tag_result
        ])
        
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(tags_df)
        with col2:
            fig2, ax2 = plt.subplots()
            ax2.pie(tags_df["Количество"], labels=tags_df["Тег"], autopct='%1.1f%%')
            ax2.set_title("Топ-10 тегов")
            st.pyplot(fig2)
    
    # 3. Динамические запросы
    st.subheader("Гибкие запросы MongoDB")
    
    query_type = st.selectbox("Выберите тип запроса", 
                            ["Отзывы с медиа", "Отзывы с длинным текстом", "Поиск по слову"])
    
    if query_type == "Отзывы с медиа":
        # Находим отзывы, у которых есть медиа
        media_reviews = list(reviews_col.find({"media": {"$exists": True, "$ne": []}}))
        st.write(f"Найдено отзывов с медиа: {len(media_reviews)}")
        
    elif query_type == "Отзывы с длинным текстом":
        # Используем $expr для вычислений в запросе
        long_reviews = list(reviews_col.find({
            "$expr": {"$gt": [{"$strLenCP": "$review_text"}, 100]}
        }))
        st.write(f"Найдено длинных отзывов (>100 символов): {len(long_reviews)}")
        
    elif query_type == "Поиск по слову":
        search_word = st.text_input("Введите слово для поиска")
        if search_word:
            # Поиск по тексту отзыва
            search_results = list(reviews_col.find({
                "review_text": {"$regex": search_word, "$options": "i"}
            }))
            st.write(f"Найдено отзывов со словом '{search_word}': {len(search_results)}")
            for review in search_results:
                st.write(f"- {review['product']['name']}: {review['review_text'][:200]}...")