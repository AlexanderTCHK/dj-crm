from django.contrib import messages
import datetime
from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .models import Lead, Category, FollowUp
from .forms import (
    LeadModelForm,
    CustomUserCreationForm,
    AssignAgentForm,
    LeadCategoryUpdateForm,
    FollowUpModelForm
)
from django.views import generic
from agents.mixins import OrganizerLoginRequiredMixin


class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")


class LandingPageView(generic.TemplateView):
    template_name = "landing.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)


class DashboardView(OrganizerLoginRequiredMixin, generic.TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # How many leads we have in total
        total_lead_count = Lead.objects.filter(organization=user.userprofile).count()

        # How many new leads in the last 30 days
        thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
        total_in_past30 = Lead.objects.filter(
                    organization=user.userprofile, 
                    date_added__gte=thirty_days_ago).count()
                    
        # How many converted leads in the last 30 days
        converted_category = Category.objects.get(organization=user.userprofile, name="Converted")
        print(converted_category)
        converted_in_last30 = Lead.objects.filter(
                    organization=user.userprofile, 
                    category=converted_category,
                    converted_date__gte=thirty_days_ago).count()
        print(converted_in_last30)

        context.update({
                "total_lead_count": total_lead_count,
                "total_in_past30": total_in_past30,
                "converted_in_last30": converted_in_last30,
        })
        return context

class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads"
    
    # initial queryset of leads for the enire organization
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile, agent__isnull=False

            )
            queryset = Lead.objects.exclude(
                category__name="Unassigned"
                
            )
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
            # queryset = queryset.exclude(agent__user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_organizer:
            unassigned_leads = Lead.objects.filter(
                category=Category.objects.get(organization=user.userprofile, name="Unassigned")
            )
            new_leads = Lead.objects.filter(
                category=Category.objects.get(organization=user.userprofile, name="New")
            )
            context.update({
                "unassigned_leads": unassigned_leads,
                "new_leads": new_leads,
                })
        return context


class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"

    # initial queryset of leads for the enire organization
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset


class LeadCreateView(OrganizerLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({"request": self.request})
        return kwargs

    def get_success_url(self) -> str:
        return reverse("leads:lead-list")

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organization = self.request.user.userprofile
        if lead.agent and (lead.category == None):
            categoty_instanse_id = Category.objects.get(
                name="New", organization=lead.organization
            )
            lead.category = categoty_instanse_id
        else:
            categoty_instanse_id = Category.objects.get(
                name="Unassigned", organization=lead.organization
            )
            lead.category = categoty_instanse_id
        lead.save()

        
        send_mail(
            subject="A lead has been created",
            message="Go to the site to see a new lead",
            from_email="test@test.com",
            recipient_list=["test2@test.com"],
        )
        messages.success(self.request, "You have successfully created a lead!")
        return super(LeadCreateView, self).form_valid(form)


class LeadUpdateView(OrganizerLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({"request": self.request})
        return kwargs

    # initial queryset of leads for the enire organization
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self) -> str:
        return reverse("leads:lead-list")


class LeadDeleteView(OrganizerLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"

    def get_success_url(self) -> str:
        return reverse("leads:lead-list")

    # initial queryset of leads for the enire organization
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organization=user.userprofile)


class AssignAgentView(OrganizerLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({"request": self.request})
        return kwargs

    def get_success_url(self) -> str:
        return reverse("leads:lead-list")

    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        user = self.request.user
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.category = Category.objects.get(organization=user.userprofile, name="New")
        lead.save()
        return super().form_valid(form)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_organizer:
            queryset = Lead.objects.filter(
                organization=user.userprofile,
            )

        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)

        contex.update(
            {
                "new": queryset.filter(category__name__iexact="New").count(),
                "unassigned": queryset.filter(
                    category__name__iexact="Unassigned"
                ).count(),
                "contacted": queryset.filter(
                    category__name__iexact="Contacted"
                ).count(),
                "converted": queryset.filter(
                    category__name__iexact="Converted"
                ).count(),
                "unconverted": queryset.filter(
                    category__name__iexact="Unconverted"
                ).count(),
            }
        )
        return contex

    # initial queryset of leads for the enire organization
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Category.objects.filter(
                organization=user.userprofile,
            )
        else:
            queryset = Category.objects.filter(organization=user.agent.organization)
        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    contex_object_name = "category"

    def get_queryset(self):
        user = self.request.user

        if user.is_organizer:
            queryset = Category.objects.filter(
                organization=user.userprofile,
            )
        else:
            queryset = Category.objects.filter(organization=user.agent.organization)
        return queryset


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm
    model = Lead

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({"request": self.request})
        return kwargs

    def get_success_url(self) -> str:
        return reverse("leads:lead-list")

    def form_valid(self, form):
        user = self.request.user
        lead_befor_update = self.get_object()
        instance = form.save(commit=False)
        converted_category = Category.objects.get(organization=user.userprofile, name="Converted")
        if form.cleaned_data["category"] == converted_category:
            # update the date at which this lead was converted
            if lead_befor_update.category != converted_category:
                # this lead has now been converted
                instance.converted_date = timezone.now()
        instance.save()
        return super().form_valid(form)

class FollowUpCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "leads/followup_create.html"
    form_class = FollowUpModelForm

    def get_success_url(self) -> str:
        print(self.kwargs["pk"])
        return reverse("leads:lead-detail", kwargs={"pk": self.kwargs["pk"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "lead": Lead.objects.get(pk=self.kwargs["pk"])
        })
        return context
    
    def form_valid(self, form):
        lead = Lead.objects.get(pk=self.kwargs["pk"])
        followup = form.save(commit=False)
        followup.lead = lead
        followup.save()
        return super().form_valid(form)


class FollowUpUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_followup_update.html"
    form_class = FollowUpModelForm

    def get_success_url(self) -> str:
        return reverse("leads:lead-detail", kwargs={"pk": self.get_object().lead.id})

    # initial queryset of leads for the enire organization
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:

            queryset = FollowUp.objects.filter(lead__organization=user.userprofile)
        else:
            queryset = FollowUp.objects.filter(lead__organization=user.agent.organization)
            # filter for the agent that is logged in
            queryset = queryset.filter(lead__agent__user=user)
        return queryset


class FollowUpDeleteView(OrganizerLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/followup_delete.html"

    def get_success_url(self) -> str:
        return reverse("leads:lead-detail", kwargs={"pk": self.get_object().lead.id})

    # initial queryset of leads for the enire organization
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:

            queryset = FollowUp.objects.filter(lead__organization=user.userprofile)
        else:
            queryset = FollowUp.objects.filter(lead__organization=user.agent.organization)
            # filter for the agent that is logged in
            queryset = queryset.filter(lead__agent__user=user)
        return queryset

