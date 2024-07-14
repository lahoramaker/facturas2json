# Extractor de Facturas

Este proyecto es una aplicación de Streamlit diseñada para extraer información de facturas en formato PDF y convertirla en un formato estructurado (JSON).

## Características

- Interfaz de usuario en español
- Carga múltiple de archivos PDF
- Extracción de texto de PDFs utilizando la biblioteca Marker
- Extracción de datos estructurados utilizando el de modelo de lenguaje nuExtract. 
- Vista previa de PDFs y edición de datos extraídos
- Guardado de datos en formato JSONL
- Procesamiento en segundo plano para mejorar la eficiencia

## Requisitos del sistema

- Python 3.8 o superior
- Bibliotecas adicionales especificadas en `requirements.txt`

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/lahoramaker/facturas2json.git
   cd facturas2json
   ```

2. Crea un entorno virtual (opcional pero recomendado):
   ```
   python -m venv .venv
   source venv/bin/activate  # En Windows use `venv\Scripts\activate`
   ```

3. Opcional: Instala uv para acelerar el proceso de instalación de paquetes pip
   ```
   pip install uv
   ```

4. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
   En caso de haber instalado uv puedes hacerlo con el siguiente comando:
   ```
   uv pip install -r requirements.txt
   ```

## Uso

1. Ejecuta la aplicación:
   ```
   streamlit run src/facturas2json.py
   ```

2. Abre tu navegador web y ve a la dirección que se muestra en la consola (generalmente http://localhost:8501).

3. Usa la interfaz para cargar archivos PDF, revisar los datos extraídos y guardar los resultados.

## Notas

- Asegúrate de que tus PDFs sean legibles y estén en un formato estándar para obtener los mejores resultados.
- La aplicación utiliza modelos de IA para la extracción de datos, por lo que los resultados pueden variar dependiendo de la calidad y el formato de los PDFs.
- Ten en cuenta que los pesos del modelo Marker están bajo la licencia cc-by-nc-sa-4.0, pero el autor ha renunciado a esta restricción para cualquier organización con ingresos brutos inferiores a 5 millones de dólares estadounidenses en los últimos 12 meses y con menos de 5 millones de dólares en financiación total recibida de capital de riesgo o business angels. Si desea obtener más información sobre la licencia, por favor visita el [repositorio de Marker](https://github.com/VikParuchuri/marker).

## Recursos adicionales

Si quieres saber más sobre el proyecto, puedes consultar los siguientes videos:
- Descripción general de la aplicación y de los modelos utilizados: https://youtu.be/I7N2DSzUXbc
- Demostración de la aplicación y explicación más detallada de los distintos componentes: https://youtu.be/Gov8eR5LBHQ

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios importantes antes de crear un pull request.

## Licencia

[MIT](https://choosealicense.com/licenses/mit/)
