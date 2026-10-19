"""
Password Manager
----------------
A simple command-line program that generates, validates, stores,
searches, and displays passwords.

Run with:  python password_manager.py
"""

import csv
import os
import secrets
import string

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 32
SPECIAL_CHARACTERS = "!@#$%^&*()-_=+?"
DATA_FILE = "passwords.csv"
MASK_VISIBLE_CHARS = 2  # how many characters to show when masking


# ---------------------------------------------------------------------------
# Password generation & validation
# ---------------------------------------------------------------------------
def generate_password(length, use_upper=True, use_digits=True, use_special=True):
    """Generate a secure random password that follows the user's requirements."""
    if length < MIN_PASSWORD_LENGTH or length > MAX_PASSWORD_LENGTH:
        raise ValueError(
            f"Length must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH}."
        )

    # Build the pool of allowed characters (string concatenation)
    pool = string.ascii_lowercase
    required = [secrets.choice(string.ascii_lowercase)]

    if use_upper:
        pool += string.ascii_uppercase
        required.append(secrets.choice(string.ascii_uppercase))
    if use_digits:
        pool += string.digits
        required.append(secrets.choice(string.digits))
    if use_special:
        pool += SPECIAL_CHARACTERS
        required.append(secrets.choice(SPECIAL_CHARACTERS))

    # Fill the remaining length, then shuffle so required characters aren't first
    remaining = [secrets.choice(pool) for _ in range(length - len(required))]
    characters = required + remaining
    secrets.SystemRandom().shuffle(characters)
    return "".join(characters)


def validate_password(password):
    """
    Check password strength.
    Returns (is_valid, list_of_problems).
    """
    problems = []

    # Length checks
    if len(password) < MIN_PASSWORD_LENGTH:
        problems.append(f"Too short (minimum {MIN_PASSWORD_LENGTH} characters).")
    if len(password) > MAX_PASSWORD_LENGTH:
        problems.append(f"Too long (maximum {MAX_PASSWORD_LENGTH} characters).")

    # Character checks
    if not any(c.islower() for c in password):
        problems.append("Needs at least one lowercase letter.")
    if not any(c.isupper() for c in password):
        problems.append("Needs at least one uppercase letter.")
    if not any(c.isdigit() for c in password):
        problems.append("Needs at least one digit.")
    if not any(c in SPECIAL_CHARACTERS for c in password):
        problems.append(f"Needs at least one special character ({SPECIAL_CHARACTERS}).")
    if " " in password:
        problems.append("Cannot contain spaces.")

    return len(problems) == 0, problems


def mask_password(password):
    """Mask a password using substrings + concatenation: 'Ab********'."""
    if len(password) <= MASK_VISIBLE_CHARS:
        return "*" * len(password)
    visible = password[:MASK_VISIBLE_CHARS]               # substring
    hidden = "*" * (len(password) - MASK_VISIBLE_CHARS)   # repetition
    return visible + hidden                               # concatenation


# ---------------------------------------------------------------------------
# File handling
# ---------------------------------------------------------------------------
def load_accounts():
    """Read all stored accounts from the file. Returns a list of dicts."""
    accounts = []
    if not os.path.exists(DATA_FILE):
        return accounts

    with open(DATA_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) == 3:
                accounts.append(
                    {"account": row[0], "username": row[1], "password": row[2]}
                )
    return accounts


def save_accounts(accounts):
    """Write all accounts to the file."""
    with open(DATA_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for entry in accounts:
            writer.writerow([entry["account"], entry["username"], entry["password"]])


# ---------------------------------------------------------------------------
# Challenge features: duplicates & search
# ---------------------------------------------------------------------------
def is_duplicate_account(accounts, account, username):
    """True if this account name + username combo is already stored."""
    for entry in accounts:
        if (
            entry["account"].lower() == account.lower()
            and entry["username"].lower() == username.lower()
        ):
            return True
    return False


def is_password_reused(accounts, password):
    """True if the password is already used by another stored account."""
    return any(entry["password"] == password for entry in accounts)


def search_accounts(accounts, keyword):
    """Return accounts whose name contains the keyword (case-insensitive)."""
    keyword = keyword.lower()
    return [e for e in accounts if keyword in e["account"].lower()]


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
def display_accounts(accounts, show_passwords=False):
    """Print accounts in a table. Passwords are masked unless show_passwords."""
    if not accounts:
        print("\nNo accounts found.")
        return

    print(f"\n{'#':<4}{'Account':<22}{'Username':<22}{'Password'}")
    print("-" * 70)
    for i, entry in enumerate(accounts, start=1):
        pwd = entry["password"] if show_passwords else mask_password(entry["password"])
        print(f"{i:<4}{entry['account']:<22}{entry['username']:<22}{pwd}")


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------
def ask_yes_no(prompt):
    return input(prompt + " (y/n): ").strip().lower().startswith("y")


def ask_length():
    """Keep asking until the user enters a valid length."""
    while True:
        raw = input(
            f"Password length ({MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH}): "
        ).strip()
        if raw.isdigit() and MIN_PASSWORD_LENGTH <= int(raw) <= MAX_PASSWORD_LENGTH:
            return int(raw)
        print("Please enter a valid number in range.")


def add_account(accounts):
    print("\n--- Add New Account ---")
    account = input("Account name (e.g., Gmail): ").strip()
    username = input("Username: ").strip()

    if not account or not username:
        print("Account name and username cannot be empty.")
        return

    if is_duplicate_account(accounts, account, username):
        print("That account/username combination already exists.")
        return

    if ask_yes_no("Generate a password for you?"):
        length = ask_length()
        use_upper = ask_yes_no("Include uppercase letters?")
        use_digits = ask_yes_no("Include digits?")
        use_special = ask_yes_no("Include special characters?")
        password = generate_password(length, use_upper, use_digits, use_special)
        print(f"Generated password: {password}")
    else:
        password = input("Enter your password: ").strip()
        is_valid, problems = validate_password(password)
        if not is_valid:
            print("Password is not strong enough:")
            for problem in problems:
                print(f"  - {problem}")
            return

    if is_password_reused(accounts, password):
        print("Warning: this password is already used for another account!")
        if not ask_yes_no("Save it anyway?"):
            return

    accounts.append({"account": account, "username": username, "password": password})
    save_accounts(accounts)
    print("Account saved!")


def view_accounts(accounts):
    reveal = ask_yes_no("Show full passwords? (otherwise they are masked)")
    display_accounts(accounts, show_passwords=reveal)


def search_menu(accounts):
    keyword = input("Search for account name: ").strip()
    if not keyword:
        print("Please enter a search term.")
        return
    display_accounts(search_accounts(accounts, keyword))


def check_password_menu():
    password = input("Enter a password to check: ").strip()
    is_valid, problems = validate_password(password)
    if is_valid:
        print("Strong password!")
    else:
        print("Weak password:")
        for problem in problems:
            print(f"  - {problem}")


# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------
def main():
    accounts = load_accounts()

    while True:
        print("\n===== PASSWORD MANAGER =====")
        print("1. Add account")
        print("2. View all accounts")
        print("3. Search accounts")
        print("4. Check password strength")
        print("5. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_account(accounts)
        elif choice == "2":
            view_accounts(accounts)
        elif choice == "3":
            search_menu(accounts)
        elif choice == "4":
            check_password_menu()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
