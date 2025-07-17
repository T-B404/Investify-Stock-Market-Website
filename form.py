from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint,jsonify,session
from flask_cors import CORS
import bcrypt

form=Blueprint('form',__name__)
CORS(form)
#form.secret_key = "192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf"  # Required for flash messages

import sqlite3
import re
# Validation Regex
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{3,15}$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")

# Initialize the database
def get_db_connection():
    return sqlite3.connect("users.db", check_same_thread=False)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()  # Run once to create the database

# Registration route
@form.route("/", methods=["GET"])
def index():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")  # Only for registration
        password = request.form.get("password")

        if not USERNAME_REGEX.match(username):
            flash("Invalid Username: 3-15 chars (letters, numbers, _)", "danger")
        elif email and not EMAIL_REGEX.match(email):  # Validate email for registration
            flash("Invalid Email Format!", "error")
        elif not PASSWORD_REGEX.match(password):
            flash("Invalid Password: Min 8 chars, 1 uppercase, 1 number, 1 special", "danger")
        else:
            try:
                conn = sqlite3.connect("users.db")
                c = conn.cursor()
                c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                          (username, email, password))
                conn.commit()
                conn.close()
                flash("Registration Successful! Please Login.", "success")
                return redirect(url_for("form.index"))
            except sqlite3.IntegrityError:
                flash("Username or Email already exists!", "danger")

    return render_template("form.html",show_form="register")

@form.route('/form/')
def form_page():
    return render_template('form.html') 

# Login route
@form.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    print(f"Registration attempt: {username}, {email}, {password}")

    if not username:
        return jsonify({"message": "Username is required!"}), 400
    if not email:
        return jsonify({"message": "Email is required!"}), 400
    if not password:
        return jsonify({"message": "Password is required!"}), 400

    if not USERNAME_REGEX.match(username):
        return jsonify({"message": "Invalid Username"}), 400
    elif not EMAIL_REGEX.match(email):
        return jsonify({"message": "Invalid Email Format!"}), 400
    elif not PASSWORD_REGEX.match(password):
        return jsonify({"message": "Invalid Password Format!"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                  (username, email, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"message": "Registration Successful!", "redirect": "/form/login"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"message": "Username or Email already exists!"}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    

# Login Route
@form.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # Show login form
        return render_template("form.html", show_form="login")
    
    # Handle POST request
    if request.is_json:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[0].encode('utf-8')):
        session['username'] = username
        # Redirect to dashboard if using HTML forms
        return jsonify({
                "message": "Login Successful! Redirecting...",
                "redirect": "/dashboard"
            }), 200  # Make sure you have a dashboard route
    else:
        # Show login form with error message
        return render_template("form.html", 
                             show_form="login",
                             error="Invalid credentials!")

@form.route("/form/logout")
def logout():
    session.pop('username', None) 
    return jsonify({"message": "Logged out successfully!"}), 200