from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, login_not_required
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.http import url_has_allowed_host_and_scheme, urlsafe_base64_decode
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import views as auth_views

from .forms import UserRegistrationForm, UserProfileForm, CustomAuthenticationForm
from order.models import Order
from address.models import Address
from wishlist.models import WishList
from .models import Profile

UserModel = get_user_model()
INTERNAL_REGISTRATION_SESSION_TOKEN = "_registration_token"

class PasswordContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {"title": self.title, "subtitle": None, **(self.extra_context or {})}
        )
        return context

class RegistrationView(CreateView):
    email_template_name = "registration/registration_email.html"
    extra_email_context = None
    form_class = UserRegistrationForm
    from_email = None
    html_email_template_name = None
    subject_template_name = "registration/registration_subject.txt"
    success_url = reverse_lazy("account:registration_done")
    template_name = "registration/register.html"
    title = _("Register")
    token_generator = default_token_generator

    def form_valid(self, form):
        opts = {
            "use_https": self.request.is_secure(),
            "token_generator": self.token_generator,
            "from_email": self.from_email,
            "email_template_name": self.email_template_name,
            "subject_template_name": self.subject_template_name,
            "request": self.request,
            "html_email_template_name": self.html_email_template_name,
            "extra_email_context": self.extra_email_context,
        }
        form.save(**opts)
        self.request.session["email"] = form.cleaned_data["email"]
        return super().form_valid(form)



class RegistrationDoneView(PasswordContextMixin, TemplateView):
    template_name = "registration/registration_done.html"
    title = _("Activition Email sent")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = self.request.session.get("email")
        return context


@method_decorator(login_not_required, name="dispatch")
class RegistrationConfirmView(PasswordContextMixin, TemplateView):
    template_name = 'registration/registration_complete.html'
    token_generator = default_token_generator
    title = "registration complete"
    confirm_registration_url_token = "confirm-registration"

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):

        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        self.validlink = False
        self.user = self.get_user(kwargs["uidb64"])
       
        if self.user is not None:
            token = kwargs["token"]
            if token == self.confirm_registration_url_token:
                session_token = self.request.session.get(INTERNAL_REGISTRATION_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    self.validlink=True
                    self.user.is_active=True
                    self.user.save()
                    Profile.objects.create(user=self.user)
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_REGISTRATION_SESSION_TOKEN] = token

                    redirect_url = self.request.path.replace(
                        token, self.confirm_registration_url_token
                    )
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())



    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            pk = UserModel._meta.pk.to_python(uid)
            user = UserModel._default_manager.get(pk=pk)
        except (
            TypeError,
            ValueError,
            OverflowError,
            UserModel.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context["validlink"] = True
        else:
            context.update(
                {

                    "title": _("Password reset unsuccessful"),
                    "validlink": False,
                }
            )
        return context



class ProfileView(TemplateView):
    template_name = "account/profile.html"

class UpdateProfileView(UpdateView):
    model = UserModel
    form_class = UserProfileForm
    template_name = "account/edit_profile.html"


    def form_valid(self, form):
        obj = form.save()
        return JsonResponse({"status":True})

    def form_invalid(self, form):
        errors = form.errors
        return JsonResponse({"status":False, "errors":errors})


class DeleteProfileView(DeleteView):
    model = UserModel
    template_name = "account/delete_profile.html"
    success_url = "login"

class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "registration/password_change.html"

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return JsonResponse({"status":True})
    def form_invalid(self, form):

        return JsonResponse({"status":False, "errors":form.errors})


class OrderHistoryView(ListView):
    model = Order
    template_name = "account/order/order_history.html"


    def get_queryset(self):
        qs = super().get_queryset()

        return qs.filter(user=self.request.user)

class OrderDetailView(DetailView):
    model = Order
    template_name = "account/order/order_detail.html"


class AddressBookView(ListView):
    model = Address
    template_name = "account/address/address_book.html"


    def get_queryset(self):
        qs = super().get_queryset()

        return qs.filter(user=self.request.user)

class WishlistView(ListView):
    model = WishList
    template_name = "account/wishlist/wishlist.html"


    def get_queryset(self):
        qs = super().get_queryset()

        return qs.filter(user=self.request.user)

class WishlistDeleteView(DeleteView):
    model = WishList

    def get_object(self, queryset=None):
        wishlist_id = self.request.POST.get("id")
        try:
            wishlist_id = int(wishlist_id)
            wishlist_object = WishList.objects.get(id=wishlist_id)
        except (WishList.DoesNotExist, ValueError):
            return None
        return wishlist_object

    def form_valid(self, form):
        if self.object:
            self.object.delete()
            return JsonResponse({"status":True})
        return JsonResponse({"status":False})





class LoginView(auth_views.LoginView):
    form_class = CustomAuthenticationForm

class PasswordResetView(auth_views. PasswordResetView):
    template_name = "registration/pass_reset_form.html"
    email_template_name = "registration/pass_reset_email.html"
    subject_template_name = "registration/pass_reset_subject.txt"
    success_url = reverse_lazy("account:password_reset_done")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        self.request.session["email"] = email
        print(self.request.session.get("email"))
        return super().form_valid(form) 

class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "registration/pass_reset_done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email"] = self.request.session.get("email")
        return context



class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "registration/pass_reset_confirm.html"
    success_url = reverse_lazy("account:password_reset_complete")

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "registration/pass_reset_complete.html"

class LogoutView(auth_views.LogoutView):
    pass