# IMPORTACIÓN DE LIBRERÍAS
import pika         # Cliente de Python para RabbitMQ
import json         # Para codificar los datos en formato JSON
import time         # Para gestionar pausas entre mensajes y obtener timestamps
import traceback    # Para imprimir detalles de errores si ocurren

# FUNCIÓN PRINCIPAL
def main():
    print("Iniciando producer...")
  
# CONEXIÓN A RABBITMQ CON REINTENTOS
    connection = None
    for intento in range(10):  # Hasta 10 intentos de conexión
        try:
            # Intentar conectar al servidor RabbitMQ
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq',  # Nombre del contenedor del broker en docker-compose
                    credentials=pika.PlainCredentials('user', 'password')  # Usuario y contraseña
                )
            )
            print("Conexión a RabbitMQ establecida")
            break  # Si la conexión fue exitosa, sale del ciclo
        except pika.exceptions.AMQPConnectionError as e:
            # Si hay un error, se imprime y esperar 5 segundos antes de reintentar
            print(f"Error de conexión ({intento + 1}/10): {e}")
            time.sleep(5)
    else:
        # Si no se logró conectar después de 10 intentos, se finaliza el programa
        print("No se pudo conectar a RabbitMQ después de varios intentos.")
        return

    # ENVÍO DE MENSAJES CONTINUO
    try:
        # Crear canal para enviar mensajes
        channel = connection.channel()

        # Declarar el exchange 'weather' (fanout = se envía a todas las colas vinculadas)
        channel.exchange_declare(exchange='weather', exchange_type='fanout', durable=True)

        # Enviar mensajes en un bucle infinito (cada 5 segundos)
        while True:
            # Crear un mensaje con datos simulados de estación meteorológica
            message = {
                "station_id": "ST001",
                "temperature": 23.5,
                "humidity": 67.2,
                "timestamp": time.time()  # Marca de tiempo actual
            }

            # Publicar el mensaje al exchange 'weather'
            channel.basic_publish(
                exchange='weather',       # Exchange al que se envía
                routing_key='',           # Sin routing_key porque es fanout
                body=json.dumps(message), # Convertir a JSON el cuerpo del mensaje
                properties=pika.BasicProperties(
                    delivery_mode=2       # delivery_mode=2 => mensaje persistente
                )
            )

            # Muestra el mensaje enviado en consola
            print("Mensaje enviado:", message)

            # Espera 5 segundos antes de enviar el siguiente
            time.sleep(5)

    except Exception as e:
        # En caso de error, se imprime detalles para la depuración
        print("Error en producer:")
        traceback.print_exc()
        time.sleep(10)


# EJECUCIÓN DEL SCRIPT PRINCIPAL

# Si el archivo se ejecuta directamente, se inicia la función main()
if __name__ == "__main__":
    main()
