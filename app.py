# uvicorn app:app --host localhost --port 7860 --reload
from datetime import datetime
import os
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, status
from pydantic import BaseModel
from queue import Queue
import threading
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# class DatabaseConnection:
#     """
#     Clase para gestionar las conexiones a la base de datos con un pool.
#     """

#     _instance = None
#     _lock = threading.Lock()
#     _connection_pool = Queue(maxsize=5)

#     def __new__(cls):
#         """
#         Crea una nueva instancia de la clase si no existe.
#         """
#         with cls._lock:
#             if cls._instance is None:
#                 cls._instance = super().__new__(cls)
#                 cls._instance.conn = cls._instance._create_connection()
#         return cls._instance

#     def _create_connection(self):
#         """
#         Crea una conexión a la base de datos.
#         """
#         if not self._connection_pool.empty():
#             return self._connection_pool.get()
#         else:
#             connection = sqlite3.connect("colegio.db")
#             connection.row_factory = sqlite3.Row
#             return connection

#     def get_connection(self):
#         """
#         Obtener el objeto de conexión de la base de datos.
#         """
#         return self._instance._create_connection()

#     def release_connection(self):
#         """
#         Liberar la conexión de nuevo al pool.
#         """
#         if self._instance is not None:
#             self._connection_pool.put(self._instance.conn)
#             self._instance.conn = None  # Marcar la instancia como sin conexión


class DatabaseConnection:
    _instance = None
    _lock = threading.Lock()
    _connection_pool = Queue(maxsize=5)
    _database_name = "colegio.db"

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.conn = cls._instance._create_connection()
        return cls._instance

    def _create_connection(self):
        if not self._connection_pool.empty():
            return self._connection_pool.get()
        else:
            connection = sqlite3.connect(self._database_name)
            connection.row_factory = sqlite3.Row
            return connection

    def __enter__(self):
        self.conn = self._create_connection()
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        self.release_connection()

    def release_connection(self):
        if self._instance is not None:
            self._connection_pool.put(self._instance.conn)
            self._instance.conn = None


"""
CREATE TABLE Usuarios (
  idusuario INTEGER PRIMARY KEY AUTOINCREMENT,
  dni VARCHAR,
  contrasena VARCHAR,
  rol VARCHAR
);
"""


# metodos GET, POST, PUT, DELETE para la tabla Usuarios
# get
@app.get("/usuarios")
def get_usuarios():
    """
    Obtener todos los usuarios.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Usuarios")
            usuarios = cursor.fetchall()
            if usuarios is None:
                return []
            else:
                return usuarios
    except Exception as e:
        print(e)
        return []


# usando una clase model para el POST
class Usuario(BaseModel):
    """
    Modelo para la creación de un usuario.
    """

    dni: str
    contrasena: str
    rol: str


# post
@app.post("/usuarios")
def post_usuario(usuario: Usuario):
    """
    Crear un nuevo usuario.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Usuarios (dni, contrasena, rol) VALUES (?, ?, ?)",
                (usuario.dni, usuario.contrasena, usuario.rol),
            )
            conn.commit()
            return {"mensaje": "Usuario creado exitosamente"}
    except Exception as e:
        print(e)
        return []


# clase model para el PUT
class UsuarioUpdate(BaseModel):
    """
    Modelo para la actualización de un usuario.
    """

    dni: str
    contrasena: str
    rol: str


# put
@app.put("/usuarios/{idusuario}")
def put_usuario(idusuario: int, usuario: UsuarioUpdate):
    """
    Actualizar un usuario.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Usuarios SET dni = ?, contrasena = ?, rol = ? WHERE idusuario = ?",
                (usuario.dni, usuario.contrasena, usuario.rol, idusuario),
            )
            conn.commit()
            return {"mensaje": "Usuario actualizado exitosamente"}
    except Exception as e:
        print(e)
        return []


# delete
@app.delete("/usuarios/{idusuario}")
def delete_usuario(idusuario: int):
    """
    Eliminar un usuario.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Usuarios WHERE idusuario = ?", (idusuario,))
            conn.commit()
            return {"mensaje": "Usuario eliminado exitosamente"}
    except Exception as e:
        print(e)
        return []


class Login(BaseModel):
    """
    Modelo para el login de un usuario.
    """

    dni: str
    contrasena: str


