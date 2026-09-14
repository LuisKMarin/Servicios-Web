from datetime import datetime


def normalizar_fecha_hora(fecha, formato=None):
    if not fecha or not fecha.strip():
        raise ValueError("fecha_hora vacía")

    fecha = fecha.strip()

    if formato == "proveedor_b":
        fecha_convertida = datetime.strptime(fecha, "%d/%m/%Y %H:%M")
    else:
        fecha_convertida = datetime.fromisoformat(fecha)

    return fecha_convertida.isoformat()


def normalizar_proveedor_a(registro):
    temperatura_c = (
        (float(registro["measurements"]["temperature_f"]) - 32) * 5 / 9
    )

    viento_kmh = float(
        registro["measurements"]["wind_speed_ms"]
    ) * 3.6

    return {
        "ciudad": registro["station"]["city_name"],
        "pais": registro["station"]["country_code"],
        "latitud": float(registro["location"]["lat"]),
        "longitud": float(registro["location"]["lon"]),
        "temperatura_c": temperatura_c,
        "humedad": float(registro["measurements"]["relative_humidity"]),
        "viento_kmh": viento_kmh,
        "fecha_hora": normalizar_fecha_hora(
            registro["observed_at"]
        ),
        "origen": "proveedor_a"
    }


def normalizar_proveedor_b(registro):
    return {
        "ciudad": registro["municipality"],
        "pais": registro["country"],
        "latitud": float(registro["latitude_deg"]),
        "longitud": float(registro["longitude_deg"]),
        "temperatura_c": float(registro["temp_celsius"]),
        "humedad": float(registro["humidity_pct"]),
        "viento_kmh": float(registro["wind_kmh"]),
        "fecha_hora": normalizar_fecha_hora(
            registro["measurement_time"],
            "proveedor_b"
        ),
        "origen": "proveedor_b"
    }