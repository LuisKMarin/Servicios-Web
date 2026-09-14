# Estudiantes  
- Luis Carlos Marín Mayo  
- Jorge Andrés Carvajal Sepúlveda  

# Análisis de integración de datos entre aplicaciones

Para este proyecto tuvimos que unir la información de dos proveedores distintos de datos meteorológicos. Aunque ambos hablan de lo mismo, cada uno entrega los datos a su manera, por lo que el reto principal fue dejarlos en un solo formato compatible con la API institucional.

## 1. Cómo venían los datos y qué pide la API

El Proveedor A envía un archivo JSON bastante anidado. Los datos vienen separados en bloques como `station`, `location` y `measurements`. Además, maneja la temperatura en Fahrenheit y la velocidad del viento en metros por segundo.

El Proveedor B es más directo: entrega un CSV con todo en columnas. En su caso la temperatura ya viene en Celsius y el viento en km/h, lo cual facilita un poco las cosas.

El problema es que la API institucional solo acepta una estructura fija: `ciudad, pais, latitud, longitud, temperatura_c, humedad, viento_kmh, fecha_hora y origen`.

Incluso los nombres cambian según el proveedor. Por ejemplo, lo que para uno es `city_name`, para el otro es `municipality`, pero en el fondo es la misma ciudad. Por eso creamos un integrador que se encarga de traducir y unificar todo antes de enviarlo.

## 2. Qué tuvimos que normalizar

Para el Proveedor A hicimos el mapeo completo y dos conversiones clave:

`station.city_name` se convierte en `ciudad`, `location.lat` en `latitud`, `measurements.temperature_f` en `temperatura_c`, etc.

Como venía en otras unidades, aplicamos:
- Temperatura: `°C = (°F - 32) × 5/9`
- Viento: `km/h = m/s × 3.6`

Con el Proveedor B el trabajo fue más simple, porque ya venía en las unidades correctas. Solo fue renombrar campos: `municipality` a `ciudad`, `temp_celsius` a `temperatura_c`, y así sucesivamente. Lo único extra fue convertir su fecha, que venía como `DD/MM/YYYY HH:MM`, al formato estándar ISO 8601 que pide la API.

Si un registro traía un dato faltante o un valor que no se podía convertir, lo marcamos como error de normalización y no lo enviamos.

## 3. Validación antes de enviar

Antes de hacer el POST, validamos cada registro para no enviar basura a la API. Revisamos lo básico: que ciudad y país no estén vacíos, que la latitud esté entre -90 y 90, la longitud entre -180 y 180, la humedad entre 0 y 100%, que el viento no sea negativo y que la fecha exista.

Gracias a este filtro previo procesamos 400 registros así:
- 391 se pudieron normalizar y 9 fallaron desde el inicio.
- De esos 391, 380 pasaron la validación local y 11 fueron descartados por traer valores ilógicos, como humedades de más de 100% o coordenadas fuera de rango.

Esto nos ahorró muchos rechazos innecesarios.

## 4. Cómo se hizo el envío 

Los 380 registros válidos se enviaron por POST a `/api/v1/mediciones` con los headers `Content-Type: application/json` y `X-Equipo: EQUIPO-22-APPSWEB`.

Aquí tuvimos en cuenta el tipo de error que devuelve la API: si responde con 400, 409 o 422 es un error de datos y no tiene sentido reintentarlo. Pero si responde con 500, 503 o hay un problema de conexión, lo reintentamos hasta 3 veces porque puede ser algo temporal.

También previmos que la API a veces responde con un formato inesperado, para que eso no tumbe todo el proceso.

Al final, hicimos un GET a `/api/v1/mediciones?equipo=EQUIPO-22-APPSWEB` para confirmar qué quedó realmente guardado.

## 5. Qué resultados obtuvimos
Concepto	Cantidad
Procesados	400
Normalizados	391
Errores de normalización	9
Válidos localmente	380
Rechazados localmente	11
Enviados a la API	380
Aceptados por la API	190
Rechazados por la API	190
Los 9 errores de normalización fueron por datos vacíos, letras donde debía haber números y fechas mal formateadas. Los 11 rechazos locales fueron por reglas de negocio que no se cumplieron.

Lo más interesante es que de los 380 que nosotros consideramos válidos, la API solo aceptó 190. Esto confirma que la validación local no reemplaza la validación del servidor; la API tiene sus propias reglas adicionales.

La consulta final confirmó que efectivamente quedaron 190 mediciones registradas para nuestro equipo.

*En conclusión*, el integrador cumplió su función: logramos leer dos fuentes totalmente diferentes, unificarlas, filtrar lo que no servía y dejar un control claro de todo el proceso hasta la verificación final en la API.
