import os
import sys
import assemblyai as aai


def obtener_clave_api() -> str:
    """
    Obtiene la clave de API desde una variable de entorno o un valor predeterminado.
    """
    return os.getenv("CLAVE_API_ASSEMBLYAI", "456664d7a27245c78350da6ebff598a5")


def listar_idiomas_disponibles() -> list[str]:
    """
    Devuelve una lista de idiomas soportados por la API de AssemblyAI.
    """
    return [
        "en (Inglés)",
        "es (Español)",
        "fr (Francés)",
        "de (Alemán)",
        "it (Italiano)",
        "pt (Portugués)",
        "nl (Holandés)",
        "ru (Ruso)",
        "zh (Chino Mandarín)",
        "ja (Japonés)",
        "ko (Coreano)",
        # Agrega más idiomas según la documentación de AssemblyAI
    ]


def seleccionar_idioma() -> str:
    """
    Permite al usuario seleccionar un idioma de la lista disponible.
    """
    idiomas = listar_idiomas_disponibles()
    print("Por favor, selecciona el idioma del audio:")
    for i, idioma in enumerate(idiomas, start=1):
        print(f"{i}. {idioma}")

    while True:
        try:
            opcion = int(input("Introduce el número del idioma: "))
            if 1 <= opcion <= len(idiomas):
                codigo_idioma = idiomas[opcion - 1].split(" ")[0]  # Extrae el código del idioma
                return codigo_idioma
            else:
                print("Por favor, selecciona un número válido.")
        except ValueError:
            print("Entrada no válida. Introduce un número.")


def procesar_argumentos(args: list[str]) -> dict:
    """
    Procesa los argumentos de la línea de comandos y devuelve un diccionario con las opciones.
    """
    opciones = {
        "listar_idiomas": False,
        "mostrar_ayuda": False,
        "forzar_cancion": False,
        "salida_cruda": False,
        "canal_dual": False,
        "etiquetas_hablantes": False,
        "sin_formato_texto": False,
        "lista_palabras_clave": [],
        "nivel_impulso": None,
        "codigo_idioma": None,
        "fuente": None,
        "detectar_idioma": False,  # Nueva opción para detección automática de idioma
    }

    i = 0
    while i < len(args):
        arg = args[i]
        if arg in {"--ayuda", "-h"}:
            opciones["mostrar_ayuda"] = True
        elif arg == "--listar-idiomas":
            opciones["listar_idiomas"] = True
        elif arg == "--forzar-cancion":
            opciones["forzar_cancion"] = True
        elif arg == "--salida-cruda":
            opciones["salida_cruda"] = True
        elif arg == "--canal-dual":
            opciones["canal_dual"] = True
        elif arg == "--etiquetas-hablantes":
            opciones["etiquetas_hablantes"] = True
        elif arg == "--sin-formato-texto":
            opciones["sin_formato_texto"] = True
        elif arg.startswith("--lista-palabras="):
            opciones["lista_palabras_clave"] = [w.strip() for w in arg.split("=", 1)[1].split(",") if w.strip()]
        elif arg == "--lista-palabras" and i + 1 < len(args):
            opciones["lista_palabras_clave"] = [w.strip() for w in args[i + 1].split(",") if w.strip()]
            i += 1
        elif arg.startswith("--nivel-impulso="):
            opciones["nivel_impulso"] = arg.split("=", 1)[1].strip()
        elif arg == "--nivel-impulso" and i + 1 < len(args):
            opciones["nivel_impulso"] = args[i + 1].strip()
            i += 1
        elif arg.startswith("--idioma="):
            opciones["codigo_idioma"] = arg.split("=", 1)[1].strip()
        elif arg == "--idioma" and i + 1 < len(args):
            opciones["codigo_idioma"] = args[i + 1].strip()
            i += 1
        elif arg == "--detectar-idioma":
            opciones["detectar_idioma"] = True
        elif opciones["fuente"] is None:
            opciones["fuente"] = arg
        i += 1

    return opciones


