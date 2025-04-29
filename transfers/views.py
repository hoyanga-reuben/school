from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib import messages
from .models import District, Ward, School, TransferRequest, TeacherProfile,SchoolOfficer, DistrictOfficer, TamisemiOfficer, SchoolOfficerProfile, DistrictOfficerProfile, TamisemiOfficerProfile
from .forms import TransferRequestForm, ExchangeRequestForm,TeacherRegistrationForm
from django.db.models import Q
from django.utils.timezone import now
from datetime import timedelta
import json
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from transfers.models import TransferRequest, ExchangeRequest
from django.utils import timezone
from django.views.decorators.http import require_POST
from .decorators import  check_teacher_transfer_unlock
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse

def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('home'))  # Redirect to the home page or wherever you want
        else:
            # Handle invalid login attempt (optional)
            pass

    return render(request, 'login.html')  # Your custom template


@login_required
def transfer_summary(request):
    transfer_requests = TransferRequest.objects.filter(teacher=request.user).order_by('-created_at')

    # Calculate expiration time and time left for each transfer request
    for transfer_request in transfer_requests:
        if transfer_request.status == "Pending" and transfer_request.can_cancel:
            transfer_request.expiration_time = transfer_request.created_at + timedelta(hours=24)
            transfer_request.time_left = transfer_request.expiration_time - timezone.now()
        else:
            transfer_request.expiration_time = None
            transfer_request.time_left = None

    return render(request, 'transfer_summary.html', {
        'transfer_requests': transfer_requests
    })





@login_required
def contact_admin(request):
    return render(request, 'contact_admin.html')

@login_required
@require_POST
def cancel_transfer(request, pk):
    transfer = get_object_or_404(TransferRequest, pk=pk, teacher=request.user)
    time_diff = timezone.now() - transfer.created_at
    if (
        transfer.status == "Pending" and
        not transfer.school_approval and
        time_diff <= timedelta(hours=24) and
        transfer.cancel_count < 3
    ):
        transfer.status = "Cancelled"
        transfer.cancel_count += 1
        transfer.save()
        messages.success(request, "Transfer request cancelled successfully.")
    else:
        messages.error(request, "You cannot cancel this request.")
    return redirect('transfer_summary')

# -------------------------
# Registration View
# -------------------------

def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.is_active = False  # Awaiting admin approval
            user.save()

            print("User created:", user.username)

            # Assign group correctly
            role = form.cleaned_data['role']

            # Map form role to real group name
            role_to_group = {
                'Teacher': 'Teachers',
                'School Officer': 'school_officer',
                'District Officer': 'district_officer',
                'TAMISEMI Officer': 'tamisemi_officer',
            }

            group_name = role_to_group.get(role)
            if group_name:
                group, _ = Group.objects.get_or_create(name=group_name)
                group.user_set.add(user)
                print(f"Group '{group_name}' assigned to user.")

            # Create related profile
            phone = form.cleaned_data.get('phone_number')
            address = form.cleaned_data.get('address')
            picture = form.cleaned_data.get('profile_picture')
            school = form.cleaned_data.get('school')
            district = form.cleaned_data.get('district')
            region = form.cleaned_data.get('region')

            if role == 'Teacher':
                print("Creating TeacherProfile")
                TeacherProfile.objects.create(
                    user=user,
                    phone_number=phone,
                    address=address,
                    profile_picture=picture,
                    school=school
                )
                try:
                    transfer_ct = ContentType.objects.get_for_model(TransferRequest)
                    exchange_ct = ContentType.objects.get_for_model(ExchangeRequest)
                    permissions = [
                        Permission.objects.get(codename='add_transferrequest', content_type=transfer_ct),
                        Permission.objects.get(codename='view_transferrequest', content_type=transfer_ct),
                        Permission.objects.get(codename='change_transferrequest', content_type=transfer_ct),
                        Permission.objects.get(codename='add_exchangerequest', content_type=exchange_ct),
                        Permission.objects.get(codename='view_exchangerequest', content_type=exchange_ct),
                    ]
                    group.permissions.set(permissions)
                    print("Permissions assigned to Teacher group.")
                except Permission.DoesNotExist as e:
                    print(f"Permission error: {e}")

            elif role == 'School Officer':
                print("Creating SchoolOfficerProfile")
                SchoolOfficerProfile.objects.create(
                    user=user,
                    phone_number=phone,
                    address=address,
                    school=school
                )

            elif role == 'District Officer':
                print("Creating DistrictOfficerProfile")
                DistrictOfficerProfile.objects.create(
                    user=user,
                    phone_number=phone,
                    address=address,
                    district=district
                )

            elif role == 'TAMISEMI Officer':
                print("Creating TamisemiOfficerProfile")
                TamisemiOfficerProfile.objects.create(
                    user=user,
                    phone_number=phone,
                    address=address,
                    region=region
                )

            return render(request, 'registration/pending_approval.html')
        else:
            print("Form errors:", form.errors)
    else:
        form = TeacherRegistrationForm()

    return render(request, 'registration/register_teacher.html', {'form': form})

