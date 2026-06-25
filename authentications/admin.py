from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    
    # Optionally, you can add filters or search fields for better admin interface
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')

# Register the CustomUser model with the CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)