def validar_fuente(fuente: str) -> bool:
    """
    Valida si la fuente es un archivo local existente.
    """
    return os.path.exists(fuente)


def transcribir_audio(fuente: str, opciones: dict) -> str:
    """
    Realiza la transcripción del audio utilizando la API de AssemblyAI.
    """
    transcriptor = aai.Transcriber()
    configuracion = {}

    if opciones["codigo_idioma"]:
        configuracion["language_code"] = opciones["codigo_idioma"]
    if opciones["canal_dual"]:
        configuracion["dual_channel"] = True
    if opciones["sin_formato_texto"]:
        configuracion["format_text"] = False
    if opciones["lista_palabras_clave"]:
        configuracion["word_boost"] = opciones["lista_palabras_clave"]
    if opciones["nivel_impulso"] in {"low", "default", "high"}:
        configuracion["boost_param"] = opciones["nivel_impulso"]

    config = aai.TranscriptionConfig(**configuracion) if configuracion else None

    try:
        transcripcion = transcriptor.transcribe(fuente, config=config)
        if transcripcion.status == aai.TranscriptStatus.error:
            raise ValueError(f"Error en la transcripción: {transcripcion.error}")

        return transcripcion.text or ""
    except AttributeError as e:
        raise RuntimeError(f"Error inesperado al manejar la respuesta de la API: {e}")
    except Exception as e:
        raise RuntimeError(f"Error al transcribir el archivo: {e}")


def guardar_transcripcion(fuente: str, texto: str, tipo: str):
    """
    Guarda la transcripción en un archivo de texto junto al archivo fuente.
    """
    base, _ = os.path.splitext(fuente)
    ruta_salida = f"{base}.transcripcion.{tipo}.txt"
    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        archivo.write(texto)
    print(f"Transcripción guardada en: {ruta_salida}")


def mostrar_ayuda():
    """
    Muestra la ayuda sobre los argumentos y opciones del programa.
    """
    ayuda = """
    Uso: transcriptor.py [opciones] <archivo>

    Opciones:
      -h, --ayuda            Muestra esta ayuda.
      --listar-idiomas        Lista los idiomas disponibles.
      --forzar-cancion       Fuerza el formato de canción.
      --salida-cruda          Salida sin formato.
      --canal-dual           Activa el canal dual.
      --etiquetas-hablantes  Activa las etiquetas para hablantes.
      --sin-formato-texto    Desactiva el formato de texto.
      --lista-palabras=<palabras>  Lista de palabras clave separadas por comas.
      --nivel-impulso=<nivel>    Nivel de impulso para palabras clave.
      --idioma=<código>      Código del idioma (por defecto, se detecta automáticamente).
      --detectar-idioma      Detecta el idioma automáticamente.

    Ejemplo:
      transcriptor.py --idioma=es --forzar-cancion mi_archivo.mp3
    """
    print(ayuda)


def _classify_transcript_simple(text: str) -> str:
    """
    Clasifica el texto transcrito como "canción" o "diálogo" utilizando una heurística simple.

    - Indicadores de canción: alta repetición de palabras, líneas cortas, pocas marcas de puntuación.
    - Indicadores de diálogo: oraciones largas, puntuación como '.', '?', '!', indicaciones de hablantes.
    """
    if not text:
        return "diálogo"

    texto_minusculas = text.lower()

    # Densidad básica de puntuación
    conteo_puntuacion = sum(texto_minusculas.count(ch) for ch in ".?!")
    densidad_puntuacion = conteo_puntuacion / max(len(text), 1)

    # Puntuación de repetición: cuenta palabras que aparecen >= 4 veces
    palabras = [w for w in ''.join(ch if ch.isalnum() or ch.isspace() else ' ' for ch in texto_minusculas).split() if w]
    frecuencia = {}
    for palabra in palabras:
        frecuencia[palabra] = frecuencia.get(palabra, 0) + 1
    repeticiones = sum(1 for _, conteo in frecuencia.items() if conteo >= 4)
    proporcion_repeticion = repeticiones / max(len(frecuencia), 1)

    # Métricas de longitud de línea
    lineas = [ln.strip() for ln in text.splitlines() if ln.strip()]
    longitud_promedio_linea = sum(len(ln) for ln in lineas) / max(len(lineas), 1)

    # Decisión heurística
    puntuacion_cancion = 0.0
    if proporcion_repeticion > 0.03:
        puntuacion_cancion += 1.0
    if densidad_puntuacion < 0.005:
        puntuacion_cancion += 1.0
    if longitud_promedio_linea < 45:
        puntuacion_cancion += 1.0

    return "canción" if puntuacion_cancion >= 2.0 else "diálogo"