# login
@app.post("/login")
def login(login: Login):
    """
    Login de un usuario.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Usuarios WHERE dni = ? AND contrasena = ?",
                (login.dni, login.contrasena),
            )
            usuario = cursor.fetchone()
            if usuario is None:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            else:
                return usuario
    except Exception as e:
        print(e)
        return []


"""
CREATE TABLE Profesores (
  idprofesor INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre VARCHAR,
  dni VARCHAR,
  correo VARCHAR,
  idusuario INTEGER REFERENCES Usuarios(idusuario)
);
"""


# metodos GET, POST, PUT, DELETE para la tabla Profesores
# get
@app.get("/profesores")
def get_profesores():
    """
    Obtener todos los profesores.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Profesores")
            profesores = cursor.fetchall()
            if profesores is None:
                return []
            else:
                return profesores
    except Exception as e:
        print(e)
        return []


# usando una clase model para el POST
class Profesor(BaseModel):
    """
    Modelo para la creación de un profesor.
    """

    nombre: str
    dni: str
    correo: str
    idusuario: int


# post
@app.post("/profesores")
def post_profesor(profesor: Profesor):
    """
    Crear un nuevo profesor.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Profesores (nombre, dni, correo, idusuario) VALUES (?, ?, ?, ?)",
                (profesor.nombre, profesor.dni, profesor.correo, profesor.idusuario),
            )
            conn.commit()
            return {"mensaje": "Profesor creado exitosamente"}
    except Exception as e:
        print(e)
        return []


# clase model para el PUT
class ProfesorUpdate(BaseModel):
    """
    Modelo para la actualización de un profesor.
    """

    nombre: str
    dni: str
    correo: str
    idusuario: int


# put
@app.put("/profesores/{idprofesor}")
def put_profesor(idprofesor: int, profesor: ProfesorUpdate):
    """
    Actualizar un profesor.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Profesores SET nombre = ?, dni = ?, correo = ?, idusuario = ? WHERE idprofesor = ?",
                (
                    profesor.nombre,
                    profesor.dni,
                    profesor.correo,
                    profesor.idusuario,
                    idprofesor,
                ),
            )
            conn.commit()
            return {"mensaje": "Profesor actualizado exitosamente"}
    except Exception as e:
        print(e)
        return []


# delete
@app.delete("/profesores/{idprofesor}")
def delete_profesor(idprofesor: int):
    """
    Eliminar un profesor.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Profesores WHERE idprofesor = ?", (idprofesor,))
            conn.commit()
            return {"mensaje": "Profesor eliminado exitosamente"}
    except Exception as e:
        print(e)
        return []


"""
CREATE TABLE Estudiantes (
  idestudiante INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre VARCHAR,
  dni VARCHAR,
  idclase INTEGER,
  idusuario INTEGER REFERENCES Usuarios(idusuario)
);
"""


# metodos GET, POST, PUT, DELETE para la tabla Estudiantes
# get
@app.get("/estudiantes")
def get_estudiantes():
    """
    Obtener todos los estudiantes.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Estudiantes")
            estudiantes = cursor.fetchall()
            if estudiantes is None:
                return []
            else:
                return estudiantes
    except Exception as e:
        print(e)
        return []


# usando una clase model para el POST
class Estudiante(BaseModel):
    """
    Modelo para la creación de un estudiante.
    """

    nombre: str
    dni: str
    idclase: int
    idusuario: int


# post
@app.post("/estudiantes")
def post_estudiante(estudiante: Estudiante):
    """
    Crear un nuevo estudiante.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Estudiantes (nombre, dni, idclase, idusuario) VALUES (?, ?, ?, ?)",
                (
                    estudiante.nombre,
                    estudiante.dni,
                    estudiante.idclase,
                    estudiante.idusuario,
                ),
            )
            conn.commit()
            return {"mensaje": "Estudiante creado exitosamente"}
    except Exception as e:
        print(e)
        return []


# clase model para el PUT
class EstudianteUpdate(BaseModel):
    """
    Modelo para la actualización de un estudiante.
    """

    nombre: str
    dni: str
    idclase: int
    idusuario: int


# put
@app.put("/estudiantes/{idestudiante}")
def put_estudiante(idestudiante: int, estudiante: EstudianteUpdate):
    """
    Actualizar un estudiante.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Estudiantes SET nombre = ?, dni = ?, idclase = ?, idusuario = ? WHERE idestudiante = ?",
                (
                    estudiante.nombre,
                    estudiante.dni,
                    estudiante.idclase,
                    estudiante.idusuario,
                    idestudiante,
                ),
            )
            conn.commit()
            return {"mensaje": "Estudiante actualizado exitosamente"}
    except Exception as e:
        print(e)
        return []


