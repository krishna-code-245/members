import os
import secrets

import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)


def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "fitness_center"),
    )


@app.route("/", methods=["GET", "POST"])
@app.route("/members", methods=["GET", "POST"])
def members_page():
    if request.method == "POST":
        session["member_id"] = request.form.get("member_id")
        return redirect(url_for("members_page"))

    member_id = session.get("member_id", 2)
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT m.*, t.name AS trainer_name, t.specialization
            FROM Members m
            LEFT JOIN Trainers t ON m.trainer_id = t.trainer_id
            WHERE m.member_id = %s
        """, (member_id,))
        member = cursor.fetchone()

        cursor.execute("""
            SELECT c.*, t.name AS trainer_name
            FROM Classes c
            LEFT JOIN Trainers t ON c.trainer_id = t.trainer_id
        """)
        classes = cursor.fetchall()

        cursor.execute("SELECT * FROM Payments WHERE member_id = %s", (member_id,))
        payments = cursor.fetchall()
    except mysql.connector.Error:
        app.logger.exception("Unable to load member data from MySQL")
        return render_template(
            "members.html",
            member=None,
            classes=[],
            payments=[],
            database_error=(
                "Member data is unavailable. Check that MySQL is running and "
                "the fitness_center database is configured."
            ),
        ), 503
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return render_template("members.html", member=member, classes=classes, payments=payments)


@app.route("/members/update_email", methods=["POST"])
def member_update_email():
    member_id = session.get("member_id", 2)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Members SET email = %s WHERE member_id = %s",
        (request.form["new_email"], member_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash("Member email updated successfully!", "success")
    return redirect(url_for("members_page"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
