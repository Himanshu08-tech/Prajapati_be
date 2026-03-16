from django.shortcuts import render
from .serializers import LoginSerializer, AdminSerializer, ProductSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User,Product
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from .permissions import IsAdminUser, CanCreateAdmin
# Create your views here.
class AdminLoginAPIView(APIView):
    """
    Login for both Superuser and Admin
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        user = authenticate(username=email, password=password)

        if user is None:
            return Response(
                {"error": "Invalid email or password"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if user is admin or superuser
        if not (user.is_admin or user.is_superuser):
            return Response(
                {"error": "You don't have permission to access dashboard"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.is_active:
            return Response(
                {"error": "Account is disabled"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        
        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "is_superuser": user.is_superuser,
                "is_admin": user.is_admin,
                "can_create_admin": user.can_create_admin(),
            }
        }, status=status.HTTP_200_OK)


class AdminRegisterAPIView(APIView):
    """
    Admin CRUD
    Superuser + Admin dono admin create kar sakte hain
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # ✅ Superuser OR Admin allowed
        if not (request.user.is_superuser or request.user.is_admin):
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = AdminSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            admin = serializer.save()
            return Response(
                {
                    "message": "Admin registered successfully",
                    "admin": AdminSerializer(admin).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        """Get Admins - Admin aur Superuser dono dekh sakte hain"""
        if pk:
            try:
                admin = User.objects.get(pk=pk, is_admin=True, is_superuser=False)
                serializer = AdminSerializer(admin)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response(
                    {"error": "Admin not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Sirf admins dikhao, superusers nahi
        admins = User.objects.filter(is_admin=True, is_superuser=False)
        serializer = AdminSerializer(admins, many=True)
        return Response({
            "count": admins.count(),
            "admins": serializer.data
        })

    def patch(self, request, pk):
        """Update Admin - Admin aur Superuser dono"""
        # ✅ Admin ya Superuser check
        if not (request.user.is_superuser or request.user.is_admin):
            return Response(
                {"error": "Only admin or superuser can update admin"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            admin = User.objects.get(pk=pk, is_admin=True, is_superuser=False)
            
            # ✅ Admin sirf khud ko update kar sakta hai (optional security)
            # Agar aap chahte ho ki admin sirf apna profile update kare:
            # if request.user.is_admin and request.user.id != admin.id:
            #     return Response(
            #         {"error": "Admin can only update their own profile"}, 
            #         status=status.HTTP_403_FORBIDDEN
            #     )
            
            serializer = AdminSerializer(admin, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Admin updated successfully",
                    "admin": serializer.data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except User.DoesNotExist:
            return Response(
                {"error": "Admin not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, pk):
        """Delete Admin - Admin aur Superuser dono"""
        # ✅ Admin ya Superuser check
        if not (request.user.is_superuser or request.user.is_admin):
            return Response(
                {"error": "Only admin or superuser can delete admin"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            admin = User.objects.get(pk=pk, is_admin=True, is_superuser=False)
            
            # ✅ Admin khud ko delete nahi kar sakta (security)
            if request.user.id == admin.id:
                return Response(
                    {"error": "You cannot delete yourself"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            admin_email = admin.email
            admin.delete()
            return Response({
                "message": f"Admin '{admin_email}' deleted successfully"
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {"error": "Admin not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class AdminLogoutAPIView(APIView):
    """
    Admin Logout - refresh token blacklist
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {"error": "Refresh token required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )

        except Exception:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class ProductAPIView(APIView):
    """
    GET -> Public
    POST / PATCH / DELETE -> Admin + Superuser
    """
    parser_classes = (MultiPartParser, FormParser,JSONParser)

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request, pk=None):

        if pk:
            try:
                product = Product.objects.get(pk=pk)
                serializer = ProductSerializer(product, context={"request": request})
                return Response(serializer.data)
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        products = Product.objects.all().order_by("-created_at")

        serializer = ProductSerializer(
            products, many=True, context={"request": request}
        )

        return Response({
            "count": products.count(),
            "products": serializer.data
        })

    def post(self, request):
        serializer = ProductSerializer(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Product added", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Product updated", "data": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return Response(
                {"message": "Product deleted"},
                status=status.HTTP_200_OK
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
