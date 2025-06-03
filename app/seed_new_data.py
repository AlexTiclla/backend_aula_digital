#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import random
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from faker import Faker

# Añadir el directorio padre al path para poder importar los modelos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import (
    Base, Usuario, RolUsuario, Tutor, Estudiante, Profesor, 
    Administrativo, Periodo, Curso, CursoPeriodo, Materia, 
    CursoMateria, Participaciones, Asistencia, Nota
)

# Configuración
DATABASE_URL = "postgresql://aula_digital_owner:npg_qCTF5NndhQf3@ep-restless-darkness-a8rbakii-pooler.eastus2.azure.neon.tech/aula_digital?sslmode=require"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

# Configuración para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fake = Faker('es_ES')

def hash_password(password):
    return pwd_context.hash(password)

def seed_data():
    db = SessionLocal()
    try:
        # Limpiar datos existentes (opcional)
        # db.query(Nota).delete()
        # db.query(Asistencia).delete()
        # db.query(Participaciones).delete()
        # db.query(CursoMateria).delete()
        # db.query(Materia).delete()
        # db.query(CursoPeriodo).delete()
        # db.query(Curso).delete()
        # db.query(Periodo).delete()
        # db.query(Estudiante).delete()
        # db.query(Profesor).delete()
        # db.query(Administrativo).delete()
        # db.query(Tutor).delete()
        # db.query(Usuario).delete()
        # db.commit()

        # 1. Crear Periodos (Bimestres de años anteriores y actual)
        periodos = []
        años = [2022, 2023, 2024]
        for año in años:
            for bimestre in range(1, 5):  # 4 bimestres por año
                fecha_inicio = date(año, 2 + (bimestre - 1) * 2, 1)  # Aproximado
                fecha_fin = date(año, 2 + bimestre * 2, 28 if bimestre < 4 else 20)
                
                periodo = Periodo(
                    bimestre=bimestre,
                    anio=año,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    is_active=año == 2024 and bimestre >= 3,
                    descripcion=f"Bimestre {bimestre} del año {año}"
                )
                db.add(periodo)
                periodos.append(periodo)
        
        db.commit()
        print(f"Creados {len(periodos)} periodos")

        # 2. Crear Cursos (Primaria y Secundaria)
        cursos = []
        # Primaria
        for grado in range(1, 7):
            curso = Curso(
                nombre=f"{grado}° de Primaria",
                sigla=f"P{grado}",
                nivel="Primaria",
                capacidad_maxima=30,
                descripcion=f"Grado {grado} de nivel primario",
                is_active=True
            )
            db.add(curso)
            cursos.append(curso)
        
        # Secundaria
        for grado in range(1, 7):
            curso = Curso(
                nombre=f"{grado}° de Secundaria",
                sigla=f"S{grado}",
                nivel="Secundaria",
                capacidad_maxima=35,
                descripcion=f"Grado {grado} de nivel secundario",
                is_active=True
            )
            db.add(curso)
            cursos.append(curso)
        
        db.commit()
        print(f"Creados {len(cursos)} cursos")

        # 3. Crear Materias
        materias_primaria = [
            {"nombre": "Matemáticas", "area": "Ciencias Exactas", "horas": 6},
            {"nombre": "Lenguaje", "area": "Humanidades", "horas": 6},
            {"nombre": "Ciencias Naturales", "area": "Ciencias Naturales", "horas": 4},
            {"nombre": "Ciencias Sociales", "area": "Ciencias Sociales", "horas": 4},
            {"nombre": "Educación Física", "area": "Educación Física", "horas": 2},
            {"nombre": "Artes Plásticas", "area": "Artes", "horas": 2},
            {"nombre": "Música", "area": "Artes", "horas": 2},
            {"nombre": "Religión", "area": "Humanidades", "horas": 2},
        ]
        
        materias_secundaria = [
            {"nombre": "Matemáticas", "area": "Ciencias Exactas", "horas": 6},
            {"nombre": "Literatura", "area": "Humanidades", "horas": 5},
            {"nombre": "Física", "area": "Ciencias Naturales", "horas": 4},
            {"nombre": "Química", "area": "Ciencias Naturales", "horas": 4},
            {"nombre": "Biología", "area": "Ciencias Naturales", "horas": 4},
            {"nombre": "Historia", "area": "Ciencias Sociales", "horas": 4},
            {"nombre": "Geografía", "area": "Ciencias Sociales", "horas": 3},
            {"nombre": "Educación Física", "area": "Educación Física", "horas": 2},
            {"nombre": "Artes", "area": "Artes", "horas": 2},
            {"nombre": "Inglés", "area": "Idiomas", "horas": 4},
            {"nombre": "Informática", "area": "Tecnología", "horas": 2},
            {"nombre": "Educación Cívica", "area": "Ciencias Sociales", "horas": 2},
        ]
        
        materias = []
        for materia_data in materias_primaria:
            materia = Materia(
                nombre=materia_data["nombre"],
                descripcion=f"Materia de {materia_data['nombre']} para nivel primario",
                area_conocimiento=materia_data["area"],
                horas_semanales=materia_data["horas"],
                is_active=True
            )
            db.add(materia)
            materias.append(materia)
        
        for materia_data in materias_secundaria:
            materia = Materia(
                nombre=materia_data["nombre"],
                descripcion=f"Materia de {materia_data['nombre']} para nivel secundario",
                area_conocimiento=materia_data["area"],
                horas_semanales=materia_data["horas"],
                is_active=True
            )
            db.add(materia)
            materias.append(materia)
        
        db.commit()
        print(f"Creadas {len(materias)} materias")

        # 4. Crear un usuario administrativo
        admin_user = Usuario(
            nombre="Admin",
            apellido="Sistema",
            email="admin@colegio.edu",
            password=hash_password("admin123"),
            rol=RolUsuario.ADMINISTRATIVO,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        
        admin = Administrativo(
            usuario_id=admin_user.id
        )
        db.add(admin)
        db.commit()
        print("Creado usuario administrativo")

        # 5. Crear profesores
        profesores_data = [
            {"nombre": "Juan", "apellido": "Pérez", "especialidad": "Matemáticas", "nivel": "Licenciatura"},
            {"nombre": "María", "apellido": "González", "especialidad": "Lenguaje", "nivel": "Maestría"},
            {"nombre": "Carlos", "apellido": "Rodríguez", "especialidad": "Ciencias Naturales", "nivel": "Licenciatura"},
            {"nombre": "Ana", "apellido": "López", "especialidad": "Ciencias Sociales", "nivel": "Doctorado"},
            {"nombre": "Pedro", "apellido": "Martínez", "especialidad": "Educación Física", "nivel": "Licenciatura"},
            {"nombre": "Laura", "apellido": "Sánchez", "especialidad": "Artes", "nivel": "Maestría"},
            {"nombre": "Miguel", "apellido": "Fernández", "especialidad": "Música", "nivel": "Licenciatura"},
            {"nombre": "Isabel", "apellido": "Torres", "especialidad": "Religión", "nivel": "Licenciatura"},
            {"nombre": "Roberto", "apellido": "Díaz", "especialidad": "Física", "nivel": "Doctorado"},
            {"nombre": "Sofía", "apellido": "Vargas", "especialidad": "Química", "nivel": "Maestría"},
            {"nombre": "Javier", "apellido": "Ruiz", "especialidad": "Biología", "nivel": "Licenciatura"},
            {"nombre": "Elena", "apellido": "Gómez", "especialidad": "Historia", "nivel": "Maestría"},
            {"nombre": "Diego", "apellido": "Castro", "especialidad": "Geografía", "nivel": "Licenciatura"},
            {"nombre": "Carmen", "apellido": "Herrera", "especialidad": "Inglés", "nivel": "Licenciatura"},
            {"nombre": "Fernando", "apellido": "Ortega", "especialidad": "Informática", "nivel": "Maestría"}
        ]
        
        profesores = []
        for i, prof_data in enumerate(profesores_data):
            prof_user = Usuario(
                nombre=prof_data["nombre"],
                apellido=prof_data["apellido"],
                email=f"{prof_data['nombre'].lower()}.{prof_data['apellido'].lower()}@colegio.edu",
                password=hash_password("profesor123"),
                rol=RolUsuario.PROFESOR,
                is_active=True
            )
            db.add(prof_user)
            db.commit()
            
            profesor = Profesor(
                usuario_id=prof_user.id,
                telefono=f"6{random.randint(1000000, 9999999)}",
                carnet_identidad=f"{random.randint(1000000, 9999999)} LP",
                especialidad=prof_data["especialidad"],
                nivel_academico=prof_data["nivel"]
            )
            db.add(profesor)
            profesores.append(profesor)
        
        db.commit()
        print(f"Creados {len(profesores)} profesores")

        # 6. Crear tutores
        tutores = []
        for i in range(20):
            genero = random.choice(['M', 'F'])
            nombre = fake.first_name_male() if genero == 'M' else fake.first_name_female()
            apellido = fake.last_name()
            
            tutor = Tutor(
                nombre=nombre,
                apellido=apellido,
                relacion_estudiante=random.choice(["Padre", "Madre", "Abuelo", "Abuela", "Tío", "Tía"]),
                ocupacion=fake.job(),
                lugar_trabajo=fake.company(),
                correo=f"{nombre.lower()}.{apellido.lower()}{random.randint(10, 99)}@gmail.com",
                telefono=f"7{random.randint(1000000, 9999999)}"
            )
            db.add(tutor)
            tutores.append(tutor)
        
        db.commit()
        print(f"Creados {len(tutores)} tutores")

        # 7. Crear CursoPeriodo
        curso_periodos = []
        for periodo in periodos:
            for curso in cursos:
                # No todos los cursos están activos en todos los periodos
                if random.random() < 0.8:  # 80% de probabilidad
                    curso_periodo = CursoPeriodo(
                        curso_id=curso.id,
                        periodo_id=periodo.id,
                        aula=f"Aula {random.randint(101, 320)}",
                        turno=random.choice(["Mañana", "Tarde"]),
                        capacidad_actual=random.randint(15, curso.capacidad_maxima),
                        is_active=periodo.is_active
                    )
                    db.add(curso_periodo)
                    curso_periodos.append(curso_periodo)
        
        db.commit()
        print(f"Creados {len(curso_periodos)} curso-periodos")

        # 8. Crear estudiantes
        estudiantes = []
        for i in range(50):
            genero = random.choice(['M', 'F'])
            nombre = fake.first_name_male() if genero == 'M' else fake.first_name_female()
            apellido = fake.last_name()
            
            est_user = Usuario(
                nombre=nombre,
                apellido=apellido,
                email=f"estudiante{i+1}@colegio.edu",
                password=hash_password("estudiante123"),
                rol=RolUsuario.ESTUDIANTE,
                is_active=True
            )
            db.add(est_user)
            db.commit()
            
            # Fecha de nacimiento según nivel (primaria o secundaria)
            nivel = random.choice(["Primaria", "Secundaria"])
            if nivel == "Primaria":
                # Entre 6 y 12 años
                años_atras = random.randint(6, 12)
            else:
                # Entre 12 y 18 años
                años_atras = random.randint(12, 18)
                
            fecha_nac = datetime.now() - timedelta(days=365 * años_atras)
            
            # Asignar un curso_periodo adecuado según el nivel
            cps_nivel = [cp for cp in curso_periodos if nivel in cp.curso.nombre and cp.is_active]
            curso_periodo_seleccionado = random.choice(cps_nivel) if cps_nivel else None
            
            estudiante = Estudiante(
                usuario_id=est_user.id,
                tutor_id=random.choice(tutores).id,
                curso_periodo_id=curso_periodo_seleccionado.id if curso_periodo_seleccionado else None,
                direccion=fake.address(),
                fecha_nacimiento=fecha_nac
            )
            db.add(estudiante)
            estudiantes.append(estudiante)
        
        db.commit()
        print(f"Creados {len(estudiantes)} estudiantes")

        # 9. Crear CursoMateria
        curso_materias = []
        for cp in curso_periodos:
            # Determinar qué materias corresponden según el nivel
            materias_nivel = materias[:8] if "Primaria" in cp.curso.nombre else materias[8:]
            
            # Asignar algunas materias (no todas) a cada curso-periodo
            num_materias = random.randint(5, len(materias_nivel))
            materias_seleccionadas = random.sample(materias_nivel, num_materias)
            
            for materia in materias_seleccionadas:
                # Encontrar un profesor adecuado para la materia
                profesor_adecuado = None
                for profesor in profesores:
                    if materia.nombre in profesor.especialidad or profesor.especialidad in materia.nombre:
                        profesor_adecuado = profesor
                        break
                
                # Si no hay profesor especializado, elegir uno al azar
                if not profesor_adecuado:
                    profesor_adecuado = random.choice(profesores)
                
                # Horarios posibles
                horarios_mañana = ["08:00-09:30", "09:45-11:15", "11:30-13:00"]
                horarios_tarde = ["14:00-15:30", "15:45-17:15", "17:30-19:00"]
                horarios = horarios_mañana if cp.turno == "Mañana" else horarios_tarde
                
                curso_materia = CursoMateria(
                    materia_id=materia.id,
                    curso_periodo_id=cp.id,
                    profesor_id=profesor_adecuado.id,
                    horario=random.choice(horarios),
                    aula=cp.aula,
                    modalidad=random.choice(["Presencial", "Virtual", "Híbrida"])
                )
                db.add(curso_materia)
                curso_materias.append(curso_materia)
        
        db.commit()
        print(f"Creados {len(curso_materias)} curso-materias")

        # 10. Crear Notas, Asistencias y Participaciones para algunos estudiantes
        # Seleccionamos algunos estudiantes para los datos de rendimiento
        estudiantes_muestra = random.sample(estudiantes, min(30, len(estudiantes)))
        
        # Para cada estudiante, asignamos algunas materias
        for estudiante in estudiantes_muestra:
            # Determinar nivel del estudiante (primaria o secundaria) basado en la edad
            edad = (datetime.now().date() - estudiante.fecha_nacimiento.date()).days // 365
            nivel = "Primaria" if edad < 12 else "Secundaria"
            
            # Filtrar curso_materias por nivel
            cms_nivel = [cm for cm in curso_materias if nivel in cm.curso_periodo.curso.nombre]
            
            # Seleccionar algunas materias para este estudiante
            num_materias = random.randint(3, 6)
            cms_estudiante = random.sample(cms_nivel, min(num_materias, len(cms_nivel)))
            
            for cm in cms_estudiante:
                # Crear notas (2-4 por materia)
                num_notas = random.randint(2, 4)
                for _ in range(num_notas):
                    # Valor de la nota (0-100)
                    valor = random.randint(40, 100)
                    
                    # Determinar rendimiento
                    if valor < 60:
                        rendimiento = "bajo"
                    elif valor < 80:
                        rendimiento = "medio"
                    else:
                        rendimiento = "alto"
                    
                    # Fecha de la nota (dentro del periodo del curso)
                    fecha_inicio = cm.curso_periodo.periodo.fecha_inicio
                    fecha_fin = cm.curso_periodo.periodo.fecha_fin
                    dias_periodo = (fecha_fin - fecha_inicio).days
                    fecha_nota = fecha_inicio + timedelta(days=random.randint(0, dias_periodo))
                    
                    nota = Nota(
                        estudiante_id=estudiante.id,
                        curso_materia_id=cm.id,
                        valor=valor,
                        fecha=fecha_nota,
                        descripcion=random.choice(["Examen parcial", "Examen final", "Trabajo práctico", "Exposición", "Tarea"]),
                        rendimiento=rendimiento
                    )
                    db.add(nota)
                
                # Crear asistencias (5-10 por materia)
                num_asistencias = random.randint(5, 10)
                for _ in range(num_asistencias):
                    # Fecha de la asistencia
                    fecha_inicio = cm.curso_periodo.periodo.fecha_inicio
                    fecha_fin = cm.curso_periodo.periodo.fecha_fin
                    dias_periodo = (fecha_fin - fecha_inicio).days
                    fecha_asistencia = fecha_inicio + timedelta(days=random.randint(0, dias_periodo))
                    
                    # Valor (presente o ausente)
                    valor = random.random() < 0.9  # 90% de probabilidad de asistencia
                    
                    asistencia = Asistencia(
                        estudiante_id=estudiante.id,
                        curso_materia_id=cm.id,
                        valor=valor,
                        fecha=fecha_asistencia
                    )
                    db.add(asistencia)
                
                # Crear participaciones (3-6 por materia)
                num_participaciones = random.randint(3, 6)
                for _ in range(num_participaciones):
                    # Fecha de la participación
                    fecha_inicio = cm.curso_periodo.periodo.fecha_inicio
                    fecha_fin = cm.curso_periodo.periodo.fecha_fin
                    dias_periodo = (fecha_fin - fecha_inicio).days
                    fecha_participacion = fecha_inicio + timedelta(days=random.randint(0, dias_periodo))
                    
                    participacion = Participaciones(
                        estudiante_id=estudiante.id,
                        curso_materia_id=cm.id,
                        participacion_clase=random.choice(["Alta", "Media", "Baja"]),
                        fecha=fecha_participacion,
                        observacion=random.choice([
                            "Participó activamente en clase",
                            "Hizo preguntas relevantes",
                            "Respondió correctamente",
                            "Participación limitada",
                            "No mostró interés",
                            "Participación destacada",
                            None
                        ])
                    )
                    db.add(participacion)
        
        db.commit()
        print("Creados datos de rendimiento (notas, asistencias y participaciones)")
        
        print("¡Datos de muestra creados exitosamente!")
        
    except Exception as e:
        db.rollback()
        print(f"Error al crear datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
