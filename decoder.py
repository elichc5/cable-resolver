"""
Lógica de decodificación de códigos de cables eléctricos bajo el estándar
armonizado CENELEC (HD 361 S3), compatible con el mismo principio de IEC 60228 / IEC 60245-60227.

Formato general soportado:

    [H|A][VV][I][S?]-[C][N][G|X][SECCIÓN]

    Ejemplo:  H07RN-F 3G1.5
              │ │ │  │ │ │ └─ Sección transversal (mm²)
              │ │ │  │ │ └─── Con (G) o sin (X) toma a tierra
              │ │ │  │ └───── Número de conductores
              │ │ │  └─────── Tipo de conductor (U/R/K/F)
              │ │ └────────── Material de cubierta (opcional)
              │ └──────────── Material de aislamiento
              └────────────── Tensión nominal (2 dígitos)
    H ─────────────────────── Relación de armonización
"""

import re
from dataclasses import dataclass, field
from typing import Optional


class CableDecodeError(ValueError):
    """Se lanza cuando el código de cable no cumple el patrón CENELEC esperado."""


# --- Tablas de referencia -----------------------------------------------

HARMONIZATION = {
    "H": "Cable armonizado (reconocido en toda la normativa CENELEC)",
    "A": "Cable de tipo nacional reconocido",
}

VOLTAGE = {
    "01": "100/100 V",
    "03": "300/300 V",
    "05": "300/500 V",
    "07": "450/750 V",
}

INSULATION = {
    "V": "Policloruro de vinilo (PVC)",
    "R": "Goma de etileno-propileno (EPR)",
    "S": "Goma de silicona",
    "B": "Goma de acrilonitrilobutileno",
}

SHEATH = {
    "V": "Policloruro de vinilo (PVC)",
    "N": "Policloropreno (Neopreno)",
    "J": "Trenza de fibra de vidrio",
    "T": "Trenza textil",
}

CONDUCTOR_TYPE = {
    "U": "Cobre rígido unifilar (conductor sólido)",
    "R": "Cobre rígido multifilar",
    "K": "Cobre flexible para instalaciones fijas",
    "F": "Cobre flexible para servicios móviles",
}

EARTH = {
    "G": "Incluye conductor de protección (toma a tierra amarillo/verde)",
    "X": "No incluye conductor de toma a tierra",
}

_CORE_SECTION_RE = re.compile(r"^(\d{1,3})([GX])(\d+(?:\.\d+)?)$")


@dataclass
class Field:
    code: str
    label: str


@dataclass
class CableInfo:
    original_code: str
    normalized_code: str
    harmonization: Field
    voltage: Field
    insulation: Field
    conductor_type: Field
    conductors_count: int
    earth: Field
    section_mm2: float
    sheath: Optional[Field] = field(default=None)


def decode_cable(raw_code: str) -> CableInfo:
    """Parsea y valida un código de cable componente a componente.

    Lanza CableDecodeError con un mensaje específico señalando qué parte
    del código es inválida y qué se esperaba en su lugar.
    """
    if raw_code is None or not raw_code.strip():
        raise CableDecodeError("El código no puede estar vacío.")

    code = raw_code.strip().upper().replace(" ", "")
    pos = 0

    # 1. Relación de armonización
    char = code[pos] if pos < len(code) else ""
    if char not in HARMONIZATION:
        raise CableDecodeError(
            f"Carácter de armonización inválido: '{char or '(vacío)'}'. "
            "Debe ser 'H' (armonizado) o 'A' (nacional reconocido)."
        )
    harmonization = Field(char, HARMONIZATION[char])
    pos += 1

    # 2. Tensión nominal (2 dígitos)
    voltage_code = code[pos:pos + 2]
    if voltage_code not in VOLTAGE:
        raise CableDecodeError(
            f"Código de tensión nominal inválido: '{voltage_code or '(vacío)'}'. "
            "Valores permitidos: 01, 03, 05, 07."
        )
    voltage = Field(voltage_code, VOLTAGE[voltage_code])
    pos += 2

    # 3. Material de aislamiento
    char = code[pos] if pos < len(code) else ""
    if char not in INSULATION:
        raise CableDecodeError(
            f"Material de aislamiento inválido: '{char or '(vacío)'}'. "
            "Valores permitidos: V, R, S, B."
        )
    insulation = Field(char, INSULATION[char])
    pos += 1

    # 4. Material de cubierta (opcional): solo si el siguiente carácter no es '-'
    sheath = None
    if pos < len(code) and code[pos] != "-":
        char = code[pos]
        if char not in SHEATH:
            raise CableDecodeError(
                f"Material de cubierta inválido: '{char}'. "
                "Valores permitidos: V, N, J, T (u omitir si el cable no tiene cubierta)."
            )
        sheath = Field(char, SHEATH[char])
        pos += 1

    # Separador '-' obligatorio antes del tipo de conductor
    if pos >= len(code) or code[pos] != "-":
        raise CableDecodeError(
            "Falta el guion separador '-' antes del tipo de conductor (ej. H07RN-F)."
        )
    pos += 1

    # 5. Tipo de conductor
    char = code[pos] if pos < len(code) else ""
    if char not in CONDUCTOR_TYPE:
        raise CableDecodeError(
            f"Tipo de conductor inválido: '{char or '(vacío)'}'. "
            "Valores permitidos: U, R, K, F."
        )
    conductor_type = Field(char, CONDUCTOR_TYPE[char])
    pos += 1

    # 6. Número de conductores, presencia de tierra y sección (ej. 3G1.5)
    remainder = code[pos:]
    match = _CORE_SECTION_RE.match(remainder)
    if not match:
        raise CableDecodeError(
            f"Formato de conductores/sección inválido: '{remainder or '(vacío)'}'. "
            "Formato esperado: <número><G|X><sección_mm²> (ej. 3G1.5 o 2X2.5)."
        )
    count_str, earth_code, section_str = match.groups()
    earth = Field(earth_code, EARTH[earth_code])

    return CableInfo(
        original_code=raw_code.strip(),
        normalized_code=code,
        harmonization=harmonization,
        voltage=voltage,
        insulation=insulation,
        sheath=sheath,
        conductor_type=conductor_type,
        conductors_count=int(count_str),
        earth=earth,
        section_mm2=float(section_str),
    )


EXAMPLE_CODES = [
    "H05VV-F 3G1.5",
    "H07RN-F 5G2.5",
    "A05VV-U 3G1.5",
    "H05V-K 4G2.5",
    "H03VV-F2X0.75",
]
