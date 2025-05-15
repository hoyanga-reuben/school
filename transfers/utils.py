# transfers/utils.py

from .models import TeacherProfile, SchoolOfficerProfile, DistrictOfficerProfile, TamisemiOfficerProfile
from django.contrib.auth.models import Group

def get_user_profile(user):
    if user.groups.filter(name="Teacher").exists():
        return TeacherProfile.objects.get(user=user)
    elif user.groups.filter(name="School Officer").exists():
        return SchoolOfficerProfile.objects.get(user=user)
    elif user.groups.filter(name="District Officer").exists():
        return DistrictOfficerProfile.objects.get(user=user)
    elif user.groups.filter(name="Tamisemi Officer").exists():
        return TamisemiOfficerProfile.objects.get(user=user)
    return None
