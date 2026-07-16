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