# delete
@app.delete("/estudiantes/{idestudiante}")
def delete_estudiante(idestudiante: int):
    """
    Eliminar un estudiante.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM Estudiantes WHERE idestudiante = ?", (idestudiante,)
            )
            conn.commit()
            return {"mensaje": "Estudiante eliminado exitosamente"}
    except Exception as e:
        print(e)
        return []


"""
CREATE TABLE Clases (
  idclase INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre VARCHAR,
  idprofesor INTEGER REFERENCES Profesores(idprofesor)
);
"""


# metodos GET, POST, PUT, DELETE para la tabla Clases
# get
@app.get("/clases")
def get_clases():
    """
    Obtener todas las clases.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Clases")
            clases = cursor.fetchall()
            if clases is None:
                return []
            else:
                return clases
    except Exception as e:
        print(e)
        return []


# usando una clase model para el POST
class Clase(BaseModel):
    """
    Modelo para la creación de una clase.
    """

    nombre: str
    idprofesor: int


# post
@app.post("/clases")
def post_clase(clase: Clase):
    """
    Crear una nueva clase.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Clases (nombre, idprofesor) VALUES (?, ?)",
                (clase.nombre, clase.idprofesor),
            )
            conn.commit()
            return {"mensaje": "Clase creada exitosamente"}
    except Exception as e:
        print(e)
        return []


# clase model para el PUT
class ClaseUpdate(BaseModel):
    """
    Modelo para la actualización de una clase.
    """

    nombre: str
    idprofesor: int


# put
@app.put("/clases/{idclase}")
def put_clase(idclase: int, clase: ClaseUpdate):
    """
    Actualizar una clase.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Clases SET nombre = ?, idprofesor = ? WHERE idclase = ?",
                (clase.nombre, clase.idprofesor, idclase),
            )
            conn.commit()
            return {"mensaje": "Clase actualizada exitosamente"}
    except Exception as e:
        print(e)
        return []


# delete
@app.delete("/clases/{idclase}")
def delete_clase(idclase: int):
    """
    Eliminar una clase.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Clases WHERE idclase = ?", (idclase,))
            conn.commit()
            return {"mensaje": "Clase eliminada exitosamente"}
    except Exception as e:
        print(e)
        return []


"""
CREATE TABLE Tareas (
  idtarea INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre_tarea VARCHAR,
  instrucciones TEXT,
  fecha_vencimiento DATE,
  idclase INTEGER REFERENCES Clases(idclase),
  idestudiante INTEGER REFERENCES Estudiantes(idestudiante),
  estado VARCHAR
);
"""


# metodos GET, POST, PUT, DELETE para la tabla Tareas
# get
@app.get("/tareas")
def get_tareas():
    """
    Obtener todas las tareas.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Tareas")
            tareas = cursor.fetchall()
            if tareas is None:
                return []
            else:
                return tareas
    except Exception as e:
        print(e)
        return []


# usando una clase model para el POST
class Tarea(BaseModel):
    """
    Modelo para la creación de una tarea.
    """

    nombre_tarea: str
    instrucciones: str
    fecha_vencimiento: str
    idclase: int
    idestudiante: int
    estado: str


