from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404, JsonResponse

from stock.models import StockRecord


class DeleteMixin:
    def form_valid(self, form):
        self.object.delete()
        return JsonResponse({"status": True})

    def form_invalid(self, form):
        return JsonResponse({"status": False})


class StockRecordContexMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stock_records"] = StockRecord.objects.filter(seller=self.request.user)
        return context


class FormHandlerMixin:
    def form_valid(self, form):
        form.save()
        return JsonResponse({"status": True})

    def form_invalid(self, form):
        errors = self.serialize_errors(form)
        return JsonResponse({"status": False, "errors": errors})

    def serialize_errors(self, form):
        errors = form.errors.get_json_data()
        return errors


class FilterQuerySetMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        if self.filterable:
            qs = self.apply_filter(qs)
        if self.searchable:
            qs = self.search(qs)
        return qs


class AjaxMixin:
    def render_to_response(self, context, **response_kwargs):
        is_ajax = self.request.headers.get("AJAX")
        if is_ajax == "true":
            self.template_name = self.Ajax_template
        return super().render_to_response(context, **response_kwargs)


class AjaxQuerysetMixin(FilterQuerySetMixin, AjaxMixin):
    pass


class collectionMixin(FilterQuerySetMixin):
    def apply_filter(self, qs):
        status = self.request.GET.get("status")
        query = Q()
        if status != "all" and status:
            query = Q(status=status)
        return qs.filter(query)

    def search(self, qs):
        search = self.request.GET.get("search")
        query = Q()
        if search:
            query = Q(name__icontains=search)

        return qs.filter(query)


class IsSellerMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        if not request.user.user_type == "seller":
            raise Http404()

        return super().dispatch(request, *args, **kwargs)
