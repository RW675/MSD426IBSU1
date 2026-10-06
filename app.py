import os
from datetime import date, datetime

from flask import Flask, redirect, render_template, request, url_for
from sqlalchemy import or_

from models import Guardian, Member, Registration, Team, db


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL",
        app.config.get(
            "SQLALCHEMY_DATABASE_URI",
            "sqlite:///warrigal_park.db",
        ),
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/members")
    def members():
        search = request.args.get("search", "").strip()

        query = Member.query

        if search:
            query = query.filter(
                Member.name.ilike(f"%{search}%")
            )

        member_list = (
            query
            .order_by(Member.name.asc())
            .all()
        )

        return render_template(
            "members.html",
            members=member_list,
            search=search,
        )

    @app.route("/registrations/new", methods=["GET", "POST"])
    def new_registration():
        def render_form(error=None, status=200):
            guardians = (
                Guardian.query
                .filter_by(is_active=True)
                .order_by(Guardian.name.asc())
                .all()
            )

            return render_template(
                "registration_form.html",
                error=error,
                guardians=guardians,
            ), status

        if request.method == "POST":
            name = request.form.get(
                "member_name",
                "",
            ).strip()

            dob_str = request.form.get("date_of_birth")

            season = request.form.get(
                "season",
                "",
            ).strip()

            age_group = request.form.get(
                "age_group",
                "",
            ).strip()

            guardian_id = request.form.get(
                "guardian_id",
                type=int,
            )

            try:
                if not all(
                    (
                        name,
                        dob_str,
                        season,
                        age_group,
                    )
                ):
                    raise ValueError

                dob = datetime.strptime(
                    dob_str,
                    "%Y-%m-%d",
                ).date()

            except (TypeError, ValueError):
                return render_form(
                    error=(
                        "Please provide a valid name, date of birth, "
                        "season, and age group."
                    ),
                    status=400,
                )

            existing_member = Member.query.filter_by(
                name=name,
                date_of_birth=dob,
            ).first()

            selected_guardian = None

            if guardian_id is not None:
                selected_guardian = db.session.get(
                    Guardian,
                    guardian_id,
                )

                if selected_guardian is None:
                    return render_form(
                        error=(
                            "The selected guardian does not exist. "
                            "Please select an existing guardian record."
                        ),
                        status=400,
                    )

                if not selected_guardian.is_active:
                    return render_form(
                        error=(
                            "Please select a valid active guardian record."
                        ),
                        status=400,
                    )

            if self_is_junior(dob):
                already_linked = (
                    existing_member is not None
                    and existing_member.guardian_id is not None
                )

                if (
                    selected_guardian is None
                    and not already_linked
                ):
                    return render_form(
                        error=(
                            "Junior registrations require a linked guardian "
                            "record before the registration can be completed. "
                            "Please select an existing guardian."
                        ),
                        status=400,
                    )

            member = existing_member or Member(
                name=name,
                date_of_birth=dob,
            )

            if selected_guardian is not None:
                member.guardian_id = selected_guardian.id

            registration = Registration(
                member=member,
                season=season,
                age_group=age_group,
            )

            db.session.add(registration)
            db.session.commit()

            return redirect(url_for("home"))

        return render_form()

    @app.route("/registrations/history")
    def registration_history():
        members = (
            Member.query
            .order_by(Member.name.asc())
            .all()
        )

        selected_member_id = request.args.get(
            "member_id",
            type=int,
        )

        registrations = []

        if selected_member_id:
            registrations = (
                Registration.query
                .filter_by(member_id=selected_member_id)
                .order_by(
                    Registration.created_at.desc()
                )
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
            name = request.form.get(
                "guardian_name",
                "",
            ).strip()

            mobile = request.form.get(
                "mobile",
                "",
            ).strip()

            email = request.form.get(
                "email",
                "",
            ).strip()

            relationship = request.form.get(
                "relationship",
                "",
            ).strip()

            address = request.form.get(
                "address",
                "",
            ).strip()

            if not name:
                return render_template(
                    "guardian_form.html",
                    error="Guardian name is required.",
                ), 400

            guardian = Guardian(
                name=name,
                mobile=mobile or None,
                email=email or None,
                relationship=relationship or None,
                address=address or None,
                is_active=True,
            )

            db.session.add(guardian)
            db.session.commit()

            return redirect(url_for("home"))

        return render_template("guardian_form.html")

    @app.route("/guardians")
    def guardian_list():
        search = request.args.get(
            "q",
            "",
        ).strip()

        query = Guardian.query

        if search:
            search_pattern = f"%{search}%"

            query = query.filter(
                or_(
                    Guardian.name.ilike(search_pattern),
                    Guardian.mobile.ilike(search_pattern),
                    Guardian.email.ilike(search_pattern),
                )
            )

        guardians = (
            query
            .order_by(Guardian.name.asc())
            .all()
        )

        return render_template(
            "guardian_list.html",
            guardians=guardians,
            search=search,
        )

    @app.route(
        "/guardians/<int:guardian_id>/edit",
        methods=["GET", "POST"],
    )
    def edit_guardian(guardian_id):
        guardian = db.session.get(
            Guardian,
            guardian_id,
        )

        if guardian is None:
            return "Guardian not found", 404

        if request.method == "POST":
            name = request.form.get(
                "guardian_name",
                "",
            ).strip()

            mobile = request.form.get(
                "mobile",
                "",
            ).strip()

            email = request.form.get(
                "email",
                "",
            ).strip()

            relationship = request.form.get(
                "relationship",
                "",
            ).strip()

            address = request.form.get(
                "address",
                "",
            ).strip()

            if not name:
                return render_template(
                    "guardian_edit.html",
                    guardian=guardian,
                    error="Guardian name is required.",
                ), 400

            guardian.name = name
            guardian.mobile = mobile or None
            guardian.email = email or None
            guardian.relationship = relationship or None
            guardian.address = address or None

            db.session.commit()

            return redirect(
                url_for("guardian_list")
            )

        return render_template(
            "guardian_edit.html",
            guardian=guardian,
        )

    @app.route(
        "/guardians/<int:guardian_id>/deactivate",
        methods=["POST"],
    )
    def deactivate_guardian(guardian_id):
        guardian = db.session.get(
            Guardian,
            guardian_id,
        )

        if guardian is None:
            return "Guardian not found", 404

        guardian.is_active = False

        db.session.commit()

        return redirect(
            url_for("guardian_list")
        )

    @app.route("/teams/new", methods=["GET", "POST"])
    def new_team():
        if request.method == "POST":
            name = request.form.get(
                "team_name",
                "",
            ).strip()

            season = request.form.get(
                "season",
                "",
            ).strip()

            age_group = request.form.get(
                "age_group",
                "",
            ).strip()

            if not all(
                (
                    name,
                    season,
                    age_group,
                )
            ):
                return render_template(
                    "team_form.html",
                    error=(
                        "Team name, season, and age group are required."
                    ),
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

    @app.route(
        "/teams/<int:team_id>/players/add",
        methods=["GET", "POST"],
    )
    def add_player_to_team(team_id):
        team = db.session.get(
            Team,
            team_id,
        )

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
                    error=(
                        "Please select a valid registered player."
                    ),
                ), 400

            if registration.team_id is not None:
                return render_template(
                    "add_player_to_team.html",
                    team=team,
                    registrations=registrations,
                    error=(
                        "This player is already assigned to a team."
                    ),
                ), 400

            if registration.season != team.season:
                return render_template(
                    "add_player_to_team.html",
                    team=team,
                    registrations=registrations,
                    error=(
                        "The player's registration season "
                        "does not match the team."
                    ),
                ), 400

            if registration.age_group != team.age_group:
                return render_template(
                    "add_player_to_team.html",
                    team=team,
                    registrations=registrations,
                    error=(
                        "The player's age group "
                        "does not match the team."
                    ),
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

    @app.route(
        "/teams/<int:team_id>/players/<int:registration_id>/remove",
        methods=["POST"],
    )
    def remove_player_from_team(team_id, registration_id):
        team = db.session.get(Team, team_id)

        if team is None:
            return "Team not found", 404

        registration = db.session.get(
            Registration,
            registration_id,
        )

        if (
            registration is None
            or registration.team_id != team.id
        ):
            return "Registration not found on this team", 404

        registration.team_id = None
        db.session.commit()

        return redirect(
            url_for(
                "add_player_to_team",
                team_id=team.id,
            )
        )

    @app.route(
        "/teams/<int:team_id>/players/<int:registration_id>/move",
        methods=["GET", "POST"],
    )
    def move_player_to_team(team_id, registration_id):
        current_team = db.session.get(
            Team,
            team_id,
        )

        if current_team is None:
            return "Team not found", 404

        registration = db.session.get(
            Registration,
            registration_id,
        )

        if (
            registration is None
            or registration.team_id != current_team.id
        ):
            return "Registration not found on this team", 404

        target_teams = (
            Team.query
            .filter(
                Team.season == current_team.season,
                Team.age_group == current_team.age_group,
                Team.id != current_team.id,
            )
            .order_by(Team.name.asc())
            .all()
        )

        if request.method == "POST":
            target_team_id = request.form.get(
                "target_team_id",
                type=int,
            )

            target_team = (
                db.session.get(Team, target_team_id)
                if target_team_id
                else None
            )

            if target_team is None:
                return render_template(
                    "move_player_to_team.html",
                    team=current_team,
                    registration=registration,
                    target_teams=target_teams,
                    error=(
                        "Please select a valid destination team."
                    ),
                ), 400

            if (
                target_team.season != current_team.season
                or target_team.age_group != current_team.age_group
            ):
                return render_template(
                    "move_player_to_team.html",
                    team=current_team,
                    registration=registration,
                    target_teams=target_teams,
                    error=(
                        "The destination team must match "
                        "the season and age group."
                    ),
                ), 400

            registration.team_id = target_team.id
            db.session.commit()

            return redirect(
                url_for(
                    "add_player_to_team",
                    team_id=target_team.id,
                )
            )

        return render_template(
            "move_player_to_team.html",
            team=current_team,
            registration=registration,
            target_teams=target_teams,
        )

    @app.route("/teams/<int:team_id>/manage")
    def manage_team_players(team_id):
        team = db.session.get(Team, team_id)

        if team is None:
            return "Team not found", 404

        roster = (
            Registration.query
            .filter_by(team_id=team.id)
            .join(Member)
            .order_by(Member.name.asc())
            .all()
        )

        return render_template(
            "manage_team_players.html",
            team=team,
            roster=roster,
        )

    return app


def self_is_junior(dob):
    today = date.today()

    return (
        today.year - dob.year
    ) - (
        (today.month, today.day)
        < (dob.month, dob.day)
    ) < 18


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                "5000",
            )
        ),
    )