# -------------------------
# Role Checks
# -------------------------

def is_school_officer(user):
    return user.groups.filter(name='school_officer').exists()

def is_district_officer(user):
    return user.groups.filter(name='district_officer').exists()

def is_tamisemi_officer(user):
    return user.groups.filter(name='tamisemi_officer').exists()

def is_teacher(user):
    return user.groups.filter(name='Teachers').exists()

# -------------------------
# Role-Based Redirection
# -------------------------

@login_required
def role_redirect(request):
    user = request.user
    if is_teacher(user) or is_school_officer(user) or is_district_officer(user) or is_tamisemi_officer(user):
        return redirect('transfers:main_dashboard')
    return redirect('transfers:home')

@login_required
def main_dashboard(request):
    user = request.user
    context = {}

    if is_teacher(user):
        context['view'] = 'teacher'
        context['transfer_requests'] = TransferRequest.objects.filter(teacher=user)

    elif is_school_officer(user):
        context['view'] = 'school_officer'
        try:
            officer = SchoolOfficerProfile.objects.get(user=user)
            context['transfer_requests'] = TransferRequest.objects.filter(current_school=officer.school)
        except SchoolOfficerProfile.DoesNotExist:
            messages.error(request, "School Officer profile not found. Please contact admin.")

    elif is_district_officer(user):
        context['view'] = 'district_officer'
        try:
            officer = DistrictOfficerProfile.objects.get(user=user)
            context['transfer_requests'] = TransferRequest.objects.filter(current_district=officer.district)
        except DistrictOfficerProfile.DoesNotExist:
            messages.error(request, "District Officer profile not found. Please contact admin.")

    elif is_tamisemi_officer(user):
        context['view'] = 'tamisemi_officer'
        try:
            officer = TamisemiOfficerProfile.objects.get(user=user)
            context['transfer_requests'] = TransferRequest.objects.filter(current_region=officer.region)
        except TamisemiOfficerProfile.DoesNotExist:
            messages.error(request, "TAMISEMI Officer profile not found. Please contact admin.")

    return render(request, 'transfers/main_dashboard.html', context)


# ✅ Combined Approval Logic
@login_required
def approve_transfer(request, transfer_id):
    transfer = get_object_or_404(TransferRequest, id=transfer_id)
    user = request.user

    if request.method == 'POST':
        approved = False

        # Approve button clicked
        if 'approve' in request.POST:
            if is_school_officer(user):
                if transfer.status == 'Pending':
                    transfer.school_approval = True
                    approved = True
                else:
                    messages.warning(request, "Only pending requests can be approved.")
            
            elif is_district_officer(user):
                if not transfer.school_approval:
                    messages.warning(request, "School officer must approve before you can approve.")
                elif transfer.status == 'Pending':
                    transfer.district_approval = True
                    approved = True
                else:
                    messages.warning(request, "Only pending requests can be approved.")

            elif is_tamisemi_officer(user):
                if not transfer.district_approval:
                    messages.warning(request, "District officer must approve before you can approve.")
                elif transfer.status == 'Pending':
                    transfer.tamisemi_approval = True
                    approved = True
                else:
                    messages.warning(request, "Only pending requests can be approved.")

            if approved:
                messages.success(request, "Transfer approved successfully.")
                if transfer.school_approval and transfer.district_approval and transfer.tamisemi_approval:
                    transfer.status = 'Approved'

        # Reject button clicked
        elif 'reject' in request.POST:
            if is_school_officer(user):
                if transfer.status == 'Pending':
                    transfer.status = 'Rejected'
                    messages.error(request, "Transfer request rejected by school officer.")
                else:
                    messages.warning(request, "Only pending requests can be rejected.")

            elif is_district_officer(user):
                if not transfer.school_approval:
                    messages.warning(request, "School officer must approve before you can reject.")
                elif transfer.status == 'Pending':
                    transfer.status = 'Rejected'
                    messages.error(request, "Transfer request rejected by district officer.")
                else:
                    messages.warning(request, "Only pending requests can be rejected.")

            elif is_tamisemi_officer(user):
                if not transfer.district_approval:
                    messages.warning(request, "District officer must approve before you can reject.")
                elif transfer.status == 'Pending':
                    transfer.status = 'Rejected'
                    messages.error(request, "Transfer request rejected by TAMISEMI officer.")
                else:
                    messages.warning(request, "Only pending requests can be rejected.")

        transfer.save()

    # Determine where to redirect back
    if is_school_officer(user):
        back_url = 'transfers:main_dashboard'
    elif is_district_officer(user):
        back_url = 'transfers:main_dashboard'
    elif is_tamisemi_officer(user):
        back_url = 'transfers:main_dashboard'
    else:
        back_url = 'transfers:home'

    return render(request, 'approve_transfer.html', {'transfer': transfer, 'back_url': back_url})

