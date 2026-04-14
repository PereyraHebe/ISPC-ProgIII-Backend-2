# Django Backend API

API backend con Django REST Framework + JWT + OAuth2.

Autenticacion completa con JWT tokens, OAuth2 (Google/GitHub), y CORS para frontend Angular.

## Caracteristicas

- JWT con access/refresh tokens
- OAuth2: Google y GitHub
- 6 endpoints de autenticacion
- Cambio de contrasena seguro
- CORS habilitado
- Validacion de contrasenas
- Token rotation y blacklisting
- 20 tests unitarios

## Requisitos

- Python 3.13+
- Virtual environment

## Setup Rapido

**macOS/Linux:**
```bash
chmod +x setup.sh && ./setup.sh
python manage.py runserver
```

**Windows:**
```powershell
.\setup.bat
python manage.py runserver
```

**Manual:**
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Servidor en: **http://localhost:8000**

## API Endpoints

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | `/api/register/` | Registrar usuario |
| POST | `/api/login/` | Loguear |
| POST | `/api/logout/` | Logout (blacklist token) |
| GET | `/api/user/` | Detalles usuario |
| PUT | `/api/user/change-password/` | Cambiar contraseña |
| POST | `/api/token/refresh/` | Refrescar token |

## Ejemplo Rapido

**Registrarse:**
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'
```

**Loguear:**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "password": "SecurePass123!"
  }'
```

**Usar Token:**
```bash
curl -X GET http://localhost:8000/api/user/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Configuracion

### Variables de Ambiente

```bash
cp .env.example .env
```

Campos importantes:
- `SECRET_KEY`: Django secret key
- `DEBUG`: True/False
- `CORS_ALLOWED_ORIGINS`: URLs frontend (ej: http://localhost:4200)
- OAuth2: Google y GitHub keys (opcional)

### Base de Datos

- Por defecto: SQLite (db.sqlite3)
- Produccion: PostgreSQL (ver DOCUMENTATION.md)

## Testing

```bash
python manage.py test accounts
```

Ejecuta 20 tests unitarios para todos los endpoints.

**Con Postman:** Importa `Django_API.postman_collection.json`

## Documentacion Completa

Ver [DOCUMENTATION.md](DOCUMENTATION.md) para:
- Guia completa de JWT y OAuth2
- Pasos detallados de configuracion
- Todos los endpoints con ejemplos
- Troubleshooting
- Notas de seguridad
- Integracion con Angular

## Estructura

```
.
├── README.md                             (Este archivo)
├── DOCUMENTATION.md                      (Documentacion completa)
├── backend/
│   ├── settings.py                       (JWT + OAuth2)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
│   ├── views.py                          (6 vistas)
│   ├── serializers.py                    (4 serializers)
│   ├── models.py
│   ├── urls.py                           (10+ endpoints)
│   ├── tests.py                          (20 tests)
│   └── migrations/
├── manage.py
├── requirements.txt
├── .env.example
├── setup.sh
├── setup.bat
└── db.sqlite3 (generado)
```

## Seguridad

**Desarrollo:**
- DEBUG = True
- SQLite database

**Produccion:**
- DEBUG = False
- PostgreSQL database
- HTTPS (JWT_AUTH_SECURE = True)
- CORS_ALLOWED_ORIGINS restrictas
- Email configurado

Ver [DOCUMENTATION.md](DOCUMENTATION.md) para mas detalles.
