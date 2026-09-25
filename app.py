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

    connection.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            season TEXT NOT NULL,
            age_group TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS team_players (
            team_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            PRIMARY KEY (team_id, member_id),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            FOREIGN KEY (member_id) REFERENCES members(id)
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

def add_sample_team():
    connection = get_db()

    existing_team = connection.execute(
        "SELECT COUNT(*) FROM teams"
    ).fetchone()[0]

    if existing_team == 0:
        connection.execute(
            """
            INSERT INTO teams (name, season, age_group)
            VALUES (?, ?, ?)
            """,
            ("U18 Tigers", "2026", "U18")
        )

        connection.commit()

    connection.close()

def add_sample_players():
    connection = get_db()

    team = connection.execute(
        "SELECT id FROM teams WHERE name = ? AND season = ?",
        ("U18 Tigers", "2026")
    ).fetchone()

    if team:
        members = connection.execute(
            """
            SELECT id FROM members
            WHERE name IN (?, ?)
            ORDER BY id
            LIMIT 2
            """,
            ("John Smith", "Michael Brown")
        ).fetchall()

        for member in members:
            connection.execute(
                """
                INSERT OR IGNORE INTO team_players (team_id, member_id)
                VALUES (?, ?)
                """,
                (team["id"], member["id"])
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

@app.route("/teams/<int:team_id>")
def team_roster(team_id):
    connection = get_db()

    team = connection.execute(
        """
        SELECT id, name, season, age_group
        FROM teams
        WHERE id = ?
        """,
        (team_id,)
    ).fetchone()

    if team is None:
        connection.close()
        return "Team not found", 404

    players = connection.execute(
        """
        SELECT members.id, members.name, members.date_of_birth
        FROM members
        JOIN team_players
            ON members.id = team_players.member_id
        WHERE team_players.team_id = ?
        ORDER BY members.name
        """,
        (team_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "team_roster.html",
        team=team,
        players=players
    )

if __name__ == "__main__":
    init_db()
    add_sample_members()
    add_sample_team()
    add_sample_players()
    app.run(debug=True)