from normalizacion import normalizar_proveedor_a
from validacion import validar_registro


def test_normalizacion_proveedor_a():
    registro = {
        "station": {
            "city_name": "Medellin",
            "country_code": "CO"
        },
        "location": {
            "lat": 6.25,
            "lon": -75.56
        },
        "measurements": {
            "temperature_f": 68,
            "relative_humidity": 70,
            "wind_speed_ms": 10
        },
        "observed_at": "2026-09-01T10:00:00-05:00"
    }

    resultado = normalizar_proveedor_a(registro)

    assert resultado["ciudad"] == "Medellin"
    assert resultado["pais"] == "CO"
    assert resultado["temperatura_c"] == 20
    assert resultado["viento_kmh"] == 36
    assert resultado["origen"] == "proveedor_a"


def test_conversion_temperatura_y_viento():
    registro = {
        "station": {
            "city_name": "Bogota",
            "country_code": "CO"
        },
        "location": {
            "lat": 4.71,
            "lon": -74.07
        },
        "measurements": {
            "temperature_f": 86,
            "relative_humidity": 50,
            "wind_speed_ms": 5
        },
        "observed_at": "2026-09-01T10:00:00-05:00"
    }

    resultado = normalizar_proveedor_a(registro)

    assert resultado["temperatura_c"] == 30
    assert resultado["viento_kmh"] == 18


def test_registro_valido():
    registro = {
        "ciudad": "Medellin",
        "pais": "CO",
        "latitud": 6.25,
        "longitud": -75.56,
        "temperatura_c": 20,
        "humedad": 70,
        "viento_kmh": 10,
        "fecha_hora": "2026-09-01T10:00:00",
        "origen": "proveedor_a"
    }

    errores = validar_registro(registro)

    assert errores == []


def test_registro_invalido():
    registro = {
        "ciudad": "",
        "pais": "CO",
        "latitud": 100,
        "longitud": -75.56,
        "temperatura_c": 20,
        "humedad": 120,
        "viento_kmh": -5,
        "fecha_hora": "2026-09-01T10:00:00",
        "origen": "proveedor_a"
    }

    errores = validar_registro(registro)

    assert len(errores) == 4


def test_limites_validos():
    registro = {
        "ciudad": "Medellin",
        "pais": "CO",
        "latitud": 90,
        "longitud": -180,
        "temperatura_c": 20,
        "humedad": 100,
        "viento_kmh": 0,
        "fecha_hora": "2026-09-01T10:00:00",
        "origen": "proveedor_b"
    }

    errores = validar_registro(registro)

    assert errores == []