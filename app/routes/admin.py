from flask import Blueprint, render_template

from app.models import Grade, Topic


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
)


@admin_bp.get("/")
def index():
    return render_template("admin/index.html")


@admin_bp.get("/grades")
def grades():
    grade_list = Grade.query.order_by(
        Grade.grade_number
    ).all()

    return render_template(
        "admin/grades.html",
        grades=grade_list,
    )

@admin_bp.get("/topics")
def topics():
    topic_list = Topic.query.order_by(
        Topic.name
    ).all()

    return render_template(
        "admin/topics.html",
        topics=topic_list,
    )
