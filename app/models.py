from app.extensions import db



class Grade(db.Model):
    __tablename__ = "grade"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    grade_number = db.Column(
        db.SmallInteger,
        nullable=False,
        unique=True
    )

    name = db.Column(
        db.String(50),
        nullable=False
    )

    def __repr__(self):
        return (
            f"<Grade {self.grade_number}>"
        )

class Topic(db.Model):
    __tablename__ = "topic"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    def __repr__(self) -> str:
        return f"<Topic {self.name}>"