# post
@app.post("/tareas")
def post_tarea(tarea: Tarea):
    """
    Crear una nueva tarea.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Tareas (nombre_tarea, instrucciones, fecha_vencimiento, idclase, idestudiante, estado) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    tarea.nombre_tarea,
                    tarea.instrucciones,
                    tarea.fecha_vencimiento,
                    tarea.idclase,
                    tarea.idestudiante,
                    tarea.estado,
                ),
            )
            conn.commit()
            return {"mensaje": "Tarea creada exitosamente"}
    except Exception as e:
        print(e)
        return []


# clase model para el PUT
class TareaUpdate(BaseModel):
    """
    Modelo para la actualización de una tarea.
    """

    nombre_tarea: str
    instrucciones: str
    fecha_vencimiento: str
    idclase: int
    idestudiante: int
    estado: str


# put
@app.put("/tareas/{idtarea}")
def put_tarea(idtarea: int, tarea: TareaUpdate):
    """
    Actualizar una tarea.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Tareas SET nombre_tarea = ?, instrucciones = ?, fecha_vencimiento = ?, idclase = ?, idestudiante = ?, estado = ? WHERE idtarea = ?",
                (
                    tarea.nombre_tarea,
                    tarea.instrucciones,
                    tarea.fecha_vencimiento,
                    tarea.idclase,
                    tarea.idestudiante,
                    tarea.estado,
                    idtarea,
                ),
            )
            conn.commit()
            return {"mensaje": "Tarea actualizada exitosamente"}
    except Exception as e:
        print(e)
        return []


# delete
@app.delete("/tareas/{idtarea}")
def delete_tarea(idtarea: int):
    """
    Eliminar una tarea.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Tareas WHERE idtarea = ?", (idtarea,))
            conn.commit()
            return {"mensaje": "Tarea eliminada exitosamente"}
    except Exception as e:
        print(e)
        return []


"""CREATE TABLE Entregas (
  identrega INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha_entrega DATE,
  nombre_archivo VARCHAR,
  tipo_archivo VARCHAR,
  idtarea INTEGER REFERENCES Tareas(idtarea),
  idestudiante INTEGER REFERENCES Estudiantes(idestudiante)
);"""

directorio_pdf = "pdf"


@app.get("/pdf/{nombre_archivo}")
def get_pdf(nombre_archivo: str):
    # Ruta completa del archivo
    ruta_archivo = Path(directorio_pdf) / nombre_archivo

    # Verificar si el archivo existe
    if ruta_archivo.exists():
        # Retornar el archivo como respuesta
        return FileResponse(
            ruta_archivo, media_type="application/pdf", filename=nombre_archivo
        )
    else:
        return {"mensaje": "Archivo no encontrado"}


# get
@app.get("/entregas")
def get_entregas():
    """
    Obtener todas las entregas.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Entregas")
            entregas = cursor.fetchall()
            if entregas is None:
                return []
            else:
                return entregas
    except Exception as e:
        print(e)
        return []


from datetime import datetime

# ...


# post
@app.post("/entregas")
def post_entrega(idtarea: int, idestudiante: int, archivo: UploadFile = File(...)):
    """
    Crear una nueva entrega y registrar un cambio de estado.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            # Establecer la fecha de entrega como la fecha actual
            fecha_entrega = datetime.now().strftime("%Y-%m-%d")

            # Obtener el tipo de archivo real del objeto UploadFile
            tipo_archivo = archivo.content_type

            # Insertar la entrega en la base de datos
            cursor.execute(
                "INSERT INTO Entregas (fecha_entrega, nombre_archivo, tipo_archivo, idtarea, idestudiante) VALUES (?, ?, ?, ?, ?)",
                (
                    fecha_entrega,
                    archivo.filename,
                    tipo_archivo,
                    idtarea,
                    idestudiante,
                ),
            )

            # Obtener el ID de la última fila insertada
            id_entrega = cursor.lastrowid

            # Crear el directorio si no existe
            directorio_archivos = "pdf"
            Path(directorio_archivos).mkdir(parents=True, exist_ok=True)

            # Guardar el archivo en el sistema de archivos
            ruta_archivo = Path(directorio_archivos) / archivo.filename

            # Verificar si el archivo ya existe
            if ruta_archivo.exists():
                # Si existe, agregar un timestamp al nombre del archivo
                nombre_archivo = (
                    archivo.filename.split(".")[0]
                    + "_"
                    + datetime.now().strftime("%Y%m%d%H%M%S")
                    + "."
                    + archivo.filename.split(".")[1]
                )
                ruta_archivo = Path(directorio_archivos) / nombre_archivo
            else:
                nombre_archivo = archivo.filename

            # Guardar el archivo en el sistema de archivos
            with ruta_archivo.open("wb") as file:
                file.write(archivo.file.read())

            # Actualizar el nombre del archivo en la base de datos
            cursor.execute(
                "UPDATE Entregas SET nombre_archivo = ? WHERE identrega = ?",
                (nombre_archivo, id_entrega),
            )

            # Registrar un cambio de estado
            nuevo_estado = "entregado"  # Puedes cambiar esto según tus necesidades
            fecha_cambio = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "INSERT INTO CambiosEstado (idtarea, nuevo_estado, fecha_cambio) VALUES (?, ?, ?)",
                (idtarea, nuevo_estado, fecha_cambio),
            )

            conn.commit()

            return {"mensaje": "Entrega creada exitosamente"}
    except Exception as e:
        print(e)
        return {"mensaje": "Error al procesar la entrega"}


# @app.post("/entregas")
# def post_entrega(idtarea: int, idestudiante: int, archivo: UploadFile = File(...)):
#     """
#     Crear una nueva entrega.
#     """
#     try:
#         with DatabaseConnection() as conn:
#             cursor = conn.cursor()

