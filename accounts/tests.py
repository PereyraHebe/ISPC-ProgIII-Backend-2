"""
Tests para autenticación JWT y OAuth
"""

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterTestCase(APITestCase):
    """Tests para endpoint de registro"""

    def setUp(self):
        self.register_url = reverse('register')
        self.user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPassword123!',
            'password2': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_register_success(self):
        """Test: Registrar nuevo usuario exitosamente"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')

    def test_register_duplicate_username(self):
        """Test: Registrar con username duplicado"""
        User.objects.create_user(
            username='newuser',
            email='existing@example.com',
            password='TestPassword123!'
        )
        
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        """Test: Registrar con email duplicado"""
        User.objects.create_user(
            username='existinguser',
            email='newuser@example.com',
            password='TestPassword123!'
        )
        
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        """Test: Contraseñas no coinciden"""
        data = self.user_data.copy()
        data['password2'] = 'DifferentPassword123!'
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        """Test: Contraseña débil"""
        data = self.user_data.copy()
        data['password'] = '123'
        data['password2'] = '123'
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        """Test: Campos faltantes"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTestCase(APITestCase):
    """Tests para endpoint de login"""

    def setUp(self):
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!'
        )

    def test_login_success(self):
        """Test: Login exitoso"""
        data = {
            'username': 'testuser',
            'password': 'TestPassword123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_login_invalid_username(self):
        """Test: Username incorrecto"""
        data = {
            'username': 'wronguser',
            'password': 'TestPassword123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_invalid_password(self):
        """Test: Contraseña incorrecta"""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_credentials(self):
        """Test: Falta el password"""
        data = {
            'username': 'testuser'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutTestCase(APITestCase):
    """Tests para endpoint de logout"""

    def setUp(self):
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_logout_success(self):
        """Test: Logout exitoso"""
        data = {'refresh': str(self.refresh)}
        
        response = self.client.post(
            self.logout_url,
            data,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_without_auth(self):
        """Test: Logout sin autenticación"""
        data = {'refresh': str(self.refresh)}
        
        response = self.client.post(self.logout_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserDetailTestCase(APITestCase):
    """Tests para endpoint de detalles del usuario"""

    def setUp(self):
        self.user_detail_url = reverse('user_detail')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_get_user_detail(self):
        """Test: Obtener detalles del usuario"""
        response = self.client.get(
            self.user_detail_url,
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_get_user_detail_without_auth(self):
        """Test: Obtener detalles sin autenticación"""
        response = self.client.get(self.user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_detail(self):
        """Test: Actualizar detalles del usuario"""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.put(
            self.user_detail_url,
            data,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')


class ChangePasswordTestCase(APITestCase):
    """Tests para cambio de contraseña"""

    def setUp(self):
        self.change_password_url = reverse('change_password')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='OldPassword123!'
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

    def test_change_password_success(self):
        """Test: Cambiar contraseña exitosamente"""
        data = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
        
        response = self.client.put(
            self.change_password_url,
            data,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old_password(self):
        """Test: Contraseña anterior incorrecta"""
        data = {
            'old_password': 'WrongPassword123!',
            'new_password': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
        
        response = self.client.put(
            self.change_password_url,
            data,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        """Test: Nuevas contraseñas no coinciden"""
        data = {
            'old_password': 'OldPassword123!',
            'new_password': 'NewPassword123!',
            'new_password2': 'DifferentPassword123!'
        }
        
        response = self.client.put(
            self.change_password_url,
            data,
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshTestCase(APITestCase):
    """Tests para refresh token"""

    def setUp(self):
        self.token_refresh_url = reverse('token_refresh')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!'
        )
        self.refresh = RefreshToken.for_user(self.user)

    def test_token_refresh_success(self):
        """Test: Refrescar token exitosamente"""
        data = {'refresh': str(self.refresh)}
        
        response = self.client.post(self.token_refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_invalid_token(self):
        """Test: Token inválido"""
        data = {'refresh': 'invalid_token'}
        
        response = self.client.post(self.token_refresh_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordResetRequestTestCase(APITestCase):
    """Tests para endpoint de solicitud de reset de contraseña"""

    def setUp(self):
        self.url = reverse('password_reset_request')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!'
        )

    def test_password_reset_request_success(self):
        """Test: Solicitar reset exitosamente"""
        data = {'email': 'test@example.com'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_password_reset_request_nonexistent_email(self):
        """Test: Email no existe (seguridad)"""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.url, data, format='json')
        
        # No revela si el email existe o no
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_request_invalid_email(self):
        """Test: Email inválido"""
        data = {'email': 'invalid-email'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class VerifyOTPTestCase(APITestCase):
    """Tests para endpoint de verificación de OTP"""

    def setUp(self):
        self.url = reverse('verify_otp')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!'
        )
        
        # Crear OTP válido
        from .models import PasswordResetOTP
        self.otp_obj = PasswordResetOTP.create_otp(self.user)

    def test_verify_otp_valid(self):
        """Test: Verificar OTP válido"""
        data = {
            'email': 'test@example.com',
            'otp': self.otp_obj.otp
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])

    def test_verify_otp_invalid(self):
        """Test: OTP inválido"""
        data = {
            'email': 'test@example.com',
            'otp': '000000'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_otp_used(self):
        """Test: OTP ya fue usado"""
        self.otp_obj.mark_as_used()
        
        data = {
            'email': 'test@example.com',
            'otp': self.otp_obj.otp
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ConfirmPasswordResetTestCase(APITestCase):
    """Tests para endpoint de confirmación de reset de contraseña"""

    def setUp(self):
        self.url = reverse('confirm_password_reset')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='OldPassword123!'
        )
        
        # Crear OTP válido
        from .models import PasswordResetOTP
        self.otp_obj = PasswordResetOTP.create_otp(self.user)

    def test_confirm_password_reset_success(self):
        """Test: Reset de contraseña exitoso"""
        data = {
            'email': 'test@example.com',
            'otp': self.otp_obj.otp,
            'new_password': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que la contraseña cambió
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))

    def test_confirm_password_reset_invalid_otp(self):
        """Test: OTP inválido"""
        data = {
            'email': 'test@example.com',
            'otp': '000000',
            'new_password': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_password_reset_password_mismatch(self):
        """Test: Contraseñas no coinciden"""
        data = {
            'email': 'test@example.com',
            'otp': self.otp_obj.otp,
            'new_password': 'NewPassword123!',
            'new_password2': 'DifferentPassword123!'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_password_reset_weak_password(self):
        """Test: Contraseña débil"""
        data = {
            'email': 'test@example.com',
            'otp': self.otp_obj.otp,
            'new_password': 'weak',
            'new_password2': 'weak'
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


