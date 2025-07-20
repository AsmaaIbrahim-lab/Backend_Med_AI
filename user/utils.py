# utils.py
from datetime import date
import re
import redis
import random
import string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
import random


def send_otp_email(email, otp, user_type="Doctor"):
    print(f"Sending OTP to {email} with value {otp} for user type {user_type}")
    subject = f"Your {user_type} Registration OTP"
    html_content = f"<p>Your OTP code is <strong>{otp}</strong>. It will expire in 10 minutes.</p>"
    try:
        msg = EmailMultiAlternatives(subject, strip_tags(html_content), "Slamtak Support <support@slamtak.com>", [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print("OTP email sent successfully")
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {e}")
        return False, str(e)


def calculate_age(birth_date):
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )

def is_strong_password(password):
    # Password must meet the following high-security criteria:
    return (
        len(password) >= 12 and  # Minimum length of 12 characters
        re.search(r"[A-Z]", password) and  # At least one uppercase letter
        re.search(r"[a-z]", password) and  # At least one lowercase letter
        re.search(r"\d", password) and  # At least one digit
        re.search(r"[@$!%*?&]", password) and  # At least one special character
        not re.search(r"(.)\1{2,}", password) and  # No repeating characters (e.g., 'aaaa')
        not re.search(r"\b(password|123456|qwerty|admin|welcome)\b", password, re.IGNORECASE)  # Avoid common passwords
    )
def generate_username(first_name, last_name):
    return f"{first_name.strip()} {last_name.strip()}".title()

def generate_random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits + "@$!%*?&", k=10))
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)



def generate_otp():
    return str(random.randint(1000, 9999))

def generate_location(governorate, area):
    gov_name = governorate.name if hasattr(governorate, "name") else str(governorate) if governorate else None
    area_name = area.name if hasattr(area, "name") else str(area) if area else None

    if gov_name and area_name:
        return f"{gov_name} - {area_name}"
    elif gov_name:
        return gov_name
    elif area_name:
        return area_name
    else:
        return "Unknown Location"