#             # Establecer la fecha de entrega como la fecha actual
#             fecha_entrega = datetime.now().strftime("%Y-%m-%d")

#             # Obtener el tipo de archivo real del objeto UploadFile
#             tipo_archivo = archivo.content_type

#             # Insertar la entrega en la base de datos
#             cursor.execute(
#                 "INSERT INTO Entregas (fecha_entrega, tipo_archivo, idtarea, idestudiante) VALUES (?, ?, ?, ?)",
#                 (
#                     fecha_entrega,
#                     tipo_archivo,
#                     idtarea,
#                     idestudiante,
#                 ),
#             )

#             # Obtener el ID de la última fila insertada
#             id_entrega = cursor.lastrowid

#             # Crear el directorio si no existe
#             directorio_archivos = "pdf"
#             Path(directorio_archivos).mkdir(parents=True, exist_ok=True)

#             # Obtener el timestamp actual
#             timestamp_actual = datetime.now().strftime("%Y%m%d%H%M%S")

#             # Modificar el nombre del archivo para evitar conflictos
#             nombre_archivo = f"{archivo.filename.split('.')[0]}_{timestamp_actual}_{idestudiante}.{archivo.filename.split('.')[1]}"

#             # Guardar el archivo en el sistema de archivos
#             ruta_archivo = Path(directorio_archivos) / nombre_archivo
#             with ruta_archivo.open("wb") as file:
#                 file.write(archivo.file.read())

#             # Actualizar el nombre del archivo en la base de datos
#             cursor.execute(
#                 "UPDATE Entregas SET nombre_archivo = ? WHERE identrega = ?",
#                 (nombre_archivo, id_entrega),
#             )

#             conn.commit()

#             return {"mensaje": "Entrega creada exitosamente"}
#     except Exception as e:
#         print(e)
#         return {"mensaje": "Error al procesar la entrega"}


# # put
# @app.put("/entregas/{identrega}")
# def put_entrega(
#     identrega: int, idtarea: int, idestudiante: int, archivo: UploadFile = File(...)
# ):
#     """
#     Actualizar una entrega.
#     """
#     try:
#         with DatabaseConnection() as conn:
#             cursor = conn.cursor()

#             # Establecer la fecha de entrega como la fecha actual
#             fecha_entrega = datetime.now().strftime("%Y-%m-%d")

#             # Obtener el tipo de archivo real del objeto UploadFile
#             tipo_archivo = archivo.content_type

#             # Actualizar la entrega en la base de datos
#             cursor.execute(
#                 "UPDATE Entregas SET fecha_entrega = ?, tipo_archivo = ?, idtarea = ?, idestudiante = ? WHERE identrega = ?",
#                 (
#                     fecha_entrega,
#                     tipo_archivo,
#                     idtarea,
#                     idestudiante,
#                     identrega,
#                 ),
#             )

#             # Crear el directorio si no existe
#             directorio_archivos = "pdf"
#             Path(directorio_archivos).mkdir(parents=True, exist_ok=True)

#             # Obtener el timestamp actual
#             timestamp_actual = datetime.now().strftime("%Y%m%d%H%M%S")

#             # Modificar el nombre del archivo para evitar conflictos
#             nombre_archivo = f"{archivo.filename.split('.')[0]}_{timestamp_actual}_{idestudiante}.{archivo.filename.split('.')[1]}"

