import os

def get_db_config():
    return {
        "dbname": os.getenv("POSTGRES_DB", "quantum_tasks"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "host": os.getenv("POSTGRES_HOST", "db"),
        "port": os.getenv("POSTGRES_PORT", "5432")
    }

def get_nats_config():
    return {
        "url": os.getenv("NATS_URL", "nats://nats:4222")
    }
