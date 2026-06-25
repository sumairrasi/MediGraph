from django.contrib import admin
from .models import ModelConfiguration, NameChoice
from django import forms

class ModelConfigurationForm(forms.ModelForm):
    class Meta:
        model = ModelConfiguration
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate the `name` field with choices from NameChoice
        self.fields['name'].widget = forms.Select(
            choices=[(choice.key, choice.display) for choice in NameChoice.objects.all()]
        )


@admin.register(ModelConfiguration)
class ModelConfigurationAdmin(admin.ModelAdmin):
    # Use the custom form
    form = ModelConfigurationForm
    list_display = ('name', 'sector_id', 'role_id', 'model_id', 'save_chat')
    # Fields to filter the configurations
    list_filter = ('sector_id', 'role_id', 'model_id', 'save_chat')
    # Fields to search
    search_fields = ('name', 'sector_id', 'role_id', 'model_id')
    # Fields editable in the form view
    fields = ('name', 'sector_id', 'role_id', 'model_id', 'save_chat')


@admin.register(NameChoice)
class NameChoiceAdmin(admin.ModelAdmin):
    list_display = ('key', 'display')
    search_fields = ('key', 'display')