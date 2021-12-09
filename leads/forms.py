from django import forms
from .models import Category, Lead, Agent, FollowUp
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField


User = get_user_model()


class LeadModelForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = (
            "first_name",
            "last_name",
            "age",
            "agent",
            "description",
            "phone_number",
            "email",
            "profile_picture",
        )

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        agents = Agent.objects.filter(organization=request.user.userprofile)
        super().__init__(*args, **kwargs)
        self.fields["agent"].queryset = agents


class LeadForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    age = forms.IntegerField(min_value=0)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {"username": UsernameField}


class AssignAgentForm(forms.Form):
    agent = forms.ModelChoiceField(queryset=Agent.objects.none())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        agents = Agent.objects.filter(organization=request.user.userprofile)
        super().__init__(*args, **kwargs)
        self.fields["agent"].queryset = agents


class LeadCategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ("category",)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        user = request.user
        queryset = Category.objects.filter(organization=user.userprofile)
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = queryset
        

class FollowUpModelForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = (
            "notes",
            "file"
        )