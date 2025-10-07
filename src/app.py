import os
import tempfile
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash

# Reuse logic from transcribe.py
import transcribe as trans



app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")


@app.route("/", methods=["GET"]) 
def index():
    # Construir lista de idiomas desde CSV (o fallback interno)
    brutos = trans.listar_idiomas_disponibles()
    idiomas = []  # lista de tuplas (codigo, etiqueta)
    for item in brutos:
        # item viene como "xx (Nombre)"; separar el código del resto para usar como value
        codigo = (item.split(" ")[0] or "").strip()
        etiqueta = item
        if codigo:
            idiomas.append((codigo, etiqueta))
    return render_template("index.html", idiomas=idiomas)


@app.route("/transcribe", methods=["POST"]) 
def transcribe_upload():
    archivo = request.files.get("file")
    idioma_elegido = request.form.get("idioma", "auto").strip()
    if not archivo or archivo.filename == "":
        flash("Sube un archivo de audio o video.")
        return redirect(url_for("index"))

    # Guardar temporalmente y ejecutar transcripción
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta_tmp = os.path.join(tmpdir, archivo.filename)
        archivo.save(ruta_tmp)

        # Configurar API key
        aai_key = trans.obtener_clave_api()
        if not aai_key:
            flash("Falta la clave de API de AssemblyAI. Configura CLAVE_API_ASSEMBLYAI.")
            return redirect(url_for("index"))

        # Preparar opciones mínimas: detectar idioma automáticamente
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
            "codigo_idioma": None if idioma_elegido == "auto" else idioma_elegido,
            "fuente": ruta_tmp,
            "detectar_idioma": idioma_elegido == "auto",
            "ruta_idiomas_csv": None,
            "mapa_nombres_hablantes": {},
        }

        try:
            # Establecer API key en settings del SDK
            import assemblyai as aai
            aai.settings.api_key = aai_key

            texto, transcripcion_obj = trans.transcribir_audio(ruta_tmp, opciones)
            tipo = "cancion" if opciones["forzar_cancion"] else trans._classify_transcript_simple(texto)
            texto_formateado = (
                texto if opciones["salida_cruda"] else
                trans._format_as_lyrics(texto) if tipo == "cancion" else
                trans._format_as_dialogue(texto)
            )

            utterances = getattr(transcripcion_obj, 'utterances', []) or []
            num_speakers = len({str(u.speaker) for u in utterances}) if utterances else 0
            usar_speakers = bool(opciones["etiquetas_hablantes"]) or num_speakers > 1

            # Si se usa formato con speakers, construimos una representación simple para la web
            lineas_speakers = []
            if usar_speakers and utterances:
                for u in utterances:
                    etiqueta = str(u.speaker)
                    prefijo = opciones.get("mapa_nombres_hablantes", {}).get(etiqueta, f"Speaker {etiqueta}")
                    lineas_speakers.append(f"{prefijo}: {u.text}")

            idioma_detectado = getattr(transcripcion_obj, 'language_code', None) or getattr(transcripcion_obj, 'language', None)

            return render_template(
                "result.html",
                texto=texto_formateado,
                tipo=tipo,
                usar_speakers=usar_speakers,
                lineas_speakers=lineas_speakers,
                idioma_detectado=idioma_detectado,
            )
        except Exception as e:
            flash(f"Error: {e}")
            return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)


