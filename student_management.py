"""
STUDENT MANAGEMENT SYSTEM
Major Project: Database Management System using Python 3 and SQLite3

Features:
- Automatic SQLite database creation
- User registration, login and logout
- Two roles: Admin and Staff
- Role-based permissions
- Student and course CRUD operations
- Student-course enrollment (foreign-key relationship)
- Input validation and exception handling

Run:
    python student_management.py

First registered account becomes Admin. Later registrations become Staff.
"""

import sqlite3
import hashlib
import getpass
from pathlib import Path

DB_NAME = Path(__file__).with_name("student_management.db")


# -------------------- DATABASE --------------------

def get_connection():
    """Create a database connection and enable foreign-key checks."""
    connection = sqlite3.connect(DB_NAME)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    """Create all required tables if they do not already exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'staff'))
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK(age BETWEEN 5 AND 100),
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name TEXT NOT NULL UNIQUE,
                duration TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                enrollment_date TEXT NOT NULL DEFAULT (DATE('now')),
                UNIQUE(student_id, course_id),
                FOREIGN KEY(student_id) REFERENCES students(student_id)
                    ON DELETE CASCADE,
                FOREIGN KEY(course_id) REFERENCES courses(course_id)
                    ON DELETE CASCADE
            )
        """)


# -------------------- COMMON HELPERS --------------------

def password_digest(password):
    """Return a SHA-256 digest of a password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def read_nonempty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def read_integer(prompt, minimum=None, maximum=None):
    while True:
        try:
            value = int(input(prompt).strip())
            if minimum is not None and value < minimum:
                print(f"Enter a number greater than or equal to {minimum}.")
                continue
            if maximum is not None and value > maximum:
                print(f"Enter a number less than or equal to {maximum}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid whole number.")


def pause():
    input("\nPress Enter to continue...")


def print_table(headers, rows):
    if not rows:
        print("\nNo records found.")
        return

    widths = [len(str(header)) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(str(value)))

    line = "-+-".join("-" * width for width in widths)
    print("\n" + " | ".join(str(h).ljust(widths[i])
                            for i, h in enumerate(headers)))
    print(line)
    for row in rows:
        print(" | ".join(str(value).ljust(widths[i])
                         for i, value in enumerate(row)))


# -------------------- AUTHENTICATION --------------------

def register_user():
    print("\n--- USER REGISTRATION ---")
    username = read_nonempty("Choose username: ")

    while True:
        password = getpass.getpass("Choose password (minimum 6 characters): ")
        if len(password) >= 6:
            break
        print("Password must contain at least 6 characters.")

    try:
        with get_connection() as conn:
            user_count = conn.execute(
                "SELECT COUNT(*) FROM users"
            ).fetchone()[0]

            # The first account is Admin; later accounts are Staff.
            role = "admin" if user_count == 0 else "staff"
            conn.execute(
                "INSERT INTO users(username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_digest(password), role)
            )
        print(f"Registration successful. Your role is: {role.upper()}")
    except sqlite3.IntegrityError:
        print("That username already exists. Please choose another username.")
    except sqlite3.Error as error:
        print("Database error:", error)


def login_user():
    print("\n--- USER LOGIN ---")
    username = read_nonempty("Username: ")
    password = getpass.getpass("Password: ")

    try:
        with get_connection() as conn:
            user = conn.execute(
                """SELECT user_id, username, role
                   FROM users
                   WHERE username = ? AND password_hash = ?""",
                (username, password_digest(password))
            ).fetchone()

        if user:
            print(f"\nWelcome, {user[1]}! Role: {user[2].upper()}")
            return {"user_id": user[0], "username": user[1], "role": user[2]}

        print("Invalid username or password.")
    except sqlite3.Error as error:
        print("Database error:", error)

    return None


# -------------------- STUDENT CRUD --------------------

def add_student():
    print("\n--- ADD STUDENT ---")
    name = read_nonempty("Student name: ")
    age = read_integer("Age: ", 5, 100)
    email = read_nonempty("Email: ")
    phone = read_nonempty("Phone: ")

    if "@" not in email or "." not in email:
        print("Please enter a valid email address.")
        return

    try:
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO students(name, age, email, phone)
                   VALUES (?, ?, ?, ?)""",
                (name, age, email, phone)
            )
        print("Student added successfully.")
    except sqlite3.IntegrityError:
        print("A student with that email already exists.")
    except sqlite3.Error as error:
        print("Database error:", error)


