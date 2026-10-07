import csv
import io
import os
import re

from datetime import date, datetime
from functools import wraps

from flask import (
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_migrate import Migrate
from sqlalchemy import or_, text
from sqlalchemy.exc import IntegrityError

from models import Guardian, Member, Registration, Team, db

migrate = Migrate()


def normalize_text(value):
    if value is None:
        return ""
    return str(value).strip()


def valid_season(value):
    return bool(re.fullmatch(r"\d{4}", value or ""))


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not app.config.get("ADMIN_ENABLED", False):
            return view(*args, **kwargs)
        if not session.get("is_admin"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


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
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()
        unique_indexes = [
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_member_name_dob ON member (name, date_of_birth)",
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_guardian_email ON guardian (email) WHERE email IS NOT NULL",
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_team_name_season_age_group ON team (LOWER(name), LOWER(season), LOWER(age_group))",
        ]

        for statement in unique_indexes:
            try:
                db.session.execute(text(statement))
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @app.route("/health")
    def health():
        return render_template(
            "health.html",
            status="ok",
            database_uri=app.config.get("SQLALCHEMY_DATABASE_URI", "sqlite://"),
        )

    @app.errorhandler(404)
    def not_found(error):
        return render_template("error.html", error_code=404, message="Page not found."), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template("error.html", error_code=500, message="Something went wrong on the server."), 500

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = normalize_text(request.form.get("username", ""))
            password = request.form.get("password", "")
            if (app.config.get("ADMIN_ENABLED", False)
                and username == app.config.get("ADMIN_USERNAME")
                and password == app.config.get("ADMIN_PASSWORD")):
                session["is_admin"] = True
                flash("Signed in successfully.", "success")
                return redirect(url_for("home"))
            flash("Invalid username or password.", "error")
            return render_template("login.html", error="Invalid username or password."), 401
        return render_template("login.html")

    @app.route("/logout", methods=["POST"])
    def logout():
        session.pop("is_admin", None)
        flash("Signed out successfully.", "info")
        return redirect(url_for("home"))

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
            name = normalize_text(request.form.get("member_name", ""))
            dob_str = normalize_text(request.form.get("date_of_birth"))
            season = normalize_text(request.form.get("season", ""))
            age_group = normalize_text(request.form.get("age_group", ""))
            guardian_id = request.form.get("guardian_id", type=int)

            try:
                if not all((name, dob_str, season, age_group)):
                    raise ValueError

                if not valid_season(season):
                    raise ValueError

                dob = datetime.strptime(dob_str, "%Y-%m-%d").date()

                if dob > date.today():
                    raise ValueError

            except (TypeError, ValueError):
                return render_form(
                    error=(
                        "Please provide a valid name, date of birth, "
                        "season, and age group."
                    ),
                    status=400,
                )

            existing_member = Member.query.filter(
                db.func.lower(Member.name) == name.lower(),
                Member.date_of_birth == dob,
            ).first()

            if existing_member is not None:
                return render_form(
                    error=(
                        "A registration already exists for this member on the same date of birth. "
                        "Please review the member history or select the existing record."
                    ),
                    status=400,
                )

            normalized_name = name.strip()
            if not normalized_name or not season or not age_group:
                return render_form(
                    error=(
                        "Please provide a valid name, date of birth, "
                        "season, and age group."
                    ),
                    status=400,
                )

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
                name=normalized_name,
                date_of_birth=dob,
            )

            if selected_guardian is not None:
                member.guardian_id = selected_guardian.id

            registration = Registration(
                member=member,
                season=season,
                age_group=age_group,
            )

            try:
                db.session.add(registration)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return render_form(
                    error=(
                        "This registration could not be saved because it duplicates an existing record. "
                        "Please check the member and registration details before trying again."
                    ),
                    status=400,
                )
            flash("Registration created successfully.", "success")

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

    @app.route("/reports")
    def reports():
        all_registrations = Registration.query.order_by(Registration.created_at.desc()).all()
        season_counts = {}
        age_group_counts = {}

        for registration in all_registrations:
            season_counts[registration.season] = season_counts.get(registration.season, 0) + 1
            age_group_counts[registration.age_group] = age_group_counts.get(registration.age_group, 0) + 1

        return render_template(
            "reports.html",
            registrations=all_registrations,
            total_registrations=len(all_registrations),
            season_counts=season_counts,
            age_group_counts=age_group_counts,
            teams=Team.query.order_by(
            Team.season.desc(),
            Team.age_group.asc(),
            Team.name.asc(),
            ).all(),
        )

    @app.route("/reports/registrations.csv")
    def registrations_csv():
        registrations = (
            Registration.query
            .join(Member)
            .outerjoin(Team)
            .order_by(
                Registration.season.desc(),
                Registration.age_group.asc(),
                Team.name.asc(),
                Member.name.asc(),
            )
            .all()
                )

        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow([
            "member_name",
            "date_of_birth",
            "guardian_mobile",
            "season",
            "age_group",
            "team_name",
            "status",
        ])

        for registration in registrations:
            member = registration.member
            writer.writerow([
                member.name if member else "",
                member.date_of_birth.isoformat() if member else "",
                member.guardian_mobile if member else "",
                registration.season,
                registration.age_group,
                registration.team.name if registration.team else "Unassigned",
                registration.status.value if registration.status else "",
            ])

        response = Response(stream.getvalue(), mimetype="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=registrations.csv"
        return response

    @app.route("/guardians/new", methods=["GET", "POST"])
    def new_guardian():
        if request.method == "POST":
            name = normalize_text(request.form.get("guardian_name", ""))
            mobile = normalize_text(request.form.get("mobile", ""))
            email = normalize_text(request.form.get("email", ""))
            relationship = normalize_text(request.form.get("relationship", ""))
            address = normalize_text(request.form.get("address", ""))

            if not name:
                return render_template(
                    "guardian_form.html",
                    error="Guardian name is required.",
                ), 400

            if email:
                existing_guardian = Guardian.query.filter(
                    db.func.lower(Guardian.email) == email.lower(),
                ).first()
                if existing_guardian is not None:
                    return render_template(
                        "guardian_form.html",
                        error="A guardian with this email address already exists. Please use the existing record or update it instead.",
                    ), 400

            guardian = Guardian(
                name=name,
                mobile=mobile or None,
                email=email or None,
                relationship=relationship or None,
                address=address or None,
                is_active=True,
            )

            try:
                db.session.add(guardian)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return render_template(
                    "guardian_form.html",
                    error="This guardian record already exists. Please check whether the same contact details are already on file.",
                ), 400
            flash("Guardian added successfully.", "success")

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
            name = normalize_text(request.form.get("guardian_name", ""))
            mobile = normalize_text(request.form.get("mobile", ""))
            email = normalize_text(request.form.get("email", ""))
            relationship = normalize_text(request.form.get("relationship", ""))
            address = normalize_text(request.form.get("address", ""))

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
            flash("Guardian updated successfully.", "success")

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
    @admin_required
    def deactivate_guardian(guardian_id):
        guardian = db.session.get(
            Guardian,
            guardian_id,
        )

        if guardian is None:
            return "Guardian not found", 404

        guardian.is_active = False

        db.session.commit()
        flash("Guardian deactivated.", "info")

        return redirect(
            url_for("guardian_list")
        )

    @app.route("/teams")
    def team_list():
        teams = (
            Team.query
            .order_by(
                Team.season.desc(),
                Team.age_group.asc(),
                Team.name.asc(),
            )
            .all()
        )

        return render_template(
            "team_list.html",
            teams=teams,
        )

    @app.route(
        "/teams/<int:team_id>/delete",
        methods=["POST"],
    )
    @admin_required
    def delete_team(team_id):
        team = db.session.get(Team, team_id)

        if team is None:
            return "Team not found", 404

        assigned_registration = (
            Registration.query
            .filter_by(team_id=team.id)
            .first()
        )

        if assigned_registration is not None:
            teams = (
                Team.query
                .order_by(
                    Team.season.desc(),
                    Team.age_group.asc(),
                    Team.name.asc(),
                )
                .all()
            )

            return render_template(
                "team_list.html",
                teams=teams,
                error=(
                    "This team cannot be deleted while players are assigned. "
                    "Move or remove the players first."
                ),
            ), 400

        db.session.delete(team)
        db.session.commit()
        flash("Team deleted successfully.", "success")

        return redirect(url_for("team_list"))

    @app.route("/teams/new", methods=["GET", "POST"])
    def new_team():
        if request.method == "POST":
            name = normalize_text(request.form.get("team_name", ""))
            season = normalize_text(request.form.get("season", ""))
            age_group = normalize_text(request.form.get("age_group", ""))

            if not all((name, season, age_group)):
                return render_template(
                    "team_form.html",
                    error=(
                        "Team name, season, and age group are required."
                    ),
                ), 400

            if not valid_season(season):
                return render_template(
                    "team_form.html",
                    error="Season must be a four-digit year.",
                ), 400

            existing_team = Team.query.filter(
                db.func.lower(Team.name) == name.lower(),
                db.func.lower(Team.season) == season.lower(),
                db.func.lower(Team.age_group) == age_group.lower(),
            ).first()

            if existing_team is not None:
                return render_template(
                    "team_form.html",
                    error=(
                        "A team with this name, season, and age group "
                        "already exists."
                    ),
                ), 400

            team = Team(
                name=name,
                season=season,
                age_group=age_group,
            )

            try:
                db.session.add(team)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return render_template(
                    "team_form.html",
                    error="A team with this name, season and age group already exists.",
                ), 400
            flash("Team created successfully.", "success")

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
            flash("Player added to the team.", "success")

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
        flash("Player removed from the team.", "info")

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
            flash("Player moved successfully.", "success")

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

    @app.route("/teams/<int:team_id>/roster.csv")
    def export_team_roster_csv(team_id):
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

        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(["member_name", "date_of_birth", "guardian_mobile", "registration_status"])
        for registration in roster:
            member = registration.member
            writer.writerow([
                member.name if member else "",
                member.date_of_birth.isoformat() if member else "",
                member.guardian_mobile if member else "",
                registration.status.value if registration.status else "",
            ])

        response = Response(stream.getvalue(), mimetype="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={team.name.lower().replace(' ', '_')}_roster.csv"
        return response

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