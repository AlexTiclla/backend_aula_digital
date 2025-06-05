from .estudiantes import router as estudiantes_router
from .tutores import router as tutores_router
from .profesores import router as profesores_router
from .materia import router as materias_router
from .asistencia import router as asistencia_router
from .participacion import router as participacion_router
from .nota import router as nota_router
from .auth import router as auth_router
from .usuarios import router as usuarios_router
from .curso_periodo import router as curso_periodo_router
from .curso import router as curso_router
from .periodo import router as periodo_router
from .curso_materia import router as curso_materia_router
from .prediccion import router as prediccion_router

routers = [
    estudiantes_router,
    tutores_router,
    profesores_router,
    materias_router,
    asistencia_router,
    participacion_router,
    nota_router,
    auth_router,
    usuarios_router,
    curso_periodo_router,
    curso_router,
    periodo_router,
    curso_materia_router,
    prediccion_router
]
