from django.shortcuts import render
from .serializers import LoginSerializer, AdminSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User

# Create your views here.
class AdminLoginAPIView(APIView):
    """
    Login only for Admin
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

        # ✅ Sirf admin login karega
        if not user.is_admin:
            return Response(
                {"error": "Only admin can access dashboard"},
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
                "is_admin": user.is_admin
            }
        }, status=status.HTTP_200_OK)
    
class AdminRegisterAPIView(APIView):
    """
    Admin CRUD
    Sirf Admin hi admin create/update/delete karega
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):

        # ✅ Sirf admin admin create karega
        if not request.user.is_admin:
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

            return Response({
                "message": "Admin registered successfully",
                "admin": AdminSerializer(admin).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        """Get admins"""

        if not request.user.is_admin:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        if pk:
            try:
                admin = User.objects.get(pk=pk, is_admin=True)
                serializer = AdminSerializer(admin)
                return Response(serializer.data)

            except User.DoesNotExist:
                return Response(
                    {"error": "Admin not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        admins = User.objects.filter(is_admin=True)
        serializer = AdminSerializer(admins, many=True)

        return Response({
            "count": admins.count(),
            "admins": serializer.data
        })

    def patch(self, request, pk):

        if not request.user.is_admin:
            return Response(
                {"error": "Only admin can update admin"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            admin = User.objects.get(pk=pk, is_admin=True)

            serializer = AdminSerializer(
                admin,
                data=request.data,
                partial=True
            )

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

        if not request.user.is_admin:
            return Response(
                {"error": "Only admin can delete admin"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            admin = User.objects.get(pk=pk, is_admin=True)

            # ✅ Admin khud ko delete nahi karega
            if request.user.id == admin.id:
                return Response(
                    {"error": "You cannot delete yourself"},
                    status=status.HTTP_403_FORBIDDEN
                )

            admin_email = admin.email
            admin.delete()

            return Response({
                "message": f"Admin '{admin_email}' deleted successfully"
            })

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