import json

from archivos import leer_proveedor_a, leer_proveedor_b, guardar_json
from normalizacion import normalizar_proveedor_a, normalizar_proveedor_b
from validacion import validar_registro
from api import enviar_medicion, consultar_mediciones


URL_BASE = "https://appsweb.quantaiot.co"
EQUIPO = "EQUIPO-22-APPSWEB"


def procesar_proveedor_a(datos, normalizadas, errores_normalizacion,
                         rechazadas_localmente, trazabilidad):

    for posicion, registro in enumerate(datos["records"], start=1):

        identificador = registro.get(
            "provider_record_id",
            f"posicion-{posicion}"
        )

        try:
            normalizado = normalizar_proveedor_a(registro)
            errores = validar_registro(normalizado)

            normalizadas.append(normalizado)

            estado = "rechazado_localmente" if errores else "valido"

            trazabilidad.append({
                "id": identificador,
                "origen": "proveedor_a",
                "estado_local": estado
            })

            if errores:
                rechazadas_localmente.append({
                    "origen": "proveedor_a",
                    "id": identificador,
                    "motivos": errores
                })
            else:
                trazabilidad[-1]["medicion"] = normalizado

        except (KeyError, TypeError, ValueError) as error:

            errores_normalizacion.append({
                "origen": "proveedor_a",
                "id": identificador,
                "motivo": str(error)
            })

            trazabilidad.append({
                "id": identificador,
                "origen": "proveedor_a",
                "estado_local": "error_normalizacion",
                "motivo": str(error)
            })


def procesar_proveedor_b(datos, normalizadas, errores_normalizacion,
                         rechazadas_localmente, trazabilidad):

    for posicion, registro in enumerate(datos, start=1):

        identificador = registro.get(
            "record_code",
            f"posicion-{posicion}"
        )

        try:
            normalizado = normalizar_proveedor_b(registro)
            errores = validar_registro(normalizado)

            normalizadas.append(normalizado)

            estado = "rechazado_localmente" if errores else "valido"

            trazabilidad.append({
                "id": identificador,
                "origen": "proveedor_b",
                "estado_local": estado
            })

            if errores:
                rechazadas_localmente.append({
                    "origen": "proveedor_b",
                    "id": identificador,
                    "motivos": errores
                })
            else:
                trazabilidad[-1]["medicion"] = normalizado

        except (KeyError, TypeError, ValueError) as error:

            errores_normalizacion.append({
                "origen": "proveedor_b",
                "id": identificador,
                "motivo": str(error)
            })

            trazabilidad.append({
                "id": identificador,
                "origen": "proveedor_b",
                "estado_local": "error_normalizacion",
                "motivo": str(error)
            })


def enviar_validos(trazabilidad):

    for registro in trazabilidad:

        if registro["estado_local"] != "valido":
            continue

        resultado = enviar_medicion(
            URL_BASE,
            EQUIPO,
            registro["medicion"]
        )

        registro["resultado_api"] = {
            "estado": resultado["estado"],
            "codigo_http": resultado["codigo_http"],
            "intentos": resultado["intentos"]
        }


