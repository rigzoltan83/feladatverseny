import csv
import io

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.extensions import db
from app.models import (
    AnswerOption,
    Grade,
    Question,
    SourceYear,
    Topic,
)

from app.routes.admin_media import (
    get_question_image_path,
)

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
)

CSV_FIELDNAMES = [
    "forrasev",
    "sorszam",
    "nehezseg",
    "evfolyamok",
    "temakorok",
    "feladat",
    "valasz1",
    "valasz2",
    "valasz3",
    "valasz4",
    "valasz5",
    "helyes",
    "magyarazat",
    "aktiv",
]

def parse_boolean(value: str) -> bool | None:
    normalized = value.strip().lower()

    if normalized in {
        "igen",
        "true",
        "1",
        "yes",
        "aktív",
        "aktiv",
    }:
        return True

    if normalized in {
        "nem",
        "false",
        "0",
        "no",
        "inaktív",
        "inaktiv",
    }:
        return False

    return None



@admin_bp.get("/")
def index():
    return render_template("admin/index.html")

@admin_bp.get("/questions")
def questions():
    question_list = (
        Question.query
        .order_by(
            Question.source_year_id.desc(),
            Question.original_position.asc(),
        )
        .all()
    )

    return render_template(
        "admin/questions.html",
        questions=question_list,
    )


@admin_bp.route("/questions/new", methods=["GET", "POST"])
def question_new():
    grade_list = Grade.query.order_by(
        Grade.grade_number
    ).all()

    topic_list = (
        Topic.query
        .filter_by(is_active=True)
        .order_by(Topic.name)
        .all()
    )

    source_year_list = (
        SourceYear.query
        .filter_by(is_active=True)
        .order_by(SourceYear.year_number.desc())
        .all()
    )

    if request.method == "POST":
        source_year_id = request.form.get(
            "source_year_id",
            type=int,
        )

        original_position = request.form.get(
            "original_position",
            type=int,
        )

        difficulty = request.form.get(
            "difficulty",
            type=int,
        )

        question_text = request.form.get(
            "question_text",
            "",
        ).strip()

        explanation = request.form.get(
            "explanation",
            "",
        ).strip()

        selected_grade_ids = request.form.getlist(
            "grade_ids",
            type=int,
        )

        selected_topic_ids = request.form.getlist(
            "topic_ids",
            type=int,
        )

        answer_texts = [
            request.form.get(
                f"answer_{position}",
                "",
            ).strip()
            for position in range(1, 6)
        ]

        correct_answer = request.form.get(
            "correct_answer",
            type=int,
        )

        errors = []

        source_year = db.session.get(
            SourceYear,
            source_year_id,
        )

        if source_year is None:
            errors.append(
                "Érvényes forrásévet kell választani."
            )

        if (
            original_position is None
            or not 1 <= original_position <= 25
        ):
            errors.append(
                "A feladat sorszáma 1 és 25 közötti lehet."
            )

        if (
            difficulty is None
            or not 1 <= difficulty <= 25
        ):
            errors.append(
                "A nehézség 1 és 25 közötti lehet."
            )

        if not question_text:
            errors.append(
                "A feladat szövege kötelező."
            )

        if not selected_grade_ids:
            errors.append(
                "Legalább egy évfolyamot ki kell választani."
            )

        if not selected_topic_ids:
            errors.append(
                "Legalább egy témakört ki kell választani."
            )

        if any(
            not answer_text
            for answer_text in answer_texts
        ):
            errors.append(
                "Mind az öt válaszlehetőséget ki kell tölteni."
            )

        if correct_answer not in range(1, 6):
            errors.append(
                "Ki kell választani a helyes választ."
            )

        selected_grades = Grade.query.filter(
            Grade.id.in_(selected_grade_ids)
        ).all()

        selected_topics = Topic.query.filter(
            Topic.id.in_(selected_topic_ids)
        ).all()

        if len(selected_grades) != len(
            set(selected_grade_ids)
        ):
            errors.append(
                "Az évfolyamválasztás érvénytelen."
            )

        if len(selected_topics) != len(
            set(selected_topic_ids)
        ):
            errors.append(
                "A témakörválasztás érvénytelen."
            )

        if errors:
            for error in errors:
                flash(error, "error")

        else:
            question = Question(
                source_year=source_year,
                original_position=original_position,
                difficulty=difficulty,
                question_text=question_text,
                explanation=explanation or None,
                is_active=True,
            )

            question.grades = selected_grades
            question.topics = selected_topics

            for position, answer_text in enumerate(
                answer_texts,
                start=1,
            ):
                question.answer_options.append(
                    AnswerOption(
                        original_position=position,
                        answer_text=answer_text,
                        is_correct=(
                            position == correct_answer
                        ),
                    )
                )

            db.session.add(question)
            db.session.commit()

            flash(
                (
                    "A feladatot és az öt "
                    "válaszlehetőséget elmentettük."
                ),
                "success",
            )

            return redirect(
                url_for("admin.questions")
            )

    return render_template(
        "admin/question_form.html",
        question=None,
        grades=grade_list,
        topics=topic_list,
        source_years=source_year_list,
        selected_grade_ids=set(),
        selected_topic_ids=set(),
        answer_by_position={},
    )


