import queue
import os


class Proceso:
    def __init__(self, id, burst_time, arrival_time, queue, priority):
        self.id = id
        self.burst_time = burst_time
        self.arrival_time = arrival_time
        self.queue = queue
        self.priority = priority
        self.waiting_time = 0
        self.completion_time = 0
        self.turnaround_time = 0
        self.response_time = None  # None indica que aún no ha sido calculado
        self.tiempo_restante = burst_time  # Inicialmente es igual a burst_time

    
class Cola:

    def __init__(self, politica, quantum=None):
        self.procesos = queue.Queue()  # Cola de procesos
        self.politica = politica       # Política de planificación (RR, SJF, FCFS, etc.)
        self.quantum = quantum         # Quantum para Round Robin
        self.proceso_actual = None

    def agregar_proceso(self, proceso):
        self.procesos.put(proceso)

    def ejecutar_proceso(self, tiempo_actual):
        if self.politica == 'RR':
            return self.ejecutar_RR(tiempo_actual)
        elif self.politica == 'SJF':
            return self.ejecutar_SJF(tiempo_actual)
        elif self.politica == 'FCFS':
            return self.ejecutar_FCFS(tiempo_actual)
        elif self.politica == 'STCF':
            return self.ejecutar_STCF(tiempo_actual)
        else:
            raise ValueError("Política no reconocida")

    def ejecutar_RR(self, tiempo_actual):
        if not self.procesos.empty():
          proceso = self.procesos.get()
          
         # Verificar si el proceso ha llegado
          if proceso.arrival_time > tiempo_actual:
             # Si el proceso aún no ha llegado, devolverlo a la cola y pasar al siguiente
             self.procesos.put(proceso)
             return None, 0  # No ejecutar este proceso, pasar al siguiente turno

          # Actualiza el tiempo de respuesta (solo la primera vez que es ejecutado)
          if proceso.response_time is None:
             proceso.response_time = tiempo_actual - proceso.arrival_time
             

          # Si es el único proceso en la cola, ejecútalo completamente
          if self.procesos.empty():
             # Ejecutar el proceso hasta que termine
             tiempo_ejecucion = proceso.tiempo_restante
             proceso.tiempo_restante = 0
          else:
             # Ejecutar por el quantum o el tiempo restante, lo que sea menor
             tiempo_ejecucion = min(self.quantum, proceso.tiempo_restante)
             proceso.tiempo_restante -= tiempo_ejecucion

      

          if proceso.tiempo_restante == 0:  # Proceso completado
             #se actualizan los datos
             proceso.completion_time = tiempo_actual + tiempo_ejecucion
             proceso.turnaround_time = proceso.completion_time - proceso.arrival_time
             proceso.waiting_time = proceso.turnaround_time-proceso.burst_time          
          else:
             self.procesos.put(proceso)  # Volver a la cola si no ha terminado

          return proceso, tiempo_ejecucion
        return None, 0

    def ejecutar_SJF(self, tiempo_actual):
      if not self.procesos.empty():
         # Obtener todos los procesos de la cola
         procesos_list = []
         procesos_no_llegados = []  # Lista para procesos que no han llegado

         # Separar procesos que han llegado de los que no
         while not self.procesos.empty():
             proceso = self.procesos.get()
             if proceso.arrival_time <= tiempo_actual:
                 procesos_list.append(proceso)  # Proceso ha llegado
             else:
                 procesos_no_llegados.append(proceso)  # Proceso no ha llegado

         # Si no hay procesos listos, volver a agregar los que no han llegado
         if not procesos_list:
             for p in procesos_no_llegados:
                 self.procesos.put(p)  # Reagregar a la cola
             # Volver a agregar los procesos listos también
             for p in procesos_list:
                 self.procesos.put(p)
             return None, 0

         # Ordenar los procesos listos por tiempo restante (SJF)
         procesos_list.sort(key=lambda p: p.tiempo_restante)
 
         # Ejecutar el proceso con el menor tiempo restante
         proceso = procesos_list.pop(0)

         # Actualiza el tiempo de respuesta
         if proceso.response_time is None:
            proceso.response_time = tiempo_actual - proceso.arrival_time

         tiempo_ejecucion = proceso.tiempo_restante
         proceso.tiempo_restante -= tiempo_ejecucion

         proceso.waiting_time += tiempo_actual - proceso.arrival_time
         proceso.completion_time = tiempo_actual + tiempo_ejecucion
         proceso.turnaround_time = proceso.completion_time - proceso.arrival_time

         # Volver a agregar todos los procesos a la cola
         for p in procesos_no_llegados:
             self.procesos.put(p)  # Procesos que no han llegado
         for p in procesos_list:
             self.procesos.put(p)  # Procesos que han llegado

         return proceso, tiempo_ejecucion

      return None, 0

    def ejecutar_FCFS(self, tiempo_actual):
        if not self.procesos.empty():
            # Obtener todos los procesos de la cola
            procesos_list = []
            while not self.procesos.empty():
                procesos_list.append(self.procesos.get())
            # Ordenar por tiempo de llegada (FCFS)
            procesos_list.sort(key=lambda p:  p.arrival_time)

            # Ejecutar el proceso que llegó primero
            proceso = procesos_list.pop(0)

            # Actualiza el tiempo de respuesta
            if proceso.response_time is None:
                proceso.response_time = tiempo_actual - proceso.arrival_time

            tiempo_ejecucion = proceso.tiempo_restante
            proceso.tiempo_restante -= tiempo_ejecucion

            proceso.waiting_time += tiempo_actual - proceso.arrival_time
            proceso.completion_time = tiempo_actual + tiempo_ejecucion
            proceso.turnaround_time = proceso.completion_time - proceso.arrival_time

            for p in procesos_list:
             self.procesos.put(p) 

            return proceso, tiempo_ejecucion

        return None, 0

    def ejecutar_STCF(self, tiempo_actual):
        if not self.procesos.empty():
            procesos_list = []
            procesos_no_llegados = []
            #se separan los  procesos que ya estan en cola de los que no
            while not self.procesos.empty():
                proceso = self.procesos.get()
                if proceso.arrival_time <= tiempo_actual:
                    procesos_list.append(proceso)
                else:
                    procesos_no_llegados.append(proceso)
            #se regresan los procesos que aun no llegan a la cola 
            if not procesos_list:
                for p in procesos_no_llegados:
                    self.procesos.put(p)
                return None, 0

            # Ordenar los procesos listos por tiempo restante 
            procesos_list.sort(key=lambda p: p.tiempo_restante)

            proceso = procesos_list.pop(0)

            if proceso.response_time is None:
                proceso.response_time = tiempo_actual - proceso.arrival_time

            tiempo_ejecucion = 1  # En cada ciclo ejecutamos solo una unidad de tiempo
            proceso.tiempo_restante -= tiempo_ejecucion

            if proceso.tiempo_restante == 0:
                proceso.completion_time = tiempo_actual + tiempo_ejecucion
                proceso.turnaround_time = proceso.completion_time - proceso.arrival_time
                proceso.waiting_time = proceso.turnaround_time-proceso.burst_time
            else:
                procesos_list.append(proceso)

            for p in procesos_no_llegados:
                self.procesos.put(p)
            for p in procesos_list:
                self.procesos.put(p)

            return proceso, tiempo_ejecucion

        return None, 0

