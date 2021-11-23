from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from .models import Lead, Category
from .forms import LeadModelForm, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm
from django.views import generic 
from agents.mixins import OrganizerLoginRequiredMixin



class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm 

    def get_success_url(self):
        return reverse('login')

class LandingPageView(generic.TemplateView):
    template_name = "landing.html"

class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads"

    # initial queryset of leads for the enire organization
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset =Lead.objects.filter(
                organization=user.userprofile,
                agent__isnull=False
                )
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_organizer:
            queryset =Lead.objects.filter(
                organization=user.userprofile, 
                agent__isnull=True
            )
            context.update(
                {
                    "unassigned_leads": queryset
                }
            )
        return context

def lead_list(request):
    leads = Lead.objects.all()
    context = {
        "leads": leads,

    }
    return render(request, "leads/lead_list.html", context)

class LeadDetailView(LoginRequiredMixin, generic.DetailView): 
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"

    # initial queryset of leads for the enire organization
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset =Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset

def lead_detail(request, pk):
    lead = Lead.objects.get(id=pk)
    context = {
        "lead": lead
    }
    
    return render(request, "leads/lead_detail.html", context)

class LeadCreateView(OrganizerLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm

    def get_success_url(self) -> str:
        return reverse("leads:lead-list")

    def form_valid(self, form) -> HttpResponse:
        #TODO send email
        send_mail(
            subject = "A lead has been created",
            message = "Go to the site to see a new lead",
            from_email = "test@test.com",
            recipient_list = ["test2@test.com"] 

        )
        return super(LeadCreateView, self).form_valid(form)

def lead_create(request):
    form = LeadModelForm()
    if request.method == "POST":
        print("Receiving a post request")
        form = LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        "form": form
    }
    return render(request, "leads/lead_create.html", context)

class LeadUpdateView(OrganizerLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm

    # initial queryset of leads for the enire organization
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self) -> str:
        return reverse("leads:lead-list")

def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadModelForm(instance=lead)
    if request.method == "POST":
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        "lead": lead,
        "form": form
    }
    return render(request, "leads/lead_update.html", context)

class LeadDeleteView(OrganizerLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"
    form_class = LeadModelForm
    queryset = Lead.objects.all()

    def get_success_url(self) -> str:
        return reverse("leads:lead-list")
        
    # initial queryset of leads for the enire organization
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organization=user.userprofile)
        
def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()

class AssignAgentView(OrganizerLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({
            "request": self.request
        })
        return kwargs

    def get_success_url(self) -> str:
        return reverse("leads:lead-list")
        
    def form_valid(self, form):
        agent = form.cleaned_data['agent']
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super().form_valid(form)

class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        contex = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_organizer:
            queryset =Lead.objects.filter(
                organization=user.userprofile,
            )
        else:
            queryset = Lead.objects.filter(
                organization=user.agent.organization
            )

        contex.update({
            "unassigned_lead_count": Lead.objects.filter(category__isnull=True).count()
        }
        )
        return contex

    # initial queryset of leads for the enire organization
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset =Category.objects.filter(
                organization=user.userprofile,
            )
        else:
            queryset = Category.objects.filter(
                organization=user.agent.organization
            )
        return queryset

class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    contex_object_name = "category"

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset =Category.objects.filter(
                organization=user.userprofile,
            )
        else:
            queryset = Category.objects.filter(
                organization=user.agent.organization
            )
        return queryset

class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm

    def get_success_url(self) -> str:
        return reverse("leads:lead-detail", kwargs={"pk": self.get_object().id})

    # initial queryset of leads for the enire organization
    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset =Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset

# def lead_update(request, pk):
#     lead = Lead.objects.get(id=pk)
#     form = LeadForm()
#     if request.method == "POST":
#         print("Receiving a post request")
#         form = LeadForm(request.POST)
#         if form.is_valid():
#             print("The form is valid")
#             print(form.cleaned_data)
#             first_name = form.cleaned_data["first_name"]
#             last_name = form.cleaned_data["last_name"]
#             age = form.cleaned_data["age"]
#             lead.first_name = first_name
#             lead.last_name = last_name
#             lead.age = age
#             lead.save()

#             return redirect("/leads")
#     context = {
#         "form": form,
#         "lead": lead
#     }
#     return render(request, "leads/lead_update.html", context)



# def lead_create(request):
    # form = LeadForm()
    # if request.method == "POST":
    #     print("Receiving a post request")
    #     form = LeadForm(request.POST)
    #     if form.is_valid():
    #         print("The form is valid")
    #         print(form.cleaned_data)
    #         first_name = form.cleaned_data["first_name"]
    #         last_name = form.cleaned_data["last_name"]
    #         age = form.cleaned_data["age"]
    #         agent = Agent.objects.first()
    #         Lead.objects.create(
    #             first_name = first_name,
    #             last_name = last_name,
    #             age = age,
    #             agent = agent
    #         )
    #         print("The lead has been created")
    #         return redirect("/leads")
    # context = {
    #     "form": form
    # }
#     return render(request, "leads/lead_create.html", context)