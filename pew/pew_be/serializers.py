from rest_framework import serializers
from .models import User,Product


class AdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'contact_no', 'role', 'created_at']
        read_only_fields = ['id', 'role', 'created_at']

    def create(self, validated_data):
        """
        Dashboard se admin create - Sirf dashboard access, Django admin nahi
        """
        request = self.context.get('request')
        
        user = User.objects.create_admin(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data.get("name", ""),
            contact_no=validated_data.get("contact_no", ""),
        )
        
        # Track who created this admin
        if request and request.user.is_authenticated:
            user.created_by = request.user
            user.save()
            
        return user

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.contact_no = validated_data.get('contact_no', instance.contact_no)
        
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        
        instance.save()
        return instance
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ProductSerializer(serializers.ModelSerializer):

    photo_url = serializers.SerializerMethodField()
    optimized_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_photo_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_optimized_image_url(self, obj):
        request = self.context.get("request")
        if obj.image_optimized and request:
            return request.build_absolute_uri(obj.image_optimized.url)
        return None
    def validate_image(self, image):

        max_size = 5 * 1024 * 1024

        if image.size > max_size:
            raise serializers.ValidationError(
                "Image size must be under 5MB"
            )

        return image