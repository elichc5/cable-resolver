from flask import Flask, render_template, request

from decoder import EXAMPLE_CODES, CableDecodeError, decode_cable

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    submitted_code = ""

    if request.method == "POST":
        submitted_code = request.form.get("cable_code", "")
        try:
            result = decode_cable(submitted_code)
        except CableDecodeError as exc:
            error = str(exc)

    return render_template(
        "index.html",
        result=result,
        error=error,
        submitted_code=submitted_code,
        example_codes=EXAMPLE_CODES,
    )


if __name__ == "__main__":
    app.run(debug=True)
