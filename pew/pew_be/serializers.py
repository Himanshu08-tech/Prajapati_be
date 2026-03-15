from rest_framework import serializers
from .models import User


class AdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "password",
            "contact_no",
            "role",
            "created_at"
        ]
        read_only_fields = ["id", "role", "created_at"]

    def create(self, validated_data):
        request = self.context.get("request")

        user = User.objects.create_admin(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data.get("name", ""),
            contact_no=validated_data.get("contact_no", "")
        )

        # kis admin ne create kiya track karne ke liye
        if request and request.user.is_authenticated:
            user.created_by = request.user
            user.save(update_fields=["created_by"])

        return user

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.email = validated_data.get("email", instance.email)
        instance.contact_no = validated_data.get("contact_no", instance.contact_no)

        if "password" in validated_data:
            instance.set_password(validated_data["password"])

        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