#             # Guardar el archivo en el sistema de archivos
#             ruta_archivo = Path(directorio_archivos) / nombre_archivo
#             with ruta_archivo.open("wb") as file:
#                 file.write(archivo.file.read())

#             # Actualizar el nombre del archivo en la base de datos
#             cursor.execute(
#                 "UPDATE Entregas SET nombre_archivo = ? WHERE identrega = ?",
#                 (nombre_archivo, identrega),
#             )

#             conn.commit()

#             return {"mensaje": "Entrega actualizada exitosamente"}
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Error al procesar la entrega")


# put
# put
@app.put("/entregas/{identrega}")
def put_entrega(identrega: int, archivo: UploadFile = File(...)):
    """
    Actualizar una entrega y registrar un cambio de estado.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            # Establecer la fecha de entrega como la fecha actual
            fecha_entrega = datetime.now().strftime("%Y-%m-%d")

            # Obtener el tipo de archivo real del objeto UploadFile
            tipo_archivo = archivo.content_type

            # Actualizar la entrega en la base de datos
            cursor.execute(
                "UPDATE Entregas SET fecha_entrega = ?, nombre_archivo = ?, tipo_archivo = ? WHERE identrega = ?",
                (
                    fecha_entrega,
                    archivo.filename,
                    tipo_archivo,
                    identrega,
                ),
            )

            # Obtener el idtarea asociado a la entrega
            cursor.execute(
                "SELECT idtarea FROM Entregas WHERE identrega = ?", (identrega,)
            )
            idtarea = cursor.fetchone()["idtarea"]

            # Crear el directorio si no existe
            directorio_archivos = "pdf"
            Path(directorio_archivos).mkdir(parents=True, exist_ok=True)

            # Guardar el archivo en el sistema de archivos
            ruta_archivo = Path(directorio_archivos) / archivo.filename

            # Verificar si el archivo ya existe
            if ruta_archivo.exists():
                # Si existe, agregar un timestamp al nombre del archivo
                nombre_archivo = (
                    archivo.filename.split(".")[0]
                    + "_"
                    + datetime.now().strftime("%Y%m%d%H%M%S")
                    + "."
                    + archivo.filename.split(".")[1]
                )
                ruta_archivo = Path(directorio_archivos) / nombre_archivo
            else:
                nombre_archivo = archivo.filename

            # Guardar el archivo en el sistema de archivos
            with ruta_archivo.open("wb") as file:
                file.write(archivo.file.read())

            # Actualizar el nombre del archivo en la base de datos
            cursor.execute(
                "UPDATE Entregas SET nombre_archivo = ? WHERE identrega = ?",
                (nombre_archivo, identrega),
            )

            # Registrar un cambio de estado
            nuevo_estado = "actualizado"  # Puedes cambiar esto según tus necesidades
            fecha_cambio = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "INSERT INTO CambiosEstado (idtarea, nuevo_estado, fecha_cambio) VALUES (?, ?, ?)",
                (idtarea, nuevo_estado, fecha_cambio),
            )

            conn.commit()

            return {"mensaje": "Entrega actualizada exitosamente"}
    except Exception as e:
        print(e)
        return {"mensaje": "Error al procesar la entrega"}


# delete
@app.delete("/entregas/{identrega}")
def delete_entrega(identrega: int):
    """
    Eliminar una entrega y registrar un cambio de estado.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            # Obtener la información de la entrega antes de eliminarla
            cursor.execute("SELECT * FROM Entregas WHERE identrega = ?", (identrega,))
            entrega = cursor.fetchone()

            if entrega:
                # Eliminar el archivo asociado si existe
                directorio_archivos = "pdf"
                ruta_archivo = Path(directorio_archivos) / entrega["nombre_archivo"]
                if ruta_archivo.exists():
                    ruta_archivo.unlink()

                # Eliminar la entrega de la base de datos
                cursor.execute("DELETE FROM Entregas WHERE identrega = ?", (identrega,))

                # Registrar un cambio de estado
                nuevo_estado = "eliminado"  # Puedes cambiar esto según tus necesidades
                fecha_cambio = datetime.now().strftime("%Y-%m-%d")
                cursor.execute(
                    "INSERT INTO CambiosEstado (idtarea, nuevo_estado, fecha_cambio) VALUES (?, ?, ?)",
                    (entrega["idtarea"], nuevo_estado, fecha_cambio),
                )

                conn.commit()

                return {"mensaje": "Entrega eliminada exitosamente"}

            else:
                return {"mensaje": "Entrega no encontrada"}

    except Exception as e:
        print(e)
        return {"mensaje": "Error al procesar la eliminación de la entrega"}


