## Transcriptor de Audio y Video con AssemblyAI

### Descripción
Este programa permite transcribir archivos de audio y video utilizando la API de AssemblyAI. Es capaz de permitir al usuario seleccionar el idioma manualmente. 

### Funcionalidades
- Transcripción de archivos de audio y video.
- selección manual.
- Soporte para múltiples idiomas.

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
   Obtén tu clave de API de AssemblyAI y configúrala como una variable de entorno:
   ```bash
   export ASSEMBLYAI_API_KEY="TU_CLAVE_DE_API"
   ```
   Si no configuras una clave, el programa utilizará una clave de ejemplo incluida en el código.

### Uso
1. **Transcribir un archivo:**
   ```bash
   python transcribe.py <ruta_del_archivo>
   ```
   Ejemplo:
   ```bash
   python transcribe.py "mi_audio.mp4"
   ```

2. **Seleccionar el idioma manualmente:**
   Si no configuras el idioma con `--idioma`, el programa te pedirá que selecciones uno de la lista disponible.



### Ejemplo de Ejecución
```bash
python transcribe.py  "mi_video.mp4"
```

### Notas
- Asegúrate de que el archivo de entrada sea accesible y esté en un formato compatible.
- Consulta la documentación de AssemblyAI para más detalles sobre las capacidades de la API.


