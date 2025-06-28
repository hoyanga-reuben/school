from django.urls import path,include
from django.contrib.auth.views import LogoutView 
from django.contrib.auth import views as auth_views
from .views import all_users_api


from . import views  
from .views import custom_login

app_name = 'transfers'

urlpatterns = [
    path('messaging/', include('transfers.urls_messaging')),  # 👈 link messaging 
    path('home/', views.home, name='home'),
    path('login/', custom_login, name='login'), 
    path('dashboard/', views.main_dashboard, name='main_dashboard'),
    path('contact-admin/', views.contact_admin, name='contact_admin'),
    path('summary/', views.transfer_summary, name='transfer_summary'),
    path('register/', views.register_teacher, name='register_teacher'),
    path('redirect/', views.role_redirect, name='role_redirect'),
    path('cancel/<int:request_id>/', views.cancel_transfer, name='cancel_transfer'),
    path('approve_transfer/<int:transfer_id>/', views.approve_transfer, name='approve_transfer'),
    path('reject_transfer/<int:transfer_id>/', views.reject_transfer, name='reject_transfer'),
    path('transfer_map/', views.transfer_map, name='transfer_map'),
    path('exchange-request/send/<int:receiver_id>/', views.send_exchange_request, name='send_exchange_request'),
    path('exchange-request/inbox/', views.received_exchange_requests, name='received_exchange_requests'),
    path('exchange-matches/', views.exchange_matches, name='exchange_matches'),
    path('all-requests/', views.all_transfer_requests, name='all_requests'),
    path('districts/', views.get_districts, name='get_districts'),
    path('wards/', views.get_wards, name='get_wards'),
    path('schools/', views.get_schools, name='get_schools'),
    path('submit_transfer/', views.submit_transfer, name='submit_transfer'),
    path('success/', views.transfer_success, name='transfer_success'),
    path('history/', views.transfer_history, name='transfer_history'),
    path('school_all_transfers/', views.school_all_transfers, name='school_all_transfers'),
    path('district_all_transfers/', views.district_all_transfers, name='district_all_transfers'),
    path('tamisemi_all_transfers/', views.tamisemi_all_transfers, name='tamisemi_all_transfers'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('logout/', LogoutView.as_view(next_page='transfers:login'), name='logout'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('incoming/', views.incoming_transfers, name='incoming_transfers'),
    path('outgoing/', views.outgoing_transfers, name='outgoing_transfers'),
    path('district/', views.district_transfers, name='district_transfers'),
    path('inter-region/', views.inter_region_transfers, name='inter_region_transfers'),
    path('inbox/', views.inbox, name='inbox'),
    path('send-message/', views.send_message, name='send_message'),
    path('unread-count/', views.unread_count, name='unread_count'),
    path('exchange/received/', views.received_exchange_requests, name='received_exchange_requests'),
    path('exchange/approve/<int:request_id>/', views.approve_exchange, name='approve_exchange'),
    path('exchange/reject/<int:request_id>/', views.reject_exchange, name='reject_exchange')
]
