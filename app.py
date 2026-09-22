from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from models import db, Member, Registration

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///warrigal_park.db"
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "Warrigal Park FC app is running!"

@app.route("/registrations/new", methods=["GET", "POST"])
def new_registration():
    if request.method == "POST":
        name = request.form.get("member_name")
        dob_str = request.form.get("date_of_birth")
        season = request.form.get("season")
        age_group = request.form.get("age_group")

        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()

        member = Member(name=name, date_of_birth=dob)
        db.session.add(member)
        db.session.commit()

        registration = Registration(
            member_id=member.id,
            season=season,
            age_group=age_group,
        )
        db.session.add(registration)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("registration_form.html")

@app.route("/registrations/history")
def registration_history():
    registrations = Registration.query.order_by(
        Registration.created_at.desc()
    ).all()

    return render_template(
        "registration_history.html",
        registrations=registrations,
    )

if __name__ == "__main__":
    app.run(debug=True)