def crear_reporte(trazabilidad, resultado_get):

    procesados = len(trazabilidad)

    normalizados = sum(
        1 for registro in trazabilidad
        if registro["estado_local"] in [
            "valido",
            "rechazado_localmente"
        ]
    )

    errores_normalizacion = sum(
        1 for registro in trazabilidad
        if registro["estado_local"] == "error_normalizacion"
    )

    rechazados_localmente = sum(
        1 for registro in trazabilidad
        if registro["estado_local"] == "rechazado_localmente"
    )

    validos_localmente = sum(
        1 for registro in trazabilidad
        if registro["estado_local"] == "valido"
    )

    enviados = sum(
        1 for registro in trazabilidad
        if "resultado_api" in registro
    )

    aceptados_api = sum(
        1 for registro in trazabilidad
        if registro.get("resultado_api", {}).get("estado") == "aceptado"
    )

    rechazados_api = sum(
        1 for registro in trazabilidad
        if registro.get("resultado_api", {}).get("estado") == "rechazado_api"
    )

    errores_comunicacion = sum(
        1 for registro in trazabilidad
        if registro.get("resultado_api", {}).get("estado")
        == "error_comunicacion"
    )

    trazabilidad_reporte = []

    for registro in trazabilidad:

        resultado = {
            "id": registro["id"],
            "origen": registro["origen"],
            "estado_local": registro["estado_local"]
        }

        if "motivo" in registro:
            resultado["motivo"] = registro["motivo"]

        if "resultado_api" in registro:
            resultado["resultado_api"] = registro["resultado_api"]

        trazabilidad_reporte.append(resultado)

    reporte = {
        "equipo": EQUIPO,
        "resumen": {
            "procesados": procesados,
            "normalizados": normalizados,
            "errores_normalizacion": errores_normalizacion,
            "validos_localmente": validos_localmente,
            "rechazados_localmente": rechazados_localmente,
            "enviados": enviados,
            "aceptados_api": aceptados_api,
            "rechazados_api": rechazados_api,
            "errores_comunicacion": errores_comunicacion
        },
        "consulta_final": resultado_get,
        "trazabilidad": trazabilidad_reporte
    }

    guardar_json(
        "salida/reporte.json",
        reporte
    )


def mostrar_resultados(trazabilidad, resultado_get):

    enviados = sum(
        1 for registro in trazabilidad
        if "resultado_api" in registro
    )

    aceptados = sum(
        1 for registro in trazabilidad
        if registro.get("resultado_api", {}).get("estado")
        == "aceptado"
    )

    rechazados = sum(
        1 for registro in trazabilidad
        if registro.get("resultado_api", {}).get("estado")
        == "rechazado_api"
    )

    errores = sum(
        1 for registro in trazabilidad
        if registro.get("resultado_api", {}).get("estado")
        == "error_comunicacion"
    )

    print("\n=== RESULTADO ===")
    print(f"Procesados: {len(trazabilidad)}")
    print(
        "Normalizados: "
        + str(sum(
            1 for r in trazabilidad
            if r["estado_local"] in [
                "valido",
                "rechazado_localmente"
            ]
        ))
    )
    print(
        "Errores de normalización: "
        + str(sum(
            1 for r in trazabilidad
            if r["estado_local"] == "error_normalizacion"
        ))
    )
    print(
        "Rechazados localmente: "
        + str(sum(
            1 for r in trazabilidad
            if r["estado_local"] == "rechazado_localmente"
        ))
    )
    print(f"Enviados a la API: {enviados}")
    print(f"Aceptados por la API: {aceptados}")
    print(f"Rechazados por la API: {rechazados}")
    print(f"Errores de comunicación: {errores}")

    print("\n=== CONSULTA FINAL ===")
    print(f"GET HTTP: {resultado_get.get('codigo_http')}")

    if resultado_get.get("estado") == "exitoso":
        respuesta = resultado_get.get("respuesta", {})
        print(
            f"Registros registrados en la API: "
            f"{resultado_get.get('cantidad', 'No informado')}"
        )
    else:
        print("No fue posible consultar las mediciones.")


def main():

    datos_a = leer_proveedor_a()
    datos_b = leer_proveedor_b()

    normalizadas = []
    errores_normalizacion = []
    rechazadas_localmente = []
    trazabilidad = []

    procesar_proveedor_a(
        datos_a,
        normalizadas,
        errores_normalizacion,
        rechazadas_localmente,
        trazabilidad
    )

    procesar_proveedor_b(
        datos_b,
        normalizadas,
        errores_normalizacion,
        rechazadas_localmente,
        trazabilidad
    )

    guardar_json(
        "salida/normalizadas.json",
        normalizadas
    )

    print("Enviando mediciones válidas a la API...")

    enviar_validos(trazabilidad)

    print("\nConsultando mediciones registradas en la API...")

    resultado_get = consultar_mediciones(
        URL_BASE,
        EQUIPO
    )

    crear_reporte(
        trazabilidad,
        resultado_get
    )

    mostrar_resultados(
        trazabilidad,
        resultado_get
    )


if __name__ == "__main__":
    main()