def view_students():
    try:
        with get_connection() as conn:
            rows = conn.execute(
                """SELECT student_id, name, age, email, phone
                   FROM students ORDER BY student_id"""
            ).fetchall()
        print_table(["ID", "Name", "Age", "Email", "Phone"], rows)
    except sqlite3.Error as error:
        print("Database error:", error)


def update_student():
    print("\n--- UPDATE STUDENT ---")
    student_id = read_integer("Student ID to update: ", 1)

    try:
        with get_connection() as conn:
            student = conn.execute(
                "SELECT name, age, email, phone FROM students WHERE student_id = ?",
                (student_id,)
            ).fetchone()

            if not student:
                print("Student ID not found.")
                return

            print("Press Enter to keep the current value.")
            name = input(f"Name [{student[0]}]: ").strip() or student[0]

            age_text = input(f"Age [{student[1]}]: ").strip()
            if age_text:
                try:
                    age = int(age_text)
                    if not 5 <= age <= 100:
                        print("Age must be between 5 and 100.")
                        return
                except ValueError:
                    print("Age must be a whole number.")
                    return
            else:
                age = student[1]

            email = input(f"Email [{student[2]}]: ").strip() or student[2]
            phone = input(f"Phone [{student[3]}]: ").strip() or student[3]

            if "@" not in email or "." not in email:
                print("Please enter a valid email address.")
                return

            conn.execute(
                """UPDATE students
                   SET name = ?, age = ?, email = ?, phone = ?
                   WHERE student_id = ?""",
                (name, age, email, phone, student_id)
            )
        print("Student updated successfully.")
    except sqlite3.IntegrityError:
        print("That email address is already used by another student.")
    except sqlite3.Error as error:
        print("Database error:", error)


def delete_student():
    print("\n--- DELETE STUDENT ---")
    student_id = read_integer("Student ID to delete: ", 1)
    confirm = input("Are you sure you want to delete this student? (y/n): ").lower()

    if confirm != "y":
        print("Delete cancelled.")
        return

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM students WHERE student_id = ?", (student_id,)
            )
        print("Student deleted successfully." if cursor.rowcount
              else "Student ID not found.")
    except sqlite3.Error as error:
        print("Database error:", error)


# -------------------- COURSE CRUD --------------------

def add_course():
    print("\n--- ADD COURSE ---")
    course_name = read_nonempty("Course name: ")
    duration = read_nonempty("Course duration (e.g. 6 months): ")

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO courses(course_name, duration) VALUES (?, ?)",
                (course_name, duration)
            )
        print("Course added successfully.")
    except sqlite3.IntegrityError:
        print("That course already exists.")
    except sqlite3.Error as error:
        print("Database error:", error)


def view_courses():
    try:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT course_id, course_name, duration FROM courses ORDER BY course_id"
            ).fetchall()
        print_table(["Course ID", "Course Name", "Duration"], rows)
    except sqlite3.Error as error:
        print("Database error:", error)


def update_course():
    print("\n--- UPDATE COURSE ---")
    course_id = read_integer("Course ID to update: ", 1)

    try:
        with get_connection() as conn:
            course = conn.execute(
                "SELECT course_name, duration FROM courses WHERE course_id = ?",
                (course_id,)
            ).fetchone()

            if not course:
                print("Course ID not found.")
                return

            print("Press Enter to keep the current value.")
            name = input(f"Course name [{course[0]}]: ").strip() or course[0]
            duration = input(f"Duration [{course[1]}]: ").strip() or course[1]

            conn.execute(
                """UPDATE courses SET course_name = ?, duration = ?
                   WHERE course_id = ?""",
                (name, duration, course_id)
            )
        print("Course updated successfully.")
    except sqlite3.IntegrityError:
        print("A course with that name already exists.")
    except sqlite3.Error as error:
        print("Database error:", error)


