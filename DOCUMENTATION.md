# Documentacion Completa

Indice de contenidos para toda la documentacion tecnica del proyecto.

## Tabla de Contenidos

1. [Inicio Rapido](#inicio-rapido)
2. [Guia JWT & OAuth2](#guia-jwt--oauth2)
3. [Detalles de Implementacion](#detalles-de-implementacion)
4. [Checklist y Verificacion](#checklist-y-verificacion)
5. [Estructura del Proyecto](#estructura-del-proyecto)

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

