# Cimiento v2 — Deploy
**Sesión:** Deploy a producción — ivanvallejos.dev + convivencia con blog FastAPI
**Fecha:** 25–26 Jul 2026 · VPS Hetzner (ivanCloud, Ubuntu, 3.7G RAM, 38G disco)
**Estado global:** ✅ Objetivos 1–4 completados. Terreno preparado para SmartExpense (fase siguiente).

---

## 1. Topología final

### Servicios (systemd)

| Unit | Qué corre | Bind | Estado |
|---|---|---|---|
| `landing.service` | Django · gunicorn + UvicornWorker ×2 | 127.0.0.1:8000 | active, **enabled** |
| `blog.service` | FastAPI · gunicorn + UvicornWorker ×2 | 127.0.0.1:8001 | active, **enabled** |
| `nginx.service` | Reverse proxy + TLS + estáticos | 0.0.0.0:80/443 | active, **enabled** |
| `postgresql@18-main.service` | PostgreSQL 18 | localhost:5432 | active, **enabled** (DATO: estaba `enabled-runtime`; corregido con `enable` explícito — no sobrevivía reboots) |
| `redis-server.service` | Redis (para SmartExpense) | 127.0.0.1:6379 | instalado y enabled |

Diferencia clave entre units: `blog.service` usa `EnvironmentFile=/home/ivan/blog/.env` porque la app lee `os.environ.get()` pelado; la landing no lo necesita porque django-environ carga el archivo por su cuenta.

### nginx (sites-enabled)

- `ivanvallejos.dev` — estáticos desde `staticfiles/` (alias, expires 30d), proxy a :8000, redirects www→apex y http→https.
- `blog.ivanvallejos.dev` — estáticos desde `/home/ivan/blog/static/`, proxy a :8001, redirect http→https. (Reemplazó al placeholder de Certbot que servía `/var/www`.)
- `default` — catch-all en :80. Rol útil: recibe los desafíos ACME de subdominios sin server block propio.

### TLS

- **Un solo certificado** Let's Encrypt, authenticator nginx, SANs: `ivanvallejos.dev`, `www.`, `blog.`, `smartexpense.` (expandido en esta sesión con `--expand`).
- Cloudflare orange-proxy en apex y subdominios; el desafío HTTP-01 atraviesa el proxy sin problema (`/.well-known/acme-challenge/` pasa).
- **Pendiente de 1 minuto:** confirmar en el panel de Cloudflare (SSL/TLS → Overview) que el modo sea **Full (strict)**. El cert de origen lo habilita; nunca se verificó el modo actual.

### Bases de datos (PostgreSQL compartido, DBs aisladas)

- `blog_db` / `blog_user` — en uso, migrada con Alembic.
- `smartexpense_db` / `smartexpense_user` — creada, vacía, lista para el deploy futuro.
- Landing: su DB preexistente.

### Filesystem

```
/home/ivan/
├── ivanvallejos.dev/   repo git · .venv propio · .env · staticfiles/ (collectstatic)
├── blog/               repo git · .venv propio · .env (600) · static/ (del repo)
└── (futuro) smartexpense/
```

Prerequisito de entorno: **`www-data` pertenece al grupo `ivan`** (fix del 403 — `/home/ivan` es 750 y nginx necesita atravesarlo). Aplica automáticamente a todo proyecto futuro bajo `/home/ivan`.

---

## 2. Runbooks de release

### Landing (Django)

```bash
# local: merge/push a main
# VPS:
cd /home/ivan/ivanvallejos.dev && source .venv/bin/activate
git pull
python manage.py migrate            # solo si hay migraciones
python manage.py collectstatic --noinput
sudo systemctl restart landing
./scripts/smoke_test.sh --local     # verificación protocolar
```

Rollback: `git reset --hard <commit-anterior>` + collectstatic + restart.

### Blog (FastAPI)

```bash
cd /home/ivan/blog && source .venv/bin/activate
git pull
pip install .                        # solo si cambió pyproject.toml
set -a; source .env; set +a
alembic upgrade head                 # solo si hay migraciones
sudo systemctl restart blog
```

Rollback: mismo patrón git. Nota: `pip install .` copia estado al venv; los cambios de código llegan por pull+restart, los de dependencias requieren re-install.

### Cambios de nginx (raros)

```bash
sudo cp /etc/nginx/sites-available/<sitio> ~/<sitio>.nginx.bak   # backup SIEMPRE
# editar
sudo nginx -t                        # validar ANTES de aplicar
sudo systemctl reload nginx          # reload, no restart (no corta conexiones)
```

### Verificación protocolar

`scripts/smoke_test.sh` (repo de la landing): 12 checks externos (via Cloudflare) + 7 internos con `--local` (backends, units, enabled). Exit code ≠ 0 si algo falla → usable en CI/timer a futuro. **Resultado final de sesión: 12/12 externo, 17/19 interno** (los 2 FAIL eran: check de Host mal formulado —fix de una línea pendiente en el script— y el enable-runtime de Postgres, ya corregido; re-corrida esperada 19/19).

---

## 3. Decisiones tomadas y porqué

