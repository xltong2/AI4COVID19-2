from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from app.models import Account

class RegistrationForm(UserCreationForm):
    
    email = forms.EmailField(max_length=255, help_text="Required. Add a valid email address.")
    
    class Meta:
        model = Account
        fields = ('email', 'username', 'password1', 'password2', 'name', 'phone')
        # fields = ('email', 'username', 'password1', 'password2')
        
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError('Email "%s" is already in use.' % account)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            account = Account.objects.exclude(pk=self.instance.pk).get(username=username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError('Username "%s" is already in use.' % username)

class AccountAuthenticationForm(forms.ModelForm):
    
	password = forms.CharField(label='Password', widget=forms.PasswordInput)

	class Meta:
		model = Account
		fields = ('email', 'password')

	def clean(self):
		if self.is_valid():
			email = self.cleaned_data['email']
			password = self.cleaned_data['password']
			if not authenticate(email=email, password=password):
				raise forms.ValidationError("Invalid login")

class AccountUpdateUsernameForm(forms.ModelForm):
    
    class Meta:
        model = Account
        fields = ('username',)
        
    def clean_username(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            try:
                account = Account.objects.exclude(pk=self.instance.pk).get(username=username)
            except Account.DoesNotExist:
                return username
            raise forms.ValidationError('Username "%s" is already in use.' % username)
        
class AccountUpdateEmailForm(forms.ModelForm):
    
    class Meta:
        model = Account
        fields = ('email',)
        
    def clean_email(self):
        if self.is_valid():
            email = self.cleaned_data['email'].lower()
        try:
            account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError('Email "%s" is already in use.' % account)        

class AccountUpdateNameForm(forms.ModelForm):
    
    class Meta:
        model = Account
        fields = ('name',)
        
    def clean_name(self):
        if self.is_valid():
            name = self.cleaned_data['name']
            return name

class AccountUpdatePhoneForm(forms.ModelForm):
    
    class Meta:
        model = Account
        fields = ('phone',)
        
    def clean_phone(self):
        if self.is_valid():
            phone = self.cleaned_data['phone']
            return phone