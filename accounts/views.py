from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .serializers import (
    RegisterSerializer, 
    UserSerializer, 
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    VerifyOTPSerializer,
    ConfirmPasswordResetSerializer,
    CustomTokenObtainPairSerializer
)
from .models import PasswordResetOTP
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import redirect
from urllib.parse import urlencode

# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

"""class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response(
            {'error': 'Invalid username or password'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )"""
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = (AllowAny,)
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'success': 'Logout successful'}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            validated_data = serializer.validated_data

            # Check old password
            if not self.object.check_password(validated_data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            self.object.set_password(validated_data.get("new_password"))
            self.object.save()
            return Response(
                {'success': 'Password changed successfully'}, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

class RefreshTokenView(TokenRefreshView):
    """
    Custom token refresh view that handles JWT token refresh.
    """
    permission_classes = (AllowAny,)


class OAuthSuccessView(APIView):
    """
    Endpoint de puente para OAuth2.
    Se usa luego del login social para emitir JWT y redirigir al frontend.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        refresh = RefreshToken.for_user(request.user)
        query = urlencode({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
        return redirect(f"{settings.FRONTEND_URL}/?{query}")


class PasswordResetRequestView(APIView):
    """
    Endpoint para solicitar reset de contraseña.
    Genera un OTP y lo envía al email del usuario.
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Crear OTP
                otp_obj = PasswordResetOTP.create_otp(user)
                otp = otp_obj.otp
                
                # Renderizar templates
                context = {
                    'username': user.username,
                    'otp': otp,
                }
                
                # Template HTML
                html_message = render_to_string(
                    'emails/password_reset_otp.html',
                    context
                )
                
                # Template texto plano
                text_message = render_to_string(
                    'emails/password_reset_otp.txt',
                    context
                )
                
                # Enviar email con ambas versiones
                send_mail(
                    subject='Password Reset OTP',
                    message=text_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                return Response(
                    {'message': 'OTP enviado a tu email'},
                    status=status.HTTP_200_OK
                )
                
            except User.DoesNotExist:
                # No revelar si el email existe o no
                return Response(
                    {'message': 'Si el email existe, recibirás un OTP'},
                    status=status.HTTP_200_OK
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """
    Endpoint para verificar si el OTP es válido.
    No cambia la contraseña, solo valida el OTP.
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            
            try:
                user = User.objects.get(email=email)
                
                # Buscar OTP válido
                otp_obj = PasswordResetOTP.objects.filter(
                    user=user,
                    otp=otp,
                    is_used=False
                ).first()
                
                if otp_obj and otp_obj.is_valid():
                    return Response(
                        {'message': 'OTP válido', 'valid': True},
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {'error': 'OTP inválido o expirado'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            except User.DoesNotExist:
                return Response(
                    {'error': 'Usuario no encontrado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConfirmPasswordResetView(APIView):
    """
    Endpoint para confirmar el reset de contraseña.
    Valida el OTP y actualiza la contraseña.
    """
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = ConfirmPasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']
            
            try:
                user = User.objects.get(email=email)
                
                # Buscar OTP válido
                otp_obj = PasswordResetOTP.objects.filter(
                    user=user,
                    otp=otp,
                    is_used=False
                ).first()
                
                if otp_obj and otp_obj.is_valid():
                    # Actualizar contraseña
                    user.set_password(new_password)
                    user.save()
                    
                    # Marcar OTP como usado
                    otp_obj.mark_as_used()
                    
                    return Response(
                        {'message': 'Contraseña actualizada exitosamente'},
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {'error': 'OTP inválido o expirado'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
            except User.DoesNotExist:
                return Response(
                    {'error': 'Usuario no encontrado'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
