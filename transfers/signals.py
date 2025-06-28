from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import TeacherProfile, SchoolOfficerProfile, DistrictOfficerProfile, TamisemiOfficerProfile
from .models import TransferRequest, Notification
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create the corresponding profile when a new User is created."""
    if created:
        role = instance.profile.role if hasattr(instance, 'profile') else None

        if role == 'Teacher':
            TeacherProfile.objects.create(user=instance)
        elif role == 'School Officer':
            SchoolOfficerProfile.objects.create(user=instance)
        elif role == 'District Officer':
            DistrictOfficerProfile.objects.create(user=instance)
        elif role == 'TAMISEMI Officer':
            TamisemiOfficerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Save the profile when the User is saved."""
    if hasattr(instance, 'teacherprofile'):
        instance.teacherprofile.save()
    elif hasattr(instance, 'schoolofficerprofile'):
        instance.schoolofficerprofile.save()
    elif hasattr(instance, 'districtofficerprofile'):
        instance.districtofficerprofile.save()
    elif hasattr(instance, 'tamisemiofficerprofile'):
        instance.tamisemiofficerprofile.save()



@receiver(post_save, sender=TransferRequest)
def create_transfer_notification(sender, instance, created, **kwargs):
    if not created:
        status = instance.status
        teacher_user = instance.teacher
        if status in ['School Approved', 'District Approved', 'TAMISEMI Approved', 'Rejected']:
            Notification.objects.create(
                user=teacher_user,
                message=f"Your transfer request was {status.lower()}."
            )

