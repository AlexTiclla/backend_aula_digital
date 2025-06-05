from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Nota, Asistencia, Participaciones, Estudiante, CursoMateria
from ..dependencies.auth import get_current_user
from ..schemas.prediccion import PrediccionRequest, PrediccionResponse
from ..schemas.nota import NotaResponse
from ..schemas.asistencia import Asistencia as AsistenciaSchema
from ..schemas.participacion import Participacion as ParticipacionSchema

router = APIRouter(
    prefix="/api/v1/predicciones",
    tags=["predicciones"],
    responses={404: {"description": "No encontrado"}},
)

def _preparar_datos_notas(notas):
    """Prepara los datos de notas para el modelo predictivo"""
    if not notas:
        return None
    
    # Convertir a DataFrame
    df = pd.DataFrame([{
        'valor': nota.valor,
        'dias_desde_inicio': (nota.fecha - notas[0].fecha).days,
        'rendimiento': 0 if nota.rendimiento == 'bajo' else 1 if nota.rendimiento == 'medio' else 2,
    } for nota in notas])
    
    # Limitamos a los últimos 5 registros para una predicción más relevante
    if len(df) > 5:
        df = df.sort_values('dias_desde_inicio', ascending=False).head(5)
    
    return df

def _preparar_datos_asistencia(asistencias):
    """Prepara los datos de asistencia para el modelo predictivo"""
    if not asistencias:
        return None
    
    # Convertir a DataFrame
    df = pd.DataFrame([{
        'valor': 1 if asistencia.valor else 0,
        'dias_desde_inicio': (asistencia.fecha - asistencias[0].fecha).days,
        'dia_semana': asistencia.fecha.weekday(),
    } for asistencia in asistencias])
    
    # Limitamos a los últimos 5 registros
    if len(df) > 5:
        df = df.sort_values('dias_desde_inicio', ascending=False).head(5)
    
    return df

def _preparar_datos_participacion(participaciones):
    """Prepara los datos de participación para el modelo predictivo"""
    if not participaciones:
        return None
    
    # Convertir a DataFrame
    df = pd.DataFrame([{
        'participacion': 1,  # Siempre es 1 si hay registro
        'dias_desde_inicio': (participacion.fecha - participaciones[0].fecha).days,
        'dia_semana': participacion.fecha.weekday(),
    } for participacion in participaciones])
    
    # Limitamos a los últimos 5 registros
    if len(df) > 5:
        df = df.sort_values('dias_desde_inicio', ascending=False).head(5)
    
    return df

@router.post("/predict", response_model=PrediccionResponse)
async def predecir_rendimiento(
    request: PrediccionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Verificar que el estudiante existe
    estudiante = db.query(Estudiante).filter(Estudiante.id == request.estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Obtener los datos históricos
    notas = db.query(Nota).filter(
        Nota.estudiante_id == request.estudiante_id
    ).order_by(Nota.fecha).all()
    
    asistencias = db.query(Asistencia).filter(
        Asistencia.estudiante_id == request.estudiante_id
    ).order_by(Asistencia.fecha).all()
    
    participaciones = db.query(Participaciones).filter(
        Participaciones.estudiante_id == request.estudiante_id
    ).order_by(Participaciones.fecha).all()
    
    # Inicializar las respuestas
    prediccion_nota = None
    prediccion_asistencia = False
    prediccion_participacion = False
    confianza_nota = 0
    confianza_asistencia = 0
    confianza_participacion = 0
    
    # Predecir nota (si hay suficientes datos)
    if len(notas) >= 3:
        df_notas = _preparar_datos_notas(notas)
        X = df_notas.drop('valor', axis=1).values
        y = df_notas['valor'].values
        
        # Normalizar datos
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Entrenar modelo
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(X_scaled, y)
        
        # Preparar datos para predicción (último registro + 1 día)
        ultimo_registro = df_notas.iloc[-1].copy()
        ultimo_registro['dias_desde_inicio'] += 1
        X_pred = scaler.transform([ultimo_registro.drop('valor')])
        
        # Predecir
        prediccion_nota = int(round(model.predict(X_pred)[0]))
        confianza_nota = model.score(X_scaled, y)
    
    # Predecir asistencia (si hay suficientes datos)
    if len(asistencias) >= 3:
        df_asistencias = _preparar_datos_asistencia(asistencias)
        X = df_asistencias.drop('valor', axis=1).values
        y = df_asistencias['valor'].values
        
        # Entrenar modelo
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X, y)
        
        # Preparar datos para predicción (último registro + 1 día)
        ultimo_registro = df_asistencias.iloc[-1].copy()
        ultimo_registro['dias_desde_inicio'] += 1
        # Para el día de la semana, simulamos el próximo día
        ultimo_dia = datetime.now()
        siguiente_dia = ultimo_dia + timedelta(days=1)
        ultimo_registro['dia_semana'] = siguiente_dia.weekday()
        
        X_pred = [ultimo_registro.drop('valor')]
        
        # Predecir
        prediccion_asistencia = bool(model.predict(X_pred)[0])
        confianza_asistencia = model.score(X, y)
    
    # Predecir participación (si hay suficientes datos)
    # Para participación, usamos un enfoque similar a asistencia pero considerando
    # la existencia o no de registros como indicador
    if len(participaciones) >= 2:
        df_participacion = _preparar_datos_participacion(participaciones)
        
        # Aquí simplificamos: si participó en al menos 3 de los últimos 5 registros, 
        # predecimos que participará
        prediccion_participacion = len(df_participacion) > 2
        confianza_participacion = 0.7  # Confianza estática para simplificar
    
    # Retornar predicciones
    ultimas_notas_raw = notas[-5:] if len(notas) >= 5 else notas
    ultimas_asistencias_raw = asistencias[-5:] if len(asistencias) >= 5 else asistencias
    ultimas_participaciones_raw = participaciones[-5:] if len(participaciones) >= 5 else participaciones
    
    # Convertir objetos SQLAlchemy a esquemas Pydantic
    ultimas_notas = [NotaResponse.from_orm(nota) for nota in ultimas_notas_raw]
    ultimas_asistencias = [AsistenciaSchema.from_orm(asistencia) for asistencia in ultimas_asistencias_raw]
    ultimas_participaciones = [ParticipacionSchema.from_orm(participacion) for participacion in ultimas_participaciones_raw]
    
    return PrediccionResponse(
        estudiante=estudiante,
        prediccion_nota=prediccion_nota,
        prediccion_asistencia=prediccion_asistencia,
        prediccion_participacion=prediccion_participacion,
        confianza_nota=confianza_nota,
        confianza_asistencia=confianza_asistencia,
        confianza_participacion=confianza_participacion,
        ultimas_notas=ultimas_notas,
        ultimas_asistencias=ultimas_asistencias,
        ultimas_participaciones=ultimas_participaciones
    ) 