from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[c for c in CustomUser.ROLE_CHOICES if c[0] != CustomUser.ROLE_COORDINATOR],
        widget=forms.RadioSelect,
        initial=CustomUser.ROLE_SEEKER,
        help_text='Choose "Support Seeker" if you need help, or "Helper / Volunteer" to offer help.',
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email',
                  'role', 'suburb', 'postcode', 'phone', 'skills', 'bio',
                  'password1', 'password2']
        widgets = {'bio': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'role':
                css = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (css + ' form-control').strip()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone',
                  'suburb', 'postcode', 'skills', 'bio']
        widgets = {'bio': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (css + ' form-control').strip()
