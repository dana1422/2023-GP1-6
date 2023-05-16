from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm
from .models import User,Seeker,Recruiter


class SignupForm(UserCreationForm):
   
    User_Type = forms.ChoiceField(choices=[('Seeker','Seeker'),('Recruiter','Recruiter')])
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'email', 'username', 'password1', 'password2']
        labels = {'first_name': 'Name',}

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})



class SeekerAccountForm(ModelForm):
    class Meta:
        model = Seeker
        fields = ['name', 'email', 'username',
                  'cv','knowledge_area_id',
                  'city', 'short_intro','bio','profile_image',
                  'social_github', 'social_linkedin', 'social_twitter',
                  'social_website']
        labels = {'knowledge_area_id': 'Knowledge area',}
        
        

    def __init__(self, *args, **kwargs):
        super(SeekerAccountForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})


class RecruiterAccountForm(ModelForm):
    class Meta:
        model = Recruiter
        fields = ['name', 'email', 'username','organization',
                  'city', 'short_intro','bio','profile_image',
                  'social_github', 'social_linkedin', 'social_twitter',
                  'social_website']
       

    def __init__(self, *args, **kwargs):
        super(RecruiterAccountForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})
           
    
    