def _format_as_lyrics(text: str) -> str:
    """
    Da formato al texto como letras de canción, aplicando un estilo específico.

    Estrategia:
    - Divide el texto en estrofas y versos.
    - Aplica sangrías y saltos de línea para dar formato de canción.
    """
    if not text:
        return text

    # Divide en estrofas asumiendo que están separadas por dos saltos de línea
    estrofas = [estrofa.strip() for estrofa in text.split("\n\n") if estrofa.strip()]

    letras_formateadas = []
    for estrofa in estrofas:
        # Divide en versos asumiendo que están separados por un salto de línea
        versos = [verso.strip() for verso in estrofa.split("\n") if verso.strip()]
        for verso in versos:
            letras_formateadas.append(f"  {verso}")  # Sangría para el verso
        letras_formateadas.append("")  # Salto de línea entre versos

    return "\n".join(letras_formateadas).strip()


def _format_as_dialogue(text: str) -> str:
    """
    Da formato al texto como diálogo, envolviendo las líneas para que sean legibles.

    Estrategia:
    - Divide en oraciones usando puntuación.
    - Envuelve cada oración a ~80 caracteres.
    """
    if not text:
        return text

    import re
    import textwrap

    # Normaliza los espacios en blanco
    texto_normalizado = " ".join(text.split())

    # Divide en límites de oración, manteniendo los delimitadores
    partes = re.split(r"(?<=[\.\?!])\s+", texto_normalizado)

    lineas_envueltas: list[str] = []
    for parte in partes:
        if not parte:
            continue
        lineas_envueltas.extend(textwrap.wrap(parte, width=80))

    return "\n".join(lineas_envueltas)


def main() -> int:
    """
    Función principal que coordina el flujo del programa.
    """
    clave_api = obtener_clave_api()
    if not clave_api:
        print("Falta la clave de API de AssemblyAI. Configura CLAVE_API_ASSEMBLYAI.", file=sys.stderr)
        return 1

    aai.settings.api_key = clave_api

    opciones = procesar_argumentos(sys.argv[1:])

    if opciones["mostrar_ayuda"]:
        mostrar_ayuda()
        return 0

    if opciones["listar_idiomas"]:
        for idioma in listar_idiomas_disponibles():
            print(f"- {idioma}")
        return 0

    if not opciones["fuente"] or not validar_fuente(opciones["fuente"]):
        print("Fuente no válida o no encontrada.", file=sys.stderr)
        return 1

    if not opciones["codigo_idioma"] and not opciones["detectar_idioma"]:
        opciones["codigo_idioma"] = seleccionar_idioma()

    try:
        texto = transcribir_audio(opciones["fuente"], opciones)
        tipo = "cancion" if opciones["forzar_cancion"] else _classify_transcript_simple(texto)
        texto_formateado = (
            texto if opciones["salida_cruda"] else
            _format_as_lyrics(texto) if tipo == "cancion" else
            _format_as_dialogue(texto)
        )
        guardar_transcripcion(opciones["fuente"], texto_formateado, tipo)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

