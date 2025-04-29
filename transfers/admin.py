from django.contrib import admin, messages
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from socket import timeout

from . import models

# Get the custom user model
User = get_user_model()

# ✅ Admin action: Allow teachers to submit transfer requests again
@admin.action(description="Allow selected teachers to submit transfer requests again")
def allow_transfer_submission(modeladmin, request, queryset):
    updated = queryset.update(allow_transfer_submission=True)
    modeladmin.message_user(
        request,
        f"{updated} teacher(s) can now submit transfer requests again.",
        level=messages.SUCCESS
    )

# ✅ Admin action: Activate user accounts linked to profiles
def activate_user_accounts(modeladmin, request, queryset):
    updated_count = 0
    for profile in queryset:
        if profile.user:
            profile.user.is_active = True
            profile.user.save()
            updated_count += 1
    modeladmin.message_user(
        request,
        f"{updated_count} account(s) activated.",
        level=messages.SUCCESS
    )
activate_user_accounts.short_description = "Activate selected user accounts"

# ✅ TeacherProfile admin
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'allow_transfer_submission')
    actions = [allow_transfer_submission, activate_user_accounts]

# ✅ SchoolOfficerProfile admin
class SchoolOfficerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'school')
    actions = [activate_user_accounts]

# ✅ DistrictOfficerProfile admin
class DistrictOfficerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'district')
    actions = [activate_user_accounts]

# ✅ TamisemiOfficerProfile admin
class TamisemiOfficerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'region')
    actions = [activate_user_accounts]

# ✅ TransferRequest admin with role-based approval and notifications
class TransferRequestAdmin(admin.ModelAdmin):
    list_display = (
        'teacher', 'status', 'created_at',
        'school_approval', 'district_approval', 'tamisemi_approval'
    )
    list_filter = ('status', 'school_approval', 'district_approval', 'tamisemi_approval')

    def get_readonly_fields(self, request, obj=None):
        all_fields = [field.name for field in self.model._meta.fields]
        user = request.user

        if user.groups.filter(name='school_officer').exists():
            return [f for f in all_fields if f != 'school_approval']
        elif user.groups.filter(name='district_officer').exists():
            if obj and obj.school_approval == 'Pending':
                return all_fields
            return [f for f in all_fields if f != 'district_approval']
        elif user.groups.filter(name='tamisemi_officer').exists():
            if obj and obj.district_approval == 'Pending':
                return all_fields
            return [f for f in all_fields if f != 'tamisemi_approval']
        return all_fields

    def save_model(self, request, obj, form, change):
        user = request.user

        if change:
            try:
                old_obj = models.TransferRequest.objects.get(pk=obj.pk)
            except ObjectDoesNotExist:
                old_obj = None

            # Role-based restrictions
            if user.groups.filter(name='district_officer').exists() and old_obj and old_obj.school_approval == 'Pending':
                self.message_user(request, "District officer cannot act before the school officer.", level=messages.ERROR)
                return

            if user.groups.filter(name='tamisemi_officer').exists() and old_obj and old_obj.district_approval == 'Pending':
                self.message_user(request, "TAMISEMI officer cannot act before the district officer.", level=messages.ERROR)
                return

            # Auto-update overall status
            approvals = {
                'school': obj.school_approval,
                'district': obj.district_approval,
                'tamisemi': obj.tamisemi_approval,
            }

            if all(val == 'Approved' for val in approvals.values()):
                obj.status = 'Approved'
                self.message_user(request, "Transfer status auto-updated to Approved.", level=messages.INFO)
            elif any(val == 'Rejected' for val in approvals.values()):
                obj.status = 'Rejected'
                self.message_user(request, "Transfer status auto-updated to Rejected.", level=messages.INFO)

            # Notify teacher if any changes
            if old_obj and (
                old_obj.school_approval != obj.school_approval or
                old_obj.district_approval != obj.district_approval or
                old_obj.tamisemi_approval != obj.tamisemi_approval or
                old_obj.status != obj.status
            ):
                self.notify_teacher(request, obj)

        super().save_model(request, obj, form, change)

    def notify_teacher(self, request, transfer_request):
        email = transfer_request.teacher.email
        if email:
            subject = f"Transfer Request Update: {transfer_request.status}"
            message = (
                f"Dear {transfer_request.teacher.username},\n\n"
                f"Your transfer request has been updated:\n"
                f"- School Approval: {transfer_request.school_approval}\n"
                f"- District Approval: {transfer_request.district_approval}\n"
                f"- TAMISEMI Approval: {transfer_request.tamisemi_approval}\n"
                f"- Overall Status: {transfer_request.status}\n\n"
                f"Thank you."
            )
            try:
                send_mail(subject, message, None, [email])
            except timeout:
                self.message_user(request, "Email timeout: Unable to notify the teacher.", level=messages.WARNING)
            except Exception as e:
                self.message_user(request, f"Email error: {str(e)}", level=messages.WARNING)

# ✅ Register all models with admin
admin.site.register(models.TeacherProfile, TeacherProfileAdmin)
admin.site.register(models.SchoolOfficerProfile, SchoolOfficerProfileAdmin)
admin.site.register(models.DistrictOfficerProfile, DistrictOfficerProfileAdmin)
admin.site.register(models.TamisemiOfficerProfile, TamisemiOfficerProfileAdmin)
admin.site.register(models.TransferRequest, TransferRequestAdmin)
admin.site.register(models.Region)
admin.site.register(models.District)
admin.site.register(models.Ward)
admin.site.register(models.School)
