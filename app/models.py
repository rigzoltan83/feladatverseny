from app.extensions import db

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

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

test_template_grade = db.Table(
    "test_template_grade",
    db.Column(
        "test_template_id",
        db.BigInteger,
        db.ForeignKey(
            "test_template.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    db.Column(
        "grade_id",
        db.Integer,
        db.ForeignKey(
            "grade.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
)


test_template_topic = db.Table(
    "test_template_topic",
    db.Column(
        "test_template_id",
        db.BigInteger,
        db.ForeignKey(
            "test_template.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    db.Column(
        "topic_id",
        db.Integer,
        db.ForeignKey(
            "topic.id",
            ondelete="CASCADE",
        ),
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

    name_en = db.Column(
        db.String(100),
        nullable=True,
    )

    @property
    def display_name(self) -> str:
        from flask_babel import get_locale

        language = str(get_locale() or "hu")

        if language.startswith("en") and self.name_en:
            return self.name_en

        return self.name

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

    grades = db.relationship(
        "Grade",
        secondary=test_template_grade,
        backref=db.backref(
            "test_templates",
            lazy="dynamic",
        ),
    )

    topics = db.relationship(
        "Topic",
        secondary=test_template_topic,
        backref=db.backref(
            "test_templates",
            lazy="dynamic",
        ),
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

class Competitor(db.Model):
    __tablename__ = "competitor"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
    )

    username = db.Column(
        db.String(80),
        nullable=False,
        unique=True,
        index=True,
    )

    full_name = db.Column(
        db.String(200),
        nullable=False,
    )

    grade_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "grade.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    is_admin = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        server_default=db.false(),
    )

    preferred_language = db.Column(
        db.String(5),
        nullable=False,
        default="hu",
        server_default="hu",
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    grade = db.relationship(
        "Grade",
        backref=db.backref(
            "competitors",
            lazy="dynamic",
        ),
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password: str) -> bool:
        return check_password_hash(
            self.password_hash,
            password,
        )

    def __repr__(self) -> str:
        return (
            f"<Competitor id={self.id} "
            f"username={self.username!r}>"
        )

class GeneratedTest(db.Model):
    __tablename__ = "generated_test"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
    )

    test_template_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "test_template.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    name = db.Column(
        db.String(250),
        nullable=False,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="draft",
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    test_template = db.relationship(
        "TestTemplate",
        backref=db.backref(
            "generated_tests",
            lazy="dynamic",
        ),
    )

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('draft', 'active', 'closed')",
            name="ck_generated_test_status",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<GeneratedTest id={self.id} "
            f"name={self.name!r}>"
        )

class GeneratedTestQuestion(db.Model):
    __tablename__ = "generated_test_question"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
    )

    generated_test_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "generated_test.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    question_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "question.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    display_position = db.Column(
        db.SmallInteger,
        nullable=False,
    )

    generated_test = db.relationship(
        "GeneratedTest",
        backref=db.backref(
            "generated_questions",
            cascade="all, delete-orphan",
            order_by="GeneratedTestQuestion.display_position",
        ),
    )

    question = db.relationship(
        "Question",
    )

    __table_args__ = (
        db.CheckConstraint(
            "display_position >= 1",
            name="ck_generated_test_question_position",
        ),
        db.UniqueConstraint(
            "generated_test_id",
            "display_position",
            name="uq_generated_test_question_position",
        ),
        db.UniqueConstraint(
            "generated_test_id",
            "question_id",
            name="uq_generated_test_question_question",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<GeneratedTestQuestion "
            f"test={self.generated_test_id} "
            f"position={self.display_position}>"
        )

class GeneratedTestAnswer(db.Model):
    __tablename__ = "generated_test_answer"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
    )

    generated_test_question_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "generated_test_question.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    answer_option_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "answer_option.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    display_position = db.Column(
        db.SmallInteger,
        nullable=False,
    )

    generated_test_question = db.relationship(
        "GeneratedTestQuestion",
        backref=db.backref(
            "generated_answers",
            cascade="all, delete-orphan",
            order_by="GeneratedTestAnswer.display_position",
        ),
    )

    answer_option = db.relationship(
        "AnswerOption",
    )

    __table_args__ = (
        db.CheckConstraint(
            "display_position BETWEEN 1 AND 5",
            name="ck_generated_test_answer_position",
        ),
        db.UniqueConstraint(
            "generated_test_question_id",
            "display_position",
            name="uq_generated_test_answer_position",
        ),
        db.UniqueConstraint(
            "generated_test_question_id",
            "answer_option_id",
            name="uq_generated_test_answer_option",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<GeneratedTestAnswer "
            f"question={self.generated_test_question_id} "
            f"position={self.display_position}>"
        )

class CompetitorAttempt(db.Model):
    __tablename__ = "competitor_attempt"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
    )

    competitor_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "competitor.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    generated_test_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "generated_test.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="in_progress",
    )

    started_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
    )

    submitted_at = db.Column(
        db.DateTime(timezone=True),
        nullable=True,
    )

    competitor = db.relationship(
        "Competitor",
        backref=db.backref(
            "attempts",
            lazy="dynamic",
        ),
    )

    generated_test = db.relationship(
        "GeneratedTest",
        backref=db.backref(
            "competitor_attempts",
            lazy="dynamic",
        ),
    )

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('in_progress', 'submitted')",
            name="ck_competitor_attempt_status",
        ),
        db.UniqueConstraint(
            "competitor_id",
            "generated_test_id",
            name="uq_competitor_attempt_test",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<CompetitorAttempt id={self.id} "
            f"competitor={self.competitor_id} "
            f"test={self.generated_test_id}>"
        )


class CompetitorAnswer(db.Model):
    __tablename__ = "competitor_answer"

    id = db.Column(
        db.BigInteger,
        primary_key=True,
    )

    attempt_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "competitor_attempt.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    generated_test_question_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "generated_test_question.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    generated_test_answer_id = db.Column(
        db.BigInteger,
        db.ForeignKey(
            "generated_test_answer.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    saved_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )

    attempt = db.relationship(
        "CompetitorAttempt",
        backref=db.backref(
            "answers",
            cascade="all, delete-orphan",
        ),
    )

    generated_test_question = db.relationship(
        "GeneratedTestQuestion",
    )

    generated_test_answer = db.relationship(
        "GeneratedTestAnswer",
    )

    __table_args__ = (
        db.UniqueConstraint(
            "attempt_id",
            "generated_test_question_id",
            name="uq_competitor_answer_question",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<CompetitorAnswer id={self.id} "
            f"attempt={self.attempt_id} "
            f"question={self.generated_test_question_id}>"
        )
