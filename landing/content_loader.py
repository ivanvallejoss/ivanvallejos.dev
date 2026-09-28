"""Carga del contenido editable de la landing desde YAML.

El contenido vive en archivos dentro del repo (landing/content/), no en la DB:
se edita y se versiona con el código. PyYAML ya estaba en requirements.txt.
"""

import re
from pathlib import Path

import yaml
from django.apps import apps
from django.conf import settings

# Caché por proceso. Solo se usa con DEBUG=False: en desarrollo el archivo se
# relee en cada request para que editarlo no obligue a reiniciar el server.
_CACHE = {}

# Un nombre es uno o más segmentos de [a-z0-9_-] separados por "/". Deja pasar
# "landing" y "casos/bricka", y no "../secrets" ni rutas absolutas: en la fase 6
# el nombre del caso va a venir de la URL.
_NAME = re.compile(r"[a-z0-9_-]+(?:/[a-z0-9_-]+)*\Z")


def content_dir():
    """Raíz del contenido, relativa a la app (no a BASE_DIR: sobrevive un move)."""
    return Path(apps.get_app_config("landing").path) / "content"


def load_content(name):
    """Devuelve el YAML `name` como dict.

    `name` acepta subcarpeta, así que los casos de estudio se piden como
    load_content("casos/bricka") → landing/content/casos/bricka.yaml.
    """
    if not _NAME.fullmatch(name):
        raise ValueError(f"Nombre de contenido inválido: {name!r}")

    if not settings.DEBUG and name in _CACHE:
        return _CACHE[name]

    path = content_dir() / f"{name}.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"No existe el contenido '{name}': se buscó en {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    if not settings.DEBUG:
        _CACHE[name] = data
    return data
