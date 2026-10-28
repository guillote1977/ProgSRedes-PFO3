import socket
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

# Configuración del Servidor y Pool de Workers
HOST = '127.0.0.1'
PORT = 5000
WORKER_POOL_SIZE = 4

# Almacenamiento thread-safe de estado y resultados de tareas
results_store = {}
results_lock = threading.Lock()

def process_worker_task(task_id, task_type, payload):
    """
    Función ejecutor por los workers del ThreadPool.
    Simula el trabajo distribuido (cálculo/procesamiento).
    """
    print(f"[WORKER] Procesando tarea {task_id} de tipo '{task_type}'...")
    
    # Simulación de carga de trabajo / I-O o cómputo
    time.sleep(1.5)
    
    if task_type == 'calcular_cuadrado':
        numero = payload.get('numero', 0)
        resultado = numero ** 2
    elif task_type == 'procesar_texto':
        texto = payload.get('texto', '')
        resultado = {
            'longitud': len(texto),
            'mayusculas': texto.upper(),
            'palabras': len(texto.split())
        }
    else:
        resultado = f"Tarea '{task_type}' ejecutada con éxito sobre payload: {payload}"

    # Guardar resultado en almacenamiento persistente / memoria
    with results_lock:
        results_store[task_id] = {
            'estado': 'COMPLETADA',
            'resultado': resultado,
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
    print(f"[WORKER] Tarea {task_id} completada exitosamente.")
    return resultado

def handle_client(conn, addr, executor):
    """
    Maneja la conexión socket de un cliente individual.
    """
    print(f"[SERVIDOR] Cliente conectado desde {addr}")
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            
            try:
                mensaje = json.loads(data.decode('utf-8'))
                comando = mensaje.get('comando')

                if comando == 'ENVIAR_TAREA':
                    task_id = f"TASK-{int(time.time() * 1000)}"
                    task_type = mensaje.get('tipo', 'generica')
                    payload = mensaje.get('payload', {})

                    # Registrar estado INICIADA
                    with results_lock:
                        results_store[task_id] = {
                            'estado': 'EN_PROCESO',
                            'resultado': None,
                            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
                        }

                    # Enviar tarea al Pool de Workers
                    future = executor.submit(process_worker_task, task_id, task_type, payload)

                    respuesta = {
                        'status': 'OK',
                        'mensaje': 'Tarea recibida y asignada a un worker',
                        'task_id': task_id
                    }

                elif comando == 'CONSULTAR_TAREA':
                    task_id = mensaje.get('task_id')
                    with results_lock:
                        info = results_store.get(task_id, {'estado': 'NO_ENCONTRADA', 'resultado': None})
                    
                    respuesta = {
                        'status': 'OK',
                        'task_id': task_id,
                        'info': info
                    }

                elif comando == 'SALIR':
                    respuesta = {'status': 'OK', 'mensaje': 'Conexión finalizada'}
                    conn.sendall(json.dumps(respuesta).encode('utf-8'))
                    break

                else:
                    respuesta = {'status': 'ERROR', 'mensaje': 'Comando no reconocido'}

                conn.sendall(json.dumps(respuesta).encode('utf-8'))

            except json.JSONDecodeError:
                respuesta = {'status': 'ERROR', 'mensaje': 'Formato JSON inválido'}
                conn.sendall(json.dumps(respuesta).encode('utf-8'))

    except Exception as e:
        print(f"[SERVIDOR] Error con cliente {addr}: {e}")
    finally:
        conn.close()
        print(f"[SERVIDOR] Conexión cerrada con {addr}")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Permitir reusar la dirección de socket
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    print(f"==================================================")
    print(f"[SERVIDOR DISTRIBUIDO] Escuchando en TCP {HOST}:{PORT}")
    print(f"[WORKER POOL] Hilos de ejecución activos: {WORKER_POOL_SIZE}")
    print(f"==================================================")

    # Crear pool de workers concurrente
    with ThreadPoolExecutor(max_workers=WORKER_POOL_SIZE) as executor:
        while True:
            conn, addr = server_socket.accept()
            # Asignar manejo del socket cliente en un hilo dedicado
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, executor), daemon=True)
            client_thread.start()

if __name__ == '__main__':
    main()
