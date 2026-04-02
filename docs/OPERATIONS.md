# Operación del proyecto

## Arranque en local

```bash
docker compose up -d --build
docker compose ps
```

## Parada

```bash
docker compose down
```

## Reconstrucción completa

```bash
docker compose down
docker compose up -d --build
```

## Logs

### Backend

```bash
docker compose logs -f backend
```

### Frontend

```bash
docker compose logs -f frontend
```

## Validación rápida

```bash
curl -I http://localhost:8080
curl http://localhost:8080/api/planets
curl 'http://localhost:8080/api/planets?category=solar-system'
curl 'http://localhost:8080/api/planets?category=exoplanets'
curl http://localhost:8080/api/planets/3
curl 'http://localhost:8080/api/logs/recent?limit=8'
curl http://localhost:8080/api/admin/overview
curl -X POST http://localhost:8080/api/admin/sync
```

## Tests del backend

Desde [../backend](../backend):

```bash
pytest
```

## Persistencia de datos

La base SQLite se guarda en el volumen Docker `planets-data`.

### Ver volúmenes relacionados

```bash
docker volume ls | grep planets
```

### Inspeccionar el volumen

```bash
docker volume inspect planets-demo_planets-data
```

El nombre exacto puede cambiar según el nombre del directorio del proyecto o la variable `COMPOSE_PROJECT_NAME`.

## Copia y actualización en un host remoto

Ruta de ejemplo:

```bash
/srv/docker/stacks/planets-demo
```

### Sincronizar desde el cliente local

```bash
rsync -av --delete \
	-e "ssh -p 22" \
	--exclude '.git' \
	--exclude '.venv' \
	--exclude '__pycache__' \
	--exclude '.DS_Store' \
	--exclude 'backend/data/' \
	./ usuario@host:/srv/docker/stacks/planets-demo/
```

### Reaplicar despliegue en el host

```bash
cd /srv/docker/stacks/planets-demo
docker compose up -d --build
```

## Publicación externa

La publicación no se gestiona en el compose. Se reutiliza el `cloudflared` del host.

Comandos útiles en el host:

```bash
systemctl status cloudflared --no-pager
sudo systemctl restart cloudflared
sudo journalctl -u cloudflared -n 50 --no-pager
```

## Qué revisar si algo falla

### Si falla el frontend

1. `docker compose ps`
2. `docker compose logs -f frontend`
3. `curl -I http://localhost:8080`

### Si falla la API

1. `docker compose logs -f backend`
2. `curl http://localhost:8080/api/planets`
3. `curl 'http://localhost:8080/api/logs/recent?limit=8'`
4. `curl http://localhost:8080/api/admin/overview`

### Si falla la sincronización externa

1. revisar `curl http://localhost:8080/api/admin/overview`
2. revisar logs del backend
3. verificar conectividad del host a `https://es.wikipedia.org`
4. confirmar que la app sigue sirviendo desde caché SQLite

### Si falla el acceso público

1. comprobar `cloudflared`
2. revisar [TUNNELING.md](TUNNELING.md)
3. verificar DNS y reglas en Cloudflare