from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Añadir el directorio padre al path para poder importar los modelos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Base, Periodo, Curso, CursoPeriodo, Materia, CursoMateria, Profesor

# Configuración de la base de datos
DATABASE_URL = "postgresql://aula_digital_owner:npg_qCTF5NndhQf3@ep-restless-darkness-a8rbakii-pooler.eastus2.azure.neon.tech/aula_digital?sslmode=require"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_periodos_2025():
    db = SessionLocal()
    try:
        # 1. Crear periodos (bimestres) para el año 2025 hasta junio
        periodos_2025 = []
        año = 2025
        
        # Primer bimestre (febrero-marzo)
        periodo1 = Periodo(
            bimestre=1,
            anio=año,
            fecha_inicio=date(año, 2, 1),
            fecha_fin=date(año, 3, 31),
            is_active=True,
            descripcion=f"Bimestre 1 del año {año}"
        )
        db.add(periodo1)
        periodos_2025.append(periodo1)
        
        # Segundo bimestre (abril-mayo)
        periodo2 = Periodo(
            bimestre=2,
            anio=año,
            fecha_inicio=date(año, 4, 1),
            fecha_fin=date(año, 5, 31),
            is_active=True,
            descripcion=f"Bimestre 2 del año {año}"
        )
        db.add(periodo2)
        periodos_2025.append(periodo2)
        
        # Tercer bimestre (junio-julio) - Solo incluimos junio
        periodo3 = Periodo(
            bimestre=3,
            anio=año,
            fecha_inicio=date(año, 6, 1),
            fecha_fin=date(año, 6, 30),
            is_active=True,
            descripcion=f"Bimestre 3 del año {año} (parcial)"
        )
        db.add(periodo3)
        periodos_2025.append(periodo3)
        
        db.commit()
        print(f"Creados {len(periodos_2025)} periodos para el año 2025")
        
        # 2. Asignar estos periodos a cursos existentes (curso_periodo)
        # Primero obtenemos todos los cursos
        cursos = db.query(Curso).filter(Curso.is_active == True).all()
        
        curso_periodos_2025 = []
        for periodo in periodos_2025:
            for curso in cursos:
                curso_periodo = CursoPeriodo(
                    curso_id=curso.id,
                    periodo_id=periodo.id,
                    aula=f"Aula {curso.sigla}-{periodo.bimestre}",
                    turno="Mañana" if curso.nivel == "Primaria" else "Tarde",
                    capacidad_actual=curso.capacidad_maxima - 5,  # Dejamos 5 cupos libres
                    is_active=True
                )
                db.add(curso_periodo)
                curso_periodos_2025.append(curso_periodo)
        
        db.commit()
        print(f"Creados {len(curso_periodos_2025)} curso-periodos para el año 2025")
        
        # 3. Asignar materias a los curso_periodo (curso_materia)
        # Obtenemos todas las materias
        materias_primaria = db.query(Materia).filter(
            Materia.is_active == True, 
            Materia.area_conocimiento.in_(["Ciencias Exactas", "Humanidades", "Ciencias Naturales", "Ciencias Sociales", "Educación Física", "Artes"])
        ).limit(8).all()
        
        materias_secundaria = db.query(Materia).filter(
            Materia.is_active == True,
            Materia.area_conocimiento.in_(["Ciencias Exactas", "Humanidades", "Ciencias Naturales", "Ciencias Sociales", "Educación Física", "Artes", "Idiomas", "Tecnología"])
        ).offset(8).limit(12).all()
        
        # Obtenemos todos los profesores
        profesores = db.query(Profesor).all()
        
        curso_materias_2025 = []
        for cp in curso_periodos_2025:
            # Determinar qué materias corresponden según el nivel
            materias_nivel = materias_primaria if "Primaria" in cp.curso.nombre else materias_secundaria
            
            # Horarios según turno
            horarios_mañana = ["08:00-09:30", "09:45-11:15", "11:30-13:00"]
            horarios_tarde = ["14:00-15:30", "15:45-17:15", "17:30-19:00"]
            horarios = horarios_mañana if cp.turno == "Mañana" else horarios_tarde
            
            # Asignar cada materia a un profesor
            for i, materia in enumerate(materias_nivel):
                # Seleccionar un profesor adecuado
                profesor_idx = i % len(profesores)
                profesor = profesores[profesor_idx]
                
                # Seleccionar un horario
                horario_idx = i % len(horarios)
                
                curso_materia = CursoMateria(
                    materia_id=materia.id,
                    curso_periodo_id=cp.id,
                    profesor_id=profesor.id,
                    horario=horarios[horario_idx],
                    aula=cp.aula,
                    modalidad="Presencial"
                )
                db.add(curso_materia)
                curso_materias_2025.append(curso_materia)
        
        db.commit()
        print(f"Creados {len(curso_materias_2025)} curso-materias para el año 2025")
        
        print("¡Datos para el año 2025 creados exitosamente!")
        
    except Exception as e:
        db.rollback()
        print(f"Error al crear datos: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_periodos_2025()