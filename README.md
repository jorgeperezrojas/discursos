# Discursos presidenciales chilenos

Datos originales de discursos presidenciales chilenos obtenidos desde la Web, y scripts para procesarlos (extraer texto, limpiarlo y eliminar duplicados). Actualmente contiene:

- 575 discursos de Sebastián Piñera desde 2010 hasta 2014, obtenidos desde el sitio http://2010-2014.gob.cl/discursos/ (descargados en diciembre 2017). Todos los discursos se encuentran en archivos en formato .htm. Aproximadamente 560 son discursos únicos en español.
- 1581 discursos de Michelle Bachelet desde 2014 hasta 2017, obtenidos desde el sitio https://prensa.presidencia.cl/discursos.aspx (descargados en diciembre 2017). Todos los discursos se encuentran en archivos en formato .html. Aproximadamente 1540 son discursos únicos en español.
- 249 discursos de Salvador Allende desde 1970 hasta 1973, obtenidos desde el sitio https://www.marxists.org/espanol/allende/ (descargados en mayo de 2018).  Todos los discursos se encuentran en archivos en formato .htm (Algunos son entrevistas).

Para descargar los datos originales y descomprimirlos (siguiendo la estructura de carpetas esperada) se debe ejecutar los siguientes comandos desde la raiz, cambianndo `<presidente>` por `piñera_1`, `bachelet_2` o `allende`.

```
wget http://dcc.uchile.cl/~jperez/resources/<presidente>.tar.gz
tar zxvf <presidente>.tar.gz
```

Para extraer el texto crudo desde los archivos .html (o .htm) se debe ejecutar

```
python src/html_to_txt_plus_meta_<presidente>.py
```

en la raiz (requiere python 3, un par de librerías estandar y [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)). Esto también almacena archivos (meta.txt) con algunos metadatos de cada discurso obtenidos desde los .html (o .htm) correspondientes (como fecha, títulos, subtítulos y direcciones de archivos de imágenes para ciertos discursos).

Para limpiar los datos de texto, eliminando textos con muy pocos caracteres útiles, eliminar algunos discursos duplicados (o discursos que son realmente extractos de otros), y eliminar párrafos con palabras de baja frecuencia (para borrar partes en idioma no español, por ejemplo) se debe ejecutar

```
python src/text_processing.py data/<presidente>/ --duplicateDeletion --frequencyCleaning 0.19 --verbose
```

El script tiene varias otras opciones para regular la limpieza de los textos.

Importante: la extracción de texto desde los archivos más el chequeo de duplicados puede tardar un par de minutos pues el chequeo implica encontrar el traslape máximo entre pares de discursos y eliminar el discurso de menor tamaño cuando el string comun más largo pase cierto umbral. Para modificar los valores de chequeos de duplicados se pueden usar las opciones `--lookAhead` y `--numEquals`.

## Visualización de discursos por temas

Una forma amigable de visualizar algunos temas de discursos es construyendo embeddings para las frases en cada discurso. Los siguientes archivos contienen embeddings para algunas frases de los discursos de Sebastián Piñera.

- [Embeddings para 2039 frases](http://dcc.uchile.cl/~jperez/resources/ev_vec.tsv) (vectores de 300 dimensiones)
- [Metadata](http://dcc.uchile.cl/~jperez/resources/ev_cols.tsv) para los embeddings (texto de la frase más fecha y título del discurso desde donde viene la frase)

Estos datos se pueden visualizar en [projector.tensorflow.org](http://projector.tensorflow.org/). Solo se debe cargar los datos en el sitio. Luego se pueden projectar usando t-SNE o PCA. Un ejemplo de proyecciones usando t-SNE se pueden ver [acá](https://twitter.com/perez/status/955319971931934720).

Actualmente me encuentro trabajando en visualizaciones basadas en [Software Galaxies](https://github.com/anvaka/pm#software-galaxies) adaptado a texto. Pueden ver una demo de 18K+ frases de discursos de Bachelet (2014-2018) [acá](https://twitter.com/perez/status/993291012087967744). El proyecto en curso de esta visualización lo pueden encontrar [acá](https://github.com/jorgeperezrojas/disviz#galaxias-de-discursos).

## Bonus! discursos de presidentes argentinos

Similar a los discursos de presidentes chilenos, los siguientes son datos originales de discursos presidenciales argentinos obtenidos desde la Web, y scripts para procesarlos (extraer texto, limpiarlo y eliminar duplicados). Actualmente contiene:

- 948 discursos de Néstor Kirchner desde 2003 a 2007 obtenidos desde el sitio https://www.casarosada.gob.ar/informacion/archivo (descargados a inicios de enero 2018). Aproximadamente 930 son discursos únicos.
- 1558 discursos de Cristina Fernández desde 2007 a 2015 obtenidos desde el sitio https://www.casarosada.gob.ar/informacion/archivo (descargados a inicios de enero 2018). 
Aproximadamente 1540 son discursos únicos.
- 372 discursos de Mauricio Macri desde 2015 a enero de 2018 obtenidos desde el sitio https://www.casarosada.gob.ar/informacion/discursos (descargados a inicios de enero 2018). Aproximadamente 360 son discursos únicos. 

Para procesarlos hay que hacer casi lo mismo que arriba. Desde la raiz ejecutar los siguientes comandos, reemplazando `<presidente>` por `kirchner`, `fernandez`, o `macri`.

```
wget http://dcc.uchile.cl/~jperez/resources/<presidente>.tar.gz
tar zxvf <presidente>.tar.gz
python src/html_to_txt_plus_meta_<presidente>.py
python src/text_processing.py data/<presidente>/ --duplicateDeletion --frequencyCleaning 0.19 --verbose
```


