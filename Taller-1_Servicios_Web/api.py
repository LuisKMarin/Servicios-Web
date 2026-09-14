import requests


def enviar_medicion(url_base, equipo, medicion):

    url = f"{url_base}/api/v1/mediciones"

    headers = {
        "Content-Type": "application/json",
        "X-Equipo": equipo
    }

    max_intentos = 3

    for intento in range(1, max_intentos + 1):
        try:
            respuesta = requests.post(
                url,
                json=medicion,
                headers=headers,
                timeout=10
            )

            if respuesta.status_code == 201:
                try:
                    datos_respuesta = respuesta.json()
                except ValueError:
                    datos_respuesta = None

                return {
                    "estado": "aceptado",
                    "codigo_http": 201,
                    "intentos": intento,
                    "respuesta": datos_respuesta
                }

            if respuesta.status_code in [400, 409, 422]:
                try:
                    datos_respuesta = respuesta.json()
                except ValueError:
                    datos_respuesta = None

                return {
                    "estado": "rechazado_api",
                    "codigo_http": respuesta.status_code,
                    "intentos": intento,
                    "respuesta": datos_respuesta
                }

            if respuesta.status_code in [500, 503]:
                if intento < max_intentos:
                    continue

                return {
                    "estado": "error_comunicacion",
                    "codigo_http": respuesta.status_code,
                    "intentos": intento,
                    "respuesta": None
                }

            return {
                "estado": "error_comunicacion",
                "codigo_http": respuesta.status_code,
                "intentos": intento,
                "respuesta": None
            }

        except (requests.Timeout, requests.ConnectionError) as error:
            if intento < max_intentos:
                continue

            return {
                "estado": "error_comunicacion",
                "codigo_http": None,
                "intentos": intento,
                "respuesta": str(error)
            }

        except requests.RequestException as error:
            return {
                "estado": "error_comunicacion",
                "codigo_http": None,
                "intentos": intento,
                "respuesta": str(error)
            }

def consultar_mediciones(url_base, equipo):
    url = f"{url_base}/api/v1/mediciones"

    parametros = {
        "equipo": equipo
    }

    try:
        respuesta = requests.get(
            url,
            params=parametros,
            timeout=10
        )

        if respuesta.status_code != 200:
            return {
                "estado": "error",
                "codigo_http": respuesta.status_code,
                "respuesta": None
            }

        try:
            datos_respuesta = respuesta.json()
        except ValueError:
            return {
                "estado": "error",
                "codigo_http": 200,
                "respuesta": None
            }

        cantidad = len(datos_respuesta.get("mediciones", []))

        return {
            "estado": "exitoso",
            "codigo_http": 200,
            "cantidad": cantidad,
            "respuesta": datos_respuesta
        }

    except (requests.Timeout, requests.ConnectionError) as error:
        return {
            "estado": "error_comunicacion",
            "codigo_http": None,
            "respuesta": str(error)
        }

    except requests.RequestException as error:
        return {
            "estado": "error_comunicacion",
            "codigo_http": None,
            "respuesta": str(error)
        }

    