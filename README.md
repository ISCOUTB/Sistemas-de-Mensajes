# Sistemas-de-Mensajes
Este sistema simula un flujo de datos meteorológicos usando microservicios en Docker. Incluye procesamiento de datos, almacenamiento en base de datos y monitoreo con Prometheus y Grafana.
## Contenido

* [Estructura del Proyecto](#estructura-del-proyecto)
* [Tecnologías Utilizadas](#tecnologías-utilizadas)
* [Servicios](#servicios)
* [Instalación](#instalación)
* [Prometheus](#prometheus)
* [Grafana](#grafana)
* [Dashboards](#dashboards)

## Estructura del Proyecto

```
TALLER-ARQUI/
├── consumer/               # Microservicio consumidor
│   ├── consumer.py
│   └── Dockerfile
├── producer/               # Microservicio productor
│   ├── producer.py
│   └── Dockerfile
├── db/                     # Directorio de datos/db
│   └── Dockerfile
├── dashboards/             # Dashboards de Grafana
│   └── consumer-dashboard.json
├── docker-compose.yml      # Orquestación de servicios
├── prometheus.yml          # Configuración de Prometheus
└── README.md               # Documentación del proyecto
```
## Tecnologías Utilizadas

* Python 3.13 (microservicios)
* RabbitMQ (broker de mensajes)
* PostgreSQL (base de datos)
* Prometheus (monitoring)
* Grafana (visualización)
* Docker y Docker Compose (contenedorización y orquestación)

## Servicios

* **Producer**: genera datos simulados de estaciones meteorológicas y los publica en RabbitMQ.
* **Consumer**: consume mensajes de RabbitMQ, los valida, almacena en PostgreSQL y expone métricas para Prometheus.
* **RabbitMQ**: canal de comunicación entre servicios.
* **PostgreSQL**: almacena los logs meteorológicos.
* **Prometheus**: recolecta métricas expuestas por el consumidor.
* **Grafana**: visualiza las métricas desde Prometheus.

## Instalación

1. Se tiene que clonar el repositorio.
2. Asegurese de tener Docker y Docker Compose instalados.
3. Ejecutamos:

```bash
docker-compose up --build
```

4. Acceder a:

   * Prometheus: [http://localhost:9090](http://localhost:9090)
   * Grafana: [http://localhost:3000](http://localhost:3000) (usuario/contraseña por defecto: admin / admin)
   * RabbitMQ: [http://localhost:15672](http://localhost:15672) (usuario: user, contraseña: password)

## Prometheus

Prometheus recolecta métricas desde el endpoint `/metrics` del microservicio consumidor. Las métricas implementadas incluyen:

* `messages_received_total`
* `messages_failed_total`
* `messages_saved_total`

El archivo `prometheus.yml` define la configuración de scraping:

```yaml
scrape_configs:
  - job_name: 'consumer'
    static_configs:
      - targets: ['consumer:8000']
```

## Grafana

Grafana se conecta a Prometheus como fuente de datos y permite visualizar las métricas.

Pasos para configurar:

1. Iniciar sesión en Grafana: [http://localhost:3000](http://localhost:3000)
2. Añadir data source → Prometheus → URL: `http://prometheus:9090`
3. Importar el dashboard desde `dashboards/consumer-dashboard.json`

