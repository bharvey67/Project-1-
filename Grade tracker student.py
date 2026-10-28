MAX_SCORE = 100
MIN_SCORE = 0

name = input("Student name: ")
student_id = input("Student ID: ")

grades = []

for i in range(3):
    grade = float(input("Enter a grade (0-100): "))

    while grade < MIN_SCORE or grade > MAX_SCORE:
      print("Invalid grade!")
      grade = float(input("Enter a grade (0-100): "))

    grades.append(grade)

average = sum(grades) / len(grades)

if average >= 90:
    letter = "A"

elif average >= 80:
    letter = "B"

elif average >= 70:
    letter = "C"

elif average >= 60:
    letter = "D"

else:
    letter = "F"

print("\nStudent:", name)
print("ID:", student_id)
print("Average:", round(average, 2))
print("Letter grade:", letter)

with open("grades.txt", "a") as file:
    file.write(f"{name}, {student_id}, {grades}, {average:.2f}, {letter}\n")

print("Student saved to file!")