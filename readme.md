# GradeTrack

A full-stack web application for Concordia University students to track courses, grades, and CGPA in real time.

**Live app:** https://web-production-15bc.up.railway.app

---

## What it does

- Add courses with name, credits, letter grade, and semester
- Letter grades (A+ to F) automatically converted to Concordia GPA points
- Live CGPA calculation using Concordia's weighted average formula
- Target grade calculator — tells you exactly what average you need in remaining credits to hit a desired CGPA
- Delete courses with one click
- Data persists between sessions via CSV file
- Publicly deployed and accessible from any device

---

## Tech Stack

- **Python 3** — core language
- **Flask** — web framework (backend routing and server)
- **CSV** — data storage
- **HTML + CSS** — frontend (Jinja2 templating)
- **Gunicorn** — production WSGI server
- **Railway** — cloud deployment
- **GitHub** — version control

---

## Project Structure

```
gradetrack/
    app.py              # Flask backend — all routes and logic
    courses.csv         # Data file — created automatically on first run
    requirements.txt    # Python dependencies for deployment
    Procfile            # Tells Railway how to start the app
    templates/
        index.html      # Main HTML page (Jinja2 template)
    static/
        style.css       # All CSS styling
```

---

## How to Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/nirthikkaa/gradetrack.git
cd gradetrack
```

**2. Install dependencies**
```bash
pip3 install flask
```

**3. Run the app**
```bash
python3 app.py
```

**4. Open in browser**
```
http://127.0.0.1:5000
```

---

## How It Was Built — Step by Step

### Step 1 — Install Flask
```bash
pip3 install flask
```

### Step 2 — Create project folder structure
```bash
mkdir gradetrack
cd gradetrack
mkdir templates static
```

### Step 3 — Build the Python backend (app.py)
Built `app.py` with the following:
- `load()` — reads all courses from `courses.csv`
- `save()` — writes updated course list back to CSV
- `next_id()` — generates the next unique course ID
- `calculate_cgpa()` — weighted average GPA formula
- `target_needed()` — calculates grade needed to hit a target CGPA
- Routes: `/` (home), `/add` (POST), `/delete/<id>`, `/target` (POST)
- `GRADE_CONVERSION` dictionary mapping Concordia letter grades to GPA points

### Step 4 — Create the HTML template (templates/index.html)
Built `index.html` using Jinja2 templating with four sections:
- Header
- Live CGPA display card
- Target grade calculator form
- Add course form with letter grade dropdown
- Course table with delete button per row

### Step 5 — Create the CSS (static/style.css)
Styled with a clean minimal design using navy and teal colours:
- Georgia serif font for headings
- Flexbox layout for forms
- Responsive table with hover effects
- Consistent card components

### Step 6 — Add letter grade to GPA conversion
Updated the grade input from a free text field to a dropdown. Flask passes `grade_options` to the template, and the selected letter (e.g. B+) is converted to its GPA value (3.3) in `app.py` before saving to CSV.

Also updated credits input to `step="0.5"` to support Concordia's 3.5 credit courses.

### Step 7 — Push to GitHub
```bash
git init
git add .
git commit -m "GradeTrack: Python Flask CGPA tracker"
git branch -M main
git remote add origin https://github.com/nirthikkaa/gradetrack.git
git push -u origin main
```

### Step 8 — Deploy to Railway
Created two deployment files:

`requirements.txt`:
```
flask
gunicorn
```

`Procfile`:
```
web: gunicorn app:app
```

Connected GitHub repo to Railway at railway.app. Railway automatically detected the Python app, installed dependencies, and deployed it live.

---

## Bugs Encountered & How They Were Fixed

### Bug 1 — `ValueError: invalid literal for int() with base 10: '3.5'`
**What happened:** The app crashed when loading courses that had 3.5 credits. The `calculate_cgpa()` and `target_needed()` functions used `int()` to parse credits, which can't handle decimals.

**Fix:** Changed `int(c["credits"])` to `float(c["credits"])` in both functions. Also updated the credits input in HTML to `step="0.5"` and changed the `/target` route to use `float()` instead of `int()` for upcoming credits.

```python
# Before (broken)
graded = [(int(c["credits"]), float(c["grade"])) for c in courses if c["grade"]]

# After (fixed)
graded = [(float(c["credits"]), float(c["grade"])) for c in courses if c["grade"]]
```

### Bug 2 — Browser validation rejecting valid inputs
**What happened:** The browser was blocking form submission with "enter a valid value" because number inputs lacked a `step` attribute, causing HTML5 validation to reject decimal values.

**Fix:** Added `step="0.5"` to the credits input and `step="0.01"` to the target CGPA input so the browser accepts decimal values.

---

## Concordia Grade Conversion Table

| Letter | GPA Points |
|--------|-----------|
| A+     | 4.3       |
| A      | 4.0       |
| A-     | 3.7       |
| B+     | 3.3       |
| B      | 3.0       |
| B-     | 2.7       |
| C+     | 2.3       |
| C      | 2.0       |
| C-     | 1.7       |
| D+     | 1.3       |
| D      | 1.0       |
| F      | 0.0       |

---

## CGPA Formula

```
CGPA = sum(credits × gpa_points) / sum(credits)
```

Target grade needed formula:
```
x = (target × (current_credits + upcoming_credits) - current_points) / upcoming_credits
```

---

*Built by Nirthika Ilaiyarajah — Concordia University, Computer Engineering, March 2026*