@login_required
def transfer_map(request):
    transfers = TransferRequest.objects.filter(status='pending').select_related('current_school', 'desired_school')
    transfers = [t for t in transfers if t.current_school and t.desired_school and t.current_school.latitude and t.desired_school.latitude]

    transfer_data = [{
        'full_name': t.full_name,
        'current_name': t.current_school.name,
        'desired_name': t.desired_school.name,
        'current_lat': t.current_school.latitude,
        'current_lng': t.current_school.longitude,
        'desired_lat': t.desired_school.latitude,
        'desired_lng': t.desired_school.longitude,
    } for t in transfers]

    return render(request, 'transfer_map.html', {'transfers': transfers, 'transfers_json': json.dumps(transfer_data)})


@login_required
def received_exchange_requests(request):
    requests = request.user.received_requests.all()
    return render(request, 'received_exchange_requests.html', {'requests': requests})


@login_required
def send_exchange_request(request, receiver_id):
    from django.contrib.auth.models import User
    receiver = get_object_or_404(User, id=receiver_id)

    if request.method == 'POST':
        form = ExchangeRequestForm(request.POST)
        if form.is_valid():
            exchange_request = form.save(commit=False)
            exchange_request.sender = request.user
            exchange_request.receiver = receiver
            exchange_request.save()
            messages.success(request, 'Exchange request sent!')
            return redirect('transfers:exchange_matches')
    else:
        form = ExchangeRequestForm()

    return render(request, 'send_exchange_request.html', {'form': form, 'receiver': receiver})


@login_required
def exchange_matches(request):
    user = request.user
    try:
        current_request = TransferRequest.objects.filter(teacher=user).latest('id')
    except TransferRequest.DoesNotExist:
        messages.error(request, "You must submit a transfer request first.")
        return redirect('transfers:submit_transfer')

    matches = TransferRequest.objects.filter(
        current_school=current_request.desired_school,
        desired_school=current_request.current_school,
        status='pending'
    ).exclude(teacher=user)

    return render(request, 'exchange_matches.html', {'matches': matches})


@login_required
def all_transfer_requests(request):
    user = request.user
    subject_filter = request.GET.get('subject')
    status_filter = request.GET.get('status')

    try:
        current_request = TransferRequest.objects.filter(teacher=user).latest('id')
        user_region = current_request.current_region
    except TransferRequest.DoesNotExist:
        user_region = None

    requests = TransferRequest.objects.filter(current_region=user_region).exclude(teacher=user) if user_region else TransferRequest.objects.none()

    if subject_filter:
        requests = requests.filter(subject_taught__icontains=subject_filter)
    if status_filter:
        requests = requests.filter(status=status_filter)

    return render(request, 'all_transfer_requests.html', {
        'requests': requests,
        'subject_filter': subject_filter,
        'status_filter': status_filter,
    })


def get_districts(request):
    region_id = request.GET.get('region_id')
    districts = District.objects.filter(region_id=region_id).values('id', 'name') if region_id else []
    return JsonResponse({'districts': list(districts)})


def get_wards(request):
    district_id = request.GET.get('district_id')
    wards = Ward.objects.filter(district_id=district_id).values('id', 'name') if district_id else []
    return JsonResponse({'wards': list(wards)})


def get_schools(request):
    ward_id = request.GET.get('ward_id')
    schools = School.objects.filter(ward_id=ward_id).values('id', 'name') if ward_id else []
    return JsonResponse({'schools': list(schools)})


@login_required
def transfer_success(request):
    try:
        latest_request = TransferRequest.objects.filter(teacher=request.user).latest('created_at')
    except TransferRequest.DoesNotExist:
        messages.error(request, "No transfer request found.")
        return redirect('transfers:submit_transfer')

    return render(request, 'transfer_success.html', {'request_obj': latest_request})


@login_required
@check_teacher_transfer_unlock
def submit_transfer(request):
    if request.method == "POST":
        form = TransferRequestForm(request.POST, request.FILES)
        if form.is_valid():
            transfer_request = form.save(commit=False)
            transfer_request.teacher = request.user
            transfer_request.save()
            messages.success(request, "Transfer request submitted successfully!")
            return redirect('transfers:transfer_success')
        else:
            messages.error(request, "There was an error in your form.")
    else:
        form = TransferRequestForm()
    return render(request, 'submit_transfer.html', {'form': form})


@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def transfer_history(request):
    transfer_requests = TransferRequest.objects.filter(teacher=request.user).order_by('-submitted_at')
    return render(request, 'transfer_history.html', {'transfer_requests': transfer_requests})
   

@login_required
def school_pending_transfers(request):
    return render(request, 'transfers/school_pending_transfers.html')
@login_required
def district_pending_transfers(request):
    return render(request, 'transfers/district_pending_transfers.html')
@login_required
def region_pending_transfers(request):
    return render(request, 'transfers/region_pending_transfers.html')
@login_required
def profile_view(request):
    return render(request, 'transfers/profile.html')
@login_required
def edit_profile(request):
    # For now, just render a basic page (later you can add a form)
    return render(request, 'transfers/edit_profile.html')



