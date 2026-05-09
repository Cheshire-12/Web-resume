from unicodedata import name

from flask import Flask, flash, get_flashed_messages, render_template, request, make_response, redirect, url_for
import json
from json import dumps, loads

# Это callable WSGI-приложение
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Необходимо для использования flash()

@app.before_request
def log_path():
    print(f"Request path: {request.path}")
    
@app.after_request
def add_custom_header(response):
    response.headers["X-Custom-Header"] = "value"
    return response

# Вспомогательная функция для проверки пароля
def validate_password(password: str) -> dict:
    errors = {}
    if len(password) < 4:
        errors["password"] = "Пароль должен быть не менее 4 символов"
    return errors

@app.get("/")
def index():
    return render_template("index.html")  # Возвращает результат рендеринга шаблона

# вместо пути указываем код ошибки
@app.errorhandler(404)
def not_found(error):
    return "Такой страницы нет!", 404

@app.route("/courses/<int:id_course>/")
def courses_show(id_course):
    return f"Course id: {id_course}"

@app.route("/courses/layout/")
def courses_layout():
    return render_template("/courses/layout.html")


def load_users() -> list[dict]:
    """Вспомогательная функция для чтения данных"""
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            # Если в файле один словарь, превращаем его в список из одного элемента
            if isinstance(data, dict):
                return [data]
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@app.route("/users/index/")
def get_user():
    users_data = load_users()
    return render_template("/users/index.html", users=users_data)

@app.route("/users")
def search_user():
    query = request.args.get("query", "").strip()
    users_data = load_users()
    
    if query:
        # Фильтруем по полю "name". Используем .lower() для поиска без учета регистра
        filtered_users = [
            user for user in users_data 
            if query.lower() in user.get("name", "").lower()
        ]
        return render_template("/users/index.html", users=filtered_users, search=query)
    
    return render_template("/users/index.html", users=users_data, search="")

@app.route("/users/new/")
def user_new():
    user = {
        "id": "",
        "name": "",
        "email": "",
        "password": "",
        "passwordConfirmation": ""
    }
    errors = {}
    return render_template("/users/new.html", user=user, errors=errors)

@app.post("/users")
def users_post():
    # 1. Читаем текущие данные
    users_data = load_users()

    app.logger.debug("Creating a new user")
    
    # 2. Получаем данные из формы
    user = request.form.to_dict()
    
    # 3. Генерируем ID на основе длины списка
    user["id"] = str(len(users_data) + 1)
    errors = validate_password(user.get("password", ""))
    if errors:
        return render_template("/users/new.html", user=user, errors=errors), 422
    # 4. ДОБАВЛЯЕМ нового пользователя в список
    
    users_data.append(user)

    # 5. Сохраняем ВЕСЬ список обратно в файл
    with open("data.json", "w", encoding="utf-8") as f:
        # Сериализуем весь список users_data, а не одиночного user
        json.dump(users_data, f, ensure_ascii=False, indent=4)
    
    flash("Пользователь успешно создан!", "success")
    return redirect(url_for("get_user"), code=302)