from django.utils.translation import gettext_lazy as _
from django import forms
from django.utils import timezone


class RoomSearchForm(forms.Form):
    check_in = forms.DateField(label=_('Check-in'), required=False, widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    check_out = forms.DateField(label=_('Check-out'), required=False, widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'))
    bedroom_count = forms.IntegerField(required=False, min_value=1, label=_('Bedrooms'))
    bathrooms = forms.IntegerField(required=False, min_value=1, label=_('Bathrooms'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean(self):
        data = super().clean()
        start, end = data.get('check_in'), data.get('check_out')
        if bool(start) != bool(end):
            raise forms.ValidationError(_('Please enter both check-in and check-out dates.'))
        if start and end:
            if start < timezone.localdate():
                raise forms.ValidationError(_('Check-in cannot be in the past.'))
            if end <= start:
                raise forms.ValidationError(_('Check-out must be after check-in.'))
        return data
