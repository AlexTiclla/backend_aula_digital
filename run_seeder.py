# backend_aula_digital/run_seeder.py
import os
import sys
from sqlalchemy import text
from app.database import SessionLocal
from app.seed_new_data import seed_data



if __name__ == "__main__":
    try:
        #2. Insertar datos básicos
        print("\nInsertando datos básicos...")
        seed_data()
        
        print("\nSeeding completado exitosamente!")
    except Exception as e:
        print(f"Error durante el seeding: {e}")
        sys.exit(1)