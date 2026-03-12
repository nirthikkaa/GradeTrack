from flask import Flask, render_template, request, redirect
import csv
import os

app = Flask(__name__)

FILE = "courses.csv"
HEADERS = ["id", "name", "credits", "grade", "semester"]

# Concordia's official letter grade to GPA point conversion table
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
    "":   None  # No grade entered yet
}

def load():
    # Read all courses from CSV, return empty list if file doesn't exist
    if not os.path.exists(FILE):
        return []
    with open(FILE, newline="") as f:
        return list(csv.DictReader(f))

def save(courses):
    # Overwrite CSV with updated course list
    with open(FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(courses)

def next_id(courses):
    # Generate next unique ID
    return str(max(int(c["id"]) for c in courses) + 1) if courses else "1"

def calculate_cgpa(courses):
    # Weighted average: sum(credits * gpa) / sum(credits)
    # float() used for credits to support 3.5 credit courses
    graded = [(float(c["credits"]), float(c["grade"])) for c in courses if c["grade"]]
    if not graded:
        return None
    return round(sum(c * g for c, g in graded) / sum(c for c, g in graded), 2)

def target_needed(courses, target, upcoming):
    # Grade needed = (target * total_future_credits - current_points) / upcoming_credits
    graded = [(float(c["credits"]), float(c["grade"])) for c in courses if c["grade"]]
    total_points = sum(c * g for c, g in graded)
    total_credits = sum(c for c, g in graded)
    return round((target * (total_credits + upcoming) - total_points) / upcoming, 2)

@app.route("/")
def index():
    courses = load()
    cgpa = calculate_cgpa(courses)
    grade_options = [k for k in GRADE_CONVERSION.keys() if k != ""]
    return render_template("index.html", courses=courses, cgpa=cgpa, grade_options=grade_options)

@app.route("/add", methods=["POST"])
def add():
    courses = load()
    # Convert letter grade to GPA value before saving
    letter = request.form["grade"]
    gpa_value = GRADE_CONVERSION.get(letter, None)
    courses.append({
        "id": next_id(courses),
        "name": request.form["name"],
        # Store as float string to support 3.5 credits
        "credits": str(float(request.form["credits"])),
        "grade": gpa_value if gpa_value is not None else "",
        "semester": request.form["semester"]
    })
    save(courses)
    return redirect("/")

@app.route("/delete/<id>")
def delete(id):
    courses = [c for c in load() if c["id"] != id]
    save(courses)
    return redirect("/")

@app.route("/target", methods=["POST"])
def target():
    courses = load()
    # Use float for both target and upcoming to support decimals
    target = float(request.form["target"])
    upcoming = float(request.form["upcoming"])
    cgpa = calculate_cgpa(courses)
    needed = target_needed(courses, target, upcoming)
    grade_options = [k for k in GRADE_CONVERSION.keys() if k != ""]
    return render_template("index.html", courses=courses, cgpa=cgpa,
                           needed=needed, target=target, grade_options=grade_options)

if __name__ == "__main__":
    app.run(debug=True)