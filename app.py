from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"

# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect("crowd.db")
    conn.row_factory = sqlite3.Row
    return conn

# LOGIN
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            session["role"] = "admin"
        else:
            session["role"] = "guest"

        return redirect("/dashboard")

    return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    conn = get_db()
    temples = conn.execute("SELECT * FROM temples").fetchall()
    conn.close()

    return render_template("dashboard.html", temples=temples)


# ADD TEMPLE
@app.route("/add", methods=["POST"])
def add():

    name = request.form["name"]
    location = request.form["location"]
    crowd = request.form["crowd"]

    conn = get_db()

    conn.execute(
        "INSERT INTO temples (name,location,crowd) VALUES (?,?,?)",
        (name,location,crowd)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# DELETE TEMPLE
@app.route("/delete/<int:id>")
def delete(id):

    conn = get_db()

    conn.execute("DELETE FROM temples WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# EDIT TEMPLE
@app.route("/edit/<int:id>")
def edit(id):

    conn = get_db()

    temple = conn.execute(
        "SELECT * FROM temples WHERE id=?", (id,)
    ).fetchone()

    conn.close()

    return render_template("edit.html", temple=temple)


# UPDATE TEMPLE
@app.route("/update/<int:id>", methods=["POST"])
def update(id):

    name = request.form["name"]
    location = request.form["location"]
    crowd = request.form["crowd"]

    conn = get_db()

    conn.execute(
        "UPDATE temples SET name=?,location=?,crowd=? WHERE id=?",
        (name,location,crowd,id)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# SEARCH TEMPLE
@app.route("/search")
def search():

    q = request.args.get("q")

    conn = get_db()

    temples = conn.execute(
        "SELECT name FROM temples WHERE name LIKE ?",
        ("%"+q+"%",)
    ).fetchall()

    conn.close()

    suggestions = [t["name"] for t in temples]

    return jsonify({"suggestions":suggestions})


# AUTO TEMPLE RECOMMENDATION
@app.route("/recommend")
def recommend():

    location = request.args.get("location").lower()

    temples = {

        "chennai":[
            {"name":"Kapaleeshwarar Temple","location":"Chennai"},
            {"name":"Ashtalakshmi Temple","location":"Chennai"}
        ],

        "tirupati":[
            {"name":"Tirupati Balaji Temple","location":"Tirupati"}
        ],

        "madurai":[
            {"name":"Meenakshi Amman Temple","location":"Madurai"}
        ],

        "varanasi":[
            {"name":"Kashi Vishwanath Temple","location":"Varanasi"}
        ],

        "kedarnath":[
            {"name":"Kedarnath Temple","location":"Uttarakhand"}
        ],

        "rameshwaram":[
            {"name":"Ramanathaswamy Temple","location":"Rameshwaram"}
        ]
    }

    result = temples.get(location, [])

    return jsonify({"temples":result})


if __name__ == "__main__":
    app.run(debug=True)