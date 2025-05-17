
---

# Aula Digital - Backend

**Aula Digital** es un sistema backend desarrollado con **FastAPI** y **PostgreSQL** para la gestión integral de alumnos, materias, notas por periodos, asistencia, participación y predicción del rendimiento académico utilizando Inteligencia Artificial.

---

## Características principales

- **Gestión de alumnos:** Registro, edición y consulta de información de estudiantes.
- **Gestión de materias:** Administración de asignaturas y su relación con los alumnos.
- **Notas por periodos:** Registro y consulta de calificaciones por periodos académicos.
- **Asistencia y participación:** Control de asistencia y participación en clase.
- **Predicción de rendimiento académico:** Módulo de IA para predecir el desempeño de los estudiantes.
- **API RESTful:** Endpoints claros y documentados automáticamente con Swagger.
- **Base de datos relacional:** Uso de PostgreSQL y SQLAlchemy para la persistencia de datos.
- **Configuración por entorno:** Variables sensibles gestionadas con `.env`.

---

## Tecnologías utilizadas

- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Uvicorn](https://www.uvicorn.org/)
- [Alembic](https://alembic.sqlalchemy.org/) (migraciones)
- [Python-dotenv](https://pypi.org/project/python-dotenv/)
- [psycopg2-binary](https://pypi.org/project/psycopg2-binary/)

---

## Estructura del proyecto

```
backend_aula_digital/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   └── services/
│
├── .env
├── requirements.txt
└── README.md
```

---

## Instalación y configuración

1. **Clona el repositorio:**
   ```bash
   git clone <URL-del-repositorio>
   cd backend_aula_digital
   ```

2. **Crea y activa un entorno virtual:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # En Windows
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura la base de datos:**
   - Crea una base de datos en PostgreSQL (puedes usar pgAdmin).
   - Copia el archivo `.env.example` a `.env` y edita la variable `DATABASE_URL` con tus datos de conexión:
     ```
     DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/aula_digital
     ```

5. **Ejecuta las migraciones (si usas Alembic):**
   ```bash
   alembic upgrade head
   ```

6. **Inicia el servidor:**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Accede a la documentación interactiva:**
   - [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
   - [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc)

---

## Contribución

1. Haz un fork del repositorio.
2. Crea una rama para tu feature o fix: `git checkout -b mi-feature`
3. Realiza tus cambios y haz commit: `git commit -am 'Agrega nueva funcionalidad'`
4. Haz push a tu rama: `git push origin mi-feature`
5. Abre un Pull Request.

---

## Licencia

Este proyecto está bajo la licencia MIT.

---
