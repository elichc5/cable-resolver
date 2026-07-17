# ⚡ Decodificador de Cables Eléctricos CENELEC/IEC

Aplicación web que traduce designaciones alfanuméricas de cables eléctricos
(por ejemplo `H07RN-F 3G1.5`) a una ficha técnica legible: relación de
armonización, tensión nominal, materiales de aislamiento y cubierta, tipo de
conductor, número de conductores, presencia de toma a tierra y sección
transversal.

## ¿Qué problema resuelve?

Los códigos de cable bajo el estándar armonizado **CENELEC** (HD 361 S3),
compatibles con el mismo principio de **IEC**, son difíciles de leer a
simple vista para quien no los usa a diario. Esta herramienta evita tener
que consultar la norma o memorizar las tablas de códigos: se introduce el
código y la aplicación lo descompone campo a campo, señalando con precisión
qué parte del código es inválida cuando no cumple el patrón esperado.

## Características

- Parsing robusto campo a campo (no un único regex opaco): cada segmento del
  código se valida por separado, con mensajes de error específicos.
- Interfaz de una sola página, responsive, con ejemplos de códigos listos
  para probar.
- Sin dependencias de base de datos ni servicios externos.

## Requisitos previos

- **Python 3.9+**
- `pip` (incluido con Python)
- Un navegador web

## Instalación y ejecución local

1. **Clona el repositorio**

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd cable-resolver
   ```

2. **Crea y activa un entorno virtual**

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # En Windows: venv\Scripts\activate
   ```

3. **Instala las dependencias**

   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecuta la aplicación**

   ```bash
   python3 app.py
   ```

5. **Ábrela en tu navegador**

   Visita [http://127.0.0.1:5000](http://127.0.0.1:5000)

6. **Prueba un código de ejemplo**, como `H07RN-F 3G1.5`, o usa alguno de
   los chips de ejemplo que aparecen bajo el formulario.

Para detener el servidor: `Ctrl+C`, y luego `deactivate` para salir del
entorno virtual.

## Estructura del proyecto

```
cable-resolver/
├── app.py               # Aplicación Flask (rutas y controlador)
├── decoder.py            # Lógica de parsing y validación del código de cable
├── templates/
│   └── index.html        # Interfaz (formulario + resultados)
├── requirements.txt
└── .gitignore
```

## Créditos

Desarrollado por **Francisco Chaná** ([jfran9555@gmail.com](mailto:jfran9555@gmail.com))
en colaboración con **Claude** (Anthropic) como asistente de desarrollo.