@app.get("/entregas/descargar/{identrega}")
def get_entrega_archivo(identrega: int):
    """
    Obtener el enlace al archivo de una entrega.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            # Obtener el nombre del archivo asociado a la entrega
            cursor.execute(
                "SELECT nombre_archivo FROM Entregas WHERE identrega = ?", (identrega,)
            )
            result = cursor.fetchone()

            if result:
                nombre_archivo = result[0]

                # Construir la ruta completa del archivo
                directorio_archivos = "pdf"
                ruta_archivo = Path(directorio_archivos) / nombre_archivo

                # Verificar si el archivo existe
                if ruta_archivo.exists():
                    # Retornar el enlace al archivo como respuesta
                    return FileResponse(
                        ruta_archivo,
                        media_type="application/pdf",
                        filename=nombre_archivo,
                    )
                else:
                    raise HTTPException(status_code=404, detail="Archivo no encontrado")
            else:
                raise HTTPException(status_code=404, detail="Entrega no encontrada")
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Error al procesar la solicitud del archivo de la entrega",
        )


@app.get("/entregas/ver/{identrega}")
def ver_entrega_pdf(identrega: int):
    """
    Ver el PDF de una entrega en el navegador.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            # Obtener el nombre del archivo asociado a la entrega
            cursor.execute(
                "SELECT nombre_archivo FROM Entregas WHERE identrega = ?", (identrega,)
            )
            result = cursor.fetchone()

            if result:
                nombre_archivo = result[0]

                # Construir la ruta completa del archivo
                directorio_archivos = "pdf"
                ruta_archivo = Path(directorio_archivos) / nombre_archivo

                # Verificar si el archivo existe
                if ruta_archivo.exists():
                    # Retornar el PDF como respuesta
                    return FileResponse(ruta_archivo, media_type="application/pdf")
                else:
                    raise HTTPException(status_code=404, detail="Archivo no encontrado")
            else:
                raise HTTPException(status_code=404, detail="Entrega no encontrada")
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Error al procesar la solicitud de visualización del PDF de la entrega",
        )


"""
CREATE TABLE CambiosEstado (
  idcambio INTEGER PRIMARY KEY AUTOINCREMENT,
  idtarea INTEGER REFERENCES Tareas(idtarea),
  nuevo_estado VARCHAR,
  fecha_cambio DATE
);
"""


# metodos GET, POST, PUT, DELETE para la tabla CambiosEstado
# get
@app.get("/cambios_estado")
def get_cambios_estado():
    """
    Obtener todos los cambios de estado.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM CambiosEstado")
            cambios_estado = cursor.fetchall()
            if cambios_estado is None:
                return []
            else:
                return cambios_estado
    except Exception as e:
        print(e)
        return []


# usando una clase model para el POST
class CambioEstado(BaseModel):
    """
    Modelo para la creación de un cambio de estado.
    """

    idtarea: int
    nuevo_estado: str
    fecha_cambio: str


# post
@app.post("/cambios_estado")
def post_cambio_estado(cambio_estado: CambioEstado):
    """
    Crear un nuevo cambio de estado.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO CambiosEstado (idtarea, nuevo_estado, fecha_cambio) VALUES (?, ?, ?)",
                (
                    cambio_estado.idtarea,
                    cambio_estado.nuevo_estado,
                    cambio_estado.fecha_cambio,
                ),
            )
            conn.commit()
            return {"mensaje": "Cambio de estado creado exitosamente"}
    except Exception as e:
        print(e)
        return []


# clase model para el PUT
class CambioEstadoUpdate(BaseModel):
    """
    Modelo para la actualización de un cambio de estado.
    """

    idtarea: int
    nuevo_estado: str
    fecha_cambio: str


