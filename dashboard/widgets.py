from django.forms.widgets import CheckboxSelectMultiple

class TableCheckboxSelectMultiple(CheckboxSelectMultiple):
	template_name = "dashboard/forms/widgets/table_checkbox.html"
	option_template_name = "dashboard/forms/widgets/checkbox_option.html"

	class Media:
		css = {"all": ["css/select.css"],}
		js = ["js/select.js"]


class NameCheckboxSelectMultiple(CheckboxSelectMultiple):
	template_name = "dashboard/forms/widgets/name_checkbox.html"
	option_template_name = "dashboard/forms/widgets/checkbox_option.html"

	class Media:
		css = {"all": ["css/select.css"],}
		js = ["js/select.js"]