1. **gunicorn + UvicornWorker (no uvicorn standalone)** para ambos servicios: gunicorn es el process manager (supervisa N workers, reinicia caídos, maneja señales); uvicorn es el servidor ASGI dentro de cada worker. Consistencia operativa: un solo patrón en toda la VPS. `gunicorn` se agregó a las dependencias del blog (faltaba: en local se usa uvicorn con --reload).
2. **Cert LE existente expandido, no origin-cert de Cloudflare**: los SANs ya cubrían `blog.`; expandir mantiene un solo cert/una renovación. El origin-cert de CF queda como alternativa si la renovación HTTP-01 alguna vez diera problemas a través del proxy.
3. **Sin Docker en la VPS**: PostgreSQL nativo ya corría; duplicarlo en contenedor sumaba memoria y gestión sin beneficio. docker-compose queda como herramienta de desarrollo local únicamente. Regla derivada: el sistema solo tiene nginx + PostgreSQL + Redis + systemd; todo Python vive en venvs por proyecto.
4. **`EnvironmentFile=` en systemd** (blog) en vez de `load_dotenv()` en código: cada contexto de ejecución recibe el entorno a su manera (shell interactiva: `set -a; source .env; set +a` / systemd: EnvironmentFile / la app no cambia).
5. **`www-data` → grupo `ivan`** (no `chmod 755 /home/ivan`): abre el home solo a nginx, no a todo usuario del sistema.
6. **`pyproject.toml` con `py-modules = []`**: el blog es una aplicación deployada via git, no una librería distribuible; se desactivó el auto-discovery de setuptools que fallaba por múltiples paquetes top-level.
7. **Passwords de DB**: generados con `openssl rand -hex` (sin caracteres que requieran URL-escaping); operaciones de credenciales comando por comando, nunca en heredoc (lección del fallo de auth del blog).
8. **Hardening Django aplicado**: `SECURE_PROXY_SSL_HEADER`, `CSRF_TRUSTED_ORIGINS`, cookies secure condicionadas a `not DEBUG`. No se agregó `SECURE_SSL_REDIRECT` (nginx ya redirige) ni HSTS (difícil de revertir; evaluable después).

---

## 4. Incidentes de sesión (registro de aprendizaje)

| Incidente | Causa raíz | Fix | Lección |
|---|---|---|---|
| 403 en todos los estáticos nuevos | `/home/ivan` 750, `www-data` sin traversal | `usermod -aG ivan www-data` + restart nginx | Permisos se evalúan en toda la cadena; `namei -l` diagnostica |
| Auth failed en Postgres del blog | Password del heredoc no quedó como se creía | `ALTER USER ... PASSWORD` con hex nuevo | Credenciales: comando por comando, output visible |
| `alembic`/app sin variables | `os.environ.get()` no carga `.env` | shell: `set -a; source .env; set +a` / systemd: `EnvironmentFile` | Cada contexto de ejecución tiene su mecanismo de entorno |
| certbot NXDOMAIN | Placeholder literal `SUBDOMINIO.` en el comando | Re-run con `smartexpense.` | Los placeholders se reemplazan 🙂 — el cert original nunca corrió riesgo |
| Postgres `enabled-runtime` | Enable en `/run`, no persistente | `systemctl enable postgresql@18-main` | `is-enabled` distingue runtime vs. persistente; chequearlo es parte del smoke test |

---

## 5. Estado de verificación y pendientes

**Verificado end-to-end:** landing con contenido nuevo (default + CV + señales), estáticos con mime-types y cache correctos, fuentes woff2 cargando, `/go/blog` y `/go/github` redirigiendo (302) con tracking, blog sirviendo en su subdominio, redirects http→https y www→apex, ambos backends sanos en localhost, todos los units enabled.

**Pendientes menores (no bloqueantes):**
1. Fix de una línea en `smoke_test.sh`: el check interno de la landing debe mandar `-H 'Host: ivanvallejos.dev'` (el 400 actual es Django validando ALLOWED_HOSTS correctamente).
2. Confirmar modo **Full (strict)** en panel de Cloudflare.
3. Swapfile 1–2G como red de seguridad anti-OOM (Ivan ya tiene estudiado el ajuste).
4. Warning cosmético de preload de fuentes en console (revisar `crossorigin` del `<link rel="preload">` si persiste).
5. Agregar al smoke test un estático concreto del blog cuando haya uno estable.

---

## 6. Fase siguiente: SmartExpense (terreno preparado)

**Hecho en esta sesión:** DNS A record en Cloudflare (orange) · cert expandido con `smartexpense.ivanvallejos.dev` · `smartexpense_db`/`smartexpense_user` creados y verificados · Redis instalado, enabled, escuchando solo en localhost.

**Para el deploy futuro (gateway aún en desarrollo):**
- Gateway Go → `127.0.0.1:8002`, binario **cross-compilado local** (`GOOS=linux GOARCH=amd64`) y subido — la VPS no lleva toolchain de Go; el artefacto deployado es exactamente el probado.
- Dos units nuevos: `smartexpense-gateway.service` (binario) y `smartexpense-worker.service` (Python ARQ, venv + EnvironmentFile, patrón blog), ambos con `After=redis-server.service postgresql.service`. Gateway y worker no se hablan entre sí (via Redis) → units independientes.
- Server block nginx calcado del blog, proxy a :8002 (sin location de estáticos si es API pura — a confirmar).
- Memoria proyectada con todo corriendo: ~1.1G de 3.7G. Cómodo; swapfile como red de seguridad.

**Runbook futuro del gateway** (difiere de los Python por el paso de build): build local → scp/release del binario → `sudo systemctl restart smartexpense-gateway`. Worker: patrón blog.

---
*Informe generado al cierre de sesión. Vuelve a la ventana orquestadora de la landing.*
