from django.contrib import admin

from core.models import User


@admin.register(User)
class PersonAdmin(admin.ModelAdmin):
    search_fields = ("username", "email", "first_name", "last_name")
    list_display = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_active", "is_superuser")
    exclude = ("password",)
    readonly_fields = ("date_joined", "last_login")
