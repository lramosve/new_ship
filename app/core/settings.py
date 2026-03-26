from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_CORS_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:4173',
    'http://127.0.0.1:4173',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
]


@dataclass(frozen=True)
class Settings:
    database_url: str
    secret_key: str
    access_token_expire_minutes: int
    cors_origins: list[str]


def _parse_cors_origins(value: str | None) -> list[str]:
    if not value or not value.strip():
        return DEFAULT_CORS_ORIGINS.copy()
    return [origin.strip() for origin in value.split(',') if origin.strip()]


def _parse_database_url(value: str | None) -> str:
    raw_value = (value or '').strip()
    if not raw_value or 'your_username' in raw_value or 'your_password' in raw_value:
        return 'sqlite:///./ship_db.db'
    return raw_value


settings = Settings(
    database_url=_parse_database_url(os.getenv('DATABASE_URL')),
    secret_key=os.getenv('SECRET_KEY', 'shipyard-dev-secret-key'),
    access_token_expire_minutes=int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60')),
    cors_origins=_parse_cors_origins(os.getenv('CORS_ORIGINS')),
)
