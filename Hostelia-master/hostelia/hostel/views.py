from django.utils.encoding import force_str
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import  force_bytes, force_str

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View

from .forms import MyUserCreationForm, HostelForm, BookingForm
from .models import UserP, Hostel, Room, Booking
from django.views.decorators.csrf import csrf_exempt


def home(request):
    hostels = Hostel.objects.all()
    return render(request, 'base/home.html', {'hostels': hostels})

# @login_required
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('hm_home') 
            else:
                return redirect('client_dashboard')  
        else:
            messages.error(request, "Invalid Credentials")
    return render(request, 'base/login.html')

def logoutUser(request):
    logout(request)  
    return redirect('home')

# def register(request):
#     if request.method == 'POST':
#         form = MyUserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('home')
#             else:
#                 messages.error(request, "Failed to authenticate user.")
#         else:
#             messages.error(request, "Form is not valid. Please correct the errors.")
#     else:
#         form = MyUserCreationForm()
#     return render(request, 'base/register.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Failed to authenticate user.")
        else:
            messages.error(request, "Form is not valid. Please correct the errors.")
    else:
        form = MyUserCreationForm()
    return render(request, 'base/register.html', {'form': form})


@login_required
def client_dashboard(request):
    hostels = Hostel.objects.all()
    return render(request, 'dashboard/client_dashboard.html', {'hostels': hostels})





def client_booking(request, hostel_id):
    hostel = get_object_or_404(Hostel, pk=hostel_id)
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        room = get_object_or_404(Room, hostel=hostel, room_number=room_number)
        client = request.user.profile  
        Booking.objects.create(client_name=client, room_number=room, hostel=hostel)
        return redirect('success_booking', hostel_id=hostel_id)
    else:
        rooms = Room.objects.filter(hostel=hostel)
        return render(request, 'booking/client_booking.html', {'hostel': hostel, 'rooms': rooms, 'hostel_id': hostel_id})





@login_required
def hm_booking(request):
    user_hostel = Hostel.objects.filter(manager_name=request.user.username).first()
    if user_hostel:
        bookings = Booking.objects.filter(hostel=user_hostel)
        print(bookings)  # Add this line to check bookings

    else:
        bookings = Booking.objects.none()  
    return render(request, 'booking/hm_booking.html', {'bookings': bookings})

# @login_required
def book_room(request):
    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        client_name = request.user.username
        confirmation_message = f"{client_name} booked room {room_number}"
        return JsonResponse({'message': confirmation_message})
    else:
        return JsonResponse({'error': 'Invalid request method'})


def register_hostel(request):
    if request.method == 'POST':
        form = HostelForm(request.POST, request.FILES)
        if form.is_valid():
            hostel = form.save(commit=False) 
            hostel.manager_name = request.user.username 
            hostel.save()  
            number_of_rooms = form.cleaned_data['number_of_rooms']
            for room_number in range(1, number_of_rooms + 1):
                Room.objects.create(hostel=hostel, room_number=room_number)

            return redirect('hm_home')
    else:
        form = HostelForm()
    return render(request, 'dashboard/register_hostel.html', {'form': form})




def success_booking(request, hostel_id):
    if hostel_id is None:
        hostel_id = request.GET.get('hostel_id')
        if hostel_id is None:
            return HttpResponse("Hostel ID is missing in the URL.")

    return render(request, 'booking/success_booking.html', {'hostel_id': hostel_id})



def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.approved = True
    booking.save()

    # Get hostel and manager name
    hostel_name = booking.hostel.hostel_name
    manager_name = booking.hostel.manager_name

    # Render the email content from template
    email_content = render_to_string('text/approval_email.txt', {
        'client_name': booking.client_name,
        'hostel_name': hostel_name,
        'manager_name': manager_name
    })

    # Send the email
    send_mail(
        'Booking Approval',
        email_content,
        'hostelia33@gmail.com',  # Sender's email
        [booking.client_name.user.email],  # List of recipients
        fail_silently=False,
    )

    messages.success(request, 'Booking has been approved and email sent.')
    return redirect('hm_booking')

def decline_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.declined = True
    booking.save()
    
    # Get hostel and manager name
    hostel_name = booking.hostel.hostel_name
    manager_name = booking.hostel.manager_name
    
    # Render the email content from template
    email_content = render_to_string('text/decline_email.txt', {
        'client_name': booking.client_name,
        'hostel_name': hostel_name,
        'manager_name': manager_name
    })
    
    # Send the email
    send_mail(
        'Booking Disapproval',
        email_content,
        'hostelia33@gmail.com',  # Sender's email
        [booking.client_name.user.email],  # List of recipients
        fail_silently=False,
    )
    
    messages.success(request, 'Booking has been declined and email sent.')
    return redirect('hm_booking')


