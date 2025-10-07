import os
import sys
import csv
import assemblyai as aai


def obtener_clave_api() -> str:
    """
    Obtiene la clave e API desde una variable de entorno o un valor predeterminado.
    """
    return os.getenv("CLAVE_API_ASSEMBLYAI", "456664d7a27245c78350da6ebff598a5")


def listar_idiomas_disponibles(ruta_csv: str | None = None) -> list[str]:
    """
    Devuelve una lista de idiomas soportados por la API de AssemblyAI.

    Primero intenta cargar los idiomas desde el archivo CSV "Grid view.csv".
    Si no es posible (por ejemplo, el archivo no existe), usa una lista fija.
    """
    # Fallback mínimo por si el CSV no existe o falla la lectura
    fallback = [
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
    ]

    # Ruta al CSV con el catálogo completo de idiomas (permite sobreescritura por parámetro)
    ruta_csv = ruta_csv or "/home/ervin/Desktop/text/Grid view.csv"

    try:
        if not os.path.exists(ruta_csv):
            return fallback

        idiomas: list[str] = []
        codigos_vistos: set[str] = set()

        # utf-8-sig maneja BOM al inicio del archivo (p. ej., exportado desde hojas de cálculo)
        with open(ruta_csv, "r", encoding="utf-8-sig") as f:
            lector = csv.reader(f)
            encabezados = next(lector, None)
            if not encabezados:
                return fallback

            # Determina índices de columnas relevantes
            try:
                idx_nombre = encabezados.index("Language")
                idx_codigo = encabezados.index("Language Code")
            except ValueError:
                return fallback

            for fila in lector:
                if not fila or len(fila) <= max(idx_nombre, idx_codigo):
                    continue
                nombre = (fila[idx_nombre] or "").strip()
                codigo = (fila[idx_codigo] or "").strip()
                if not nombre or not codigo:
                    continue
                # Normaliza código a minúsculas como en el CSV
                codigo_norm = codigo.strip()
                if codigo_norm in codigos_vistos:
                    continue
                codigos_vistos.add(codigo_norm)
                idiomas.append(f"{codigo_norm} ({nombre})")

        # Ordena por nombre visible (parte entre paréntesis) para facilitar la lectura
        idiomas.sort(key=lambda s: s.split("(")[-1].lower())
        # Si por alguna razón quedó vacío, usa fallback
        return idiomas or fallback
    except Exception:
        # Ante cualquier error inesperado, no interrumpir el flujo principal
        return fallback


def seleccionar_idioma(ruta_csv: str | None = None) -> str:
    """
    Permite al usuario seleccionar un idioma de la lista disponible.
    """
    idiomas = listar_idiomas_disponibles(ruta_csv)
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
        "ruta_idiomas_csv": None,
        "mapa_nombres_hablantes": {},
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
        elif arg.startswith("--ruta-idiomas="):
            opciones["ruta_idiomas_csv"] = arg.split("=", 1)[1].strip()
        elif arg == "--ruta-idiomas" and i + 1 < len(args):
            opciones["ruta_idiomas_csv"] = args[i + 1].strip()
            i += 1
        elif arg.startswith("--nombres-hablantes="):
            valor = arg.split("=", 1)[1].strip()
            pares = [p for p in (s.strip() for s in valor.split(",")) if p]
            for par in pares:
                if "=" in par:
                    clave, nombre = [s.strip() for s in par.split("=", 1)]
                    if clave and nombre:
                        opciones["mapa_nombres_hablantes"][clave] = nombre
        elif arg == "--nombres-hablantes" and i + 1 < len(args):
            valor = args[i + 1].strip()
            pares = [p for p in (s.strip() for s in valor.split(",")) if p]
            for par in pares:
                if "=" in par:
                    clave, nombre = [s.strip() for s in par.split("=", 1)]
                    if clave and nombre:
                        opciones["mapa_nombres_hablantes"][clave] = nombre
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


