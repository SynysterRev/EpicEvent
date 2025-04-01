import re
from datetime import datetime


def validate_email(email):
    if not re.match(r"^[\w.-]+@([\w-]+\.)+[\w-]{2,4}$", email):
        raise ValueError("Invalid email address.")
    return True


def validate_password(password):
    if not re.match(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9]).{8,}$",
                    password):
        raise ValueError("Your password must be at least 8 characters long, contains "
                         "at least one uppercase letter, at least one lowercase "
                         "letter, at least one number, and at least one special character.")
    return True


def validate_name(name):
    if not re.match("^[a-zA-Z- ]+$", name):
        raise ValueError("Your name must be at least 1 character long and only "
                         "contains letters, spaces and -.")
    return True


def validate_phone_number(phone_number):
    if not re.match("^[0-9]{8,15}$", phone_number):
        raise ValueError("Your phone number must be at least 8 digits long.")
    return True


def validate_digit(number):
    if not number.isdigit():
        raise ValueError("You must enter a number.")
    return True


def validate_decimal(number):
    if not number.isdecimal():
        raise ValueError("You must enter a decimal number.")
    return True


def validate_date(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        raise ValueError("Your date must be yyyy-mm-dd.")


def validate_time(time):
    try:
        datetime.strptime(time, "%H:%M")
        return True
    except ValueError:
        raise ValueError("Your time must be HH:MM.")