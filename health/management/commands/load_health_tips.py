# health/load_health_tips.py
from django.core.management.base import BaseCommand
from health.models import HealthTip

class Command(BaseCommand):
    help = 'Load predefined health tips into the database'

    def handle(self, *args, **kwargs):
        tips = [
            ("Stay hydrated", "Drink at least 8 glasses of water daily.", "general"),
            ("Eat more vegetables", "Include a variety of colorful vegetables in your meals.", "nutrition"),
            ("Get enough sleep", "Aim for 7–9 hours of quality sleep each night.", "general"),
            ("Exercise regularly", "Engage in physical activity for at least 30 minutes most days.", "fitness"),
            ("Manage stress", "Practice deep breathing, meditation, or yoga to reduce stress.", "mental_health"),
            ("Limit sugar", "Avoid sugary drinks and snacks to reduce your risk of diabetes.", "nutrition"),
            ("Practice good hygiene", "Wash your hands frequently to prevent the spread of germs.", "hygiene"),
            ("Take breaks", "Step away from screens regularly to rest your eyes and mind.", "mental_health"),
            ("Avoid processed foods", "Choose whole, unprocessed foods whenever possible.", "nutrition"),
            ("Stay socially connected", "Spend time with family or friends to boost mental health.", "mental_health"),
            ("Use sunscreen", "Protect your skin from harmful UV rays by applying SPF daily.", "general"),
            ("Stretch daily", "Improve flexibility and reduce muscle tension with daily stretches.", "fitness"),
            ("Eat a balanced breakfast", "Start your day with a healthy mix of protein, fiber, and carbs.", "nutrition"),
            ("Drink green tea", "A healthy beverage full of antioxidants.", "nutrition"),
            ("Read food labels", "Make informed decisions by checking ingredients and nutrition facts.", "nutrition"),
            ("Walk more", "Take the stairs or walk short distances instead of driving.", "fitness"),
            ("Practice gratitude", "Keep a journal or reflect on things you are thankful for.", "mental_health"),
            ("Stay mentally active", "Engage your brain with puzzles, books, or learning something new.", "mental_health"),
            ("Disinfect surfaces", "Clean commonly touched surfaces to prevent illness.", "hygiene"),
            ("Don’t skip meals", "Skipping meals can slow your metabolism and lead to overeating.", "nutrition"),
            ("Limit alcohol", "Too much alcohol can harm your liver and general health.", "general"),
            ("Avoid smoking", "Quit smoking to improve heart and lung health.", "general"),
            ("Chew your food slowly", "Helps digestion and allows your brain to register fullness.", "nutrition"),
            ("Plan your meals", "Planning helps ensure a balanced and nutritious diet.", "nutrition"),
            ("Keep a water bottle", "Carry a bottle with you as a reminder to stay hydrated.", "general"),
              ("Stay hydrated", "Drink at least 8 glasses of water a day.", "general"),
    ("Eat more fruits", "Include at least one fruit in every meal.", "nutrition"),
    ("Regular exercise", "Try to get at least 30 minutes of physical activity daily.", "fitness"),
    ("Sleep well", "Aim for 7-9 hours of sleep each night.", "general"),
    ("Wash your hands", "Wash hands with soap for at least 20 seconds.", "hygiene"),
    ("Deep breathing", "Practice deep breathing exercises to reduce stress.", "mental_health"),
    ("Cut down sugar", "Avoid sugary drinks and sweets as much as possible.", "nutrition"),
    ("Stretch daily", "Stretch to stay flexible and avoid injuries.", "fitness"),
    ("Limit screen time", "Take breaks and follow the 20-20-20 rule.", "mental_health"),
    ("Eat whole grains", "Replace white bread with whole grain options.", "nutrition"),
    ("Practice mindfulness", "Take a few minutes to meditate or stay present.", "mental_health"),
    ("Use sunscreen", "Protect your skin from harmful UV rays.", "hygiene"),
    ("Eat lean protein", "Include beans, fish, or chicken for protein.", "nutrition"),
    ("Walk more", "Use stairs, park farther, or take walks.", "fitness"),
    ("Avoid smoking", "Don’t smoke or be around secondhand smoke.", "general"),
    ("Limit alcohol", "Drink in moderation and know your limits.", "general"),
    ("Focus on posture", "Sit and stand straight to avoid back problems.", "fitness"),
    ("Read nutrition labels", "Be mindful of what you consume.", "nutrition"),
    ("Stay socially connected", "Call a friend or loved one.", "mental_health"),
    ("Get vaccinated", "Keep up to date with immunizations.", "general"),
    ("Floss daily", "Don’t skip flossing when brushing teeth.", "hygiene"),
    ("Keep a food diary", "Track what you eat to build awareness.", "nutrition"),
    ("Start small habits", "Small consistent steps make a big difference.", "mental_health"),
    ("Avoid late snacks", "Don't eat heavy meals late at night.", "nutrition"),
    ("Laugh often", "Laughter is good for your mental health.", "mental_health")
        ]

        for title, content, category in tips:
            HealthTip.objects.get_or_create(title=title, content=content, category=category)

        self.stdout.write(self.style.SUCCESS(f"Successfully loaded {len(tips)} health tips."))
