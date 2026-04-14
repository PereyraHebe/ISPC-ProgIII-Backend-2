# Django Backend API

Backend de autenticación con Django REST Framework, JWT y OAuth2 social (Google/GitHub).

## Estado Actual

- JWT con `access` y `refresh`
- Registro de usuarios con validación de username y email únicos
- Login / logout con blacklist de refresh tokens
- Recuperación de contraseña por OTP (3 pasos)
- OAuth2 social con django-allauth
- Endpoint puente para frontend SPA: `/api/oauth/success/`
- CORS habilitado para frontend Angular

## Requisitos

- Python 3.13+
- Entorno virtual

## Setup Rápido

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

### macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Servidor: `http://localhost:8000`

## Variables de Entorno Clave

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `FRONTEND_URL`
- `GOOGLE_OAUTH2_KEY`
- `GOOGLE_OAUTH2_SECRET`
- `GITHUB_APP_ID`
- `GITHUB_SECRET`

## Endpoints Principales

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/register/` | Registro (retorna `access` + `refresh`) |
| POST | `/api/login/` | Login JWT |
| POST | `/api/logout/` | Logout + blacklist |
| GET | `/api/user/` | Perfil del usuario autenticado |
| PUT | `/api/user/change-password/` | Cambio de contraseña |
| POST | `/api/token/refresh/` | Nuevo access token |
| POST | `/api/password-reset-request/` | Solicitar OTP |
| POST | `/api/password-reset-verify-otp/` | Verificar OTP |
| POST | `/api/password-reset-confirm/` | Confirmar reset |
| GET | `/accounts/google/login/?process=login` | Inicio OAuth Google |
| GET | `/accounts/github/login/?process=login` | Inicio OAuth GitHub |

## OAuth en Producción

1. Configurar credenciales OAuth en `.env`.
2. Registrar callbacks en proveedores:
   - `http://localhost:8000/accounts/google/login/callback/`
   - `http://localhost:8000/accounts/github/login/callback/`
3. Verificar `FRONTEND_URL` correcto para redirección al frontend.

## Testing

```bash
python manage.py check
python manage.py test accounts
```

Actualmente la suite `accounts` ejecuta 30 tests.

## Documentación Completa

Ver `DOCUMENTATION.md` para guía detallada de JWT, OAuth2, OTP, troubleshooting y verificación end-to-end.
