from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

DATABASE = "club.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

# Add sample members if the table is empty
def add_sample_members():
    connection = get_db()

    existing_members = connection.execute(
        "SELECT COUNT(*) FROM members"
    ).fetchone()[0]

    if existing_members == 0:
        connection.executemany(
            "INSERT INTO members (name, date_of_birth) VALUES (?, ?)",
            [
                ("John Smith", "2008-05-14"),
                ("John Smith", "2010-09-22"),
                ("Michael Brown", "2007-03-18"),
                ("Sarah Williams", "2009-11-05")
            ]
        )

        connection.commit()

    connection.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/members")
def members():
    search = request.args.get("search", "").strip()

    connection = get_db()

    if search:
        member_list = connection.execute(
            """
            SELECT id, name, date_of_birth
            FROM members
            WHERE name LIKE ?
            ORDER BY name
            """,
            (f"%{search}%",)
        ).fetchall()
    else:
        member_list = connection.execute(
            """
            SELECT id, name, date_of_birth
            FROM members
            ORDER BY name
            """
        ).fetchall()

    connection.close()

    return render_template(
        "members.html",
        members=member_list,
        search=search
    )


if __name__ == "__main__":
    init_db()
    add_sample_members()
    app.run(debug=True)