# Práctica Formativa Obligatoria 3 (PFO 3)
## Rediseño como Sistema Distribuido (Cliente-Servidor con Sockets)

**Materia:** Programación sobre Redes  
**Carrera:** Tecnicatura Superior en Desarrollo de Software (IFTS N° 29)  
**Profesor:** Alan Portillo / Germán Ríos  
**Alumno:** Guillermo Sciulli  
**Repositorio Oficial:** [https://github.com/guillote1977/ProgSRedes-PFO3](https://github.com/guillote1977/ProgSRedes-PFO3)  
**Documento de Presentación:** [PRESENTACION_ENTREGA.md](PRESENTACION_ENTREGA.md) | [PFO3_Presentacion_Sistema_Distribuido.pdf](PFO3_Presentacion_Sistema_Distribuido.pdf)

---

## 📌 1. Descripción del Proyecto

El objetivo de esta **PFO 3** es transformar un sistema monolítico o cliente-servidor básico en un **sistema distribuido escalable, tolerante a fallos y desacoplado**.

Para ello, la solución abarca dos pilares esenciales:
1. **Diseño de Arquitectura Distribuida**: Diagrama estructural que integra Clientes (móviles/web), Balanceador de Carga (Nginx/HAProxy), Servidores Workers (con Pool de Hilos), Cola de Mensajes (RabbitMQ) y Almacenamiento Distribuido (PostgreSQL y AWS S3).
2. **Implementación de Código en Python**:
   - `servidor.py`: Servidor de sockets TCP que escucha peticiones concurrentes, encola tareas y las distribuye dinámicamente mediante un **ThreadPoolExecutor** (Worker Pool).
   - `cliente.py`: Cliente interactivo de consola en Python que permite enviar tareas de procesamiento (cálculo numérico, procesamiento de texto), probar ráfagas de solicitudes concurrentes y consultar el estado y resultado de cada tarea mediante su `task_id`.

---

## 🏗️ 2. Diagrama de Arquitectura del Sistema Distribuido

El siguiente diagrama esquemático ilustra la arquitectura distribuida de 5 capas diseñada para cumplir con las consignas de la PFO 3:

![Diagrama de Arquitectura del Sistema Distribuido](diagrama_arquitectura.png)

> 💡 **Formato vectorial:** También se encuentra disponible la versión vectorial escalable en [diagrama_arquitectura.svg](diagrama_arquitectura.svg).

### 🧩 Explicación de los Componentes:

1. **Clientes (Móviles / Web)**: Dispositivos heterogéneos que inician conexiones hacia el sistema mediante sockets TCP o llamadas HTTP.
2. **Balanceador de Carga (Nginx / HAProxy)**: Recibe el tráfico del puerto de entrada público y distribuye las conexiones entrantes de forma equitativa (algoritmo Round-Robin o Least Connections) entre los nodos Workers activos, eliminando puntos únicos de fallo (SPOF).
3. **Servidores Workers (con Pool de Hilos)**: Cada instancia ejecuta `servidor.py` en Python utilizando un `ThreadPoolExecutor` para procesar tareas en paralelo de forma asíncrona, maximizando el uso de CPU y manteniendo la responsividad.
4. **Cola de Mensajes (RabbitMQ)**: Garantiza la comunicación asíncrona y el desacoplamiento entre el envío de la tarea y su ejecución. Si la carga aumenta drásticamente, los mensajes se encolan sin perder información ni degradar el servicio.
5. **Almacenamiento Distribuido**:
   - **PostgreSQL**: Base de datos relacional para el estado de las tareas, usuarios y metadatos estructurados.
   - **Amazon S3 / MinIO**: Almacenamiento de objetos masivo e inmutable para archivos pesados o adjuntos.

---

## 🚀 3. Guía de Ejecución y Pruebas del Código Python

### Prerrequisitos
El código utiliza únicamente librerías estándar de Python 3 (`socket`, `json`, `threading`, `concurrent.futures`), por lo que no requiere instalar paquetes adicionales.

```bash
python3 --version
```

---

### Pasos para Ejecutar

#### 1. Iniciar el Servidor Distribuido
Abre una terminal y ejecuta:

```bash
python3 servidor.py
```

**Salida esperada:**
```text
==================================================
[SERVIDOR DISTRIBUIDO] Escuchando en TCP 127.0.0.1:5000
[WORKER POOL] Hilos de ejecución activos: 4
==================================================
```

#### 2. Iniciar el Cliente Interactivo
Abre una **segunda terminal** en el mismo directorio y ejecuta:

```bash
python3 cliente.py
```

**Salida esperada:**
```text
[CLIENTE] Conectado exitosamente al servidor distribuido 127.0.0.1:5000

=========================================
   CLIENTE DISTRIBUIDO (SOCKET TCP)     
=========================================
1. Enviar tarea: Calcular cuadrado de un número
2. Enviar tarea: Procesar texto (longitud, palabras)
3. Consultar estado de una tarea por ID
4. Enviar ráfaga de 3 tareas concurrentes (Prueba de carga)
5. Salir
Selecciona una opción (1-5):
```

---

## 🧪 4. Ejemplo de Flujo de Prueba Exitoso

1. **Seleccionar Opción 1**:
   - Ingresa el número `12`.
   - El cliente envía la tarea vía JSON.
   - **Respuesta:** `{"status": "OK", "mensaje": "Tarea recibida y asignada a un worker", "task_id": "TASK-1793016371167"}`.

2. **Seleccionar Opción 3 (Consultar Estado)**:
   - Ingresa el ID recibido (ej. `TASK-1793016371167`).
   - **Respuesta:**
     ```json
     {
       "status": "OK",
       "task_id": "TASK-1793016371167",
       "info": {
         "estado": "COMPLETADA",
         "resultado": 144,
         "timestamp": "2026-10-26 12:06:12"
       }
     }
     ```

3. **Seleccionar Opción 4 (Prueba de Carga de 3 Tareas Simultáneas)**:
   - Demuestra la concurrencia distribuyendo 3 tareas simultáneas a los 4 hilos del Worker Pool del servidor y recuperando sus resultados.
