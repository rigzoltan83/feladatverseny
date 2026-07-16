from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    request,
    send_from_directory,
    url_for,
)

from app.extensions import db
from app.models import Question


media_bp = Blueprint(
    "admin_media",
    __name__,
    url_prefix="/admin",
)


def get_question_image_path(
    question: Question,
) -> Path:
    return (
        Path(current_app.config["MEDIA_ROOT"])
        / "questions"
        / question.image_filename
    )


@media_bp.get("/media/questions/<path:filename>")
def question_image(filename: str):
    media_root = Path(
        current_app.config["MEDIA_ROOT"]
    )

    return send_from_directory(
        media_root / "questions",
        filename,
    )


@media_bp.post("/questions/<int:question_id>/image")
def question_image_upload(question_id: int):
    question = db.get_or_404(
        Question,
        question_id,
    )

    uploaded_file = request.files.get("image")

    if (
        uploaded_file is None
        or not uploaded_file.filename
    ):
        flash(
            "Nem választottál ki képfájlt.",
            "error",
        )

        return redirect(
            url_for(
                "admin.question_detail",
                question_id=question.id,
            )
        )

    filename_lower = (
        uploaded_file.filename
        .strip()
        .lower()
    )

    if not filename_lower.endswith(
        (".jpg", ".jpeg")
    ):
        flash(
            "Csak JPG vagy JPEG kép tölthető fel.",
            "error",
        )

        return redirect(
            url_for(
                "admin.question_detail",
                question_id=question.id,
            )
        )

    image_path = get_question_image_path(
        question
    )

    image_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    uploaded_file.save(image_path)

    flash(
        f"A kép feltöltve: {question.image_filename}",
        "success",
    )

    return redirect(
        url_for(
            "admin.question_detail",
            question_id=question.id,
        )
    )


@media_bp.post(
    "/questions/<int:question_id>/image/delete"
)
def question_image_delete(question_id: int):
    question = db.get_or_404(
        Question,
        question_id,
    )

    image_path = get_question_image_path(
        question
    )

    if image_path.is_file():
        image_path.unlink()

        flash(
            "A feladat képét töröltük.",
            "success",
        )
    else:
        flash(
            "A feladathoz nem tartozik kép.",
            "error",
        )

    return redirect(
        url_for(
            "admin.question_detail",
            question_id=question.id,
        )
    )
