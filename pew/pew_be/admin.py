
# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = (
        "email",
        "name",
        "role",
        "is_admin",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_admin",
        "is_active",
    )

    search_fields = ("email", "name", "contact_no")
    ordering = ("-created_at",)

    readonly_fields = ("created_at", "last_login")

    fieldsets = (
        ("Basic Info", {
            "fields": ("email", "password", "name", "contact_no")
        }),

        ("Admin Role", {
            "fields": ("is_admin", "is_active")
        }),

        ("Tracking", {
            "fields": ("created_by", "created_at", "last_login")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "name",
                "contact_no",
                "password1",
                "password2",
                "is_admin",
                "is_active",
            ),
        }),
    )

    filter_horizontal = ()