# Importación de librerías necesarias
import pika  # Cliente para RabbitMQ
import json  # Para decodificar mensajes en formato JSON
import time  # Para manejar esperas entre intentos
import traceback  # Para imprimir errores detallados
import psycopg2  # Conector de PostgreSQL
from prometheus_client import start_http_server, Counter  # Métricas Prometheus

# MÉTRICAS PROMETHEUS

# Contador total de mensajes recibidos
messages_received_total = Counter('messages_received_total', 'Número total de mensajes recibidos')

# Contador de mensajes que fallaron al procesarse
messages_failed_total = Counter('messages_failed_total', 'Número total de mensajes fallidos')

# Contador de mensajes guardados exitosamente en la base de datos
messages_saved_total = Counter('messages_saved_total', 'Número total de mensajes guardados en la base de datos')

# Iniciar servidor de métricas en el puerto 8000 (Prometheus las podrá recolectar desde ahí)
start_http_server(8000)
print("Servidor Prometheus disponible en puerto 8000")

# FUNCIÓN CALLBACK
def callback(ch, method, properties, body):
    """
    Esta función se ejecuta cada vez que llega un nuevo mensaje desde RabbitMQ.
    """
    try:
        # Se convierte el cuerpo del mensaje desde JSON a diccionario
        data = json.loads(body)
        print("Mensaje recibido:", data)

        # Se incrementa métrica de mensajes recibidos
        messages_received_total.inc()

        # Conexión a PostgreSQL
        conn = psycopg2.connect(
            host='db',
            database='weather_logs',
            user='weather_user',
            password='weather_pass'
        )
        cur = conn.cursor()

        # Se insertar los datos en la tabla weather_logs
        cur.execute(
            """
            INSERT INTO weather_logs (station_id, temperature, humidity, timestamp)
            """,
            (data['station_id'], data['temperature'], data['humidity'], data['timestamp'])
        )
        conn.commit()
        cur.close()
        conn.close()

        # Se incrementa métrica de mensajes guardados
        messages_saved_total.inc()

        # Confirmar a RabbitMQ que el mensaje fue procesado correctamente
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        # Si ocurre un error, se mouestra el traceback completo
        print("Error procesando mensaje:")
        traceback.print_exc()

        # Se incrementa métrica de errores
        messages_failed_total.inc()

# FUNCIÓN PRINCIPAL

def main():
    """
    Función principal que configura la conexión a RabbitMQ,
    declara exchange y cola, y comienza a consumir mensajes.
    """
    print("Iniciando consumer...")

    # Intentos para conectarse a RabbitMQ (hasta 10 con espera de 5 segundos)
    for intento in range(10):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq',
                    credentials=pika.PlainCredentials('user', 'password')
                )
            )
            print("Conexión a RabbitMQ establecida")
            break
        except Exception:
            print(f"Error de conexión ({intento+1}/10)")
            time.sleep(5)
    else:
        print("No se pudo conectar a RabbitMQ")
        return  # Sale del programa si no hay conexión

    # Se configura el canal de comunicación con RabbitMQ
    channel = connection.channel()

    # Se declara el exchange "weather" como fanout y durable (sobrevive reinicios)
    channel.exchange_declare(exchange='weather', exchange_type='fanout', durable=True)

    # Se crea una cola temporal y exclusiva (solo para esta instancia)
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    # Se asocia la cola al exchange
    channel.queue_bind(exchange='weather', queue=queue_name)

    # Se indica que se empiece a consumir mensajes con la función callback
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    print("Esperando mensajes...")

    # Se inicia el consumo
    channel.start_consuming()

# EJECUCIÓN DIRECTA
if __name__ == "__main__":
    main()

