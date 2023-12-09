---
title: ColegioJPC2023
emoji: 🌖
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: apache-2.0
---

# Aplicativo para la gestión de tareas del colegio JPC 
# Backend con FastAPI

Este proyecto es un sistema de gestión académica que permite a usuarios, como estudiantes y profesores, realizar diversas acciones relacionadas con tareas, entregas y cambios de estado. A continuación, se describen las principales entidades del sistema:

## Tablas Principales

### Usuarios
- **idusuario**: Identificador único del usuario.
- **dni**: Número de identificación del usuario.
- **contrasena**: Contraseña del usuario.
- **rol**: Rol del usuario (puede ser estudiante, profesor, etc.).

### Estudiantes
- **idestudiante**: Identificador único del estudiante.
- **nombre**: Nombre del estudiante.
- **dni**: Número de identificación del estudiante.
- **idclase**: Identificador de la clase a la que pertenece el estudiante.
- **idusuario**: Identificador del usuario asociado al estudiante.

### Profesores
- **idprofesor**: Identificador único del profesor.
- **nombre**: Nombre del profesor.
- **dni**: Número de identificación del profesor.
- **correo**: Correo electrónico del profesor.
- **idusuario**: Identificador del usuario asociado al profesor.

### Tareas
- **idtarea**: Identificador único de la tarea.
- **nombre_tarea**: Nombre de la tarea.
- **instrucciones**: Instrucciones asociadas a la tarea.
- **fecha_vencimiento**: Fecha de vencimiento de la tarea.
- **idclase**: Identificador de la clase a la que pertenece la tarea.
- **idestudiante**: Identificador del estudiante asociado a la tarea.
- **estado**: Estado de la tarea (puede ser 'entregado', 'no entregado', u otros estados).

### Entregas
- **identrega**: Identificador único de la entrega.
- **fecha_entrega**: Fecha de la entrega.
- **nombre_archivo**: Nombre original del archivo entregado.
- **tipo_archivo**: Tipo MIME del archivo entregado.
- **idtarea**: Identificador de la tarea asociada a la entrega.
- **idestudiante**: Identificador del estudiante que realizó la entrega.

### Clases
- **idclase**: Identificador único de la clase.
- **nombre**: Nombre de la clase.
- **idprofesor**: Identificador del profesor asociado a la clase.

### CambiosEstado
- **idcambio**: Identificador único del cambio de estado.
- **idtarea**: Identificador de la tarea asociada al cambio de estado.
- **nuevo_estado**: Nuevo estado de la tarea (puede ser 'entregado', 'no entregado', u otros estados).
- **fecha_cambio**: Fecha en que se realizó el cambio de estado.

## Requisitos del Sistema
- Python (versión X.X.X)
- FastAPI
- Otras bibliotecas y dependencias (listar si es necesario)
- React Native

## Instalación y Uso
1. Clona este repositorio.
2. Instala las dependencias mencionadas en el archivo requirements.txt para el backend utilizando el siguiente comando:
    ```bash
    pip install -r requirements.txt
    ```
3. Para el frontend, sigue las instrucciones de instalación de React Native.
4. Ejecuta la aplicación con los comandos correspondientes al backend y al frontend.
5. Accede a la aplicación a través de la URL proporcionada para el backend y la aplicación móvil para el frontend.

## Pruebas Locales
Para probar el proyecto de forma local, sigue estos pasos:

1. Instala las librerías del archivo `requirements.txt` utilizando el siguiente comando:
    ```bash
    pip install -r requirements.txt
    ```

2. Ejecuta el backend con el siguiente comando:
    ```bash
    uvicorn app:app --host localhost --port 7860 --reload
    ```

## Pruebas Unitarias
Se han incluido pruebas unitarias para garantizar la integridad y el correcto funcionamiento de las funciones y componentes clave del sistema.
