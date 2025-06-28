from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('send/', views.send_message, name='send_message'),
    path('unread-count/', views.unread_count, name='unread_count'),

    # Threaded messaging
    path('threads/start/', views.start_thread, name='start_thread'),
    path('threads/', views.thread_list, name='thread_list'),
    path('threads/<int:thread_id>/', views.view_thread, name='view_thread'),

    # Trash, spam, etc.
    path('trash/', views.trash, name='trash'),
    path('spam/', views.spam_messages, name='spam'),
]
