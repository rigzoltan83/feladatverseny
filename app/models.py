from app.extensions import db

question_grade = db.Table(
    "question_grade",
    db.Column(
        "question_id",
        db.BigInteger,
        db.ForeignKey("question.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "grade_id",
        db.Integer,
        db.ForeignKey("grade.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


question_topic = db.Table(
    "question_topic",
    db.Column(
        "question_id",
        db.BigInteger,
        db.ForeignKey("question.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "topic_id",
        db.Integer,
        db.ForeignKey("topic.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

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

class SourceYear(db.Model):
    __tablename__ = "source_year"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    year_number = db.Column(
        db.Integer,
        nullable=False,
        unique=True,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    def __repr__(self) -> str:
        return f"<SourceYear {self.year_number}>"

class Question(db.Model):
    __tablename__ = "question"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
    )

    source_year_id = db.Column(
        db.Integer,
        db.ForeignKey("source_year.id"),
        nullable=False,
        index=True,
    )

    original_position = db.Column(
        db.SmallInteger,
        nullable=False,
    )

    difficulty = db.Column(
        db.SmallInteger,
        nullable=False,
    )

    question_text = db.Column(
        db.Text,
        nullable=False,
    )

    image_path = db.Column(
        db.Text,
        nullable=True,
    )

    explanation = db.Column(
        db.Text,
        nullable=True,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    source_year = db.relationship(
        "SourceYear",
        backref=db.backref(
            "questions",
            lazy="dynamic",
        ),
    )

    grades = db.relationship(
        "Grade",
        secondary=question_grade,
        backref=db.backref(
            "questions",
            lazy="dynamic",
        ),
    )

    topics = db.relationship(
        "Topic",
        secondary=question_topic,
        backref=db.backref(
            "questions",
            lazy="dynamic",
        ),
    )

    __table_args__ = (
        db.CheckConstraint(
            "original_position BETWEEN 1 AND 25",
            name="ck_question_original_position",
        ),
        db.CheckConstraint(
            "difficulty BETWEEN 1 AND 25",
            name="ck_question_difficulty",
        ),
    )

    @property
    def image_filename(self) -> str:
        return f"{self.id:07d}.jpg"

    def __repr__(self) -> str:
        return (
            f"<Question id={self.id} "
            f"position={self.original_position}>"
        )

class AnswerOption(db.Model):
    __tablename__ = "answer_option"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
    )

    question_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "question.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    original_position = db.Column(
        db.SmallInteger,
        nullable=False,
    )

    answer_text = db.Column(
        db.Text,
        nullable=True,
    )

    image_path = db.Column(
        db.Text,
        nullable=True,
    )

    is_correct = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    question = db.relationship(
        "Question",
        backref=db.backref(
            "answer_options",
            cascade="all, delete-orphan",
            order_by="AnswerOption.original_position",
        ),
    )

    __table_args__ = (
        db.CheckConstraint(
            "original_position BETWEEN 1 AND 5",
            name="ck_answer_option_position",
        ),
        db.CheckConstraint(
            "answer_text IS NOT NULL OR image_path IS NOT NULL",
            name="ck_answer_option_has_content",
        ),
        db.UniqueConstraint(
            "question_id",
            "original_position",
            name="uq_answer_option_question_position",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<AnswerOption question={self.question_id} "
            f"position={self.original_position}>"
        )

class TestTemplate(db.Model):
    __tablename__ = "test_template"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
    )

    name = db.Column(
        db.String(200),
        nullable=False,
        unique=True,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    question_count = db.Column(
        db.SmallInteger,
        nullable=False,
        default=25,
    )

    shuffle_questions = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    shuffle_answers = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    __table_args__ = (
        db.CheckConstraint(
            "question_count BETWEEN 1 AND 100",
            name="ck_test_template_question_count",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<TestTemplate id={self.id} "
            f"name={self.name!r}>"
        )


