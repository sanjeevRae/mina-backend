#!/usr/bin/env python
"""
Server startup script for Render deployment.
This script ensures the app package is discoverable before starting uvicorn.
"""
import os
import socket
import sys


def safe_print(message: str) -> None:
    """Print text safely in terminals that cannot encode Unicode."""
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", errors="replace").decode("ascii"))


def can_bind(host: str, port: int) -> bool:
    """Check whether the requested host/port can be bound."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def resolve_server_port(host: str, preferred_port: int) -> int:
    """Use the configured port when possible, otherwise pick a free one."""
    if can_bind(host, preferred_port):
        return preferred_port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        fallback_port = sock.getsockname()[1]

    safe_print(
        f"[WARN] Port {preferred_port} is already in use. "
        f"Starting on available port {fallback_port} instead."
    )
    return fallback_port


# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

safe_print(f"Project root: {project_root}")
safe_print(f"Python path: {sys.path}")

# Debug: List contents of project root and app folder
safe_print("\n=== Directory Contents ===")
safe_print(f"Project root contents: {os.listdir(project_root)}")

app_dir = os.path.join(project_root, "app")
if os.path.exists(app_dir):
    safe_print(f"App folder exists: {app_dir}")
    safe_print(f"App folder contents: {os.listdir(app_dir)}")

    models_dir = os.path.join(app_dir, "models")
    if os.path.exists(models_dir):
        safe_print(f"Models folder exists: {models_dir}")
        safe_print(f"Models folder contents: {os.listdir(models_dir)}")
    else:
        safe_print(f"Models folder MISSING: {models_dir}")
else:
    safe_print(f"App folder MISSING: {app_dir}")

# Check if symptom checker model exists
symptom_model_dir = os.path.join(project_root, "models", "symptom_checker")
if os.path.exists(symptom_model_dir):
    safe_print(f"\n[OK] Symptom checker model found: {symptom_model_dir}")
    model_files = os.listdir(symptom_model_dir)
    safe_print(f"   Model files: {model_files}")
else:
    safe_print("\n[WARN] Symptom checker model not found. Train it with: python train_symptom_model.py")

safe_print("=== End Directory Contents ===\n")

# Verify imports work
try:
    from app.config import settings
    from app.main import app

    safe_print("[OK] App imports successful")
except ImportError as e:
    safe_print(f"[ERROR] Import error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

if __name__ == "__main__":
    import uvicorn

    host = settings.HOST or "0.0.0.0"
    port = resolve_server_port(host, settings.PORT)
    uvicorn.run("app.main:app", host=host, port=port)
