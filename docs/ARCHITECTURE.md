# Arquitectura del proyecto

## Objetivo

Este proyecto quiere enseñar dos cosas a la vez:

1. contenido divulgativo sobre planetas para niños
2. arquitectura web real para perfiles técnicos

Por eso la interfaz se divide en dos niveles:

- experiencia principal amigable y visual
- modo técnico desplegable con explicaciones paso a paso

Además, la experiencia principal permite cambiar entre categorías de catálogo:

- sistema solar
- exoplanetas

## Librerías y herramientas usadas

### FastAPI

Se usa para construir la API HTTP del backend. Encaja bien porque:

- tiene sintaxis clara
- genera documentación automática
- funciona muy bien en proyectos pequeños y medianos
- facilita separar rutas, servicios y validación

### Uvicorn

Es el servidor ASGI que ejecuta FastAPI dentro del contenedor del backend.

### Pydantic

Se usa para definir el esquema `Planet` y garantizar que las respuestas tengan forma consistente.

### SQLite

Se eligió como primera capa de persistencia porque:

- no requiere un tercer contenedor
- es fácil de entender
- permite introducir persistencia real sin sobrecargar el proyecto
- sirve como base para migrar a PostgreSQL más adelante si hace falta

### Wikipedia REST ES

Se usa como fuente externa de sincronización porque:

- no requiere clave en este escenario
- ofrece extractos, descripciones e imágenes públicas
- encaja mejor con planetas reales que una API de ficción
- permite enseñar un patrón profesional de integración + caché local

### Nginx

El frontend se sirve con Nginx. Además, Nginx reenvía las llamadas `/api` al backend. Eso permite:

- evitar CORS
- publicar una sola URL pública
- explicar claramente el papel del reverse proxy

### Docker Compose

Se usa para separar responsabilidades:

- un contenedor para backend
- un contenedor para frontend
- una red Docker interna
- un volumen persistente para la base SQLite

### Cloudflared

No vive dentro del proyecto. En tu NUC se reutiliza como servicio systemd del host y publica el frontend en internet sin abrir puertos entrantes.

## Capas del backend

### Configuración

[../backend/app/config.py](../backend/app/config.py)

Define la configuración básica del proyecto y resuelve la ruta del directorio de datos y de la base SQLite.

### Inicialización de base de datos

[../backend/app/database.py](../backend/app/database.py)

Responsabilidades:

- crear la tabla `planets` si no existe
- migrar columnas nuevas si la base ya existía
- crear la tabla `sync_status`
- sembrar los datos iniciales si la base está vacía
- abrir conexiones SQLite con `row_factory`

### Repositorio

[../backend/app/repositories/planet_repository.py](../backend/app/repositories/planet_repository.py)

Responsabilidades:

- consultar la base SQLite
- devolver objetos validados del dominio
- aislar el acceso a datos del resto de la aplicación
- actualizar metadatos sincronizados desde la fuente externa

### Servicio

[../backend/app/services/planet_service.py](../backend/app/services/planet_service.py)

Responsabilidades:

- encapsular la lógica de negocio
- servir de puente entre rutas y repositorio
- centralizar logging del dominio

### Sincronización externa

[../backend/app/services/planet_sync_service.py](../backend/app/services/planet_sync_service.py)

Responsabilidades:

- consultar la fuente externa
- transformar la respuesta externa a campos útiles del proyecto
- actualizar SQLite
- registrar éxito o error en `sync_status`
- dejar la aplicación funcionando con caché local si falla la red

### Panel administrativo

[../backend/app/routes/admin.py](../backend/app/routes/admin.py)

Responsabilidades:

- exponer el estado actual de sincronización
- describir la arquitectura de forma estructurada
- permitir una sincronización manual desde el panel técnico del frontend

### Rutas HTTP

[../backend/app/routes/planets.py](../backend/app/routes/planets.py)

Responsabilidades:

- exponer endpoints
- traducir errores de dominio a códigos HTTP
- devolver respuestas tipadas mediante Pydantic

### Middleware

[../backend/app/middleware/logging.py](../backend/app/middleware/logging.py)

Responsabilidades:

- asignar un request id
- medir tiempo de respuesta
- registrar petición y respuesta
- exponer cabeceras útiles al frontend técnico

## Flujo de una petición

### Caso: GET /api/planets/3

1. El navegador solicita `/api/planets/3`.
2. Nginx recibe esa ruta en el contenedor frontend.
3. Nginx la reenvía al contenedor backend como `/planets/3`.
4. FastAPI resuelve la ruta en [../backend/app/routes/planets.py](../backend/app/routes/planets.py).
5. El servicio pide el planeta al repositorio.
6. El repositorio lee SQLite.
7. FastAPI serializa el objeto con Pydantic.
8. El middleware añade `X-Request-ID` y `X-Response-Time-Ms`.
9. El frontend recibe el JSON y actualiza pantalla y panel técnico.

### Caso: GET /api/planets?category=exoplanets

1. El usuario cambia el modo de exploración a exoplanetas.
2. El frontend llama a `/api/planets?category=exoplanets`.
3. FastAPI filtra la consulta por categoría.
4. SQLite devuelve solo los registros de exoplanetas.
5. La UI cambia sus tarjetas y mantiene el mismo panel técnico para explicar la llamada.

## Flujo de sincronización

### Caso: POST /api/admin/sync

1. Un administrador pulsa el botón de sincronizar en el panel técnico.
2. El frontend llama a `/api/admin/sync`.
3. FastAPI ejecuta el servicio de sincronización.
4. El servicio consulta Wikipedia REST ES para cada planeta configurado.
5. Los extractos, enlaces e imágenes se guardan en SQLite.
6. Se actualiza la tabla `sync_status` con éxito o error.
7. El frontend recarga el panel de arquitectura y sincronización.

Si la fuente externa falla, la aplicación sigue sirviendo los planetas desde SQLite.

## Persistencia

La persistencia se guarda en un volumen Docker llamado `planets-data` definido en [../docker-compose.yml](../docker-compose.yml).

Eso permite:

- reiniciar contenedores sin perder la base
- reconstruir imágenes sin perder datos
- mantener la demo portable entre entornos
- usar la base como caché local si la fuente externa no responde

## Evolución futura razonable

Siguientes mejoras naturales sin romper la arquitectura:

1. CRUD de planetas para que la persistencia sea modificable desde UI o API.
2. Migrar de SQLite a PostgreSQL si el proyecto crece.
3. Añadir autenticación para endpoints de administración.
4. Exportar logs a una solución externa si el homelab crece.