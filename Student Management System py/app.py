from flask import Flask, jsonify, send_from_directory, g
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "students.db")

# ---------------- DATABASE ----------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        student_id TEXT UNIQUE NOT NULL,
        class TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        score REAL,
        grade TEXT,
        date TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        date TEXT,
        status TEXT,
        subject TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    );
    """)

    if c.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO students (name, student_id, class) VALUES (?,?,?)",
            [
                ("Alice Johnson", "STU001", "Grade 10"),
                ("Bob Martinez", "STU002", "Grade 11"),
                ("Carol White", "STU003", "Grade 10")
            ]
        )

    if c.execute("SELECT COUNT(*) FROM grades").fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO grades (student_id, subject, score, grade, date) VALUES (?,?,?,?,?)",
            [
                (1, "Math", 85.5, "B", "2023-10-01"),
                (2, "Science", 92.0, "A", "2023-10-02"),
                (3, "History", 78.0, "C", "2023-10-03")
            ]
        )

    if c.execute("SELECT COUNT(*) FROM attendance").fetchone()[0] == 0:
        c.executemany(
            "INSERT INTO attendance (student_id, date, status, subject) VALUES (?,?,?,?)",
            [
                (1, "2023-10-01", "present", "Math"),
                (2, "2023-10-02", "absent", "Science")
            ]
        )

    conn.commit()
    conn.close()

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return send_from_directory(os.path.join(BASE_DIR, "static"), "index.html")

@app.route("/api/dashboard")
def dashboard():
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    avg = db.execute("SELECT AVG(score) FROM grades").fetchone()[0] or 0
    present = db.execute("SELECT COUNT(*) FROM attendance WHERE status='present'").fetchone()[0]
    total_att = db.execute("SELECT COUNT(*) FROM attendance").fetchone()[0]

    return jsonify({
        "total_students": total,
        "avg_score": round(avg, 1),
        "attendance_rate": round((present / total_att) * 100, 1) if total_att else 0
    })

@app.route("/api/students")
def students():
    db = get_db()
    rows = db.execute("""
        SELECT s.*, COALESCE(AVG(g.score), 0) avg_score
        FROM students s
        LEFT JOIN grades g ON g.student_id = s.id
        GROUP BY s.id
        ORDER BY s.name
    """).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/grades")
def grades():
    db = get_db()
    rows = db.execute("""
        SELECT g.*, s.name student_name
        FROM grades g
        JOIN students s ON s.id = g.student_id
        ORDER BY g.date DESC
    """).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/attendance")
def attendance():
    db = get_db()
    rows = db.execute("""
        SELECT a.*, s.name student_name
        FROM attendance a
        JOIN students s ON s.id = a.student_id
        ORDER BY a.date DESC
    """).fetchall()
    return jsonify([dict(r) for r in rows])

# ---------------- MAIN ----------------
if __name__ == "__main__":
    # Ensure DB exists even if we restart
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True, port=5050)