@admin_bp.get("/questions/<int:question_id>")
def question_detail(question_id: int):
    question = db.get_or_404(
        Question,
        question_id,
    )

    image_path = get_question_image_path(question)

    return render_template(
        "admin/question_detail.html",
        question=question,
        image_exists=image_path.is_file(),
    )

@admin_bp.route(
    "/questions/<int:question_id>/edit",
    methods=["GET", "POST"],
)
def question_edit(question_id: int):
    question = db.get_or_404(
        Question,
        question_id,
    )

    grade_list = Grade.query.order_by(
        Grade.grade_number
    ).all()

    topic_list = (
        Topic.query
        .filter_by(is_active=True)
        .order_by(Topic.name)
        .all()
    )

    source_year_list = (
        SourceYear.query
        .filter_by(is_active=True)
        .order_by(SourceYear.year_number.desc())
        .all()
    )

    existing_answers = sorted(
        question.answer_options,
        key=lambda answer: answer.original_position,
    )

    answer_by_position = {
        answer.original_position: answer
        for answer in existing_answers
    }

    selected_grade_ids = {
        grade.id
        for grade in question.grades
    }

    selected_topic_ids = {
        topic.id
        for topic in question.topics
    }

    if request.method == "POST":
        source_year_id = request.form.get(
            "source_year_id",
            type=int,
        )

        original_position = request.form.get(
            "original_position",
            type=int,
        )

        difficulty = request.form.get(
            "difficulty",
            type=int,
        )

        question_text = request.form.get(
            "question_text",
            "",
        ).strip()

        explanation = request.form.get(
            "explanation",
            "",
        ).strip()

        posted_grade_ids = request.form.getlist(
            "grade_ids",
            type=int,
        )

        posted_topic_ids = request.form.getlist(
            "topic_ids",
            type=int,
        )

        answer_texts = [
            request.form.get(
                f"answer_{position}",
                "",
            ).strip()
            for position in range(1, 6)
        ]

        correct_answer = request.form.get(
            "correct_answer",
            type=int,
        )

        errors = []

        source_year = db.session.get(
            SourceYear,
            source_year_id,
        )

        if source_year is None:
            errors.append(
                "Érvényes forrásévet kell választani."
            )

        if (
            original_position is None
            or not 1 <= original_position <= 25
        ):
            errors.append(
                "A feladat sorszáma 1 és 25 közötti lehet."
            )

        if (
            difficulty is None
            or not 1 <= difficulty <= 25
        ):
            errors.append(
                "A nehézség 1 és 25 közötti lehet."
            )

        if not question_text:
            errors.append(
                "A feladat szövege kötelező."
            )

        if not posted_grade_ids:
            errors.append(
                "Legalább egy évfolyamot ki kell választani."
            )

        if not posted_topic_ids:
            errors.append(
                "Legalább egy témakört ki kell választani."
            )

        if any(
            not answer_text
            for answer_text in answer_texts
        ):
            errors.append(
                "Mind az öt válaszlehetőséget ki kell tölteni."
            )

        if correct_answer not in range(1, 6):
            errors.append(
                "Ki kell választani a helyes választ."
            )

        selected_grades = Grade.query.filter(
            Grade.id.in_(posted_grade_ids)
        ).all()

        selected_topics = Topic.query.filter(
            Topic.id.in_(posted_topic_ids)
        ).all()

        if len(selected_grades) != len(
            set(posted_grade_ids)
        ):
            errors.append(
                "Az évfolyamválasztás érvénytelen."
            )

        if len(selected_topics) != len(
            set(posted_topic_ids)
        ):
            errors.append(
                "A témakörválasztás érvénytelen."
            )

        if errors:
            for error in errors:
                flash(error, "error")

        else:
            question.source_year = source_year
            question.original_position = original_position
            question.difficulty = difficulty
            question.question_text = question_text
            question.explanation = explanation or None
            question.grades = selected_grades
            question.topics = selected_topics

            AnswerOption.query.filter_by(
                question_id=question.id
            ).delete(
                synchronize_session=False
            )

            db.session.flush()

            for position, answer_text in enumerate(
                answer_texts,
                start=1,
            ):
                db.session.add(
                    AnswerOption(
                        question_id=question.id,
                        original_position=position,
                        answer_text=answer_text,
                        is_correct=(
                            position == correct_answer
                        ),
                    )
                )

            # Fontos: ez már a cikluson kívül van.
            db.session.commit()

            flash(
                "A feladat módosításait elmentettük.",
                "success",
            )

            return redirect(
                url_for(
                    "admin.question_detail",
                    question_id=question.id,
                )
            )

    return render_template(
        "admin/question_form.html",
        question=question,
        grades=grade_list,
        topics=topic_list,
        source_years=source_year_list,
        selected_grade_ids=selected_grade_ids,
        selected_topic_ids=selected_topic_ids,
        answer_by_position=answer_by_position,
    )