def delete_course():
    print("\n--- DELETE COURSE ---")
    course_id = read_integer("Course ID to delete: ", 1)
    confirm = input("Are you sure you want to delete this course? (y/n): ").lower()

    if confirm != "y":
        print("Delete cancelled.")
        return

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM courses WHERE course_id = ?", (course_id,)
            )
        print("Course deleted successfully." if cursor.rowcount
              else "Course ID not found.")
    except sqlite3.Error as error:
        print("Database error:", error)


# -------------------- ENROLLMENT / TABLE RELATIONSHIP --------------------

def enroll_student():
    print("\n--- ENROLL STUDENT IN COURSE ---")
    view_students()
    student_id = read_integer("Student ID: ", 1)
    view_courses()
    course_id = read_integer("Course ID: ", 1)

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO enrollments(student_id, course_id) VALUES (?, ?)",
                (student_id, course_id)
            )
        print("Student enrolled successfully.")
    except sqlite3.IntegrityError as error:
        print("Enrollment failed. Check the IDs or whether the student is "
              "already enrolled in this course.")
        print("Details:", error)
    except sqlite3.Error as error:
        print("Database error:", error)


def view_enrollments():
    try:
        with get_connection() as conn:
            rows = conn.execute("""
                SELECT e.enrollment_id, s.name, c.course_name, e.enrollment_date
                FROM enrollments e
                JOIN students s ON e.student_id = s.student_id
                JOIN courses c ON e.course_id = c.course_id
                ORDER BY e.enrollment_id
            """).fetchall()
        print_table(["Enrollment ID", "Student", "Course", "Date"], rows)
    except sqlite3.Error as error:
        print("Database error:", error)


# -------------------- MENUS / ROLE AUTHORIZATION --------------------

def admin_menu():
    print("""
========== ADMIN MENU ==========
1. Add Student
2. View Students
3. Update Student
4. Delete Student
5. Add Course
6. View Courses
7. Update Course
8. Delete Course
9. Enroll Student in Course
10. View Enrollments
0. Logout
""")


def staff_menu():
    print("""
========== STAFF MENU ==========
1. Add Student
2. View Students
3. Update Student
4. View Courses
5. Enroll Student in Course
6. View Enrollments
0. Logout
""")


def run_user_menu(user):
    while True:
        is_admin = user["role"] == "admin"
        admin_menu() if is_admin else staff_menu()
        choice = input("Enter your choice: ").strip()

        try:
            if is_admin:
                actions = {
                    "1": add_student,
                    "2": view_students,
                    "3": update_student,
                    "4": delete_student,
                    "5": add_course,
                    "6": view_courses,
                    "7": update_course,
                    "8": delete_course,
                    "9": enroll_student,
                    "10": view_enrollments,
                }
            else:
                actions = {
                    "1": add_student,
                    "2": view_students,
                    "3": update_student,
                    "4": view_courses,
                    "5": enroll_student,
                    "6": view_enrollments,
                }

            if choice == "0":
                print("Logged out successfully.")
                break
            elif choice in actions:
                actions[choice]()
            else:
                print("Invalid menu choice. Please try again.")

        except (ValueError, sqlite3.Error) as error:
            print("Operation could not be completed:", error)
        except Exception as error:
            print("Unexpected error:", error)

        pause()


def main():
    initialize_database()
    print("======================================")
    print("      STUDENT MANAGEMENT SYSTEM")
    print("       Python + SQLite Project")
    print("======================================")

    while True:
        print("""
========== MAIN MENU ==========
1. Register
2. Login
0. Exit
""")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            register_user()
            pause()
        elif choice == "2":
            user = login_user()
            if user:
                run_user_menu(user)
        elif choice == "0":
            print("Thank you for using the Student Management System.")
            break
        else:
            print("Invalid choice. Please select 1, 2 or 0.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram closed by user.")
    except Exception as error:
        print("Application error:", error)
