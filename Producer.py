import pika  #Importamos la librería de RabbitMQ para enviar y recibir mensajes
import json  #Importamos la librería json para convertir los datos en formato JSON
import time  #Importamos la librería time para gestionar los tiempos de envío de los mensajes

connection = pika.BlockingConnection( #Conexión a RabbitMQ
    pika.ConnectionParameters(
        host='rabbitmq',  #El host de RabbitMQ (en este caso, se asume que está en el contenedor llamado 'rabbitmq')
        credentials=pika.PlainCredentials('user', 'password')  #Autenticación con usuario y contraseña
    )
)
channel = connection.channel()  #Se crea un canal para la comunicación
channel.exchange_declare(exchange='weather', exchange_type='fanout', durable=True)  #Declaramos un exchange de tipo 'fanout' (división de mensajes a todos los receptores)

#Inicializamos valores base para cada estación meteorológica (simulando sensores)
stations = {
    'ST001': {'temperature': 23.5, 'humidity': 67.0},  #Estación 1 con valores de temperatura y humedad
    'ST002': {'temperature': 24.0, 'humidity': 65.0},  #Estación 2 con valores de temperatura y humedad
    'ST003': {'temperature': 22.0, 'humidity': 70.0}   #Estación 3 con valores de temperatura y humedad
}

print("Productor iniciado...")  #Indicamos que el productor está listo para enviar mensajes

#se usa un bucle infinito para enviar datos de las estaciones de manera continua
while True:
    for station_id, values in stations.items():  #Iteramos sobre cada estación
        #Aumentos progresivos en la temperatura y humedad para simular variación de datos
        values['temperature'] += 0.1
        values['humidity'] += 0.2

        #Si los valores de temperatura o humedad superan ciertos límites, los reiniciamos
        if values['temperature'] > 30:  #Si la temperatura supera 30, la reiniciamos a 20
            values['temperature'] = 20.0
        if values['humidity'] > 80:  #Si la humedad supera 80, la reiniciamos a 60
            values['humidity'] = 60.0

        #Creamos el mensaje que se enviará con la información de la estación
        data = {
            'station_id': station_id,  #ID de la estación
            'temperature': round(values['temperature'], 1),  #Temperatura redondeada a un decimal
            'humidity': round(values['humidity'], 1),  #Humedad redondeada a un decimal
            'timestamp': time.time()  #Hora actual en formato de tiempo (timestamp)
        }

        #Convertimos el mensaje a formato JSON para enviarlo
        message = json.dumps(data)

        #Publicamos el mensaje en el exchange 'weather' con una propiedad de 'delivery_mode=2' para hacer el mensaje persistente
        channel.basic_publish(
            exchange='weather',  #Nombre del exchange
            routing_key='',  #La clave de enrutamiento está vacía porque es un 'fanout' exchange
            body=message,  #El cuerpo del mensaje es el JSON que hemos creado
            properties=pika.BasicProperties(delivery_mode=2)  # Hacemos el mensaje persistente para que no se pierda
        )

        print("Mensaje enviado:", data) #Mostramos en consola el mensaje enviado

    time.sleep(1) #Esperamos 1 segundo antes de enviar el siguiente conjunto de datos

