# procesa los archivos de texto de discursos
# almacena la info procesándolos en orden segun el nombre del archivo
import argparse
import re
import os

# letras y números en expresiones regulares
re_nums = '0-9'
re_letters = 'a-záéíóúüA-ZÁÉÍÓÚÜñÑ'
re_punctuation_and_space = r'\(\)¿\?!¡\,;.:&\$% '
re_skip_chars = '[^' + re_nums + re_letters + re_punctuation_and_space + ']' 
re_skip_strings = re_skip_chars + '+'
re_months = r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)'
re_date_spec = '(([' + re_letters + ']{1,30} ?){1,3}\,? +)?[0-9]{1,2}( +de)? +' + re_months + '( +del?)? +2[0-9]{3}\.{0,10}$'
re_html_garbage = r'((br| ) )*((&([a-z0-9]+;)+(br)*)+)'


# variables globales directories
txt_directory = '' 
processed_directory = ''

banned_prefixes = []

expressions_to_delete = [
   re_html_garbage,
]

def is_date(line):
    if re.match(re_date_spec,line.lower()):
        return True
    return False

def clean_text(raw_text):
    text = raw_text.strip()
    for exp in expressions_to_delete:
        if re.search(exp,text):
            text = re.sub(exp,'',text)
    text = re.sub(re_skip_strings,'',text)
    text = re.sub(' +',' ',text)
    return text

def is_useful_line(line):
    if line == '':
        return False

    mid = int(len(line)/2)
    if line[:mid].upper() == line[:mid]: # more than half of the string is only uppercase considered not informative
        return False

    if is_date(line): # the line describes the date of the discurso
        return False

    for banned_prefix in banned_prefixes:
        if line.lower().startswith(banned_prefix.lower()):
            return False

    return True



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('base_directory', metavar='D', type=str,
                        help='Base directory')

    args = parser.parse_args()
    base_directory = args.base_directory
    txt_directory = os.path.join(base_directory, 'raw_text/')
    processed_directory = os.path.join(base_directory, 'processed_text/')
    clean_d_directory = os.path.join(processed_directory,'discursos_limpios')

    os.makedirs(processed_directory, exist_ok=True)
    os.makedirs(clean_d_directory, exist_ok=True)

    with \
        open(os.path.join(processed_directory,'all_text_single_line.txt'),'w') as outfile_single_line, \
        open(os.path.join(processed_directory,'all_text_file_names_plus_content.txt'),'w') as outfile_name_line, \
        open(os.path.join(processed_directory,'all_text_per_paragraphs.txt'),'w') as outfile_todo_por_parrafo:

        # primero junta todos los nombres y ordénalos
        filenames = []
        for filename in os.listdir(txt_directory):
            if filename.endswith(".txt"):
                filenames.append(filename)
        filenames = sorted(filenames)

        for filename in filenames:
            raw_text = open(os.path.join(txt_directory,filename)).read()
            raw_lines = raw_text.split('\n')

            useful_lines = []

            for line in raw_lines:
                clean_line = clean_text(line)
                if is_useful_line(clean_line):
                    useful_lines.append(clean_line)

            text = ' '.join(useful_lines)
            paragraphs = '\n'.join(useful_lines)
            
            outfile_single_line.write(text)
            outfile_single_line.write(' ') 

            outfile_name_line.write(filename)
            outfile_name_line.write('\t')
            outfile_name_line.write(text)
            outfile_name_line.write('\n')

            outfile_todo_por_parrafo.write(paragraphs)
            outfile_todo_por_parrafo.write('\n')

            with open(os.path.join(clean_d_directory,filename),'w') as outfile_discurso:
                outfile_discurso.write(paragraphs)
