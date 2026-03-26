from __future__ import annotations

import logging
import os
import secrets
from dataclasses import dataclass


DEFAULT_CORS_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:4173',
    'http://127.0.0.1:4173',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
]
VALID_LOG_LEVELS = {'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'}
DEFAULT_ENVIRONMENT = 'development'
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Settings:
    database_url: str
    secret_key: str
    access_token_expire_minutes: int
    cors_origins: list[str]
    environment: str
    debug: bool
    log_level: str
    sqlalchemy_log_level: str


def _parse_cors_origins(value: str | None) -> list[str]:
    if not value or not value.strip():
        return DEFAULT_CORS_ORIGINS.copy()
    return [origin.strip() for origin in value.split(',') if origin.strip()]


def _parse_database_url(value: str | None) -> str:
    raw_value = (value or '').strip()
    if not raw_value or 'your_username' in raw_value or 'your_password' in raw_value:
        return 'sqlite:///./ship_db.db'
    return raw_value


def _parse_environment(value: str | None) -> str:
    raw_value = (value or DEFAULT_ENVIRONMENT).strip().lower()
    if raw_value in {'prod', 'production'}:
        return 'production'
    if raw_value in {'stage', 'staging'}:
        return 'staging'
    if raw_value in {'test', 'testing'}:
        return 'testing'
    return 'development'


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {'1', 'true', 'yes', 'on'}:
        return True
    if normalized in {'0', 'false', 'no', 'off'}:
        return False
    return default


def _parse_log_level(value: str | None, default: str) -> str:
    candidate = (value or default).strip().upper()
    if candidate in VALID_LOG_LEVELS:
        return candidate
    logger.warning('Invalid log level %r; falling back to %s', value, default)
    return default


def _resolve_secret_key(value: str | None, environment: str) -> str:
    raw_value = (value or '').strip()
    if raw_value:
        return raw_value
    if environment == 'production':
        raise RuntimeError('SECRET_KEY must be set in production')
    return secrets.token_urlsafe(32)


_environment = _parse_environment(os.getenv('ENVIRONMENT'))
_debug_default = _environment == 'development'
_debug = _parse_bool(os.getenv('DEBUG'), _debug_default)
_log_level_default = 'DEBUG' if _debug else 'INFO'
_sqlalchemy_log_level_default = 'INFO' if _debug else 'WARNING'

settings = Settings(
    database_url=_parse_database_url(os.getenv('DATABASE_URL')),
    secret_key=_resolve_secret_key(os.getenv('SECRET_KEY'), _environment),
    access_token_expire_minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60')),
    cors_origins=_parse_cors_origins(os.getenv('CORS_ORIGINS')),
    environment=_environment,
    debug=_debug,
    log_level=_parse_log_level(os.getenv('LOG_LEVEL'), _log_level_default),
    sqlalchemy_log_level=_parse_log_level(os.getenv('SQLALCHEMY_LOG_LEVEL'), _sqlalchemy_log_level_default),
)
