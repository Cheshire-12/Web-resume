import os
import psycopg2
from flask import (
    Flask, 
    flash, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    session
)
from user_repo import UsersRepository
from dotenv import load_dotenv
app = Flask(__name__)

load_dotenv()

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# Соединение с БД
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)

repo = UsersRepository(conn)

def validate_password(password: str) -> dict:
    errors = {}
    if len(password) < 4:
        errors["password"] = "Пароль должен быть не менее 4 символов"
    return errors

@app.context_processor
def inject_user():
    user_id = session.get("user_id")
    current_user = repo.find(user_id)
    return dict(current_user=current_user)

@app.get("/")
def index():
    return render_template("index.html")

@app.route("/users/index/")
def get_user():
    users_data = repo.get_content()
    return render_template("/users/index.html", users=users_data)

@app.route("/users")
def search_user():
    query = request.args.get("query", "").strip()
    if query:
        users_data = repo.search(query)
    else:
        users_data = repo.get_content()
    return render_template("/users/index.html", users=users_data, search=query)

@app.route("/users/new/")
def user_new():
    return render_template("/users/new.html", user={}, errors={})

@app.post("/users")
def users_post():
    user_data = request.form.to_dict()
    errors = validate_password(user_data.get("password", ""))
    
    if errors:
        return render_template("/users/new.html", user=user_data, errors=errors), 422

    repo.create(user_data)
    flash("Пользователь успешно создан!", "success")
    return redirect(url_for("get_user"))

@app.route("/users/<int:id>/edit/")
def user_edit(id):
    user = repo.find(id)
    if not user:
        return "Пользователь не найден", 404
    # Превращаем user_name в name для удобства шаблона, если нужно
    user['name'] = user['user_name'] 
    return render_template("/users/edit.html", user=user, errors={})

@app.post("/users/<int:id>/update/")
def user_update(id):
    updated_data = request.form.to_dict()
    errors = validate_password(updated_data.get("password", ""))
    
    if errors:
        updated_data["id"] = id
        return render_template("/users/edit.html", user=updated_data, errors=errors), 422

    repo.update(id, updated_data)
    flash("Пользователь успешно обновлен!", "success")
    return redirect(url_for("get_user"))

@app.post("/users/<int:id>/delete")
def user_delete(id):
    repo.delete(id)
    if session.get("user_id") == id:
        session.pop("user_id", None)
    flash("Пользователь удален", "success")
    return redirect(url_for("get_user"))

@app.route("/users/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        user = repo.find_by_email(email)
        if user and user["password"] == password:
            session["user_id"] = user["id"]
            flash("Вы успешно вошли!", "success")
            return redirect(url_for("index"))
        
        flash("Неверный email или пароль", "danger")
    return render_template("/users/login.html")

@app.post("/users/logout")
def logout():
    session.clear()
    flash("Вы успешно вышли!", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)