class PlanificadorMLQ:
    def __init__(self, colas):
        self.colas = colas  # Lista de colas con diferentes políticas de planificación

    def agregar_proceso(self, proceso, indice_cola):
        if indice_cola < len(self.colas):
            self.colas[indice_cola].agregar_proceso(proceso)
        else:
            raise IndexError("Índice de cola fuera de rango")

    def ejecutar(self, tiempo_actual):
        # Ejecutar en orden de prioridad (desde la cola 1(0 por el index) a la n(n-1 por el index))
        for cola in self.colas:
            proceso, tiempo_ejecucion = cola.ejecutar_proceso(tiempo_actual)
            if proceso:
                print(f'Ejecutando proceso {proceso.id} durante {tiempo_ejecucion} unidades de tiempo')
                return proceso, tiempo_ejecucion
        print("No hay procesos listos para ejecutar.")
        return None, 0

def leer_txt(ruta_archivo):
    procesos = []
    with open(ruta_archivo, 'r') as archivo:
        for linea in archivo:
            # Ignoramos las líneas que empiezan con '#'
            if linea.startswith("#") or not linea.strip():
                continue
            # Dividimos la línea en partes separadas por ';'
            partes = linea.strip().split(";")
            id_proceso = partes[0]
            burst_time = int(partes[1])
            arrival_time = int(partes[2])
            queue = int(partes[3])
            priority = int(partes[4])
            # Creamos una instancia de Proceso y la añadimos a la lista de procesos
            proceso = Proceso(id_proceso, burst_time, arrival_time, queue, priority)
            procesos.append(proceso)
    return procesos

