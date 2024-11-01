from django.db import models
from django.contrib.auth.models import User

class UserP(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile' )
    role = models.CharField(max_length=20, choices=[('client', 'Client'), ('hostelmanager', 'Hostel Manager')])

    def __str__(self):
        return f'{self.user.username} UserP'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.role == 'hostelmanager':
            self.user.is_staff = True
            self.user.save()


class Hostel(models.Model):
    hostel_name = models.CharField(max_length=100)
    # manager = models.ForeignKey(UserP, on_delete=models.CASCADE, related_name='managed_hostels', default=.objects.get(user__username='admin').pk)
    manager_name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    picture = models.ImageField(upload_to='hostel_pictures/')
    contact = models.CharField(max_length=20)
    email = models.EmailField(max_length=254, default='example@example.com')
    number_of_rooms = models.PositiveIntegerField()

    def __str__(self):
        return self.hostel_name

class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.PositiveIntegerField()

    def __str__(self):
        return f"Room {self.room_number} - {self.hostel.hostel_name}"


class Booking(models.Model):
    client_name = models.ForeignKey(UserP, on_delete=models.CASCADE, default=None)
    room_number = models.ForeignKey(Room, on_delete=models.CASCADE, default=None)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, default=None)  
    approved = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.client_name.user.username}'s Booking for Room {self.room_number.room_number}"
