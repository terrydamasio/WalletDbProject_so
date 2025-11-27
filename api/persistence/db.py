import os
from pathlib import Path
from contextlib import contextmanager

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, Connection


# Carrega .env a partir da raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)


def get_database_url() -> str:
    host = os.getenv("DB_HOST", "mysql")
    user = os.getenv("DB_USER", "wallet_user")
    password = os.getenv("DB_PASSWORD", "wallet123")
    db = os.getenv("DB_NAME", "wallet_homolog")
    port = int(os.getenv("DB_PORT", 3306))

    if not all([user, password, db]):
        raise RuntimeError("Variáveis de ambiente do banco não configuradas corretamente.")

    # usamos mysql+mysqlconnector, mas continua tudo SQL puro
    return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}"


DATABASE_URL = get_database_url()

engine: Engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
)


@contextmanager
def get_connection() -> Connection:
    """
    Entrega uma conexão do SQLAlchemy já com transação aberta.
    Faz commit automático se der tudo certo, rollback se der erro.
    """
    conn: Connection = engine.connect()
    trans = conn.begin()
    try:
        yield conn
        trans.commit()
    except Exception:
        trans.rollback()
        raise
    finally:
        conn.close()

def test_connection() -> bool:
    """
    Testa se a conexão com o banco está funcionando.
    
    Returns:
        bool: True se conectou com sucesso
    """
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            return result == 1
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False
