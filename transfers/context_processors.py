from .models import Message

def unread_message_count(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(receiver=request.user, is_read=False).count()
        return {'unread_count': count}
    return {}
# context_processors.py
from transfers.models import ExchangeRequest

def exchange_request_notification(request):
    count = 0
    if request.user.is_authenticated:
        count = ExchangeRequest.objects.filter(teacher_2=request.user, status='Pending').count()
    return {'exchange_request_count': count}

