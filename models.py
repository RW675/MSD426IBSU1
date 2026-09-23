from datetime import datetime, timezone
import enum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates


db = SQLAlchemy()


class RegistrationStatus(enum.Enum):
    STARTED = "started"
    COMPLETE = "complete"
    WITHDRAWN = "withdrawn"


class Guardian(db.Model):
    __tablename__ = "guardian"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    mobile = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    relationship = db.Column(db.String(80), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    members = db.relationship(
        "Member",
        backref="guardian",
        lazy=True,
    )

    def link_members(self, members):
        for member in members:
            member.guardian_id = self.id
        return self


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    contact = db.Column(db.String(100))
    guardian_id = db.Column(
        db.Integer,
        db.ForeignKey("guardian.id"),
        nullable=True,
    )

    registrations = db.relationship(
        "Registration",
        backref="member",
        lazy=True,
    )

    @property
    def guardian_mobile(self):
        if self.guardian is not None:
            return self.guardian.mobile
        return self.contact


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(
        db.Integer,
        db.ForeignKey("member.id"),
        nullable=False,
    )
    season = db.Column(db.String(20), nullable=False)
    age_group = db.Column(db.String(20), nullable=False)
    status = db.Column(
        db.Enum(RegistrationStatus),
        default=RegistrationStatus.STARTED,
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    team_id = db.Column(
        db.Integer,
        db.ForeignKey("team.id"),
        nullable=True,
    )

    @validates("status")
    def validate_status(self, key, value):
        if isinstance(value, str):
            return RegistrationStatus(value.lower())
        return value


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    season = db.Column(db.String(20), nullable=False)
    age_group = db.Column(db.String(20), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    registrations = db.relationship(
        "Registration",
        backref="team",
        lazy=True,
    )

    def roster_details(self):
        rows = []
        for registration in self.registrations:
            if registration.member is None:
                continue
            member = registration.member
            rows.append(
                {
                    "member_name": member.name,
                    "dob": member.date_of_birth,
                    "guardian_mobile": member.guardian_mobile,
                    "season": registration.season,
                    "age_group": registration.age_group,
                }
            )
        return rows