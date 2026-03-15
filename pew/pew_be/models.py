
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            name=extra_fields.get("name", ""),
            contact_no=extra_fields.get("contact_no", ""),
            is_admin=extra_fields.get("is_admin", False),
            is_active=True,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_admin(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_admin", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_admins"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def role(self):
        if self.is_admin:
            return "admin"
        return "user"

    def can_login(self):
        return self.is_admin and self.is_active