def guardar_procesos_en_txt(nombre_archivo, procesos):
    # Si el archivo ya existe, cambiar su nombre agregando un sufijo numérico.
    base, extension = os.path.splitext(nombre_archivo)
    contador = 1
    while os.path.exists(nombre_archivo):
        nombre_archivo = f"{base}_{contador}{extension}"
        contador += 1

    total_wt = total_ct = total_rt = total_tat = 0
    num_procesos = len(procesos)
    
    with open(nombre_archivo, 'w') as archivo:
        # Escribir encabezado
        archivo.write(f"# archivo: {nombre_archivo}\n")
        archivo.write("# etiqueta; BT; AT; Q; Pr; WT; CT; RT; TAT\n")
        
        # Escribir cada proceso
        for p in procesos:
            archivo.write(f"{p.id};{p.burst_time};{p.arrival_time};{p.queue};{p.priority};"
                          f"{p.waiting_time};{p.completion_time};{p.response_time};{p.turnaround_time}\n")
            
            # Sumar tiempos para promedios
            total_wt += p.waiting_time
            total_ct += p.completion_time
            total_rt += p.response_time if p.response_time is not None else 0
            total_tat += p.turnaround_time
        
        # Calcular promedios
        avg_wt = total_wt / num_procesos if num_procesos > 0 else 0
        avg_ct = total_ct / num_procesos if num_procesos > 0 else 0
        avg_rt = total_rt / num_procesos if num_procesos > 0 else 0
        avg_tat = total_tat / num_procesos if num_procesos > 0 else 0
        
        # Escribir los promedios al final del archivo
        archivo.write(f"WT={avg_wt:.1f}; CT={avg_ct:.1f}; RT={avg_rt:.1f}; TAT={avg_tat:.1f};\n")
        

#colas recibidas por el planificador MLQ
#si se desea cambiar las colas editar esta lista con las colas deseadas
colas = [Cola('RR', quantum=3), Cola('RR', quantum=5), Cola('FCFS')]
planificador = PlanificadorMLQ(colas)

#lista de procesos a ejecutar por el planificador MLQ recibe la ruta donde se encuentra el archivo con las entradas si se desea cambiar las
#entradas reemplazar la ruta con un archivo con las entradas deseadas
procesos = leer_txt('C:/Users/jjp28/Desktop/parcial OS/mlq001.txt')

#seccion que añade los procesos al planificador MLQ 
for p in procesos:
  planificador.agregar_proceso(p, p.queue-1)
  
# Simulacion de la ejecución
tiempo_actual = 0
for _ in range(50):
    proceso, tiempo_ejecucion = planificador.ejecutar(tiempo_actual)
    tiempo_actual += tiempo_ejecucion

#creacion de los .txt con los datos obtenidos 
guardar_procesos_en_txt('Resultado_MLQ.txt', procesos)


#seccion para visualizar mas facilmente los datos
for proceso in procesos:
    print(f'Proceso {proceso.id}:')
    print(f'  Tiempo de respuesta: {proceso.response_time}')
    print(f'  Tiempo de espera: {proceso.waiting_time}')
    print(f'  Tiempo de finalización: {proceso.completion_time}')
    print(f'  Tiempo de turnaround: {proceso.turnaround_time}')
