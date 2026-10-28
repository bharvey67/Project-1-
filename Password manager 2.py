import os 
print("Password manager")

firstname = input("What is your first name?")
Lastname = input("What is your last name?")

Password = input("Make password?: ")

import random

options = ["Harvey#&Brody", "Broharv@#", "Braharv"]

winner = random.choice(options)

print(f"The Password is created: {winner}")

Save = input("Save password? (Yes/No): ")

if Save.lower() == "yes":
    print("Password saved!")
elif Save.lower() == "no":
    print("Password not saved.")
