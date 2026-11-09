from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # Replace with your MySQL username
        password=os.environ["DB_PASSWORD"],
        database="fitness_center"
    )

# ==================== PAGE 1: MEMBERS (FIRST PAGE) ====================
@app.route("/", methods=["GET", "POST"])
@app.route("/members", methods=["GET", "POST"])
def members_page():
    if request.method == "POST":
        session["member_id"] = request.form.get("member_id")
        return redirect(url_for("members_page"))

    member_id = session.get("member_id", 2)
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

    cursor.close()
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
