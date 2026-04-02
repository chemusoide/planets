# Tunneling seguro

## Opción recomendada: reutilizar el Cloudflare Tunnel del host

Si tu host ya ejecuta `cloudflared` como servicio systemd y mantiene su configuración en `/etc/cloudflared/config.yml`, este proyecto no necesita un contenedor `cloudflared` propio.

### Qué necesitas

- Cuenta de Cloudflare
- Dominio gestionado en Cloudflare
- Un túnel existente o permiso para crear uno nuevo
- Acceso al panel de Cloudflare Zero Trust o al archivo `/etc/cloudflared/config.yml` del host

### Enfoque recomendado

1. Reutiliza el túnel actual.
2. Añade un nuevo public hostname para `planets.example.com`.
3. Haz que ese hostname apunte a `http://localhost:8080` en el host.

### Despliegue de la app en el host

1. Crea la carpeta del proyecto siguiendo el patrón que uses en tu servidor:

   ```bash
   sudo mkdir -p /srv/docker/stacks/planets-demo
   sudo chown -R $USER:$USER /srv/docker/stacks/planets-demo
   ```

2. Copia el proyecto a esa ruta.

3. Dentro del directorio del proyecto, levanta la app:

   ```bash
   cd /srv/docker/stacks/planets-demo
   docker compose up -d --build
   ```

4. Verifica el frontend local en el host:

```bash
curl -I http://localhost:8080
```

### Añadir el hostname al túnel actual

Puedes hacerlo de dos formas.

#### Opción A: desde Cloudflare Zero Trust

1. Entra en Zero Trust.
2. Ve a Networks > Tunnels.
3. Abre el túnel que quieras reutilizar.
4. Añade un public hostname:

   - Subdomain: `planets`
   - Domain: `example.com`
   - Type: `HTTP`
   - URL: `localhost:8080`

5. Guarda los cambios.

Esta suele ser la opción más cómoda. El servicio `cloudflared` del host puede funcionar con credenciales de túnel, pero no tener disponible el archivo `cert.pem` necesario para comandos administrativos como `cloudflared tunnel route dns`.

#### Opción B: editando el archivo del host

Si tu túnel usa ingress en `/etc/cloudflared/config.yml`, añade una regla como esta antes del catch-all final:

```bash
sudo nano /etc/cloudflared/config.yml
```

Configuración esperada:

```yaml
ingress:
   - hostname: existing-app.example.com
      service: http://localhost:5678
   - hostname: planets.example.com
    service: http://localhost:8080
  - service: http_status:404
```

Después reinicia el servicio:

```bash
sudo systemctl restart cloudflared
```

#### Nota sobre `cloudflared tunnel route dns`

Si ejecutas este comando desde el host y aparece un error indicando que falta `cert.pem`, no significa que el túnel esté roto. Solo indica que ese host no tiene credenciales administrativas de Cloudflare para crear o actualizar registros DNS por CLI.

En ese caso, crea el public hostname desde Zero Trust o ajusta el DNS desde el panel web de Cloudflare.

### Verificar que funciona

1. Comprueba que los contenedores están arriba:

   ```bash
   docker compose ps
   ```

2. Revisa el frontend local en el host:

   ```bash
   curl -I http://localhost:8080
   ```

3. Revisa el estado del túnel:

   ```bash
   systemctl status cloudflared --no-pager
   journalctl -u cloudflared -n 50 --no-pager
   ```

4. Abre `https://planets.example.com`.
5. Verifica que la UI carga y que las llamadas a `/api/planets` responden correctamente.

### Reinicio

```bash
cd /srv/docker/stacks/planets-demo
docker compose restart
sudo systemctl restart cloudflared
```

## Alternativa: ngrok

Si no quieres usar Cloudflare, puedes publicar el frontend en local con:

```bash
ngrok http 8080
```

Es más rápido para una demo, pero menos cómodo que Cloudflare Tunnel para dejarlo funcionando de forma estable en homelab.
