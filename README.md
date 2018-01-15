# Discursos presidenciales chilenos

Datos originales de discursos presidenciales chilenos obtenidos desde la Web, y scripts para procesarlos (extraer texto, limpiarlo y eliminar duplicados). Actualmente contiene:

- 575 discursos de Sebastián Piñera desde 2010 hasta 2014, obtenidos desde el sitio http://2010-2014.gob.cl/discursos/ (descargados en diciembre 2017). Todos los discursos se encuentran en archivos en formato .htm. Aproximadamente 560 son discursos únicos en español.
- 1581 discursos de Michelle Bachelet desde 2014 hasta 2017, obtenidos desde el sitio https://prensa.presidencia.cl/discursos.aspx (descargados en diciembre 2017). Todos los discursos se encuentran en archivos en formato .html. Aproximadamente 1540 son discursos únicos en español.

Para descargar los datos originales y descomprimirlos (siguiendo la estructura de carpetas esperada) se debe ejecutar los siguientes comandos desde la raiz:

```
wget http://dcc.uchile.cl/~jperez/resources/bachelet_2.tar.gz
wget http://dcc.uchile.cl/~jperez/resources/piñera_1.tar.gz

tar zxvf bachelet_2.tar.gz
tar zxvf piñera_1.tar.gz
```

Para extraer el texto crudo desde los archivos .htm y .html se debe ejecutar

```
python src/html_to_txt_plus_meta_bachelet.py
python src/htm_to_txt_plus_meta_piñera.py
```

en la raiz (requiere python 3, un par de librerías estandar y [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)). Esto también almacena archivos (meta.txt) con algunos metadatos de cada discurso obtenidos desde los .htm y .html correspondientes (como fecha, títulos, subtítulos y direcciones de archivos de imágenes para ciertos discursos).

Para limpiar los datos de texto, eliminando textos con muy pocos caracteres útiles, eliminar algunos discursos duplicados (o discursos que son realmente extractos de otros), y eliminar párrafos con palabras de baja frecuencia (para borrar partes en idioma no español, por ejemplo) se debe ejecutar

```
python src/text_processing.py data/bachelet_2/ --duplicateDeletion --frequencyCleaning 0.19 --verbose
python src/text_processing.py data/piñera_1/ --duplicateDeletion --frequencyCleaning 0.19 --verbose
```

El script tiene varias otras opciones para regular la limpieza de los textos.

Importante: la extracción de texto desde los archivos más el chequeo de duplicados puede tardar un par de minutos pues el chequeo implica encontrar el traslape máximo entre pares de discursos y eliminar el discurso de menor tamaño cuando el string comun más largo pase cierto umbral. Para modificar los valores de chequeos de duplicados se pueden usar las opciones `--lookAhead` y `--numEquals`.


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


