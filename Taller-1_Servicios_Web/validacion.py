def validar_registro(registro):
    errores = []

    if not registro["ciudad"] or not registro["ciudad"].strip():
        errores.append("ciudad vacía")

    if not registro["pais"] or not registro["pais"].strip():
        errores.append("pais vacío")

    if not -90 <= registro["latitud"] <= 90:
        errores.append("latitud fuera de rango")

    if not -180 <= registro["longitud"] <= 180:
        errores.append("longitud fuera de rango")

    if not 0 <= registro["humedad"] <= 100:
        errores.append("humedad fuera de rango")

    if registro["viento_kmh"] < 0:
        errores.append("viento negativo")

    if registro["origen"] not in ["proveedor_a", "proveedor_b"]:
        errores.append("origen no permitido")

    if not registro["fecha_hora"]:
        errores.append("fecha_hora vacía")

    return errores