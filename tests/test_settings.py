import importlib
import sys

import pytest


def load_settings_module():
    sys.modules.pop('app.core.settings', None)
    return importlib.import_module('app.core.settings')


def reset_env(monkeypatch):
    for key in [
        'DATABASE_URL',
        'SECRET_KEY',
        'ACCESS_TOKEN_EXPIRE_MINUTES',
        'CORS_ORIGINS',
        'ENVIRONMENT',
        'DEBUG',
        'LOG_LEVEL',
        'SQLALCHEMY_LOG_LEVEL',
    ]:
        monkeypatch.delenv(key, raising=False)


def test_settings_use_safe_defaults_when_env_missing(monkeypatch):
    reset_env(monkeypatch)

    settings_module = load_settings_module()
    settings = settings_module.settings

    assert settings.database_url == 'sqlite:///./ship_db.db'
    assert settings.secret_key
    assert settings.secret_key != 'shipyard-dev-secret-key'
    assert settings.access_token_expire_minutes == 60
    assert settings.environment == 'development'
    assert settings.debug is True
    assert settings.log_level == 'DEBUG'
    assert settings.sqlalchemy_log_level == 'INFO'
    assert 'http://localhost:5173' in settings.cors_origins
    assert 'http://127.0.0.1:8080' in settings.cors_origins


def test_settings_parse_env_overrides(monkeypatch):
    reset_env(monkeypatch)
    monkeypatch.setenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/shipyard')
    monkeypatch.setenv('SECRET_KEY', 'production-secret-key')
    monkeypatch.setenv('ACCESS_TOKEN_EXPIRE_MINUTES', '90')
    monkeypatch.setenv('CORS_ORIGINS', 'https://shipyard.example.com, https://app.example.com')
    monkeypatch.setenv('ENVIRONMENT', 'production')
    monkeypatch.setenv('DEBUG', 'false')
    monkeypatch.setenv('LOG_LEVEL', 'warning')
    monkeypatch.setenv('SQLALCHEMY_LOG_LEVEL', 'error')

    settings_module = load_settings_module()
    settings = settings_module.settings

    assert settings.database_url == 'postgresql://postgres:postgres@db:5432/shipyard'
    assert settings.secret_key == 'production-secret-key'
    assert settings.access_token_expire_minutes == 90
    assert settings.environment == 'production'
    assert settings.debug is False
    assert settings.log_level == 'WARNING'
    assert settings.sqlalchemy_log_level == 'ERROR'
    assert settings.cors_origins == ['https://shipyard.example.com', 'https://app.example.com']


def test_settings_replace_placeholder_database_url(monkeypatch):
    reset_env(monkeypatch)
    monkeypatch.setenv('DATABASE_URL', 'postgresql://your_username:your_password@localhost:5432/app')

    settings_module = load_settings_module()

    assert settings_module.settings.database_url == 'sqlite:///./ship_db.db'


def test_settings_require_secret_key_in_production(monkeypatch):
    reset_env(monkeypatch)
    monkeypatch.setenv('ENVIRONMENT', 'production')

    with pytest.raises(RuntimeError, match='SECRET_KEY must be set in production'):
        load_settings_module()
