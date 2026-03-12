from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)

# The CSV file where all course data is stored
FILE = "courses.csv"

# Column headers for the CSV file
HEADERS = ["id", "name", "credits", "grade", "semester"]

# Concordia's official letter grade to GPA point conversion table
# Source: Concordia University Academic Calendar
GRADE_CONVERSION = {
    "A+": 4.3,  # Exceptional
    "A":  4.0,  # Outstanding
    "A-": 3.7,  # Excellent
    "B+": 3.3,  # Very good
    "B":  3.0,  # Good
    "B-": 2.7,  # Good
    "C+": 2.3,  # Satisfactory
    "C":  2.0,  # Satisfactory
    "C-": 1.7,  # Marginal
    "D+": 1.3,  # Marginal
    "D":  1.0,  # Marginal - minimum passing grade
    "F":  0.0,  # Failing
    "":   None  # No grade entered yet (course in progress)
}


def load():
    # Read all courses from the CSV file and return as a list of dictionaries
    # If the file doesn't exist yet, return an empty list
    if not os.path.exists(FILE):
        return []
    with open(FILE, newline="") as f:
        return list(csv.DictReader(f))


def save(courses):
    # Write the full list of courses back to the CSV file
    with open(FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(courses)


def next_id(courses):
    # Generate the next unique ID
    return str(max(int(c["id"]) for c in courses) + 1) if courses else "1"


def calculate_cgpa(courses):
    # Calculate CGPA using Concordia's weighted average formula:
    # CGPA = sum(credits * gpa_points) / sum(credits)
    # Use float for credits to support 3.5 credit courses
    graded = [(float(c["credits"]), float(c["grade"])) for c in courses if c["grade"]]
    if not graded:
        return None
    total_points = sum(c * g for c, g in graded)
    total_credits = sum(c for c, g in graded)
    return round(total_points / total_credits, 2)


def target_needed(courses, target, upcoming):
    # Calculate what average GPA you need in upcoming credits to reach target CGPA
    # Use float for credits to support 3.5 credit courses
    graded = [(float(c["credits"]), float(c["grade"])) for c in courses if c["grade"]]
    total_points = sum(c * g for c, g in graded)
    total_credits = sum(c for c, g in graded)
    return round((target * (total_credits + upcoming) - total_points) / upcoming, 2)


# Home page — loads all courses and calculates current CGPA
@app.route("/")
def index():
    courses = load()
    cgpa = calculate_cgpa(courses)
    grade_options = [k for k in GRADE_CONVERSION.keys() if k != ""]
    return render_template("index.html", courses=courses, cgpa=cgpa, grade_options=grade_options)


# Handle form submission to add a new course
@app.route("/add", methods=["POST"])
def add():
    courses = load()
    # Convert letter grade to GPA value before saving
    letter = request.form["grade"]
    gpa_value = GRADE_CONVERSION.get(letter, None)
    courses.append({
        "id": next_id(courses),
        "name": request.form["name"],
        "credits": request.form["credits"],
        "grade": gpa_value if gpa_value is not None else "",
        "semester": request.form["semester"]
    })
    save(courses)
    return redirect("/")


# Handle deleting a course by its ID
@app.route("/delete/<id>")
def delete(id):
    courses = [c for c in load() if c["id"] != id]
    save(courses)
    return redirect("/")


# Handle the target CGPA calculator form submission
@app.route("/target", methods=["POST"])
def target():
    courses = load()
    target = float(request.form["target"])
    upcoming = int(request.form["upcoming"])
    cgpa = calculate_cgpa(courses)
    needed = target_needed(courses, target, upcoming)
    grade_options = [k for k in GRADE_CONVERSION.keys() if k != ""]
    return render_template("index.html", courses=courses, cgpa=cgpa,
                           needed=needed, target=target, grade_options=grade_options)


# Start the Flask development server
if __name__ == "__main__":
    app.run(debug=True)