# Requisitos del Sistema - Segundo Examen Parcial

## Requisitos Funcionales

- RF01: El sistema debe permitir registrar estudiantes.
- RF02: El sistema debe permitir registrar materias.
- RF03: El sistema debe registrar notas por alumno y periodo.
- RF04: El sistema debe registrar asistencia por fecha.
- RF05: El sistema debe registrar participaciones.
- RF06: El sistema debe generar una predicción del rendimiento académico por estudiante.
- RF07: El sistema debe mostrar un dashboard con datos agregados y fichas individuales.

## Requisitos No Funcionales

### Rendimiento y Escalabilidad
- RNF01: El sistema debe soportar al menos 500 usuarios simultáneos.
- RNF02: La predicción del rendimiento no debe demorar más de 3 segundos por solicitud.

### Seguridad
- RNF03: El acceso al sistema debe estar protegido con autenticación JWT.
- RNF04: El backend debe validar y sanitizar todas las entradas del usuario.

### Usabilidad y Accesibilidad
- RNF05: El diseño debe ser responsivo y cumplir criterios de accesibilidad (WCAG 2.1).
- RNF06: La interfaz debe ser intuitiva para docentes y alumnos.

### Disponibilidad y Mantenimiento
- RNF07: El sistema debe tener al menos 99% de disponibilidad.
- RNF08: El código debe estar documentado y versionado correctamente en GitHub.
