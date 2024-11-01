from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserP
from .models import Hostel
from .models import Room
from django.forms import inlineformset_factory


class MyUserCreationForm(UserCreationForm):
    role_choices = [
        ('client', 'Client'),
        ('hostelmanager', 'Hostel Manager'),
    ]
    role = forms.ChoiceField(choices=role_choices)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True

        if commit:
            user.save()
            # Create associated UserP instance
            role = self.cleaned_data['role']
            UserP.objects.create(user=user, role=role)
        return user


        
class HostelForm(forms.ModelForm):
    class Meta:
        model = Hostel
        fields = ['hostel_name', 'location', 'picture', 'contact', 'email', 'number_of_rooms'] 
        widgets = {
            'manager_name': forms.HiddenInput(),  # Hide manager_name field
        }

    def clean_number_of_rooms(self):
        number_of_rooms = self.cleaned_data['number_of_rooms']
        if number_of_rooms <= 0:
            raise forms.ValidationError("Number of rooms must be a positive integer.")
        return number_of_rooms
    

class BookingForm(forms.Form):
    room_number = forms.IntegerField(widget=forms.HiddenInput())
    client_name = forms.CharField(widget=forms.HiddenInput())

  