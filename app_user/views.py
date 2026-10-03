from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema

from .serializers import SignUpSerializer, LoginSerializer, UserProfileSerializer
from .models import User


class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(summary="Yangi foydalanuvchini ro'yxatdan o'tkazish")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Ro'yxatdan o'tgach darhol JWT token taqdim etish
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi",
            "user": UserProfileSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(request=LoginSerializer, summary="Tizimga kirish (JWT token olish)")
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Tizimga muvaffaqiyatli kirildi",
            "user": UserProfileSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Foydalanuvchi profilini ko'rish va tahrirlash")
    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(summary="Tizimdan chiqish (Refresh tokenni bekor qilish)")
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Muvaffaqiyatli chiqildi"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Yaroqsiz token"}, status=status.HTTP_400_BAD_REQUEST)