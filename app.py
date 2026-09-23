import os
from datetime import date, datetime

from flask import Flask, redirect, render_template, request, url_for

from models import Guardian, Member, Registration, Team, db


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        app.config.get("SQLALCHEMY_DATABASE_URI", "sqlite:///warrigal_park.db"),
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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

            existing_member = Member.query.filter_by(
                name=name,
                date_of_birth=dob,
            ).first()

            if (
                existing_member is not None
                and self_is_junior(dob)
                and existing_member.guardian_id is None
            ):
                return render_template(
                    "registration_form.html",
                    error=(
                        "Junior registrations require a linked guardian record before "
                        "the registration can be completed."
                    ),
                ), 400

            member = existing_member or Member(
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

    @app.route("/guardians/new", methods=["GET", "POST"])
    def new_guardian():
        if request.method == "POST":
            name = request.form.get("guardian_name", "").strip()
            mobile = request.form.get("mobile", "").strip()
            email = request.form.get("email", "").strip()

            if not name:
                return render_template(
                    "guardian_form.html",
                    error="Guardian name is required.",
                ), 400

            guardian = Guardian(name=name, mobile=mobile or None, email=email or None)
            db.session.add(guardian)
            db.session.commit()

            return redirect(url_for("home"))

        return render_template("guardian_form.html")

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

    @app.route("/teams/<int:team_id>/players/add", methods=["GET", "POST"])
    def add_player_to_team(team_id):
        team = db.session.get(Team, team_id)
        if team is None:
            return "Team not found", 404

        registrations = (
            Registration.query
            .filter_by(
                season=team.season,
                age_group=team.age_group,
                team_id=None,
            )
            .join(Member)
            .order_by(Member.name.asc())
            .all()
        )

        if request.method == "POST":
            registration_id = request.form.get(
                "registration_id",
                type=int,
            )

            registration = db.session.get(
                Registration,
                registration_id,
            )

            if registration is None:
                return render_template(
                    "add_player_to_team.html",
                    team=team,
                    registrations=registrations,
                    error="Please select a valid registered player.",
                ), 400

            if registration.team_id is not None:
                return render_template(
                    "add_player_to_team.html",
                    team=team,
                    registrations=registrations,
                    error="This player is already assigned to a team.",
                ), 400

            if registration.season != team.season:
                return render_template(
                    "add_player_to_team.html",
                    team=team,
                    registrations=registrations,
                    error="The player's registration season does not match the team.",
                ), 400

            if registration.age_group != team.age_group:
                return render_template(
                    "add_player_to_team.html",
                    team=team,
                    registrations=registrations,
                    error="The player's age group does not match the team.",
                ), 400

            registration.team_id = team.id
            db.session.commit()

            return redirect(
                url_for(
                    "add_player_to_team",
                    team_id=team.id,
                )
            )

        return render_template(
            "add_player_to_team.html",
            team=team,
            registrations=registrations,
        )

    return app


def self_is_junior(dob):
    today = date.today()
    return (today.year - dob.year) - ((today.month, today.day) < (dob.month, dob.day)) < 18


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))

