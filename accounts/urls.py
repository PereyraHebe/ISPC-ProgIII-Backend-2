from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, 
    LoginView, 
    LogoutView, 
    ChangePasswordView, 
    UserDetailView,
    RefreshTokenView,
    PasswordResetRequestView,
    VerifyOTPView,
    ConfirmPasswordResetView,
    OAuthSuccessView,
)

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User endpoints
    path('user/', UserDetailView.as_view(), name='user_detail'),
    path('user/change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Password reset endpoints
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('password-reset-confirm/', ConfirmPasswordResetView.as_view(), name='confirm_password_reset'),
    path('oauth/success/', OAuthSuccessView.as_view(), name='oauth_success'),
    
    # dj-rest-auth endpoints (optional, for additional OAuth support)
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
]