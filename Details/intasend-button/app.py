import os
import mysql.connector
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
import json
import requests

# Initialize Flask app
app = Flask(__name__)

# --- Configuration ---
# Use environment variables for sensitive information
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "your-super-secret-key")
app.config["API_KEY"] = os.environ.get("API_KEY", "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")
app.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST", "localhost")
app.config["MYSQL_USER"] = os.environ.get("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD", "Saidi_868")
app.config["MYSQL_DB"] = os.environ.get("MYSQL_DB", "reports_db")

# Initialize extensions
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# --- Database Connection Pool ---
# Using a connection pool to manage connections efficiently
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="db_pool",
        pool_size=5,
        host=app.config["MYSQL_HOST"],
        user=app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"],
        database=app.config["MYSQL_DB"]
    )
except mysql.connector.Error as err:
    print(f"Error connecting to MySQL: {err}")
    exit(1)

def get_db_connection():
    """Gets a connection from the pool."""
    return db_pool.get_connection()

# --- Utility Functions ---
def get_user_id_by_email(cursor, email):
    """Fetches user ID by email."""
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    return result[0] if result else None

def send_message_notification(phone_number, message):
    """
    Sends a notification using a third-party service like Intasend.
    NOTE: This is a conceptual function. You would need to replace this
    with the actual API call logic for your chosen service.
    """
    # Replace with the actual API endpoint and your API key
    api_url = "https://sandbox.intasend.com/api/v1/messaging/sms/send/"
    headers = {
        "Authorization": f"Bearer {app.config['API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "phone_number": phone_number,
        "message": message
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        print(f"SMS sent successfully to {phone_number}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending SMS: {e}")

# --- API Endpoints ---

@app.route("/register", methods=["POST"])
def register():
    """Endpoint for user registration."""
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")
    id_number = data.get("id_number")
    institution_id = data.get("institution_id")

    if not all([name, email, password, role, id_number]):
        return jsonify({"msg": "Missing required fields"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Insert into users table
        cursor.execute(
            "INSERT INTO users (institution_id, id_number, name, email, password_hash, role) VALUES (%s, %s, %s, %s, %s, %s)",
            (institution_id, id_number, name, email, hashed_password, role)
        )
        user_id = cursor.lastrowid
        
        # Insert into specific role table
        if role == 'student':
            admission_number = data.get("admission_number")
            course = data.get("course")
            year_of_study = data.get("year_of_study")
            department = data.get("department")
            if not all([admission_number, course, year_of_study, department]):
                conn.rollback()
                return jsonify({"msg": "Missing student-specific fields"}), 400
            cursor.execute(
                "INSERT INTO students (id, admission_number, course, year_of_study, department) VALUES (%s, %s, %s, %s, %s)",
                (user_id, admission_number, course, year_of_study, department)
            )
        elif role == 'lecturer':
            staff_number = data.get("staff_number")
            department = data.get("department")
            specialization = data.get("specialization")
            if not all([staff_number, department, specialization]):
                conn.rollback()
                return jsonify({"msg": "Missing lecturer-specific fields"}), 400
            cursor.execute(
                "INSERT INTO lecturers (id, staff_number, department, specialization) VALUES (%s, %s, %s, %s)",
                (user_id, staff_number, department, specialization)
            )
        
        conn.commit()
        return jsonify({"msg": "User registered successfully"}), 201

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"msg": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    """Endpoint for user login."""
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"msg": "Missing email or password"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, password_hash, role, name FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user["password_hash"], password):
            access_token = create_access_token(identity={"id": user["id"], "role": user["role"], "name": user["name"]})
            return jsonify(access_token=access_token)
        
        return jsonify({"msg": "Invalid credentials"}), 401

    except mysql.connector.Error as err:
        return jsonify({"msg": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

# --- Student Endpoints ---

@app.route("/student/templates", methods=["GET"])
@jwt_required()
def get_lab_templates():
    """Student endpoint to get all available lab templates."""
    current_user = get_jwt_identity()
    if current_user["role"] != "student":
        return jsonify({"msg": "Access denied"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, lecturer_id, title, description, created_at FROM lab_templates")
        templates = cursor.fetchall()
        return jsonify(templates)
    except mysql.connector.Error as err:
        return jsonify({"msg": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/student/submit", methods=["POST"])
@jwt_required()
def submit_lab_report():
    """Student endpoint to submit a lab report."""
    current_user = get_jwt_identity()
    if current_user["role"] != "student":
        return jsonify({"msg": "Access denied"}), 403

    data = request.json
    template_id = data.get("template_id")
    submission_values = data.get("submission_values")

    if not all([template_id, submission_values]):
        return jsonify({"msg": "Missing template_id or submission_values"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO submissions (student_id, template_id, submission_values, status) VALUES (%s, %s, %s, 'pending')",
            (current_user["id"], template_id, json.dumps(submission_values))
        )
        conn.commit()
        return jsonify({"msg": "Submission successful"}), 201
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"msg": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/student/submissions", methods=["GET"])
@jwt_required()
def get_student_submissions():
    """Student endpoint to view their submissions."""
    current_user = get_jwt_identity()
    if current_user["role"] != "student":
        return jsonify({"msg": "Access denied"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM submissions WHERE student_id = %s", (current_user["id"],))
        submissions = cursor.fetchall()
        return jsonify(submissions)
    except mysql.connector.Error as err:
        return jsonify({"msg": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

# --- Lecturer Endpoints ---

@app.route("/lecturer/templates", methods=["POST"])
@jwt_required()
def create_lab_template():
    """Lecturer endpoint to create a new lab template."""
    current_user = get_jwt_identity()
    if current_user["role"] != "lecturer":
        return jsonify({"msg": "Access denied"}), 403

    data = request.json
    title = data.get("title")
    description = data.get("description")
    fields = data.get("fields")

    if not all([title, description, fields]):
        return jsonify({"msg": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO lab_templates (lecturer_id, title, description, fields) VALUES (%s, %s, %s, %s)",
            (current_user["id"], title, description, json.dumps(fields))
        )
        conn.commit()
        return jsonify({"msg": "Template created successfully"}), 201
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"msg": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/lecturer/submissions", methods=["GET"])
@jwt_required()
def get_lecturer_submissions():
    """Lecturer endpoint to get submissions for their templates."""
    current_user = get_jwt_identity()
    if current_user["role"] != "lecturer":
        return jsonify({"msg": "Access denied"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT s.*, u.name as student_name FROM submissions s JOIN lab_templates lt ON s.template_id = lt.id JOIN users u ON s.student_id = u.id WHERE lt.lecturer_id = %s",
            (current_user["id"],)
        )
        submissions = cursor.fetchall()
        return jsonify(submissions)
    except mysql.connector.Error as err:
        return jsonify({"msg": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/lecturer/grade/<int:submission_id>", methods=["PUT"])
@jwt_required()
def grade_submission(submission_id):
    """Lecturer endpoint to grade a submission."""
    current_user = get_jwt_identity()
    if current_user["role"] != "lecturer":
        return jsonify({"msg": "Access denied"}), 403

    data = request.json
    grade = data.get("grade")
    feedback = data.get("feedback")

    if grade is None:
        return jsonify({"msg": "Missing grade"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verify the submission belongs to a template created by this lecturer
        cursor.execute(
            "SELECT 1 FROM submissions s JOIN lab_templates lt ON s.template_id = lt.id WHERE s.id = %s AND lt.lecturer_id = %s",
            (submission_id, current_user["id"])
        )
        if not cursor.fetchone():
            return jsonify({"msg": "Submission not found or access denied"}), 404

        # Get the student's ID and name for the notification
        cursor.execute(
            "SELECT u.id, u.name, u.email FROM submissions s JOIN users u ON s.student_id = u.id WHERE s.id = %s",
            (submission_id,)
        )
        student_info = cursor.fetchone()

        # Update the submission with the grade and feedback
        cursor.execute(
            "UPDATE submissions SET grade = %s, feedback = %s, status = 'graded' WHERE id = %s",
            (grade, feedback, submission_id)
        )
        conn.commit()
        
        # Call the notification function (conceptual)
        # In a real app, you would need the student's phone number
        # You would also need a way to get the lecturer's name to include in the message
        # send_message_notification(student_phone_number, f"Hello {student_info['name']}, your lab report has been graded. Your score is {grade}.")
        
        return jsonify({"msg": "Submission graded successfully"}), 200
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"msg": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

# --- Admin Endpoints ---

@app.route("/admin/users", methods=["GET"])
@jwt_required()
def get_all_users():
    """Admin endpoint to get all users."""
    current_user = get_jwt_identity()
    if current_user["role"] != "admin":
        return jsonify({"msg": "Access denied"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, email, role, created_at FROM users")
        users = cursor.fetchall()
        return jsonify(users)
    except mysql.connector.Error as err:
        return jsonify({"msg": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/admin/institution", methods=["POST"])
@jwt_required()
def create_institution():
    """Admin endpoint to create a new institution."""
    current_user = get_jwt_identity()
    if current_user["role"] != "admin":
        return jsonify({"msg": "Access denied"}), 403

    data = request.json
    name = data.get("name")
    address = data.get("address")
    contact_email = data.get("contact_email")

    if not name:
        return jsonify({"msg": "Missing institution name"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO institutions (name, address, contact_email) VALUES (%s, %s, %s)",
            (name, address, contact_email)
        )
        conn.commit()
        return jsonify({"msg": "Institution created successfully"}), 201
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"msg": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

# --- Main block to run the app ---
if __name__ == "__main__":
    app.run(debug=True)
