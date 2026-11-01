from django.utils.translation import gettext_lazy as _
from django import forms
from django.utils import timezone
from .models import Booking
from room.models import Room


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('guest_name', 'guest_email', 'check_in', 'check_out', 'room', 'special_request')
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'check_out': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'special_request': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, selected_room=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(available=True)
        if selected_room:
            self.fields['room'].queryset = Room.objects.filter(pk=selected_room.pk)
            self.fields['room'].initial = selected_room
            self.fields['room'].disabled = True
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        for name in ('check_in', 'check_out'):
            self.fields[name].widget.attrs['min'] = timezone.localdate().isoformat()

    def clean_check_in(self):
        value = self.cleaned_data['check_in']
        if value < timezone.localdate():
            raise forms.ValidationError(_('Check-in cannot be in the past.'))
        return value
