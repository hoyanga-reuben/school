from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Ward(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class School(models.Model):
    name = models.CharField(max_length=100)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class TransferRequest(models.Model):
    # Approval choices
    APPROVAL_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    # Status choices
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]

    # Approval fields
    school_approval = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='Pending')
    district_approval = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='Pending')
    tamisemi_approval = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='Pending')

    # Teacher information
    SEX_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    sex = models.CharField(max_length=10, choices=SEX_CHOICES, default='Male')
    subject_taught = models.CharField(max_length=100)
    teaching_experience = models.PositiveIntegerField(help_text="Years of teaching experience")

    # Current location
    current_region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='transfer_requests_current_region')
    current_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, related_name='transfer_requests_current_district')
    current_ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, related_name='transfer_requests_current_ward')
    current_school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, related_name='transfer_requests_current_school')

    # Desired location
    desired_region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, related_name='transfer_requests_desired_region')
    desired_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, related_name='transfer_requests_desired_district')
    desired_ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, related_name='transfer_requests_desired_ward')
    desired_school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, related_name='transfer_requests_desired_school')

    # Academic details (optional)
    form_four_index = models.CharField(max_length=20, blank=True, null=True)
    form_six_or_diploma_index = models.CharField(max_length=20, blank=True, null=True)
    university_reg_number = models.CharField(max_length=30, blank=True, null=True)

    form_four_certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    form_six_or_diploma_certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    university_certificate = models.FileField(upload_to='certificates/', blank=True, null=True)

    # Transfer reason
    reason = models.TextField()

    # Request status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    # Time tracking
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Cancellation tracking
    cancel_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.full_name} - {self.status}"

    def is_inter_region(self):
        return self.current_region != self.desired_region

    @property
    def can_cancel(self):
        return (
            self.status == "Pending" and
            self.school_approval == "Pending" and
            (timezone.now() - self.created_at <= timedelta(hours=24)) and
            self.cancel_count < 3
        )

    # Approval message for status updates
    def get_approval_message(self):
     messages = {}
     if self.school_approval != 'Pending':
        messages['school_approval'] = f"Your transfer request has been {self.school_approval} by the school."
     if self.district_approval != 'Pending':
        messages['district_approval'] = f"Your transfer request has been {self.district_approval} by the district."
     if self.tamisemi_approval != 'Pending':
        messages['tamisemi_approval'] = f"Your transfer request has been {self.tamisemi_approval} by TAMISEMI."
     messages['status'] = f"Your transfer request status is {self.status}."
     return messages

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='teacher_profiles/', blank=True, null=True)
    allow_transfer_submission = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
class SchoolOfficerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username



class DistrictOfficerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    district = models.ForeignKey('District', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class TamisemiOfficerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    region = models.ForeignKey('Region', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class ExchangeRequest(models.Model):
    teacher_1 = models.ForeignKey(User, related_name='teacher_1', on_delete=models.CASCADE)
    teacher_2 = models.ForeignKey(User, related_name='teacher_2', on_delete=models.CASCADE)
    school_1 = models.ForeignKey(School, related_name='school_1', on_delete=models.CASCADE)
    school_2 = models.ForeignKey(School, related_name='school_2', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    message = models.TextField(blank=True, null=True)  # Add this line to allow messages

    def __str__(self):
        return f"Exchange Request between {self.teacher_1} and {self.teacher_2} - Status: {self.status}"


    # Exchange approval message
    def get_exchange_message(self):
        return f"Exchange request between {self.teacher_1} and {self.teacher_2} is {self.status}."
    
class SchoolOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.school.name}"
class DistrictOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.get_full_name} - {self.district.name}"


class TamisemiOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.region.name}"