from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField
from django.utils import timezone
from datetime import timedelta
import secrets
import string

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    encrypted_info = EncryptedCharField(max_length=100)  # Example encrypted field


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_otps')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.user.username}"
    
    @staticmethod
    def generate_otp():
        """Generar OTP de 6 dígitos"""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    @classmethod
    def create_otp(cls, user):
        """Crear un nuevo OTP para el usuario"""
        # Marcar OTPs anteriores como usados
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        otp = cls.generate_otp()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        return cls.objects.create(
            user=user,
            otp=otp,
            expires_at=expires_at
        )
    
    def is_valid(self):
        """Verificar si el OTP es válido"""
        return not self.is_used and timezone.now() <= self.expires_at
    
    def mark_as_used(self):
        """Marcar OTP como usado"""
        self.is_used = True
        self.save()
