"""Pruebas unitarias para app.py.

Aíslan la ruta Flask de la lógica de parsing real: decoder.decode_cable
se mockea en todos los casos salvo en test_integracion_codigo_real, que
sirve de humo (smoke test) end-to-end.
"""

from unittest.mock import patch

import pytest

import app as app_module
from decoder import CableDecodeError, CableInfo, Field


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def cable_info_valido():
    return CableInfo(
        original_code="H07RN-F 3G1.5",
        normalized_code="H07RN-F3G1.5",
        harmonization=Field("H", "Cable armonizado (reconocido en toda la normativa CENELEC)"),
        voltage=Field("07", "450/750 V"),
        insulation=Field("R", "Goma de etileno-propileno (EPR)"),
        sheath=Field("N", "Policloropreno (Neopreno)"),
        conductor_type=Field("F", "Cobre flexible para servicios móviles"),
        conductors_count=3,
        earth=Field("G", "Incluye conductor de protección (toma a tierra amarillo/verde)"),
        section_mm2=1.5,
    )


class TestIndexGet:
    """Comportamiento de la ruta "/" en peticiones GET."""

    def test_muestra_formulario_vacio(self, client):
        response = client.get("/")

        assert response.status_code == 200
        assert b'name="cable_code"' in response.data
        assert b"No se pudo decodificar" not in response.data

    def test_incluye_todos_los_codigos_de_ejemplo(self, client):
        response = client.get("/")

        for example in app_module.EXAMPLE_CODES:
            assert example.encode("utf-8") in response.data


class TestIndexPostExito:
    """POST con decode_cable mockeado devolviendo un resultado válido."""

    @patch("app.decode_cable")
    def test_invoca_decoder_con_el_valor_exacto_del_formulario(self, mock_decode, client, cable_info_valido):
        mock_decode.return_value = cable_info_valido

        client.post("/", data={"cable_code": "  H07RN-F 3G1.5  "})

        mock_decode.assert_called_once_with("  H07RN-F 3G1.5  ")

    @patch("app.decode_cable")
    def test_todos_los_campos_del_resultado_llegan_a_la_plantilla(self, mock_decode, client, cable_info_valido):
        mock_decode.return_value = cable_info_valido

        response = client.post("/", data={"cable_code": "H07RN-F 3G1.5"})
        body = response.data.decode("utf-8")

        assert response.status_code == 200
        assert "450/750 V" in body
        assert "Goma de etileno-propileno (EPR)" in body
        assert "Policloropreno (Neopreno)" in body
        assert "Cobre flexible para servicios móviles" in body
        assert "3" in body
        assert "1.5" in body

    @patch("app.decode_cable")
    def test_resultado_sin_cubierta_no_rompe_el_render(self, mock_decode, client, cable_info_valido):
        cable_info_valido.sheath = None
        mock_decode.return_value = cable_info_valido

        response = client.post("/", data={"cable_code": "H05V-K 4G2.5"})

        assert response.status_code == 200
        assert "Sin cubierta".encode("utf-8") in response.data


class TestIndexPostError:
    """POST con decode_cable mockeado lanzando CableDecodeError."""

    @patch("app.decode_cable")
    def test_mensaje_de_error_especifico_llega_a_la_plantilla(self, mock_decode, client):
        mock_decode.side_effect = CableDecodeError(
            "Carácter de armonización inválido: 'Z'. Debe ser 'H' o 'A'."
        )

        response = client.post("/", data={"cable_code": "Z07VV-F3G1.5"})
        body = response.data.decode("utf-8")

        assert response.status_code == 200
        assert "No se pudo decodificar el código" in body
        assert "Carácter de armonización inválido: &#39;Z&#39;" in body

    @patch("app.decode_cable")
    def test_error_no_deja_resultado_previo_en_el_contexto(self, mock_decode, client):
        mock_decode.side_effect = CableDecodeError("El código no puede estar vacío.")

        response = client.post("/", data={"cable_code": ""})

        assert b"section_mm2" not in response.data  # no hay fuga de datos internos
        assert "no puede estar vacío".encode("utf-8") in response.data

    def test_campo_cable_code_ausente_no_lanza_keyerror(self, client):
        # Sin mock: ejercita el fallback real request.form.get("cable_code", "")
        # y confirma que decode_cable("") produce un 200 con error controlado,
        # no un 500 por KeyError.
        response = client.post("/", data={})

        assert response.status_code == 200
        assert "no puede estar vacío".encode("utf-8") in response.data


class TestIndexPropagacionDeExcepciones:
    """El único except del código captura CableDecodeError, nada más."""

    @patch("app.decode_cable")
    def test_excepcion_no_contemplada_se_propaga(self, mock_decode, client):
        mock_decode.side_effect = RuntimeError("fallo inesperado no relacionado con el parsing")

        with pytest.raises(RuntimeError):
            client.post("/", data={"cable_code": "cualquier-cosa"})


class TestIntegracionSinMocks:
    """Smoke test end-to-end: app.py + decoder.py reales, sin mockear nada."""

    def test_codigo_real_valido_se_decodifica_correctamente(self, client):
        response = client.post("/", data={"cable_code": "H07RN-F 3G1.5"})
        body = response.data.decode("utf-8")

        assert response.status_code == 200
        assert "450/750 V" in body

    def test_codigo_real_invalido_muestra_error(self, client):
        response = client.post("/", data={"cable_code": "Z99XX"})

        assert response.status_code == 200
        assert "No se pudo decodificar el código".encode("utf-8") in response.data
