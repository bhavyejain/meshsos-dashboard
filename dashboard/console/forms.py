from django import forms
from .models import Log, Profile
from django.contrib.auth.models import User
import datetime

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('service', 'location', 'phone')


YEARS = [x for x in range(2020, 2100)]

class AnalyticsForm(forms.Form):
    curr_date = datetime.date.today()       # get current date
    startDate = forms.DateField(label="Lower Limit:", initial="2020-04-01", widget=forms.SelectDateWidget(years=YEARS)) # set initial to starting date of project
    endDate = forms.DateField(label="Upper Limit:", initial=curr_date, widget=forms.SelectDateWidget(years=YEARS))      # set initial to today