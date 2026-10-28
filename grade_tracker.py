"""
Student Grade Tracker

A simple command-line program that stores student records, validates
scores, calculates averages, and assigns letter grades.

Run with:  python grade_tracker.py
"""

import os


MAX_SCORE = 100
MIN_SCORE = 0
DATA_FILE = "students.txt"
FIELD_SEPARATOR = ","      # separates ID, name, scores in the file
SCORE_SEPARATOR = ";"      # separates individual scores

# Letter grade cutoffs (checked from highest to lowest)
GRADE_CUTOFFS = [(90, "A"), (80, "B"), (70, "C"), (60, "D")]
LOWEST_GRADE = "F"



def is_valid_score(score):
    """A score is valid if it falls between MIN_SCORE and MAX_SCORE."""
    return MIN_SCORE <= score <= MAX_SCORE


def parse_score(text):
    """Convert text to a float. Returns None if it isn't a number."""
    try:
        return float(text)
    except ValueError:
        return None





def calculate_average(scores):
    """Return the average of a list of scores (0 if the list is empty)."""
    if len(scores) == 0:
        return 0.0
    return sum(scores) / len(scores)


def get_letter_grade(average):
    """Convert a numeric average to a letter grade (A, B, C, D, F)."""
    for cutoff, letter in GRADE_CUTOFFS:
        if average >= cutoff:
            return letter
    return LOWEST_GRADE


# ---------------------------------------------------------------------------
# File handling
# ---------------------------------------------------------------------------
def load_students():
    """Read all student records from the file. Returns a list of dicts."""
    students = []
    if not os.path.exists(DATA_FILE):
        return students

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line == "":
                continue

            # String operation: split the line into its parts
            parts = line.split(FIELD_SEPARATOR)
            if len(parts) < 2:
                continue

            student_id = parts[0]
            name = parts[1]
            scores = []
            if len(parts) > 2 and parts[2] != "":
                for piece in parts[2].split(SCORE_SEPARATOR):
                    score = parse_score(piece)
                    if score is not None:
                        scores.append(score)

            students.append({"id": student_id, "name": name, "scores": scores})
    return students


def save_students(students):
    """Write all student records to the file."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        for student in students:
            # String operations: join scores, then concatenate the line
            score_text = SCORE_SEPARATOR.join(str(s) for s in student["scores"])
            line = student["id"] + FIELD_SEPARATOR + student["name"]
            line += FIELD_SEPARATOR + score_text
            file.write(line + "\n")


# ---------------------------------------------------------------------------
# Display (string formatting)
# ---------------------------------------------------------------------------
def format_name(name):
    """Clean up a name: remove extra spaces and capitalize each word."""
    return " ".join(name.split()).title()


def format_student_row(student):
    """Build one formatted table row for a student."""
    scores = student["scores"]
    average = calculate_average(scores)
    letter = get_letter_grade(average) if scores else "-"

    name = student["name"].ljust(20)
    student_id = student["id"].ljust(10)
    avg_text = f"{average:.1f}".rjust(7)
    score_text = ", ".join(f"{s:g}" for s in scores) if scores else "(none)"

    return f"{student_id}{name}{avg_text}   {letter:<6}{score_text}"


def display_students(students):
    """Print every student in a formatted table."""
    if len(students) == 0:
        print("\nNo student records found.")
        return

    header = "ID".ljust(10) + "Name".ljust(20) + "Average".rjust(7) + "   Grade " + "Scores"
    print("\n" + header)
    print("-" * 70)
    for student in students:
        print(format_student_row(student))


def display_class_summary(students):
    """Class average plus the highest and lowest scores (challenge feature)."""
    all_scores = []
    for student in students:
        all_scores.extend(student["scores"])

    if len(all_scores) == 0:
        print("\nNo scores recorded yet.")
        return

    highest = max(all_scores)
    lowest = min(all_scores)

    # Find who earned the highest and lowest scores
    highest_name = ""
    lowest_name = ""
    for student in students:
        if highest in student["scores"] and highest_name == "":
            highest_name = student["name"]
        if lowest in student["scores"] and lowest_name == "":
            lowest_name = student["name"]

    print("\n===== CLASS SUMMARY =====")
    print(f"Students:       {len(students)}")
    print(f"Total scores:   {len(all_scores)}")
    print(f"Class average:  {calculate_average(all_scores):.1f}")
    print(f"Highest score:  {highest:g} ({highest_name})")
    print(f"Lowest score:   {lowest:g} ({lowest_name})")


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------
def find_student(students, student_id):
    for student in students:
        if student["id"].lower() == student_id.lower():
            return student
    return None


def ask_scores():
    """Collect scores until the user types 'done'. Rejects out-of-range values."""
    scores = []
    print(f"Enter assignment scores ({MIN_SCORE}-{MAX_SCORE}). Type 'done' when finished.")
    while True:
        text = input(f"  Score #{len(scores) + 1}: ").strip()
        if text.lower() == "done":
            break
        score = parse_score(text)
        if score is None:
            print("  Please enter a number.")
        elif not is_valid_score(score):
            print(f"  Score must be between {MIN_SCORE} and {MAX_SCORE}.")
        else:
            scores.append(score)
    return scores


def add_student(students):
    print("\n--- Add Student ---")
    name = format_name(input("Student name: "))
    student_id = input("Student ID: ").strip()

    if name == "" or student_id == "":
        print("Name and ID cannot be empty.")
        return
    if FIELD_SEPARATOR in name or FIELD_SEPARATOR in student_id:
        print(f"Please do not use '{FIELD_SEPARATOR}' in the name or ID.")
        return
    if find_student(students, student_id) is not None:
        print("A student with that ID already exists.")
        return

    scores = ask_scores()
    students.append({"id": student_id, "name": name, "scores": scores})
    save_students(students)
    print(f"Saved {name}!")


def add_scores_to_student(students):
    print("\n--- Add Scores To Existing Student ---")
    student = find_student(students, input("Student ID: ").strip())
    if student is None:
        print("Student not found.")
        return

    new_scores = ask_scores()
    student["scores"].extend(new_scores)
    save_students(students)
    print(f"Updated {student['name']}. New average: {calculate_average(student['scores']):.1f}")


# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------
def main():
    students = load_students()

    while True:
        print("\n===== STUDENT GRADE TRACKER =====")
        print("1. Add student")
        print("2. Add scores to a student")
        print("3. View all students")
        print("4. Class summary (highest / lowest)")
        print("5. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_student(students)
        elif choice == "2":
            add_scores_to_student(students)
        elif choice == "3":
            display_students(students)
        elif choice == "4":
            display_class_summary(students)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
