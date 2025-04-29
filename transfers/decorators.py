from django.shortcuts import redirect
from django.contrib import messages
from .models import TransferRequest, TeacherProfile


# ✅ Original check_cancel_limit decorator
def check_cancel_limit(view_func):
    def _wrapped_view(request, *args, **kwargs):
        cancelled_count = TransferRequest.objects.filter(teacher=request.user, status='Cancelled').count()
        if cancelled_count >= 3:
            messages.error(request, "You have cancelled 3 transfer requests. Please contact the admin to submit another request.")
            return redirect('transfers:transfer_summary')  # You can change this to another view
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ✅ Original block_after_cancellation_redirect_to_contact decorator
def block_after_cancellation_redirect_to_contact(view_func):
    def _wrapped_view(request, *args, **kwargs):
        cancelled_count = TransferRequest.objects.filter(teacher=request.user, status='Cancelled').count()
        if cancelled_count >= 3:
            messages.error(request, "You have exceeded your cancellation limit. Please contact the admin.")
            return redirect('transfers:contact_admin')  # 👈 Ensure this view exists
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ✅ 🔒 New decorator: checks allow_transfer_submission in TeacherProfile
def check_teacher_transfer_unlock(view_func):
    def _wrapped_view(request, *args, **kwargs):
        cancelled_count = TransferRequest.objects.filter(teacher=request.user, status='Cancelled').count()
        try:
            profile = TeacherProfile.objects.get(user=request.user)
        except TeacherProfile.DoesNotExist:
            messages.error(request, "Your teacher profile is not found. Please contact admin.")
            return redirect('transfers:contact_admin')

        if cancelled_count >= 3 and not profile.allow_transfer_submission:
            messages.error(request, "Your submission access has been blocked. Please contact the admin.")
            return redirect('transfers:contact_admin')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
