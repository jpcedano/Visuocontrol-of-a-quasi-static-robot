import socket

HOST = '127.0.0.1'  # Dirección IP del servidor
PORT = 65432        # Puerto en el que el servidor está escuchando

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
        cliente.connect((HOST, PORT))
        print(f"Conectado al servidor en {HOST}:{PORT}")

        while True:
            # Recibir datos del servidor

            data = cliente.recv(1024).decode()

            # Verificar si no hay más datos
            if not data:
                continue

            # Dividir los datos en coordenadas x,y,z
            coord_x, coord_y, coord_z, mano_cerrada = data.split(',')
            print(f"Coordenadas recibidas del servidor: ({coord_x}, {coord_y}, {coord_z},{mano_cerrada})")

if __name__ == "__main__":
    main()
