"""Password Manager"""

import csv
import os
import secrets
import string

MIN_LENGTH = 8
MAX_LENGTH = 32
SPECIAL_CHARS = "!@#$%^&*()-_=+?"
DATA_FILE = "passwords.csv"


def generate_password(length):
    """Generate a random password containing every character type."""
    groups = [string.ascii_lowercase, string.ascii_uppercase, string.digits, SPECIAL_CHARS]
    pool = "".join(groups)                                   
    chars = [secrets.choice(g) for g in groups]              
    chars += [secrets.choice(pool) for _ in range(length - len(chars))]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def check_strength(password):
    """Return a list of problems (empty list = strong password)."""
    problems = []
    if len(password) < MIN_LENGTH:                           
        problems.append(f"at least {MIN_LENGTH} characters")
    if len(password) > MAX_LENGTH:
        problems.append(f"at most {MAX_LENGTH} characters")
    if not any(c.islower() for c in password):
        problems.append("a lowercase letter")
    if not any(c.isupper() for c in password):
        problems.append("an uppercase letter")
    if not any(c.isdigit() for c in password):
        problems.append("a digit")
    if not any(c in SPECIAL_CHARS for c in password):
        problems.append(f"a special character ({SPECIAL_CHARS})")
    return problems


def mask(password):
    """Show the first 2 characters (substring) and hide the rest."""
    return password[:2] + "*" * (len(password) - 2)


def load():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        return [row for row in csv.reader(f) if len(row) == 3]


def save(accounts):
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(accounts)


def show(accounts, reveal=False):
    if not accounts:
        print("\nNo accounts found.")
        return
    print(f"\n{'Account':<20}{'Username':<20}Password\n" + "-" * 60)
    for account, username, password in accounts:
        print(f"{account:<20}{username:<20}{password if reveal else mask(password)}")


def add(accounts):
    account = input("Account name: ").strip()
    username = input("Username: ").strip()
    if not account or not username:
        return print("Account name and username cannot be empty.")
    if any(a.lower() == account.lower() and u.lower() == username.lower()
           for a, u, _ in accounts):                         # duplicate check
        return print("That account and username already exist.")

    if input("Generate a password? (y/n): ").lower().startswith("y"):
        length = input(f"Length ({MIN_LENGTH}-{MAX_LENGTH}): ")
        if not length.isdigit() or not MIN_LENGTH <= int(length) <= MAX_LENGTH:
            return print("Invalid length.")
        password = generate_password(int(length))
        print("Generated password:", password)
    else:
        password = input("Password: ").strip()
        problems = check_strength(password)
        if problems:
            return print("Weak password. It needs: " + ", ".join(problems) + ".")

    if any(p == password for _, _, p in accounts):
        print("Warning: this password is already used for another account.")
    accounts.append([account, username, password])
    save(accounts)
    print("Saved!")


def main():
    accounts = load()
    while True:
        choice = input("\n1 Add  2 View  3 Search  4 Check strength  5 Quit: ").strip()
        if choice == "1":
            add(accounts)
        elif choice == "2":
            show(accounts, input("Show full passwords? (y/n): ").lower().startswith("y"))
        elif choice == "3":
            word = input("Search account name: ").lower()
            show([a for a in accounts if word in a[0].lower()])
        elif choice == "4":
            problems = check_strength(input("Password: "))
            print("Strong!" if not problems else "Weak. It needs: " + ", ".join(problems) + ".")
        elif choice == "5":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