def add_room(request):
    if request.method == 'POST':
        hostel_id = request.POST.get('hostel_id')
        room_number = request.POST.get('room_number')
        if hostel_id and room_number:
            hostel = Hostel.objects.get(id=hostel_id)
            Room.objects.create(hostel=hostel, room_number=room_number)
            messages.success(request, 'Room added successfully')
            return redirect('hm_dashboard')
        else:
            messages.error(request, 'Please provide both hostel and room number')
    hostels = Hostel.objects.all()
    return render(request, 'dashboard/add_room.html', {'hostels': hostels})




def update_room(request, room_id):
    room = Room.objects.get(id=room_id)
    # Handle room update logic here
    return redirect('hm_dashboard')


@csrf_exempt
def remove_room(request, room_id):
    if request.method == 'POST':
        try:
            room = Room.objects.get(id=room_id)
            hostel_id = room.hostel.id  # Get the hostel ID before deleting the room
            room.delete()
            messages.success(request, "Room deleted successfully")
            # Redirect back to the hostel dashboard with the same hostel_id
            return redirect('hm_dashboard', hostel_id=hostel_id)
        except Room.DoesNotExist:
            messages.error(request, "Room not found")
        except IntegrityError:
            messages.error(request, "Room is referenced by another object and cannot be deleted")
    
    return redirect('hm_dashboard')


@login_required
def hm_history(request):
    user_hostel = Hostel.objects.filter(manager_name=request.user.username).first()
    if user_hostel:
        bookings = Booking.objects.filter(hostel=user_hostel)
    else:
        bookings = Booking.objects.none()
    return render(request, 'dashboard/hm_history.html', {'bookings': bookings})




@login_required
def hm_dashboard(request, hostel_id=None):
    if hostel_id:
        hostel = get_object_or_404(Hostel, id=hostel_id)
        rooms = hostel.rooms.all()
        return render(request, 'dashboard/hm_dashboard.html', {'hostel': hostel, 'rooms': rooms})
    else:
        hostels = Hostel.objects.filter(manager_name=request.user.username)
        if not hostels.exists():
            return HttpResponseRedirect(reverse('register_hostel'))
        else:
            # If no specific hostel ID is provided, display the first hostel's dashboard
            first_hostel = hostels.first()
            rooms = first_hostel.rooms.all()
            return render(request, 'dashboard/hm_dashboard.html', {'hostel': first_hostel, 'rooms': rooms})

@login_required
def hm_home(request):
    # Retrieve hostels managed by the currently logged-in user
    hostels = Hostel.objects.filter(manager_name=request.user.username)
    user_hostel = Hostel.objects.filter(manager_name=request.user.username).first()
    hostel_name = user_hostel.hostel_name if user_hostel else None
    if not hostels.exists():
        return HttpResponseRedirect(reverse('register_hostel'))
    return render(request, 'dashboard/hm_home.html', {'hostels': hostels})


# Password Reset Form View
class PasswordResetView(View):
    def get(self, request):
        return render(request, 'reset/password_reset_form.html')
    
    def post(self, request):
        email = request.POST.get('email')
        if not email:
            messages.error(request, "Please enter a valid email address.")
            return render(request, 'reset/password_reset_form.html')

        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_decode(uidb64)
            current_site = get_current_site(request)
            domain = current_site.domain
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            subject = 'Password Reset Request'
            message = render_to_string('text/password_reset_email.txt', {
                'user': user,
                'domain': domain,
                'uid': uid,
                'token': token,
                'reset_link': reset_link
            })
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        return redirect('password_reset_done')

# Password Reset Done View
class PasswordResetDoneView(View):
    def get(self, request):
        return render(request, 'reset/password_reset_done.html')

# Password Reset Confirm View
class PasswordResetConfirmView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            return render(request, 'reset/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
        else:
            messages.error(request, "The password reset link is invalid.")
            return redirect('password_reset')

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            if new_password1 and new_password1 == new_password2:
                user.set_password(new_password1)
                user.save()
                return redirect('password_reset_complete')
            else:
                messages.error(request, "Passwords do not match.")
                return render(request, 'reset/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
        else:
            messages.error(request, "The password reset link is invalid.")
            return redirect('password_reset')


# Password Reset Complete View
class PasswordResetCompleteView(View):
    def get(self, request):
        return render(request, 'reset/password_reset_complete.html')
