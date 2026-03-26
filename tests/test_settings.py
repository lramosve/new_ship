import importlib
import os
import sys


def load_settings_module():
    sys.modules.pop('app.core.settings', None)
    return importlib.import_module('app.core.settings')


def test_settings_use_safe_defaults_when_env_missing(monkeypatch):
    monkeypatch.delenv('DATABASE_URL', raising=False)
    monkeypatch.delenv('SECRET_KEY', raising=False)
    monkeypatch.delenv('ACCESS_TOKEN_EXPIRE_MINUTES', raising=False)
    monkeypatch.delenv('CORS_ORIGINS', raising=False)

    settings_module = load_settings_module()
    settings = settings_module.settings

    assert settings.database_url == 'sqlite:///./ship_db.db'
    assert settings.secret_key == 'shipyard-dev-secret-key'
    assert settings.access_token_expire_minutes == 60
    assert 'http://localhost:5173' in settings.cors_origins
    assert 'http://127.0.0.1:8080' in settings.cors_origins


def test_settings_parse_env_overrides(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/shipyard')
    monkeypatch.setenv('SECRET_KEY', 'production-secret-key')
    monkeypatch.setenv('ACCESS_TOKEN_EXPIRE_MINUTES', '90')
    monkeypatch.setenv('CORS_ORIGINS', 'https://shipyard.example.com, https://app.example.com')

    settings_module = load_settings_module()
    settings = settings_module.settings

    assert settings.database_url == 'postgresql://postgres:postgres@db:5432/shipyard'
    assert settings.secret_key == 'production-secret-key'
    assert settings.access_token_expire_minutes == 90
    assert settings.cors_origins == ['https://shipyard.example.com', 'https://app.example.com']


def test_settings_replace_placeholder_database_url(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'postgresql://your_username:your_password@localhost:5432/app')

    settings_module = load_settings_module()

    assert settings_module.settings.database_url == 'sqlite:///./ship_db.db'
