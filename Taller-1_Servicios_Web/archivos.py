import json
import csv


def leer_proveedor_a():
    with open("datos/proveedor_a.json", "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def leer_proveedor_b():
    with open("datos/proveedor_b.csv", "r", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo, delimiter=";")
        return list(lector)


def guardar_json(nombre_archivo, datos):
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)