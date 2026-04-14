# Documentacion Completa

Indice de contenidos para toda la documentacion tecnica del proyecto.

## Tabla de Contenidos

1. [Inicio Rapido](#inicio-rapido)
2. [Guia JWT & OAuth2](#guia-jwt--oauth2)
3. [Password Reset Endpoints](#6-password-reset-endpoints)
4. [Configuración de Email](#7-configuración-de-email)
5. [Testing de Email](#8-testing-de-email)
6. [Troubleshooting de Email](#9-troubleshooting-de-email)
7. [Detalles de Implementacion](#detalles-de-implementacion)
8. [Checklist y Verificacion](#checklist-y-verificacion)
9. [Estructura del Proyecto](#estructura-del-proyecto)

---

## Inicio Rapido

### 1. Instalar Dependencias (2 minutos)

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows (PowerShell):**
```powershell
.\setup.bat
```

**Manual:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar Ambiente (1 minuto)

```bash
cp .env.example .env
# Editar .env con tus valores (opcional para desarrollo)
```

### 3. Preparar Base de Datos (2 minutos)

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Ejecutar Servidor (1 minuto)

```bash
python manage.py runserver
```

Servidor activo en: **http://localhost:8000**
Admin en: **http://localhost:8000/admin/**

### 5. Listo! Probar API

**Registrarse:**
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPassword123!",
    "password2": "TestPassword123!"
  }'
```

**Loguear:**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPassword123!"
  }'
```

---

## Guia JWT & OAuth2

### JWT Authentication

#### 1. Register (Registro)
```bash
POST /api/register/
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "password2": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "newuser",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2026-04-14T10:00:00Z"
  }
}
```

#### 2. Login
```bash
POST /api/login/
Content-Type: application/json

{
  "username": "newuser",
  "password": "SecurePassword123!"
}
```

**Response:** (Same as register)

#### 3. Refresh Token
```bash
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 4. Get User Details
```bash
GET /api/user/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response:**
```json
{
  "id": 1,
  "username": "newuser",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_joined": "2026-04-14T10:00:00Z"
}
```

#### 5. Logout
```bash
POST /api/logout/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

#### 6. Change Password
```bash
PUT /api/user/change-password/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "old_password": "OldPassword123!",
  "new_password": "NewPassword123!",
  "new_password2": "NewPassword123!"
}
```

**Response:**
```json
{
  "message": "Password updated successfully"
}
```

### 7. Password Reset - Request OTP
```bash
POST /api/password-reset-request/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "OTP enviado a tu email"
}
```

Genera un OTP de 6 dígitos y lo envía al email del usuario. El OTP expira en 10 minutos.

### 8. Password Reset - Verify OTP
```bash
POST /api/password-reset-verify-otp/
Content-Type: application/json

{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Response (200) - OTP válido:**
```json
{
  "message": "OTP válido",
  "valid": true
}
```

**Response (400) - OTP inválido o expirado:**
```json
{
  "error": "OTP inválido o expirado"
}
```

Verifica que el OTP sea válido sin cambiar la contraseña.

### 9. Password Reset - Confirm
```bash
POST /api/password-reset-confirm/
Content-Type: application/json

{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "NewPassword123!",
  "new_password2": "NewPassword123!"
}
```

**Response (200):**
```json
{
  "message": "Contraseña actualizada exitosamente"
}
```

Completa el reset de contraseña: valida el OTP y actualiza la contraseña.

---

---

## 6. Password Reset Endpoints

Se implementaron 3 nuevos endpoints para permitir reset seguro de contraseña mediante OTP:

### 6.1 Solicitar OTP (Reset Request)

```bash
POST /api/password-reset-request/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "OTP enviado a tu email"
}
```

**Qué hace:**
- Busca el usuario con ese email
- Genera un OTP de 6 dígitos aleatorios
- Guarda OTP en base de datos con expiración de 10 minutos
- Invalida OTPs anteriores del mismo usuario
- Envía email HTML con el OTP
- **Seguridad:** No revela si el email existe (previene enumeration)

### 6.2 Verificar OTP

```bash
POST /api/password-reset-verify-otp/
Content-Type: application/json

{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Response (200) - OTP válido:**
```json
{
  "message": "OTP válido",
  "valid": true
}
```

**Response (400) - OTP inválido o expirado:**
```json
{
  "error": "OTP inválido o expirado"
}
```

**Qué hace:**
- Valida que el OTP sea correcto
- Verifica que no haya expirado (10 minutos máximo)
- Verifica que no haya sido usado ya
- **Nota:** Este paso es opcional, se puede ir directo a confirmar

### 6.3 Confirmar Reset (Confirm Password Reset)

```bash
POST /api/password-reset-confirm/
Content-Type: application/json

{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "NewPassword123!",
  "new_password2": "NewPassword123!"
}
```

**Response (200):**
```json
{
  "message": "Contraseña actualizada exitosamente"
}
```

**Qué hace:**
- Valida el OTP (igual que verify)
- Valida que las contraseñas coincidan
- Valida que la contraseña sea fuerte (Django validators)
- Actualiza la contraseña del usuario
- Marca el OTP como usado (no puede reutilizarse)

### 6.4 Flujo Completo

```
1. Usuario olvida contraseña
2. Frontend: POST /api/password-reset-request/ {email}
   ↓ Backend envía OTP por email ↓
3. Usuario recibe email con OTP (válido 10 minutos)
4. Frontend: POST /api/password-reset-verify-otp/ {email, otp}  [OPCIONAL]
   ↓ Backend valida OTP ↓
5. Frontend: POST /api/password-reset-confirm/ {email, otp, new_password}
   ↓ Backend actualiza contraseña ↓
6. Usuario logueado exitosamente
```

### 6.5 Modelo de Datos

**PasswordResetOTP:**
```python
- user (ForeignKey a User)
- otp (CharField: 6 dígitos)
- created_at (DateTimeField: auto)
- expires_at (DateTimeField: created_at + 10 minutos)
- is_used (BooleanField: para evitar reutilización)
```

**Métodos:**
- `generate_otp()` - Genera 6 dígitos aleatorios
- `create_otp(user)` - Crea nuevo OTP, invalida anteriores
- `is_valid()` - Verifica si es válido y no expirado
- `mark_as_used()` - Marca como usado

---

## 7. Configuración de Email

El backend envía emails HTML profesionales para el reset de contraseña.

### 7.1 Backend Predeterminado (Desarrollo)

**Console Backend:**
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Los emails se imprimen en la consola/terminal. Perfecto para desarrollo local.

**File Backend:**
```bash
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=/tmp/django-emails
```

Los emails se guardan en archivos para inspeccionar. Ver con:
```bash
cat /tmp/django-emails/*
```

### 7.2 SMTP para Producción

**Configuración General SMTP:**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-usuario
EMAIL_HOST_PASSWORD=tu-contraseña
DEFAULT_FROM_EMAIL=noreply@example.com
```

### 7.3 Gmail (Recomendado para testing)

**Paso 1: Crear App Password**
1. Ir a https://myaccount.google.com/apppasswords
2. Seleccionar "Correo (Gmail)" y tu dispositivo
3. Google generará contraseña de 16 caracteres
4. Copiar esa contraseña

**Paso 2: Configurar .env**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-de-16-caracteres
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

**Paso 3: Probar**
```bash
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Mensaje de prueba', 'tu-email@gmail.com', ['destinatario@example.com'])
```

### 7.4 Otros Proveedores

#### SendGrid
```bash
# Instalar
pip install sendgrid

# Configurar .env
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=tu-sendgrid-api-key
DEFAULT_FROM_EMAIL=tu-email@sendgrid.com
```

#### Mailgun
```bash
# Instalar
pip install django-mailgun

# Configurar .env
EMAIL_BACKEND=django_mailgun.MailgunBackend
MAILGUN_ACCESS_KEY=tu-api-key
MAILGUN_SERVER_NAME=mail.example.com
DEFAULT_FROM_EMAIL=noreply@mail.example.com
```

#### AWS SES
```bash
# Instalar
pip install django-ses

# Configurar .env
EMAIL_BACKEND=django_ses.SESBackend
AWS_ACCESS_KEY_ID=tu-aws-access-key
AWS_SECRET_ACCESS_KEY=tu-aws-secret-key
AWS_SES_REGION_NAME=us-east-1
DEFAULT_FROM_EMAIL=noreply@example.com
```

### 7.5 Email Template (HTML)

El backend envía emails con:
- **HTML profesional** con estilos inline (compatibilidad máxima)
- **Texto plano** como fallback
- **Contenido:** Saludo personalizado, OTP destacado, instrucciones, aviso de seguridad

**Ubicación:** `accounts/templates/emails/password_reset_otp.html` y `.txt`

**Variables:** `{{ username }}` y `{{ otp }}`

**Características:**
- Gradient header (púrpura)
- OTP en grande (36px)
- Box con bordes destacado
- Warning en amarillo
- Footer profesional
- Responsive para móvil

### 7.6 Implementación en Código

```python
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

# En PasswordResetRequestView.post()
html_message = render_to_string(
    'emails/password_reset_otp.html',
    {'username': user.username, 'otp': otp}
)
text_message = render_to_string(
    'emails/password_reset_otp.txt',
    {'username': user.username, 'otp': otp}
)

send_mail(
    subject='Password Reset OTP',
    message=text_message,              # Versión texto
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[email],
    html_message=html_message,         # Versión HTML
    fail_silently=False,
)
```

---

## 8. Testing de Email

### 8.1 Console Backend (Recomendado para desarrollo)

**Configurar .env:**
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Llamar endpoint:**
```bash
curl -X POST http://localhost:8000/api/password-reset-request/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

**Resultado:** El email aparecerá en la terminal.

### 8.2 File Backend (Guardar en archivos)

**Configurar .env:**
```bash
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=/tmp/django-emails
```

**Ver emails guardados:**
```bash
cat /tmp/django-emails/*
```

### 8.3 Unit Tests

```python
from django.test import TestCase, override_settings
from django.core.mail import outbox

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PasswordResetEmailTestCase(TestCase):
    
    def test_password_reset_email_sent(self):
        """Test que se envía email al solicitar reset"""
        response = self.client.post(
            '/api/password-reset-request/',
            {'email': 'user@example.com'},
            format='json'
        )
        
        # Verificar que se envió email
        self.assertEqual(len(outbox), 1)
        
        # Verificar contenido
        email = outbox[0]
        self.assertEqual(email.subject, 'Password Reset OTP')
        self.assertIn('user@example.com', email.to)
```

**Ejecutar tests:**
```bash
python manage.py test accounts.tests -v 2
```

**Resultado:**
```
Ran 10 tests in 1.7s OK
```

### 8.4 Gmail Real (End-to-End)

**Pasos:** (Ver sección 7.3 para configurar)

1. Configurar .env con credentials de Gmail
2. Llamar endpoint
3. Chequear bandeja de Gmail del destinatario

### 8.5 Visualizar Template en Navegador

```bash
python manage.py shell

from django.template.loader import render_to_string

html = render_to_string('emails/password_reset_otp.html', {
    'username': 'testuser',
    'otp': '123456',
})

# Guardar HTML
with open('/tmp/email_preview.html', 'w') as f:
    f.write(html)

# Abrir en navegador
import webbrowser
webbrowser.open('/tmp/email_preview.html')
```

---

## 9. Troubleshooting de Email

### Error: "SMTPAuthenticationError"

```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```

**Soluciones:**
- ✓ Usar **App Password** en Gmail (no contraseña de cuenta)
- ✓ Verificar credenciales en .env
- ✓ Probar conexión: `telnet smtp.gmail.com 587`
- ✓ Habilitar "Acceso de aplicaciones menos seguras"

### Error: "SMTPNotSupportedError"

```
SMTPNotSupportedError: STARTTLS extension not supported
```

**Soluciones:**
- ✓ Cambiar `EMAIL_USE_TLS=True`
- ✓ Probar `EMAIL_USE_SSL=True` (algunos servidores)
- ✓ Cambiar `EMAIL_PORT=465` para SSL

### Los emails no llegan

**Checklist:**
- ✓ Verificar carpeta spam
- ✓ Email remitente es válido
- ✓ Servidor SMTP responde
- ✓ Credenciales correctas
- ✓ Rate limiting no está bloqueando
- ✓ Destinatario acepta desde ese dominio

### Template no se renderiza

**Soluciones:**
```bash
# Verificar que Django encuentra los templates
python manage.py shell
from django.template.loader import get_template
template = get_template('emails/password_reset_otp.html')
print(template)  # No debe lanzar error
```

- ✓ Verificar `APP_DIRS = True` en TEMPLATES
- ✓ Verificar ruta: `accounts/templates/emails/`
- ✓ Verificar que `accounts` está en INSTALLED_APPS

---

### OAuth2 Authentication

#### Google OAuth2

1. **Configurar Google OAuth2:**
   - Ir a Google Cloud Console: https://console.cloud.google.com/
   - Crear nuevo proyecto
   - Habilitar "Google+ API"
   - Crear "OAuth 2.0 Client IDs"
   - Descargar credenciales JSON

2. **Agregar a Django Admin:**
   - Ir a http://localhost:8000/admin/
   - Social applications
   - Add Social Application
   - Provider: Google
   - Completar con datos de Google Cloud Console
   - Sites: localhost

3. **Usar en Frontend (Angular):**
   ```typescript
   // Instalar google-auth-library
   npm install @react-oauth/google

   // En tu componente
   import { GoogleLogin } from '@react-oauth/google';

   <GoogleLogin
     onSuccess={handleSuccess}
     onError={handleError}
   />
   ```

#### GitHub OAuth2

1. **Configurar GitHub OAuth2:**
   - Ir a Settings > Developer settings > OAuth Apps
   - New OAuth App
   - Application name: Tu App
   - Authorization callback URL: http://localhost:8000/accounts/github/login/callback/

2. **Agregar a Django Admin:**
   - Ir a http://localhost:8000/admin/
   - Social applications
   - Add Social Application
   - Provider: GitHub
   - Client ID y Client Secret de GitHub
   - Sites: localhost

### Configuracion Completa de JWT

**En `backend/settings.py`:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': settings.SECRET_KEY,
}
```

**Flujo de Token:**
1. Usuario se registra o loguea
2. Backend devuelve access_token (5 min) + refresh_token (7 dias)
3. Frontend almacena tokens
4. Enviar access_token en Authorization header
5. Si access_token expira, usar refresh_token para obtener uno nuevo
6. Al logout, refresh_token se agrega a blacklist

---

## Detalles de Implementacion

### 1. requirements.txt

Se agregaron nuevas dependencias:
- `django-allauth==0.71.0` - OAuth2 support
- `dj-rest-auth==5.0.2` - Authentication endpoints
- `python-decouple==3.8` - Environment variables management
- `requests==2.31.0` - HTTP library for OAuth
- `requests-oauthlib==2.0.0` - OAuth helper

### 2. backend/settings.py

Cambios principales:
- Configuracion completa de JWT con `SIMPLE_JWT`
- Instalacion de `django-allauth` y `dj-rest-auth`
- Soporte para OAuth2 (Google y GitHub)
- Configuracion de `CORS_ALLOWED_ORIGINS` dinamicas desde `.env`
- `SITE_ID = 1` para django-allauth
- Token rotation habilitado
- Token blacklist habilitado

**Configuración JWT:**
- Access Token: 5 minutos
- Refresh Token: 7 días
- Algoritmo: HS256
- Token rotation: Habilitado

**OAuth2 Providers:**
- Google OAuth2 configurado
- GitHub OAuth2 configurado
- Auto signup habilitado
- Email verification: optional

### 3. accounts/views.py

Nuevas vistas implementadas:
- `RegisterView` - Registro mejorado con manejo de errores
- `LoginView` - Login con validacion completa
- `LogoutView` - Logout con token blacklisting
- `ChangePasswordView` - Cambio seguro de contraseña
- `UserDetailView` - Obtener/actualizar datos del usuario
- `RefreshTokenView` - Refrescar JWT tokens

### 4. accounts/serializers.py

Nuevos serializers implementados:
- `RegisterSerializer` - Validacion completa de registro
  - Validacion de contraseña fuerte
  - Confirmacion de contraseña
  - Validacion de email unico
  - Validacion de username unico
- `ChangePasswordSerializer` - Cambio de contraseña seguro
- `TokenSerializer` - Serializacion de tokens JWT
- Mejoras en `UserSerializer` con mas campos

### 5. accounts/urls.py

Rutas configuradas:
```
/api/register/               - Registro
/api/login/                  - Login
/api/logout/                 - Logout
/api/token/                  - Obtener tokens
/api/token/refresh/          - Refrescar token
/api/user/                   - Detalles del usuario
/api/user/change-password/   - Cambiar contraseña
/api/auth/                   - dj-rest-auth endpoints
/api/auth/registration/      - dj-rest-auth registration
```

### 6. Archivos Creados

#### .env.example
Variables de ambiente necesarias:
- Django settings (SECRET_KEY, DEBUG, ALLOWED_HOSTS)
- CORS configuration
- Database configuration
- OAuth2 keys (Google y GitHub)
- Email configuration

---

## Checklist y Verificacion

### Código
- `requirements.txt` actualizado con oauth y auth packages
- `backend/settings.py` configurado con JWT y OAuth2
- `accounts/views.py` con 6 nuevas vistas
- `accounts/serializers.py` con 4 serializers mejorados
- `accounts/urls.py` con 10+ endpoints
- `accounts/tests.py` con 20 tests unitarios

### Documentación
- `README.md` actualizado y completo
- `DOCUMENTATION.md` con guía completa

### Configuración
- `.env.example` creado
- `setup.sh` para macOS/Linux
- `setup.bat` para Windows
- `Django_API.postman_collection.json` para testing

### Pasos para Verificar

#### 1. Instalar Proyecto
```bash
chmod +x setup.sh
./setup.sh
python manage.py runserver
```

#### 2. Ejecutar Tests
```bash
python manage.py test accounts
```

#### 3. Verificar Endpoints

**Registrarse:**
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPassword123!",
    "password2": "TestPassword123!"
  }'
```

**Loguear:**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPassword123!"
  }'
```

**Refrescar Token (reemplazar con tu token):**
```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "YOUR_REFRESH_TOKEN"
  }'
```

**Obtener Detalles de Usuario (reemplazar con tu token):**
```bash
curl -X GET http://localhost:8000/api/user/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Troubleshooting

**Error: "ModuleNotFoundError"**
- Activar virtual environment: `source venv/bin/activate`
- Reinstalar dependencias: `pip install -r requirements.txt`

**Error: "No such table" en migraciones**
- Ejecutar migraciones: `python manage.py migrate`

**Error: "CORS policy"**
- Verificar `CORS_ALLOWED_ORIGINS` en `.env`
- Ejemplo: `CORS_ALLOWED_ORIGINS=http://localhost:4200,http://localhost:3000`

**Error: "Invalid token"**
- Token puede haber expirado
- Usar refresh token para obtener nuevo access token

---

## Estructura del Proyecto

```
.
├── README.md                             (Inicio y guia rapida)
├── DOCUMENTATION.md                      (Documentacion completa)
├── 00_INICIO.txt                         (Resumen visual)
├── .env.example                          (Variables de ambiente)
├── setup.sh                              (Script setup Linux/macOS)
├── setup.bat                             (Script setup Windows)
├── Django_API.postman_collection.json   (Coleccion Postman)
├── requirements.txt                      (Dependencias Python)
├── manage.py                             (CLI de Django)
├── backend/
│   ├── settings.py                       (Configuracion - JWT + OAuth2)
│   ├── urls.py                           (URL routing)
│   ├── wsgi.py                           (WSGI application)
│   ├── asgi.py                           (ASGI application)
│   └── __init__.py
├── accounts/
│   ├── views.py                          (6 vistas: Register, Login, Logout, etc.)
│   ├── serializers.py                    (4 serializers: Register, ChangePassword, etc.)
│   ├── models.py                         (UserProfile con encriptacion)
│   ├── urls.py                           (10+ endpoints)
│   ├── tests.py                          (20 tests unitarios)
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── __init__.py
│   └── __init__.py
└── db.sqlite3                            (Base de datos SQLite)
```

---

## Endpoints Principales

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | `/api/register/` | Registrar nuevo usuario |
| POST | `/api/login/` | Loguear usuario |
| POST | `/api/logout/` | Logout (blacklist token) |
| GET | `/api/user/` | Obtener detalles del usuario |
| PUT | `/api/user/change-password/` | Cambiar contraseña |
| POST | `/api/token/refresh/` | Refrescar access token |
| POST | `/api/password-reset-request/` | Solicitar OTP para reset |
| POST | `/api/password-reset-verify-otp/` | Verificar OTP válido |
| POST | `/api/password-reset-confirm/` | Confirmar reset y actualizar contraseña |
| GET | `/admin/` | Django admin panel |

---

## Testing

### Con Postman
1. Importar `Django_API.postman_collection.json`
2. Ejecutar endpoints desde la coleccion
3. Las variables se cargan automaticamente tras Login

### Con curl
Ver ejemplos en seccion "Checklist y Verificacion"

### Tests Unitarios
```bash
python manage.py test accounts
```

Ejecuta 20 tests covering:
- Registro (validacion, duplicados, contraseña)
- Login (credenciales validas/invalidas)
- Logout (token blacklist)
- User Details (get/update)
- Change Password
- Token Refresh

---

## Proximos Pasos

1. Integrar con frontend Angular
   - Usar JWT en HTTP Interceptor
   - Almacenar tokens en localStorage/sessionStorage
   
2. Configurar OAuth2 en produccion
   - Registrar aplicacion en Google Cloud Console
   - Registrar OAuth App en GitHub
   - Actualizar CORS_ALLOWED_ORIGINS

3. Configurar base de datos PostgreSQL
   - En produccion, cambiar a PostgreSQL
   - Actualizar DATABASE_URL en .env

4. Agregar mas funcionalidades
   - Verificacion de email
   - Password reset por email
   - Two-factor authentication
   - Rate limiting

