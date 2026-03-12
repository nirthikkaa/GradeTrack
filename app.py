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
    # Each row becomes a dict like: {"id": "1", "name": "COMP 232", ...}
    # If the file doesn't exist yet, return an empty list
    if not os.path.exists(FILE):
        return []
    with open(FILE, newline="") as f:
        return list(csv.DictReader(f))


def save(courses):
    # Write the full list of courses back to the CSV file
    # This completely overwrites the file each time — simple but effective for small data
    with open(FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()   # Write the column names first
        writer.writerows(courses)  # Then write all course rows


def next_id(courses):
    # Generate the next unique ID by finding the current highest ID and adding 1
    # If no courses exist yet, start at ID 1
    return str(max(int(c["id"]) for c in courses) + 1) if courses else "1"


def calculate_cgpa(courses):
    # Calculate CGPA using Concordia's weighted average formula:
    # CGPA = sum(credit_weight * gpa_points) / sum(credit_weights)
    # Only courses with a grade are included — in-progress courses are excluded
    graded = [(int(c["credits"]), float(c["grade"])) for c in courses if c["grade"]]
    if not graded:
        return None  # No grades yet, nothing to calculate
    total_points = sum(c * g for c, g in graded)   # Sum of (credits * gpa) for each course
    total_credits = sum(c for c, g in graded)       # Sum of all graded credits
    return round(total_points / total_credits, 2)


def target_needed(courses, target, upcoming):
    # Calculate what average GPA you need in your upcoming credits
    # to reach your target CGPA overall
    #
    # Formula derived from the CGPA equation:
    # target = (current_points + upcoming_credits * x) / (current_credits + upcoming_credits)
    # Solving for x:
    # x = (target * total_future_credits - current_points) / upcoming_credits
    graded = [(int(c["credits"]), float(c["grade"])) for c in courses if c["grade"]]
    total_points = sum(c * g for c, g in graded)
    total_credits = sum(c for c, g in graded)
    return round((target * (total_credits + upcoming) - total_points) / upcoming, 2)


# Home page — loads all courses and calculates current CGPA
@app.route("/")
def index():
    courses = load()
    cgpa = calculate_cgpa(courses)
    # Build the list of grade options for the dropdown (exclude the empty placeholder)
    grade_options = [k for k in GRADE_CONVERSION.keys() if k != ""]
    return render_template("index.html", courses=courses, cgpa=cgpa, grade_options=grade_options)


# Handle form submission to add a new course
# POST only — this route should never be accessed directly via URL
@app.route("/add", methods=["POST"])
def add():
    courses = load()
    # Get the selected letter grade from the form and convert it to a GPA value
    # e.g. "B+" becomes 3.3
    letter = request.form["grade"]
    gpa_value = GRADE_CONVERSION.get(letter, None)
    # Append the new course to the list
    courses.append({
        "id": next_id(courses),
        "name": request.form["name"],
        "credits": request.form["credits"],
        "grade": gpa_value if gpa_value is not None else "",  # Store empty string if no grade
        "semester": request.form["semester"]
    })
    save(courses)
    # Redirect back to home page so the user sees the updated list
    return redirect("/")


# Handle deleting a course by its ID
# The ID is passed directly in the URL e.g. /delete/3
@app.route("/delete/<id>")
def delete(id):
    # Rebuild the list excluding the course with the matching ID
    courses = [c for c in load() if c["id"] != id]
    save(courses)
    return redirect("/")


# Handle the target CGPA calculator form submission
@app.route("/target", methods=["POST"])
def target():
    courses = load()
    target = float(request.form["target"])       # Desired CGPA
    upcoming = int(request.form["upcoming"])     # Credits still to be completed
    cgpa = calculate_cgpa(courses)
    needed = target_needed(courses, target, upcoming)
    grade_options = [k for k in GRADE_CONVERSION.keys() if k != ""]
    # Pass the result back to the template to display the message
    return render_template("index.html", courses=courses, cgpa=cgpa,
                           needed=needed, target=target, grade_options=grade_options)


# Start the Flask development server
# debug=True enables auto-reload on file save and shows detailed error pages
if __name__ == "__main__":
    app.run(debug=True)