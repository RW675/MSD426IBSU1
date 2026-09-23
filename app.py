import os

from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

from models import db, Member, Registration, Team


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///warrigal_park.db",
)

db.init_app(app)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return "Warrigal Park FC app is running!"


@app.route("/registrations/new", methods=["GET", "POST"])
def new_registration():
    if request.method == "POST":
        name = request.form.get("member_name", "").strip()
        dob_str = request.form.get("date_of_birth")
        season = request.form.get("season", "").strip()
        age_group = request.form.get("age_group", "").strip()

        try:
            if not all((name, dob_str, season, age_group)):
                raise ValueError

            dob = datetime.strptime(
                dob_str,
                "%Y-%m-%d",
            ).date()

        except (TypeError, ValueError):
            return render_template(
                "registration_form.html",
                error=(
                    "Please provide a valid name, date of birth, "
                    "season, and age group."
                ),
            ), 400

        member = Member(
            name=name,
            date_of_birth=dob,
        )

        registration = Registration(
            member=member,
            season=season,
            age_group=age_group,
        )

        db.session.add(registration)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("registration_form.html")


@app.route("/registrations/history")
def registration_history():
    members = Member.query.order_by(Member.name.asc()).all()

    selected_member_id = request.args.get("member_id", type=int)

    registrations = []

    if selected_member_id:
        registrations = (
            Registration.query
            .filter_by(member_id=selected_member_id)
            .order_by(Registration.created_at.desc())
            .all()
        )

    return render_template(
        "registration_history.html",
        members=members,
        registrations=registrations,
        selected_member_id=selected_member_id,
    )

@app.route("/teams/new", methods=["GET", "POST"])
def new_team():
    if request.method == "POST":
        name = request.form.get("team_name", "").strip()
        season = request.form.get("season", "").strip()
        age_group = request.form.get("age_group", "").strip()

        if not all((name, season, age_group)):
            return render_template(
                "team_form.html",
                error="Team name, season, and age group are required.",
            ), 400

        team = Team(
            name=name,
            season=season,
            age_group=age_group,
        )

        db.session.add(team)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("team_form.html")

if __name__ == "__main__":
    app.run()
