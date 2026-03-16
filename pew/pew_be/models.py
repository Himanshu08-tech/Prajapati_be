
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            name=extra_fields.get("name", ""),
            contact_no=extra_fields.get("contact_no", ""),
            is_admin=extra_fields.get("is_admin", False),
            is_staff=extra_fields.get("is_staff", False),
            is_active=extra_fields.get("is_active", True),
            is_superuser=extra_fields.get("is_superuser", False),  # ✅ YEH LINE ADD KI
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        # ✅ Validation add karo
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        return self.create_user(email, password, **extra_fields)

    def create_admin(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", False)  # ✅ Explicitly False

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="core_user_set",
        blank=True
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="core_user_permissions_set",
        blank=True
    )

    created_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_admins",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def role(self):
        if self.is_superuser:
            return "superuser"
        elif self.is_admin:
            return "admin"
        return "user"

    def can_create_admin(self):
        return self.is_superuser




class Product(models.Model):

    title = models.CharField(max_length=200)

    code = models.CharField(max_length=20, blank=True, null=True)

    description = models.TextField()

    short_description = models.TextField(blank=True, null=True)

    best_use = models.TextField(blank=True, null=True)

    image = models.ImageField(upload_to="products/")

    image_optimized = ImageSpecField(
        source="image",
        processors=[ResizeToFit(1200, 1200)],
        format="JPEG",
        options={"quality": 80},
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)

    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    rating = models.FloatField(default=4.5)

    reviews = models.IntegerField(default=0)

    badge = models.CharField(max_length=50, blank=True, null=True)

    technology = models.TextField(blank=True, null=True)

    capacity = models.CharField(max_length=100, blank=True, null=True)

    weight = models.CharField(max_length=50, blank=True, null=True)

    dimension = models.CharField(max_length=100, blank=True, null=True)

    filters = models.TextField(blank=True, null=True)

    quick_points = models.JSONField(blank=True, null=True)

    highlights = models.JSONField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title