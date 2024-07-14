import os
from marker.convert import convert_single_pdf
# Definir las rutas del archivo PDF de entrada y el archivo Markdown de salida
input_pdf = 'c:\ia\dd\Agujast.pdf'
output_md = 'c:\ia\dd\archivo.md'

# Ejecutar la conversión de PDF a Markdown
#convert_single.convert_pdf_to_markdown(input_pdf, output_md, extract_tables=True, extract_structure=True)

convert_single_pdf(input_pdf, output_md, extract_tables=True, extract_structure=True)


# Leer y mostrar el contenido extraído (opcional)
with open(output_md, 'r') as file:
    content = file.read()
    print(content)