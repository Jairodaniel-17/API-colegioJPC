import sqlite3

# Conexión a la base de datos (se creará un nuevo archivo si no existe)
conn = sqlite3.connect("colegio.db")
cursor = conn.cursor()

# Definición de las tablas
# crear_tablas = """
# CREATE TABLE Usuarios (
#   idusuario INTEGER PRIMARY KEY AUTOINCREMENT,
#   dni VARCHAR,
#   contrasena VARCHAR,
#   rol VARCHAR
# );

# CREATE TABLE Estudiantes (
#   idestudiante INTEGER PRIMARY KEY AUTOINCREMENT,
#   nombre VARCHAR,
#   dni VARCHAR,
#   idclase INTEGER,
#   idusuario INTEGER REFERENCES Usuarios(idusuario)
# );

# CREATE TABLE Profesores (
#   idprofesor INTEGER PRIMARY KEY AUTOINCREMENT,
#   nombre VARCHAR,
#   dni VARCHAR,
#   correo VARCHAR,
#   idusuario INTEGER REFERENCES Usuarios(idusuario)
# );

# CREATE TABLE Tareas (
#   idtarea INTEGER PRIMARY KEY AUTOINCREMENT,
#   nombre_tarea VARCHAR,
#   instrucciones TEXT,
#   fecha_vencimiento DATE,
#   idclase INTEGER REFERENCES Clases(idclase),
#   idestudiante INTEGER REFERENCES Estudiantes(idestudiante),
#   estado VARCHAR
# );

# CREATE TABLE Entregas (
#   identrega INTEGER PRIMARY KEY AUTOINCREMENT,
#   fecha_entrega DATE,
#   archivo_adjunto BLOB,
#   nombre_archivo VARCHAR,
#   tipo_archivo VARCHAR,
#   idtarea INTEGER REFERENCES Tareas(idtarea),
#   idestudiante INTEGER REFERENCES Estudiantes(idestudiante)
# );

# CREATE TABLE Clases (
#   idclase INTEGER PRIMARY KEY AUTOINCREMENT,
#   nombre VARCHAR,
#   idprofesor INTEGER REFERENCES Profesores(idprofesor)
# );

# CREATE TABLE CambiosEstado (
#   idcambio INTEGER PRIMARY KEY AUTOINCREMENT,
#   idtarea INTEGER REFERENCES Tareas(idtarea),
#   nuevo_estado VARCHAR,
#   fecha_cambio DATE
# );
# """
# crear_tablas = """DROP TABLE IF EXISTS Entregas"""
crear_tablas = """CREATE TABLE Entregas (
  identrega INTEGER PRIMARY KEY AUTOINCREMENT,
  fecha_entrega DATE,
  nombre_archivo VARCHAR,
  tipo_archivo VARCHAR,
  idtarea INTEGER REFERENCES Tareas(idtarea),
  idestudiante INTEGER REFERENCES Estudiantes(idestudiante)
);"""

# Ejecutar las sentencias para crear las tablas
cursor.executescript(crear_tablas)

# Guardar y cerrar la conexión
conn.commit()
conn.close()
