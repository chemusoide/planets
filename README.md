# Demo API Planetas

Proyecto full-stack para homelab con una doble intención educativa:

- una experiencia principal pensada para niños, centrada en descubrir planetas
- un panel técnico desplegable para explicar cómo viaja una petición por la arquitectura

La demo está montada para ejecutarse en local con Docker y puede publicarse en internet a través de un Cloudflare Tunnel ya existente en el host.

El catálogo actual se organiza en dos modos principales:

- planetas del sistema solar
- planetas fuera del sistema solar

## Stack técnico

- FastAPI para la API HTTP
- Uvicorn como servidor ASGI
- Pydantic para validación y serialización
- SQLite para persistencia simple y mantenible
- Wikipedia REST en español como fuente externa de sincronización
- Nginx para servir el frontend y hacer proxy de `/api`
- Docker Compose para separar servicios
- Cloudflared en el host para exposición pública segura

## Estructura

```text
.
├── backend
│   ├── app
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── middleware
│   │   ├── repositories
│   │   ├── routes
│   │   ├── schemas
│   │   └── services
│   ├── tests
│   ├── Dockerfile
│   ├── pytest.ini
│   └── requirements.txt
├── docs
│   ├── ARCHITECTURE.md
│   ├── OPERATIONS.md
│   └── TUNNELING.md
├── frontend
│   ├── Dockerfile
│   ├── nginx.conf
│   └── public
├── docker-compose.yml
└── .env.example
```

## Arquitectura resumida

- `backend`: API FastAPI con middleware de trazabilidad, servicio de planetas, sincronización externa y persistencia en SQLite.
- `frontend`: HTML, CSS y JavaScript nativos con dos modos de uso: infantil y técnico.
- `nginx`: sirve estáticos y reenvía `/api` al backend para evitar CORS.
- `planets-data`: volumen Docker para guardar la base SQLite.
- `cloudflared`: no corre dentro del compose; se reutiliza como servicio systemd del host.

## Endpoints actuales

- `GET /health`
- `GET /planets`
- `GET /planets/{planet_id}`
- `GET /logs/recent?limit=50`
- `GET /admin/overview`
- `POST /admin/sync`

## Qué aporta la nueva versión

- persistencia real con SQLite, no datos solo en memoria
- sincronización externa hacia la base local con caché persistente si falla internet
- separación backend por capas: rutas, servicio, repositorio y configuración
- panel principal más adecuado para niños
- panel técnico desplegable con flujo pedagógico navegador → proxy → backend → SQLite
- estado de sincronización y arquitectura visible dentro del frontend
- exploración por categorías para alternar entre sistema solar y exoplanetas
- logs recientes y tiempo de respuesta visibles en la UI
- tests básicos del backend

## Arranque local

1. Levanta la aplicación:

   ```bash
   docker compose up --build
   ```

2. Abre:

- Frontend: http://localhost:8080
- Backend: http://localhost:8000/docs

3. Prueba la API desde el frontend:

   ```bash
   curl http://localhost:8080/api/planets
   curl 'http://localhost:8080/api/planets?category=exoplanets'
   curl http://localhost:8080/api/admin/overview
   ```

## Tests

Desde [backend](backend):

```bash
pytest
```

## Documentación adicional

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/OPERATIONS.md](docs/OPERATIONS.md)
- [docs/TUNNELING.md](docs/TUNNELING.md)

## Despliegue en un host Linux

Ejemplo de convención de despliegue:

- stacks en `/srv/docker/stacks`
- túnel Cloudflare gestionado en el host

Ruta de ejemplo del proyecto:

```bash
/srv/docker/stacks/planets-demo
```

Pasos mínimos:

```bash
cd /srv/docker/stacks/planets-demo
docker compose up -d --build
docker compose ps
curl -I http://localhost:8080
curl http://localhost:8080/api/planets
```

La publicación externa se configura en [docs/TUNNELING.md](docs/TUNNELING.md).
