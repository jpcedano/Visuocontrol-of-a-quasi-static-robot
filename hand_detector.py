import cv2
import mediapipe as mp
import numpy as np
import socket

HOST = '127.0.0.1'
PORT = 65432

z=0.0

# Inicializar los módulos de MediaPipe para la detección de manos
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Función para determinar el gesto del pulgar
def detect_thumb_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    
    # Calcular la diferencia vertical entre el pulgar y la muñeca
    thumb_up = thumb_tip.y < wrist.y and thumb_ip.y < wrist.y
    thumb_down = thumb_tip.y > wrist.y and thumb_ip.y > wrist.y
    
    if thumb_up:
        return "Thumb Up"
    elif thumb_down:
        return "Thumb Down"
    else:
        return "Neutral"
    
def is_hand_closed(hand_landmarks):
    """Determina si la mano está cerrada en un puño."""
    tips_ids = [mp_hands.HandLandmark.INDEX_FINGER_TIP, 
                mp_hands.HandLandmark.MIDDLE_FINGER_TIP, 
                mp_hands.HandLandmark.RING_FINGER_TIP, 
                mp_hands.HandLandmark.PINKY_TIP]
    mcp_ids = [mp_hands.HandLandmark.INDEX_FINGER_MCP, 
               mp_hands.HandLandmark.MIDDLE_FINGER_MCP, 
               mp_hands.HandLandmark.RING_FINGER_MCP, 
               mp_hands.HandLandmark.PINKY_MCP]
    
    closed = "True"
    for tip_id, mcp_id in zip(tips_ids, mcp_ids):
        if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[mcp_id].y:
            closed = "False"
            break
    
    return closed

# Función para detectar las manos en la imagen de la cámara
def detect_hands(webcam, conn):

    global z

    # Obtener las dimensiones de las ventanas
    window_width = 1200  # Ancho deseado de las ventanas
    window_height = 800  # Alto deseado de las ventanas

    # Crear una nueva ventana para mostrar la imagen de la cámara
    cv2.namedWindow('Detección de Manos', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Detección de Manos', window_width, window_height)

    # Obtener el tamaño de la ventana después de haberla creado
    actual_window_width = cv2.getWindowImageRect('Detección de Manos')[2]
    actual_window_height = cv2.getWindowImageRect('Detección de Manos')[3]

    # Establecer el tamaño de la cámara para que coincida con el tamaño de la ventana
    webcam.set(cv2.CAP_PROP_FRAME_WIDTH, actual_window_width)
    webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, actual_window_height)

    # Iniciar el bucle para capturar frames de la cámara
    with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.2, min_tracking_confidence=0.3) as hands:
        while webcam.isOpened():
            success, image = webcam.read()
            if not success:
                print("No se pudo leer el frame de la cámara.")
                break

            image = cv2.flip(image, 1)

            # Convertir la imagen de BGR a RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Detectar las manos en la imagen
            results = hands.process(image_rgb)

            # Dibujar los landmarks de las manos
            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # Determina si es la mano izquierda o derecha
                    hand_label = results.multi_handedness[idx].classification[0].label
                    
                    if hand_label == "Right":
                        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        
                        # Añade el texto de la clasificación en la imagen
                        coords = tuple(np.multiply(
                            [hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x,
                             hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y],
                            [image.shape[1], image.shape[0]]).astype(int))
                        cv2.putText(image, hand_label, coords, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                        
                        # Detectar gesto del pulgar
                        gesture = detect_thumb_gesture(hand_landmarks)
                        cv2.putText(image, gesture, (coords[0], coords[1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                        if gesture == "Thumb Up":
                            z -= 1.0
                        elif gesture == "Thumb Down":
                            z += 1.0
                        
                    elif hand_label == "Left":
                        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        
                        # Obtener las coordenadas de la muñeca (wrist)
                        wrist_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x
                        wrist_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y

                        # Ajustar las coordenadas al tamaño de la imagen
                        image_height, image_width, _ = image.shape
                        wrist_x = wrist_x * image_width
                        wrist_y = wrist_y * image_height

                        # Dividir la imagen en cuatro cuadrantes
                        half_width = image_width / 2
                        half_height = image_height / 2

                        if wrist_x < half_width:
                            wrist_x = wrist_x - half_width
                        else:
                            wrist_x = wrist_x - half_width

                        if wrist_y < half_height:
                            wrist_y = half_height - wrist_y
                        else:
                            wrist_y = half_height - wrist_y

                        is_closed = is_hand_closed(hand_landmarks)

                        # Enviar las coordenadas de la muñeca al servidor
                        Message = f'{(wrist_x / 2.5) * -1},{(wrist_y / 2.5) * -1},{z},{is_closed}'
                        print(f'Coordenadas de la muñeca: ({wrist_x}, {wrist_y}, {z}, {is_closed})')
                        conn.sendall(Message.encode())

            # Mostrar la imagen con los landmarks de las manos
            cv2.imshow('Detección de Manos', image)

            # Salir del bucle si se presiona 'q'
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

    # Liberar la cámara y cerrar las ventanas
    webcam.release()
    cv2.destroyAllWindows()

def main():
    # Crear un socket TCP/IP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORT))  # Enlazar el socket al puerto
        servidor.listen()  # Escuchar las conexiones entrantes
        print(f"Servidor TCP iniciado. Esperando conexiones en {HOST}:{PORT}")  # Mostrar mensaje de inicio

        conn, addr = servidor.accept()  # Aceptar la conexión entrante
        with conn:
            print(f"Conexión establecida desde {addr}")
            # Inicializar la cámara
            webcam = cv2.VideoCapture(0)
            detect_hands(webcam, conn)

if __name__ == "__main__":
    main()