# put
@app.put("/cambios_estado/{idcambio}")
def put_cambio_estado(idcambio: int, cambio_estado: CambioEstadoUpdate):
    """
    Actualizar un cambio de estado.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE CambiosEstado SET idtarea = ?, nuevo_estado = ?, fecha_cambio = ? WHERE idcambio = ?",
                (
                    cambio_estado.idtarea,
                    cambio_estado.nuevo_estado,
                    cambio_estado.fecha_cambio,
                    idcambio,
                ),
            )
            conn.commit()
            return {"mensaje": "Cambio de estado actualizado exitosamente"}
    except Exception as e:
        print(e)
        return []


# delete
@app.delete("/cambios_estado/{idcambio}")
def delete_cambio_estado(idcambio: int):
    """
    Eliminar un cambio de estado.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM CambiosEstado WHERE idcambio = ?", (idcambio,))
            conn.commit()
            return {"mensaje": "Cambio de estado eliminado exitosamente"}
    except Exception as e:
        print(e)
        return []


# metodo get para obtener todas las tareas de un estudiante por id
@app.get("/tareas_estudiante/{idestudiante}")
def get_tareas_estudiante(idestudiante: int):
    """
    Obtener todas las tareas de un estudiante.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Tareas WHERE idestudiante = ?", (idestudiante,)
            )
            tareas = cursor.fetchall()
            if tareas is None:
                return []
            else:
                return tareas
    except Exception as e:
        print(e)
        return []


# metodo get para obtener todas las tareas de un profesor por id
@app.get("/tareas_profesor/{idprofesor}")
def get_tareas_profesor(idprofesor: int):
    """
    Obtener todas las tareas de un profesor.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Tareas WHERE idclase IN (SELECT idclase FROM Clases WHERE idprofesor = ?)",
                (idprofesor,),
            )
            tareas = cursor.fetchall()
            if tareas is None:
                return []
            else:
                return tareas
    except Exception as e:
        print(e)
        return []


# metodo get para obtener todas las tareas de una clase por id
@app.get("/tareas_clase/{idclase}")
def get_tareas_clase(idclase: int):
    """
    Obtener todas las tareas de una clase.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Tareas WHERE idclase = ?", (idclase,))
            tareas = cursor.fetchall()
            if tareas is None:
                return []
            else:
                return tareas
    except Exception as e:
        print(e)
        return []


# metodo get para obtener todas las tareas de un profesor por de de clase
@app.get("/tareas_profesor_clase/{idprofesor}/{idclase}")
def get_tareas_profesor_clase(idprofesor: int, idclase: int):
    """
    Obtener todas las tareas de un profesor por id de clase.
    """
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Tareas WHERE idclase = ? AND idclase IN (SELECT idclase FROM Clases WHERE idprofesor = ?)",
                (
                    idclase,
                    idprofesor,
                ),
            )
            tareas = cursor.fetchall()
            if tareas is None:
                return []
            else:
                return tareas
    except Exception as e:
        print(e)
        return []


class TareaCreate(BaseModel):
    nombre_tarea: str
    instrucciones: str
    fecha_vencimiento: str
    idclase: int
    estado: str


# Ruta para obtener todos los estudiantes de una clase y crear una tarea común para cada uno
@app.post("/tareas/comun")
def create_common_task(tarea_create: TareaCreate):
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            # Obtener todos los estudiantes de una clase
            cursor.execute(
                "SELECT idestudiante FROM Estudiantes WHERE idclase = ?",
                (tarea_create.idclase,),
            )
            estudiantes = cursor.fetchall()

            # Insertar una tarea común para cada estudiante
            for estudiante in estudiantes:
                id_estudiante = estudiante["idestudiante"]
                cursor.execute(
                    """
                    INSERT INTO Tareas (nombre_tarea, instrucciones, fecha_vencimiento, idclase, idestudiante, estado)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tarea_create.nombre_tarea,
                        tarea_create.instrucciones,
                        tarea_create.fecha_vencimiento,
                        tarea_create.idclase,
                        id_estudiante,
                        tarea_create.estado,
                    ),
                )

            conn.commit()

            return JSONResponse(
                content={"mensaje": "Tarea común creada exitosamente"},
                status_code=status.HTTP_201_CREATED,
            )
    except Exception as e:
        print(e)
        return JSONResponse(
            content={"mensaje": "Error al crear tarea común"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