def transcribir_audio(fuente: str, opciones: dict) -> tuple[str, object]:
    """
    Realiza la transcripción del audio utilizando la API de AssemblyAI.
    Retorna una tupla con (texto, objeto_transcripcion) para manejar speakers.
    """
    transcriptor = aai.Transcriber()
    configuracion = {}

    if opciones["codigo_idioma"]:
        configuracion["language_code"] = opciones["codigo_idioma"]
    # Activar detección automática de idioma si se solicitó
    if opciones.get("detectar_idioma") and not opciones.get("codigo_idioma"):
        configuracion["language_detection"] = True
    if opciones["canal_dual"]:
        configuracion["dual_channel"] = True
    if opciones["sin_formato_texto"]:
        configuracion["format_text"] = False
    if opciones["lista_palabras_clave"]:
        configuracion["word_boost"] = opciones["lista_palabras_clave"]
    if opciones["nivel_impulso"] in {"low", "default", "high"}:
        configuracion["boost_param"] = opciones["nivel_impulso"]
    # Activar diarización siempre para poder detectar si hay múltiples hablantes
    configuracion["speaker_labels"] = True

    config = aai.TranscriptionConfig(**configuracion) if configuracion else None

    try:
        transcripcion = transcriptor.transcribe(fuente, config=config)
        if transcripcion.status == aai.TranscriptStatus.error:
            raise ValueError(f"Error en la transcripción: {transcripcion.error}")

        return transcripcion.text or "", transcripcion
    except AttributeError as e:
        raise RuntimeError(f"Error inesperado al manejar la respuesta de la API: {e}")
    except Exception as e:
        raise RuntimeError(f"Error al transcribir el archivo: {e}")


def guardar_transcripcion(
    fuente: str,
    texto: str,
    tipo: str,
    transcripcion_obj=None,
    con_speakers: bool=False,
    mapa_nombres: dict | None = None,
) -> None:
    """
    Guarda la transcripción en un archivo de texto junto al archivo fuente.
    Si con_speakers=True y transcripcion_obj tiene utterances, guarda con formato de speakers.
    """
    base, _ = os.path.splitext(fuente)
    ruta_salida = f"{base}.transcripcion.{tipo}.txt"
    
    contenido = texto
    speakers_detectados = set()
    
    # Si hay speakers habilitados y el objeto tiene utterances, formatear con speakers
    if con_speakers and transcripcion_obj and hasattr(transcripcion_obj, 'utterances') and transcripcion_obj.utterances:
        contenido = ""
        for utterance in transcripcion_obj.utterances:
            etiqueta = str(utterance.speaker)
            speakers_detectados.add(etiqueta)
            
            if mapa_nombres and etiqueta in mapa_nombres:
                prefijo = mapa_nombres[etiqueta]
            else:
                prefijo = f"Speaker {etiqueta}"
            contenido += f"{prefijo}: {utterance.text}\n"
        contenido = contenido.strip()
        
        # Mostrar resumen de speakers detectados
        if speakers_detectados:
            print(f"\nSpeakers detectados: {len(speakers_detectados)}")
            for speaker in sorted(speakers_detectados):
                print(f"  - Speaker {speaker}")
    
    with open(ruta_salida, "w", encoding="utf-8") as archivo:
        archivo.write(contenido)
    print(f"\nTranscripción guardada en: {ruta_salida}")


def mostrar_ayuda():
    """
    Muestra la ayuda sobre los argumentos y opciones del programa.
    """
    ayuda = """
    Uso: transcriptor.py [opciones] <archivo>

    Opciones:
      -h, --ayuda            Muestra esta ayuda.
      --listar-idiomas        Lista los idiomas disponibles.
      --ruta-idiomas <ruta>   Ruta al CSV de idiomas (opcional).
      --nombres-hablantes "A=Ana,B=Carlos"  Asigna nombres a IDs de speakers.
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
        for idioma in listar_idiomas_disponibles(opciones["ruta_idiomas_csv"]):
            print(f"- {idioma}")
        return 0

    if not opciones["fuente"] or not validar_fuente(opciones["fuente"]):
        print("Fuente no válida o no encontrada.", file=sys.stderr)
        return 1

    if not opciones["codigo_idioma"] and not opciones["detectar_idioma"]:
        opciones["codigo_idioma"] = seleccionar_idioma(opciones["ruta_idiomas_csv"])

    try:
        texto, transcripcion_obj = transcribir_audio(opciones["fuente"], opciones)
        tipo = "cancion" if opciones["forzar_cancion"] else _classify_transcript_simple(texto)
        texto_formateado = (
            texto if opciones["salida_cruda"] else
            _format_as_lyrics(texto) if tipo == "cancion" else
            _format_as_dialogue(texto)
        )
        # Usar formato con speakers si el usuario lo pidió o si se detectan >1 hablantes
        utterances = getattr(transcripcion_obj, 'utterances', []) or []
        num_speakers_detectados = len({str(u.speaker) for u in utterances}) if utterances else 0
        usar_speakers = bool(opciones["etiquetas_hablantes"]) or num_speakers_detectados > 1

        guardar_transcripcion(
            opciones["fuente"],
            texto_formateado,
            tipo,
            transcripcion_obj,
            usar_speakers,
            opciones.get("mapa_nombres_hablantes") or None,
        )
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

