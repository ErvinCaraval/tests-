## Transcriptor de Audio y Video con AssemblyAI

### Descripción
Este programa permite transcribir archivos de audio y video utilizando la API de AssemblyAI. Incluye selección de idioma manual o desde CSV, y detección automática de hablantes (diarización) con opción de asignar nombres personalizados.

### Funcionalidades
- Transcripción de archivos de audio y video.
- Detección automática de hablantes y etiquetado (Speaker A, B, C...).
- Asignación opcional de nombres a hablantes (`--nombres-hablantes "A=Ana,B=Carlos"`).
- Soporte para múltiples idiomas desde CSV (`Grid view.csv`) o lista interna.
- Selección de idioma manual si no se especifica con `--idioma`.

### Requisitos
- Python 3.8 o superior.
- Una clave de API válida de AssemblyAI.

### Configuración
1. **Crear y activar un entorno virtual:**
   ```bash
   python -m venv .venv && source .venv/bin/activate
   ```

2. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar la clave de API:**
   - Crea una cuenta y obtén tu API Key en la página de AssemblyAI: [`assemblyai.com`](https://www.assemblyai.com/).
   - Configura la variable de entorno esperada por el script (nombre correcto):
     ```bash
     export CLAVE_API_ASSEMBLYAI="TU_CLAVE_DE_API"
     ```
   - Si no configuras una clave, el programa usará el valor por defecto embebido, pero debes reemplazarlo por seguridad.

### Uso
1. **Transcribir un archivo (modo básico):**
   ```bash
   python transcribe.py <ruta_del_archivo>
   ```
   - Si detecta más de un hablante, aplicará etiquetas automáticamente.
   - Si hay un solo hablante, guardará texto simple.

2. **Activar etiquetas de hablantes explícitamente:**
   ```bash
   python transcribe.py --etiquetas-hablantes "mi_audio.mp4"
   ```

3. **Asignar nombres a hablantes:**
   ```bash
   python transcribe.py --etiquetas-hablantes --nombres-hablantes "A=Ana,B=Carlos" "mi_audio.mp4"
   ```

4. **Elegir idioma sin menú:**
   ```bash
   python transcribe.py --idioma en "mi_audio.mp4"
   ```

5. **Cargar idiomas desde CSV (AssemblyAI Grid):**
   ```bash
   python transcribe.py --listar-idiomas --ruta-idiomas "/home/ervin/Desktop/text/Grid view.csv"
   ```

2. **Seleccionar el idioma manualmente:**
   Si no configuras el idioma con `--idioma`, el programa te pedirá que selecciones uno de la lista disponible.



### Ejemplo de Ejecución
```bash
python transcribe.py  "mi_video.mp4"
```

### Notas
- Asegúrate de que el archivo de entrada sea accesible y esté en un formato compatible.
- No combines diarización con transcripción multicanal (la API lo prohíbe).
- Consulta la documentación oficial para diarización y ejemplos:
  - Documentación de diarización: [`Speaker Diarization`](https://www.assemblyai.com/docs/speech-to-text/pre-recorded-audio/speaker-diarization)
  - Sitio principal y gestión de API Keys: [`assemblyai.com`](https://www.assemblyai.com/)

### Detalles de configuración avanzada
- Detección de hablantes: el script habilita `speaker_labels=True` para poder detectar múltiples hablantes; si se detecta más de uno, se formatea automáticamente con etiquetas.
- Rango/Conteo de speakers: la API permite indicar `speakers_expected` o `speaker_options` (mínimo/máximo). Si necesitas fijar estos valores, se pueden exponer como flags adicionales.
- Idiomas: por defecto se leen desde `Grid view.csv` (columnas `Language` y `Language Code`). Si no está disponible, se usa una lista interna.


