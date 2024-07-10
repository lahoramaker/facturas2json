# Extractor de Facturas

Este proyecto es una aplicación de Streamlit diseñada para extraer información de facturas en formato PDF y convertirla en un formato estructurado (JSON).

## Características

- Interfaz de usuario en español
- Carga múltiple de archivos PDF
- Extracción de texto de PDFs utilizando la biblioteca Marker
- Extracción de datos estructurados utilizando un modelo de lenguaje
- Vista previa de PDFs y edición de datos extraídos
- Guardado de datos en formato JSONL
- Procesamiento en segundo plano para mejorar la eficiencia

## Requisitos del sistema

- Python 3.7 o superior
- Bibliotecas adicionales especificadas en `requirements.txt`

## Instalación

1. Clone este repositorio:
   ```
   git clone https://github.com/tu-usuario/extractor-de-facturas.git
   cd extractor-de-facturas
   ```

2. Cree un entorno virtual (opcional pero recomendado):
   ```
   python -m venv .venv
   source venv/bin/activate  # En Windows use `venv\Scripts\activate`
   ```

3. Opcional: Instale uv para acelerar el proceso de instalación
   ```
   pip install uv
   ```

4. Instale las dependencias:
   ```
   pip install -r requirements.txt
   ```
   En caso de haber instalado uv puede hacerlo con el siguiente comando:
   ```
   uv pip install -r requirements.txt
   ```

## Uso

1. Ejecute la aplicación:
   ```
   streamlit run src/facturas2json.py
   ```

2. Abra su navegador web y vaya a la dirección que se muestra en la consola (generalmente http://localhost:8501).

3. Use la interfaz para cargar archivos PDF, revisar los datos extraídos y guardar los resultados.

## Notas

- Asegúrese de que sus PDFs sean legibles y estén en un formato estándar para obtener los mejores resultados.
- La aplicación utiliza modelos de IA para la extracción de datos, por lo que los resultados pueden variar dependiendo de la calidad y el formato de los PDFs.

## Contribuir

Las contribuciones son bienvenidas. Por favor, abra un issue para discutir cambios importantes antes de crear un pull request.

## Licencia

[MIT](https://choosealicense.com/licenses/mit/)