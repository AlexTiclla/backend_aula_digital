from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from .config import settings

def test_connection():
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as connection:
            print("¡Conexión exitosa a la base de datos!")
    except SQLAlchemyError as e:
        print(f"Error al conectar a la base de datos: {e}")

if __name__ == "__main__":
    test_connection()