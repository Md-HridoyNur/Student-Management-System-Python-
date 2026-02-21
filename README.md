# Student Management System (Python)

This is a **Python-based Student Management System (SMS)** built using **Flask** and **SQLite**.  
It allows managing **students, grades, and attendance** through a simple **web dashboard**.

---

## 🔹 Features

- CRUD operations for **students, grades, and attendance**  
- Dashboard displays:  
  - Total number of students  
  - Average score  
  - Attendance rate  
- Frontend built with **HTML, CSS, and JavaScript**  
- JSON APIs for frontend consumption  
- **SQLite** database (created automatically on first run)

---

## 🔹 Project Structure
Student Management System/
│
├── app.py              # Flask backend & API logic
├── students.db         # SQLite database (auto-generated)
└── static/
    └── index.html      # Frontend web dashboard

---

## 🔹 Run Instructions

1. **Navigate to the project folder:**
```bash
cd StudentManagementSystem

pip install flask

python app.py

http://127.0.0.1:5050
