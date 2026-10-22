"""
app.py
Main Flask application for Prakriti AI - Smart Women's Health Assistant.
Integrates SQLite database, user authentication, ML models, and health tracking APIs.
"""

import os
import re
import json
import secrets
from datetime import datetime, date
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, Response, send_file
)
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, init_db
from ml.inference import (
    predict_cycle_health, predict_sleep_wellness, evaluate_pcos_symptoms
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize database tables on startup
init_db()

# Cached healthy recipes for fast wellness recommendations
WELLNESS_RECIPES = [
    {
        "name": "Methi Moong Dal Subzi",
        "diet": "High Protein Vegetarian",
        "benefits": "Fenugreek (Methi) supports insulin sensitivity; Moong Dal provides plant protein.",
        "cook_time": "25 mins"
    },
    {
        "name": "Sprouted Moong Salad with Lemon & Herbs",
        "diet": "Diabetic Friendly",
        "benefits": "Low glycemic index, rich in prebiotic fiber and micronutrients.",
        "cook_time": "15 mins"
    },
    {
        "name": "Masala Karela (Bitter Gourd) Stir Fry",
        "diet": "Diabetic Friendly",
        "benefits": "Contains polypeptide-p and charantin which support glucose metabolism.",
        "cook_time": "30 mins"
    },
    {
        "name": "Spinach & Flaxseed Roti with Curd",
        "diet": "Vegetarian",
        "benefits": "Omega-3 fatty acids and lignans in flaxseeds support hormone balance.",
        "cook_time": "20 mins"
    },
    {
        "name": "Ragi (Finger Millet) Vegetable Porridge",
        "diet": "High Fiber Vegetarian",
        "benefits": "High calcium and slow-digesting complex carbohydrates.",
        "cook_time": "20 mins"
    },
    {
        "name": "Roasted Chickpea & Cucumber Chaat",
        "diet": "High Protein Snack",
        "benefits": "Satisfying protein and fiber snack to prevent afternoon energy crashes.",
        "cook_time": "10 mins"
    }
]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def current_user():
    if "user_id" not in session:
        return None
    with get_db_connection() as conn:
        return conn.execute("SELECT id, name, email, age, height_cm, weight_kg, bmi FROM users WHERE id = ?", (session["user_id"],)).fetchone()

@app.context_processor
def inject_globals():
    return {
        "user": current_user(),
        "now_year": datetime.now().year
    }

# ==============================================================================
# AUTHENTICATION ROUTES
# ==============================================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        age = request.form.get("age", "").strip()
        height = request.form.get("height_cm", "").strip()
        weight = request.form.get("weight_kg", "").strip()

        # Validation
        if not name or len(name) < 2:
            flash("Please enter a valid name (at least 2 characters).", "error")
            return render_template("register.html")
            
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            flash("Please enter a valid email address.", "error")
            return render_template("register.html")

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template("register.html")

        # Optional demographic calculation
        age_val = int(age) if age and age.isdigit() and 10 <= int(age) <= 100 else None
        h_val = float(height) if height and re.match(r"^\d+(\.\d+)?$", height) else None
        w_val = float(weight) if weight and re.match(r"^\d+(\.\d+)?$", weight) else None
        bmi_val = None
        if h_val and w_val and h_val > 50:
            bmi_val = round(w_val / ((h_val / 100) ** 2), 1)

        try:
            with get_db_connection() as conn:
                existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
                if existing:
                    flash("An account with this email already exists. Please log in.", "error")
                    return render_template("register.html")

                pw_hash = generate_password_hash(password)
                cursor = conn.execute(
                    """INSERT INTO users (name, email, password_hash, age, height_cm, weight_kg, bmi)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (name, email, pw_hash, age_val, h_val, w_val, bmi_val)
                )
                user_id = cursor.lastrowid
                session.clear()
                session["user_id"] = user_id
                session["user_name"] = name
                flash("Welcome to Prakriti AI! Your account has been created.", "success")
                return redirect(url_for("dashboard"))
        except Exception as e:
            flash(f"An error occurred during registration: {str(e)}", "error")
            return render_template("register.html")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template("login.html")

        with get_db_connection() as conn:
            user = conn.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("dashboard"))
        else:
            flash("Invalid email or password. Please try again.", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out securely.", "info")
    return redirect(url_for("home"))

# ==============================================================================
# MAIN WEB PAGES
# ==============================================================================

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/awareness")
def awareness():
    return render_template("awareness.html")

@app.route("/dashboard")
@login_required
def dashboard():
    u = current_user()
    with get_db_connection() as conn:
        cycle_records = conn.execute(
            "SELECT * FROM cycle_logs WHERE user_id = ? ORDER BY start_date DESC LIMIT 6",
            (u["id"],)
        ).fetchall()
        latest_assessment = conn.execute(
            "SELECT * FROM pcos_assessments WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (u["id"],)
        ).fetchone()
        latest_wellness = conn.execute(
            "SELECT * FROM wellness_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (u["id"],)
        ).fetchone()
        consultations = conn.execute(
            "SELECT * FROM consultation_requests WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
            (u["id"],)
        ).fetchall()

    return render_template(
        "dashboard.html",
        user=u,
        cycle_records=cycle_records,
        latest_assessment=latest_assessment,
        latest_wellness=latest_wellness,
        consultations=consultations
    )

@app.route("/cycle")
@login_required
def cycle():
    u = current_user()
    with get_db_connection() as conn:
        history = conn.execute(
            "SELECT * FROM cycle_logs WHERE user_id = ? ORDER BY start_date DESC LIMIT 10",
            (u["id"],)
        ).fetchall()
    return render_template("cycle.html", user=u, history=history)

@app.route("/assessment")
@login_required
def assessment():
    u = current_user()
    with get_db_connection() as conn:
        history = conn.execute(
            "SELECT * FROM pcos_assessments WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
            (u["id"],)
        ).fetchall()
    return render_template("assessment.html", user=u, history=history)

@app.route("/wellness")
@login_required
def wellness():
    u = current_user()
    with get_db_connection() as conn:
        history = conn.execute(
            "SELECT * FROM wellness_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 6",
            (u["id"],)
        ).fetchall()
    return render_template("wellness.html", user=u, history=history, recipes=WELLNESS_RECIPES)

# ==============================================================================
# RESTFUL APIS FOR HEALTH TRACKING & ML PREDICTIONS
# ==============================================================================

@app.route("/api/cycle/log", methods=["POST"])
@login_required
def api_cycle_log():
    try:
        data = request.get_json() or request.form
        user_id = session["user_id"]
        start_date = data.get("start_date")
        end_date = data.get("end_date") or None
        cycle_length = int(data.get("cycle_length", 28))
        menses_length = int(data.get("menses_length", 5))
        pain_level = int(data.get("pain_level", 0))
        flow = data.get("flow_intensity", "Moderate")
        symptoms = data.get("symptoms", "")
        notes = data.get("notes", "")

        # Bounds validation
        if not start_date:
            return jsonify({"success": False, "error": "Start date is required."}), 400
        if not (10 <= cycle_length <= 100):
            return jsonify({"success": False, "error": "Cycle length must be between 10 and 100 days."}), 400
        if not (1 <= menses_length <= 20):
            return jsonify({"success": False, "error": "Menses length must be between 1 and 20 days."}), 400
        if not (0 <= pain_level <= 10):
            return jsonify({"success": False, "error": "Pain level must be between 0 and 10."}), 400

        # Fetch user baseline for model
        with get_db_connection() as conn:
            u = conn.execute("SELECT age, bmi FROM users WHERE id = ?", (user_id,)).fetchone()
            # Calculate historical averages if available
            avg_cycle = conn.execute("SELECT AVG(cycle_length) as avg_c FROM cycle_logs WHERE user_id = ?", (user_id,)).fetchone()
            mean_cycle = avg_cycle["avg_c"] if (avg_cycle and avg_cycle["avg_c"]) else cycle_length

        age = u["age"] if (u and u["age"]) else 24
        bmi = u["bmi"] if (u and u["bmi"]) else 22.5
        total_menses_score = 10 if flow == "Moderate" else (5 if flow == "Light" else 15)

        # Call Cycle ML pipeline
        pred_res = predict_cycle_health(
            age=age,
            bmi=bmi,
            mean_cycle_length=mean_cycle,
            length_of_menses=menses_length,
            mean_menses_length=menses_length,
            total_menses_score=total_menses_score,
            current_cycle_length=cycle_length
        )

        with get_db_connection() as conn:
            conn.execute(
                """INSERT INTO cycle_logs
                   (user_id, start_date, end_date, cycle_length, menses_length, pain_level,
                    flow_intensity, symptoms, predicted_regularity, regularity_confidence,
                    predicted_ovulation_day, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, start_date, end_date, cycle_length, menses_length, pain_level,
                 flow, symptoms, pred_res["predicted_regularity"], pred_res["confidence"],
                 pred_res["estimated_ovulation_day"], notes)
            )

        return jsonify({
            "success": True,
            "prediction": pred_res,
            "message": "Menstrual cycle record saved and evaluated successfully."
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/assessment/evaluate", methods=["POST"])
@login_required
def api_assessment_evaluate():
    try:
        data = request.get_json() or request.form
        user_id = session["user_id"]
        age = int(data.get("age", 22))
        cycle_length = int(data.get("cycle_length", 28))
        primary_concern = data.get("concern", "General Wellness")
        symptoms = data.get("symptoms", [])
        if isinstance(symptoms, str):
            try:
                symptoms = json.loads(symptoms)
            except Exception:
                symptoms = [s.strip() for s in symptoms.split(",") if s.strip()]

        pain = int(data.get("pain", 0))
        flow = data.get("flow", "Moderate")
        sleep = data.get("sleep", "Average")

        # Run non-diagnostic PCOS symptom assessment
        eval_result = evaluate_pcos_symptoms(
            age=age,
            cycle_length=cycle_length,
            primary_concern=primary_concern,
            symptoms_list=symptoms,
            pain_level=pain,
            flow_intensity=flow,
            sleep_quality=sleep
        )

        symptoms_str = json.dumps(symptoms)
        with get_db_connection() as conn:
            conn.execute(
                """INSERT INTO pcos_assessments
                   (user_id, age, cycle_length, primary_concern, symptoms_list, pain_level,
                    flow_intensity, sleep_quality, screening_score, risk_level,
                    medical_assessment, ayurvedic_perspective, recommendations, disclaimer)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, age, cycle_length, primary_concern, symptoms_str, pain, flow, sleep,
                 eval_result["screening_score"], eval_result["risk_level"],
                 eval_result["medical_assessment"], eval_result["ayurvedic_perspective"],
                 eval_result["recommendations"], eval_result["disclaimer"])
            )

        return jsonify({
            "success": True,
            "result": eval_result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/wellness/predict", methods=["POST"])
@login_required
def api_wellness_predict():
    try:
        data = request.get_json() or request.form
        user_id = session["user_id"]
        
        age = int(data.get("age", 25))
        gender = data.get("gender", "Female")
        sleep_dur = float(data.get("sleep_duration", 7.0))
        quality = int(data.get("quality_of_sleep", 7))
        activity = int(data.get("activity_minutes", 45))
        stress = int(data.get("stress_level", 5))
        bmi_cat = data.get("bmi_category", "Normal")
        heart_rate = int(data.get("heart_rate", 72))
        steps = int(data.get("daily_steps", 7500))
        systolic = int(data.get("systolic_bp", 120))
        diastolic = int(data.get("diastolic_bp", 80))
        notes = data.get("notes", "")

        # Bounds validation
        if not (3.0 <= sleep_dur <= 14.0):
            return jsonify({"success": False, "error": "Sleep duration must be between 3 and 14 hours."}), 400
        if not (1 <= quality <= 10):
            return jsonify({"success": False, "error": "Quality of sleep must be between 1 and 10."}), 400
        if not (1 <= stress <= 10):
            return jsonify({"success": False, "error": "Stress level must be between 1 and 10."}), 400

        pred_res = predict_sleep_wellness(
            age=age,
            gender=gender,
            sleep_duration=sleep_dur,
            quality_of_sleep=quality,
            activity_minutes=activity,
            stress_level=stress,
            bmi_category=bmi_cat,
            heart_rate=heart_rate,
            daily_steps=steps,
            systolic_bp=systolic,
            diastolic_bp=diastolic
        )

        probs_json = json.dumps(pred_res["class_probabilities"])
        with get_db_connection() as conn:
            conn.execute(
                """INSERT INTO wellness_logs
                   (user_id, gender, sleep_duration, quality_of_sleep, activity_minutes,
                    stress_level, bmi_category, heart_rate, daily_steps, systolic_bp,
                    diastolic_bp, predicted_disorder, confidence, probabilities_json, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, gender, sleep_dur, quality, activity, stress, bmi_cat,
                 heart_rate, steps, systolic, diastolic, pred_res["predicted_disorder"],
                 pred_res["confidence"], probs_json, notes)
            )

        return jsonify({
            "success": True,
            "prediction": pred_res
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/dashboard-data")
@login_required
def api_dashboard_data():
    user_id = session["user_id"]
    with get_db_connection() as conn:
        cycles = conn.execute(
            "SELECT start_date, cycle_length, menses_length, pain_level FROM cycle_logs WHERE user_id = ? ORDER BY start_date ASC LIMIT 12",
            (user_id,)
        ).fetchall()
        wellness = conn.execute(
            "SELECT date(created_at) as log_date, sleep_duration, quality_of_sleep, stress_level FROM wellness_logs WHERE user_id = ? ORDER BY created_at ASC LIMIT 12",
            (user_id,)
        ).fetchall()

    cycle_labels = [c["start_date"] for c in cycles]
    cycle_lengths = [c["cycle_length"] for c in cycles]
    pain_levels = [c["pain_level"] for c in cycles]

    wellness_labels = [w["log_date"] for w in wellness]
    sleep_durations = [w["sleep_duration"] for w in wellness]
    sleep_qualities = [w["quality_of_sleep"] for w in wellness]
    stress_levels = [w["stress_level"] for w in wellness]

    return jsonify({
        "cycles": {
            "labels": cycle_labels,
            "cycle_lengths": cycle_lengths,
            "pain_levels": pain_levels
        },
        "wellness": {
            "labels": wellness_labels,
            "sleep_durations": sleep_durations,
            "sleep_qualities": sleep_qualities,
            "stress_levels": stress_levels
        }
    })

@app.route("/api/consultation/request", methods=["POST"])
@login_required
def api_consultation_request():
    try:
        data = request.get_json() or request.form
        user_id = session["user_id"]
        doc_name = data.get("doctor_name", "Dr. Ananya Sharma, MD (OB/GYN)")
        specialty = data.get("specialty", "Gynecology & Reproductive Health")
        pref_date = data.get("preferred_date", str(date.today()))
        notes = data.get("notes", "")

        with get_db_connection() as conn:
            conn.execute(
                """INSERT INTO consultation_requests (user_id, doctor_name, specialty, preferred_date, notes)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, doc_name, specialty, pref_date, notes)
            )

        return jsonify({"success": True, "message": "Consultation request recorded successfully."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==============================================================================
# REPORT DOWNLOAD AND PRINTABLE VIEW
# ==============================================================================

@app.route("/report/view")
@login_required
def report_view():
    u = current_user()
    with get_db_connection() as conn:
        latest_assessment = conn.execute(
            "SELECT * FROM pcos_assessments WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (u["id"],)
        ).fetchone()
        recent_cycles = conn.execute(
            "SELECT * FROM cycle_logs WHERE user_id = ? ORDER BY start_date DESC LIMIT 5",
            (u["id"],)
        ).fetchall()
        latest_wellness = conn.execute(
            "SELECT * FROM wellness_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (u["id"],)
        ).fetchone()

    symptoms_list = []
    if latest_assessment and latest_assessment["symptoms_list"]:
        try:
            symptoms_list = json.loads(latest_assessment["symptoms_list"])
        except Exception:
            symptoms_list = [latest_assessment["symptoms_list"]]

    return render_template(
        "report.html",
        user=u,
        assessment=latest_assessment,
        symptoms_list=symptoms_list,
        cycles=recent_cycles,
        wellness=latest_wellness,
        generated_date=datetime.now().strftime("%B %d, %Y")
    )

@app.route("/report/download")
@login_required
def report_download():
    u = current_user()
    with get_db_connection() as conn:
        latest_assessment = conn.execute(
            "SELECT * FROM pcos_assessments WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
            (u["id"],)
        ).fetchone()
        recent_cycles = conn.execute(
            "SELECT * FROM cycle_logs WHERE user_id = ? ORDER BY start_date DESC LIMIT 3",
            (u["id"],)
        ).fetchall()

    symptoms_text = "None recorded"
    if latest_assessment and latest_assessment["symptoms_list"]:
        try:
            s_list = json.loads(latest_assessment["symptoms_list"])
            symptoms_text = ", ".join(s_list) if s_list else "None selected"
        except Exception:
            symptoms_text = latest_assessment["symptoms_list"]

    report_lines = [
        "PRAKRITI AI - WOMEN'S HEALTH SCREENING & CONSULTATION SUMMARY",
        "=" * 65,
        f"Generated Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"Patient Name:   {u['name']}",
        f"Patient Email:  {u['email']}",
        f"Age:            {u['age'] or 'Not provided'}",
        f"BMI:            {u['bmi'] or 'Not provided'}",
        "",
        "PCOS/PCOD SYMPTOM-AWARENESS SCREENING",
        "-" * 40,
        f"Risk Level:     {latest_assessment['risk_level'] if latest_assessment else 'No assessment completed'}",
        f"Screening Score:{latest_assessment['screening_score'] if latest_assessment else 0}/11",
        f"Reported Symptoms: {symptoms_text}",
        "",
        "RECENT MENSTRUAL CYCLE RECORDS",
        "-" * 40
    ]

    if recent_cycles:
        for idx, c in enumerate(recent_cycles, 1):
            report_lines.append(
                f"Record {idx}: Start={c['start_date']} | Cycle Length={c['cycle_length']}d | "
                f"Menses={c['menses_length']}d | Pain={c['pain_level']}/10 | Flow={c['flow_intensity']} | Status={c['predicted_regularity']}"
            )
    else:
        report_lines.append("No cycle records logged yet.")

    report_lines.extend([
        "",
        "MEDICAL HEALTH ASSESSMENT & AYURVEDIC WELLNESS NOTES",
        "-" * 55,
        latest_assessment["medical_assessment"] if latest_assessment else "Consult a qualified physician.",
        "",
        latest_assessment["ayurvedic_perspective"] if latest_assessment else "",
        "",
        "=" * 65,
        "CRITICAL MEDICAL DISCLAIMER:",
        "This health summary is generated for educational awareness and doctor consultation.",
        "Prakriti AI DOES NOT diagnose PCOS, PCOD, or any medical condition.",
        "Please present this summary to a qualified gynecologist or healthcare professional.",
        "=" * 65
    ])

    content = "\n".join(report_lines)
    return Response(
        content,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment;filename=Prakriti_AI_Doctor_Report_{u['id']}.txt"}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
