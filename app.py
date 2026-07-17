"""Aplicación web Flask para decodificar códigos de cables eléctricos.

Expone una única ruta ("/") que renderiza un formulario de entrada y,
al recibir un código de cable por POST, delega su interpretación a
``decoder.decode_cable`` y muestra el resultado estructurado o el
mensaje de error correspondiente bajo el estándar armonizado CENELEC
(compatible con el mismo principio de IEC).
"""

from flask import Flask, render_template, request

from decoder import EXAMPLE_CODES, CableDecodeError, decode_cable

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """Muestra el formulario de decodificación y procesa los envíos.

    En una petición GET simplemente renderiza el formulario vacío junto
    con los códigos de ejemplo. En una petición POST toma el valor del
    campo ``cable_code``, intenta decodificarlo con
    :func:`decoder.decode_cable` y prepara para la plantilla el
    resultado estructurado (``CableInfo``) o, si el código no cumple el
    patrón CENELEC, el mensaje de error específico.

    Returns:
        str: El HTML renderizado de la plantilla ``index.html``.
    """
    result = None
    error = None
    submitted_code = ""

    if request.method == "POST":
        submitted_code = request.form.get("cable_code", "")
        try:
            result = decode_cable(submitted_code)
        except CableDecodeError as exc:
            # El mensaje de CableDecodeError ya está redactado en
            # español para el usuario final; no requiere traducción.
            error = str(exc)

    return render_template(
        "index.html",
        result=result,
        error=error,
        submitted_code=submitted_code,
        example_codes=EXAMPLE_CODES,
    )


if __name__ == "__main__":
    # debug=True habilita el recargador automático y la página de
    # errores interactiva de Flask; debe desactivarse en producción.
    app.run(debug=True)
