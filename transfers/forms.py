from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    TeacherProfile,
    SchoolOfficerProfile,
    DistrictOfficerProfile,
    TamisemiOfficerProfile,
    TransferRequest,
    Region,
    District,
    Ward,
    School,
    ExchangeRequest,
)

# -------------------------
# Registration Form
# -------------------------

class TeacherRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=20, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(required=False)

    ROLE_CHOICES = [
        ('Teacher', 'Teacher'),
        ('School Officer', 'School Officer'),
        ('District Officer', 'District Officer'),
        ('TAMISEMI Officer', 'TAMISEMI Officer'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Registering As')

    school = forms.ModelChoiceField(queryset=School.objects.all(), required=False)
    district = forms.ModelChoiceField(queryset=District.objects.all(), required=False)
    region = forms.ModelChoiceField(queryset=Region.objects.all(), required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password1', 'password2',
            'first_name', 'last_name',
            'phone_number', 'address', 'profile_picture',
            'role', 'school', 'district', 'region'
        ]
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.is_active = False  # Require admin activation
            user.save()

            role = self.cleaned_data['role']
            phone = self.cleaned_data.get('phone_number')
            address = self.cleaned_data.get('address')
            picture = self.cleaned_data.get('profile_picture')
            school = self.cleaned_data.get('school')
            district = self.cleaned_data.get('district')
            region = self.cleaned_data.get('region')

            # Create the appropriate profile based on the selected role
            profile = self.create_profile(user, role, phone, address, picture, school, district, region)
            profile.save()

        return user

    def create_profile(self, user, role, phone, address, picture, school, district, region):
        """Helper method to create the correct profile based on the role."""
        if role == 'Teacher':
            return TeacherProfile(
                user=user,
                phone_number=phone,
                address=address,
                profile_picture=picture,
                school=school,
            )
        elif role == 'School Officer':
            return SchoolOfficerProfile(
                user=user,
                phone_number=phone,
                address=address,
                school=school,
            )
        elif role == 'District Officer':
            return DistrictOfficerProfile(
                user=user,
                phone_number=phone,
                address=address,
                district=district,
            )
        elif role == 'TAMISEMI Officer':
            return TamisemiOfficerProfile(
                user=user,
                phone_number=phone,
                address=address,
                region=region,
            )

        return user

# -------------------------
# Transfer Request Form
# -------------------------

class TransferRequestForm(forms.ModelForm):
    class Meta:
        model = TransferRequest
        fields = [
            # Personal Info
            'full_name',
            'email',
            'sex',
            'subject_taught',
            'teaching_experience',

            # Current School Information
            'current_region', 'current_district', 'current_ward', 'current_school',

            # Desired School Information
            'desired_region', 'desired_district', 'desired_ward', 'desired_school',

            # Reason for Transfer
            'reason',

            # Academic Info
            'form_four_index', 'form_four_certificate',
            'form_six_or_diploma_index', 'form_six_or_diploma_certificate',
            'university_reg_number', 'university_certificate',
        ]

# -------------------------
# Exchange Request Form
# -------------------------

class ExchangeRequestForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = ExchangeRequest
        fields = ['message']
