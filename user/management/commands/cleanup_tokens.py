from django.core.management.base import BaseCommand
from django.utils import timezone
from user.models import CustomOutstandingToken  # استبدل your_app باسم تطبيقك

class Command(BaseCommand):
    help = 'Cleans up expired tokens from the database'

    def handle(self, *args, **options):
        # حساب التوكنات المنتهية
        expired_tokens = CustomOutstandingToken.objects.filter(
            expires_at__lte=timezone.now()
        )
        
        count = expired_tokens.count()
        
        # حذف التوكنات المنتهية
        expired_tokens.delete()
        
        # رسالة الإخراج
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} expired tokens')
        )