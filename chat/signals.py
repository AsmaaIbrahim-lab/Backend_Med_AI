from chat.models import ChatRequest
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ChatMessage
#from notifications.utils import create_notification
@receiver(post_save, sender=ChatMessage)
def notify_on_new_message(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        request = ChatRequest.objects.get(doctor=instance.room.doctor, patient=instance.room.patient)
        if request.status != 'accepted':
            return  # Don't send notifications if chat not approved
    except ChatRequest.DoesNotExist:
        return

    receiver = instance.room.patient if instance.sender == instance.room.doctor else instance.room.doctor
  #  create_notification(
   #     sender=instance.sender,
    #    receiver=receiver,
     #   message=f"New message from {instance.sender.username}",
      #  type="chat"
   # )