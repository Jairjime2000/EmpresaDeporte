import sqlite3
from datetime import datetime

# Conexión a la base de datos SQLite
conn = sqlite3.connect('empresa_deportes.db')
cursor = conn.cursor()

# Función para mostrar los pedidos pendientes de cobro
def mostrar_pedidos_pendientes():
    try:
        cursor.execute("""
            SELECT Pedido.ID_Pedido, Cliente.Nombre, Pedido.Fecha_Pedido, Factura.Monto
            FROM Pedido
            JOIN Cliente ON Pedido.ID_Cliente = Cliente.ID_Cliente
            JOIN Factura ON Pedido.ID_Pedido = Factura.ID_Pedido
            WHERE Factura.Estado = 'Pendiente'
        """)
        pedidos = cursor.fetchall()
        
        if pedidos:
            print("Pedidos pendientes de cobro:")
            for pedido in pedidos:
                print(f"ID Pedido: {pedido[0]}, Cliente: {pedido[1]}, Fecha: {pedido[2]}, Monto: {pedido[3]}")
        else:
            print("No hay pedidos pendientes de cobro.")
    except sqlite3.Error as e:
        print(f"Error al mostrar los pedidos pendientes: {e}")

# Función para cobrar un pedido
def cobrar_pedido(id_pedido):
    try:
        cursor.execute("""
            UPDATE Factura
            SET Estado = 'Pagado', Fecha_Cobro = ?
            WHERE ID_Pedido = ?
        """, (datetime.now().strftime('%Y-%m-%d'), id_pedido))
        conn.commit()
        print(f"Pedido {id_pedido} cobrado exitosamente.")
    except sqlite3.Error as e:
        print(f"Error al cobrar el pedido: {e}")

# Función principal para el proceso de cobro de pedidos
def proceso_cobro_pedidos():
    mostrar_pedidos_pendientes()
    
    while True:
        id_pedido = input("Ingrese el ID del pedido a cobrar (o 'salir' para terminar): ")
        
        if id_pedido.lower() == 'salir':
            break
        
        if id_pedido.isdigit():
            cobrar_pedido(int(id_pedido))
        else:
            print("ID de pedido no válido.")
        
        mostrar_pedidos_pendientes()

# Crear la tabla de Facturas si no existe y agregar columna de estado
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Factura (
        ID_Factura INTEGER PRIMARY KEY,
        ID_Pedido INTEGER,
        Monto REAL,
        Fecha_Factura TEXT,
        Estado TEXT DEFAULT 'Pendiente',
        Fecha_Cobro TEXT,
        FOREIGN KEY (ID_Pedido) REFERENCES Pedido(ID_Pedido)
    )
""")
conn.commit()

# Ejemplo de datos iniciales en Factura
facturas_ejemplo = [
    (1, 1, 259.97, '2024-06-07', 'Pendiente', None),
    (2, 2, 29.99, '2024-06-08', 'Pendiente', None)
]

cursor.executemany("""
    INSERT OR IGNORE INTO Factura (ID_Factura, ID_Pedido, Monto, Fecha_Factura, Estado, Fecha_Cobro)
    VALUES (?, ?, ?, ?, ?, ?)
""", facturas_ejemplo)
conn.commit()

# Ejecutar el proceso de cobro de pedidos
proceso_cobro_pedidos()

# Cerrar la conexión a la base de datos
conn.close()