@admin_bp.route(
    "/questions/import",
    methods=["GET", "POST"],
)
def question_import():
    preview_rows = []
    import_errors = []

    if request.method == "POST":
        action = request.form.get(
            "action",
            "preview",
        )

        uploaded_file = request.files.get(
            "csv_file"
        )

        if (
            uploaded_file is None
            or not uploaded_file.filename
        ):
            flash(
                "Nem választottál ki CSV-fájlt.",
                "error",
            )

            return render_template(
                "admin/question_import.html",
                preview_rows=preview_rows,
                import_errors=import_errors,
            )

        if not uploaded_file.filename.lower().endswith(
            ".csv"
        ):
            flash(
                "Csak CSV-fájl tölthető fel.",
                "error",
            )

            return render_template(
                "admin/question_import.html",
                preview_rows=preview_rows,
                import_errors=import_errors,
            )

        try:
            file_content = uploaded_file.read().decode(
                "utf-8-sig"
            )

        except UnicodeDecodeError:
            flash(
                (
                    "A CSV nem olvasható "
                    "UTF-8 kódolással."
                ),
                "error",
            )

            return render_template(
                "admin/question_import.html",
                preview_rows=preview_rows,
                import_errors=import_errors,
            )

        reader = csv.DictReader(
            io.StringIO(file_content),
            delimiter=";",
        )

        actual_fieldnames = reader.fieldnames or []

        if actual_fieldnames != CSV_FIELDNAMES:
            flash(
                "A CSV fejlécének formátuma hibás.",
                "error",
            )

            return render_template(
                "admin/question_import.html",
                preview_rows=preview_rows,
                import_errors=[
                    {
                        "line": 1,
                        "messages": [
                            (
                                "Elvárt fejléc: "
                                + ";".join(
                                    CSV_FIELDNAMES
                                )
                            )
                        ],
                    }
                ],
            )

        grade_by_number = {
            grade.grade_number: grade
            for grade in Grade.query.all()
        }

        topic_by_name = {
            topic.name.casefold(): topic
            for topic in Topic.query.all()
        }

        source_year_by_number = {
            source_year.year_number: source_year
            for source_year
            in SourceYear.query.all()
        }

        for line_number, row in enumerate(
            reader,
            start=2,
        ):
            row_errors = []

            normalized_row = {
                key: (
                    value.strip()
                    if value is not None
                    else ""
                )
                for key, value in row.items()
            }

            try:
                source_year_number = int(
                    normalized_row["forrasev"]
                )
            except ValueError:
                source_year_number = None
                row_errors.append(
                    "A forrásév nem érvényes szám."
                )

            try:
                original_position = int(
                    normalized_row["sorszam"]
                )
            except ValueError:
                original_position = None
                row_errors.append(
                    "A sorszám nem érvényes szám."
                )

            try:
                difficulty = int(
                    normalized_row["nehezseg"]
                )
            except ValueError:
                difficulty = None
                row_errors.append(
                    "A nehézség nem érvényes szám."
                )

            try:
                correct_answer = int(
                    normalized_row["helyes"]
                )
            except ValueError:
                correct_answer = None
                row_errors.append(
                    (
                        "A helyes válasz "
                        "nem érvényes szám."
                    )
                )

            if (
                source_year_number is not None
                and source_year_number
                not in source_year_by_number
            ):
                row_errors.append(
                    (
                        "A forrásév nincs rögzítve: "
                        f"{source_year_number}."
                    )
                )

            if (
                original_position is not None
                and not 1 <= original_position <= 25
            ):
                row_errors.append(
                    (
                        "A sorszám 1 és 25 "
                        "közötti lehet."
                    )
                )

            if (
                difficulty is not None
                and not 1 <= difficulty <= 25
            ):
                row_errors.append(
                    (
                        "A nehézség 1 és 25 "
                        "közötti lehet."
                    )
                )

            if (
                correct_answer is not None
                and correct_answer
                not in range(1, 6)
            ):
                row_errors.append(
                    (
                        "A helyes válasz 1 és 5 "
                        "közötti lehet."
                    )
                )

            grade_numbers = []

            for grade_value in normalized_row[
                "evfolyamok"
            ].split("|"):
                grade_value = grade_value.strip()

                if not grade_value:
                    continue

                try:
                    grade_number = int(
                        grade_value
                    )

                except ValueError:
                    row_errors.append(
                        (
                            "Érvénytelen évfolyam: "
                            f"{grade_value}."
                        )
                    )
                    continue

                if grade_number not in grade_by_number:
                    row_errors.append(
                        (
                            "Nem létező évfolyam: "
                            f"{grade_number}."
                        )
                    )
                else:
                    grade_numbers.append(
                        grade_number
                    )

            if not grade_numbers:
                row_errors.append(
                    (
                        "Legalább egy évfolyam "
                        "szükséges."
                    )
                )

            topic_names = []

            for topic_value in normalized_row[
                "temakorok"
            ].split("|"):
                topic_value = topic_value.strip()

                if not topic_value:
                    continue

                topic_key = topic_value.casefold()

                if topic_key not in topic_by_name:
                    row_errors.append(
                        (
                            "Nem létező témakör: "
                            f"{topic_value}."
                        )
                    )
                else:
                    topic_names.append(
                        topic_by_name[
                            topic_key
                        ].name
                    )

            if not topic_names:
                row_errors.append(
                    (
                        "Legalább egy témakör "
                        "szükséges."
                    )
                )

            if not normalized_row["feladat"]:
                row_errors.append(
                    "A feladat szövege kötelező."
                )

            answer_texts = [
                normalized_row[
                    f"valasz{position}"
                ]
                for position in range(1, 6)
            ]

            if any(
                not answer_text
                for answer_text in answer_texts
            ):
                row_errors.append(
                    (
                        "Mind az öt "
                        "válaszlehetőséget "
                        "ki kell tölteni."
                    )
                )

            is_active = parse_boolean(
                normalized_row["aktiv"]
            )

            if is_active is None:
                row_errors.append(
                    (
                        "Az aktív mező értéke "
                        "legyen igen vagy nem."
                    )
                )

            preview_row = {
                "line": line_number,
                "source_year": source_year_number,
                "source_year_object": (
                    source_year_by_number.get(
                        source_year_number
                    )
                ),
                "original_position": (
                    original_position
                ),
                "difficulty": difficulty,
                "grades": grade_numbers,
                "grade_objects": [
                    grade_by_number[
                        grade_number
                    ]
                    for grade_number
                    in grade_numbers
                    if grade_number
                    in grade_by_number
                ],
                "topics": topic_names,
                "topic_objects": [
                    topic_by_name[
                        topic_name.casefold()
                    ]
                    for topic_name
                    in topic_names
                    if topic_name.casefold()
                    in topic_by_name
                ],
                "question_text": normalized_row[
                    "feladat"
                ],
                "answer_texts": answer_texts,
                "correct_answer": correct_answer,
                "explanation": normalized_row[
                    "magyarazat"
                ],
                "is_active": is_active,
                "errors": row_errors,
            }

            preview_rows.append(
                preview_row
            )

            if row_errors:
                import_errors.append(
                    {
                        "line": line_number,
                        "messages": row_errors,
                    }
                )

        # Fontos: ez már a for cikluson kívül van.
        if not preview_rows:
            flash(
                "A CSV nem tartalmaz adatsort.",
                "error",
            )

        elif import_errors:
            flash(
                (
                    f"{len(import_errors)} hibás "
                    "CSV-sor található. "
                    "Az import nem történt meg."
                ),
                "error",
            )

        elif action == "import":
            try:
                imported_questions = []

                for row in preview_rows:
                    question = Question(
                        source_year=row[
                            "source_year_object"
                        ],
                        original_position=row[
                            "original_position"
                        ],
                        difficulty=row[
                            "difficulty"
                        ],
                        question_text=row[
                            "question_text"
                        ],
                        explanation=(
                            row["explanation"]
                            or None
                        ),
                        is_active=row[
                            "is_active"
                        ],
                    )

                    question.grades = row[
                        "grade_objects"
                    ]

                    question.topics = row[
                        "topic_objects"
                    ]

                    for (
                        position,
                        answer_text,
                    ) in enumerate(
                        row["answer_texts"],
                        start=1,
                    ):
                        question.answer_options.append(
                            AnswerOption(
                                original_position=(
                                    position
                                ),
                                answer_text=(
                                    answer_text
                                ),
                                is_correct=(
                                    position
                                    == row[
                                        "correct_answer"
                                    ]
                                ),
                            )
                        )

                    db.session.add(
                        question
                    )

                    imported_questions.append(
                        question
                    )

                db.session.flush()

                imported_summary = [
                    {
                        "line": row["line"],
                        "question_id": (
                            question.id
                        ),
                        "image_filename": (
                            question.image_filename
                        ),
                    }
                    for row, question in zip(
                        preview_rows,
                        imported_questions,
                    )
                ]

                db.session.commit()

            except Exception:
                db.session.rollback()

                current_app.logger.exception(
                    (
                        "Hiba történt a "
                        "CSV-import során."
                    )
                )

                flash(
                    (
                        "Az importálás közben "
                        "hiba történt. Egyetlen "
                        "rekordot sem mentettünk el."
                    ),
                    "error",
                )

            else:
                return render_template(
                    (
                        "admin/"
                        "question_import_result.html"
                    ),
                    imported_summary=(
                        imported_summary
                    ),
                )

        else:
            flash(
                (
                    f"{len(preview_rows)} sor "
                    "ellenőrzése sikeres. "
                    "Az adatok még nem kerültek "
                    "az adatbázisba."
                ),
                "success",
            )

    return render_template(
        "admin/question_import.html",
        preview_rows=preview_rows,
        import_errors=import_errors,
    )
