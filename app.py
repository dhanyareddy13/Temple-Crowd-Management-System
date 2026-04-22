from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DATABASE = "temples.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS temples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            crowd INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_db()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            return redirect(url_for("dashboard", role="admin"))
        else:
            return redirect(url_for("dashboard", role="guest"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    role = request.args.get("role", "guest")

    conn = get_db_connection()
    temples = conn.execute("SELECT * FROM temples").fetchall()
    conn.close()

    return render_template("dashboard.html", temples=temples, role=role)


@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    location = request.form["location"]
    crowd = request.form["crowd"]

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO temples (name, location, crowd) VALUES (?, ?, ?)",
        (name, location, crowd),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard", role="admin"))


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form["name"]
        location = request.form["location"]
        crowd = request.form["crowd"]

        conn.execute(
            "UPDATE temples SET name=?, location=?, crowd=? WHERE id=?",
            (name, location, crowd, id),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard", role="admin"))

    temple = conn.execute("SELECT * FROM temples WHERE id=?", (id,)).fetchone()
    conn.close()

    return render_template("edit.html", temple=temple)


@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM temples WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard", role="admin"))


if __name__ == "_main_":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
