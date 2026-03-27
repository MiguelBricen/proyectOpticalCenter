import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "optica.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS Clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT,
            telefono TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            producto TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            descripcion TEXT NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY(cliente_id) REFERENCES Clientes(id)
        );
        CREATE TABLE IF NOT EXISTS Reservaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            producto TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            abono_total REAL NOT NULL DEFAULT 0,
            descripcion TEXT NOT NULL,
            fecha TEXT NOT NULL,
            estado TEXT DEFAULT 'Pendiente',
            FOREIGN KEY(cliente_id) REFERENCES Clientes(id)
        );
        CREATE TABLE IF NOT EXISTS Trabajadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cargo TEXT NOT NULL,
            telefono TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS Horas_trabajo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trabajador_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            horas REAL NOT NULL,
            observaciones TEXT,
            FOREIGN KEY(trabajador_id) REFERENCES Trabajadores(id)
        );
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            clave TEXT NOT NULL,
            rol TEXT DEFAULT 'Empleado'
        );
        CREATE TABLE IF NOT EXISTS Facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER,
            fecha TEXT NOT NULL,
            tipo TEXT NOT NULL,
            monto_total REAL NOT NULL,
            FOREIGN KEY(venta_id) REFERENCES Ventas(id)
        );
    ''')
    try:
        c.execute("ALTER TABLE Clientes ADD COLUMN cedula TEXT")
    except sqlite3.OperationalError:
        pass # La columna probablemente ya existe
    
    # Crear usuarios por defecto si no existen
    c.execute("SELECT COUNT(*) FROM Usuarios")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO Usuarios (usuario, clave, rol) VALUES (?, ?, ?)", ("admin", "admin.@Stefany.2024", "Administrador"))
        c.execute("INSERT INTO Usuarios (usuario, clave, rol) VALUES (?, ?, ?)", ("empleado", "Stefany.@Empleado.24", "Empleado"))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
