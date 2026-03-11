from django.forms.widgets import CheckboxSelectMultiple

class CustomCheckboxSelectMultiple(CheckboxSelectMultiple):
	template_name = "dashboard/forms/widgets/checkbox_select.html"
	option_template_name = "dashboard/forms/widgets/checkbox_option.html"

	class Media:
		css = {"all": ["css/select.css"],}
		js = ["js/select.js"]