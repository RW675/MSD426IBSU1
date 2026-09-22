from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class RegistrationStatus(enum.Enum):
    STARTED = "started"
    COMPLETE = "complete"
    WITHDRAWN = "withdrawn"

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    contact = db.Column(db.String(100))

    registrations = db.relationship("Registration", backref="member", lazy=True)


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)
    season = db.Column(db.String(20), nullable=False)
    age_group = db.Column(db.String(20), nullable=False)
    status = db.Column(
        db.Enum(RegistrationStatus),
        default=RegistrationStatus.STARTED,
        nullable=False,
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)