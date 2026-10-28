import socket
import json
import time

HOST = '127.0.0.1'
PORT = 5000

def conectar_servidor():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    return sock

def enviar_peticion(sock, datos):
    sock.sendall(json.dumps(datos).encode('utf-8'))
    respuesta_raw = sock.recv(4096)
    return json.loads(respuesta_raw.decode('utf-8'))

def menu():
    print("\n=========================================")
    print("   CLIENTE DISTRIBUIDO (SOCKET TCP)     ")
    print("=========================================")
    print("1. Enviar tarea: Calcular cuadrado de un número")
    print("2. Enviar tarea: Procesar texto (longitud, palabras)")
    print("3. Consultar estado de una tarea por ID")
    print("4. Enviar ráfaga de 3 tareas concurrentes (Prueba de carga)")
    print("5. Salir")
    return input("Selecciona una opción (1-5): ").strip()

def main():
    try:
        sock = conectar_servidor()
        print(f"[CLIENTE] Conectado exitosamente al servidor distribuido {HOST}:{PORT}")

        tareas_registradas = []

        while True:
            opcion = menu()

            if opcion == '1':
                num = int(input("Ingresa un número entero: "))
                peticion = {
                    'comando': 'ENVIAR_TAREA',
                    'tipo': 'calcular_cuadrado',
                    'payload': {'numero': num}
                }
                res = enviar_peticion(sock, peticion)
                print(f"\n[RESPUESTA SERVIDOR]: {res}")
                if res.get('task_id'):
                    tareas_registradas.append(res['task_id'])

            elif opcion == '2':
                texto = input("Ingresa una cadena de texto: ")
                peticion = {
                    'comando': 'ENVIAR_TAREA',
                    'tipo': 'procesar_texto',
                    'payload': {'texto': texto}
                }
                res = enviar_peticion(sock, peticion)
                print(f"\n[RESPUESTA SERVIDOR]: {res}")
                if res.get('task_id'):
                    tareas_registradas.append(res['task_id'])

            elif opcion == '3':
                if not tareas_registradas:
                    entrada = input("Ingresa el ID de la tarea a consultar: ").strip()
                    task_id = entrada
                else:
                    print("\nTareas recientes:")
                    for idx, tid in enumerate(tareas_registradas, start=1):
                        print(f"  [{idx}] {tid}")
                    entrada = input(f"Ingresa el número (1-{len(tareas_registradas)}) o ID [Enter para última]: ").strip()
                    
                    if not entrada:
                        task_id = tareas_registradas[-1]
                    elif entrada.isdigit() and 1 <= int(entrada) <= len(tareas_registradas):
                        task_id = tareas_registradas[int(entrada) - 1]
                    else:
                        task_id = entrada

                print(f"\nConsultando: {task_id} ...")
                peticion = {
                    'comando': 'CONSULTAR_TAREA',
                    'task_id': task_id
                }
                res = enviar_peticion(sock, peticion)
                print(f"\n[ESTADO TAREA]: {json.dumps(res, indent=2, ensure_ascii=False)}")

            elif opcion == '4':
                print("\n[CLIENTE] Enviando 3 tareas simultáneas a la cola de workers...")
                for i in range(1, 4):
                    peticion = {
                        'comando': 'ENVIAR_TAREA',
                        'tipo': 'calcular_cuadrado',
                        'payload': {'numero': i * 10}
                    }
                    res = enviar_peticion(sock, peticion)
                    print(f" -> Tarea {i} enviada: Task ID {res.get('task_id')}")
                    if res.get('task_id'):
                        tareas_registradas.append(res['task_id'])
                
                print("\nEsperando 2 segundos para que los workers completen el procesamiento...")
                time.sleep(2)

                print("\nConsultando estado de las 3 tareas:")
                for tid in tareas_registradas[-3:]:
                    peticion = {'comando': 'CONSULTAR_TAREA', 'task_id': tid}
                    res = enviar_peticion(sock, peticion)
                    print(f" -> {tid}: {res['info']['estado']} | Resultado: {res['info']['resultado']}")

            elif opcion == '5':
                peticion = {'comando': 'SALIR'}
                res = enviar_peticion(sock, peticion)
                print(f"\n[CLIENTE]: {res.get('mensaje')}")
                sock.close()
                break

            else:
                print("Opción inválida. Intenta nuevamente.")

    except ConnectionRefusedError:
        print(f"[ERROR] No se pudo conectar al servidor en {HOST}:{PORT}. Asegúrate de ejecutar primero 'python servidor.py'.")
    except Exception as e:
        print(f"[ERROR CLIENTE]: {e}")

if __name__ == '__main__':
    main()
