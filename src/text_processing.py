# procesa los archivos de texto de discursos
# almacena la info procesándolos en orden segun el nombre del archivo
import argparse
import re
import os
import shutil
from check_duplicates import check_duplicates
from collections import Counter

# letras y números en expresiones regulares
re_nums = '0-9'
re_letters = 'a-záéíóúüA-ZÁÉÍÓÚÜñÑ'
re_punctuation_and_space = r'\(\)¿\?!¡\,;.:&\$% '
re_skip_chars = '[^' + re_nums + re_letters + re_punctuation_and_space + ']' 
re_skip_strings = re_skip_chars + '+'
re_chars_for_splitting = '[' + re_punctuation_and_space + '–"\n' + ']+'
re_months = r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)'
re_date_spec = '(([' + re_letters + ']{1,30} ?){1,3}\,? +)?[0-9]{1,2}( +de)? +' + re_months + '( +del?)? +2[0-9]{3}\.{0,10}$'
re_html_garbage = r'((br| ) )*((&([a-z0-9]+;)+(br)*)+)'

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
    text = raw_text.replace(u'\xa0', u' ')
    for exp in expressions_to_delete:
        if re.search(exp,text):
            text = re.sub(exp,'',text)
    text = re.sub(re_skip_strings,'',text)
    text = re.sub(' +',' ',text)
    return text

def is_useful_line(line,word_counts=None,frequency=0.19,min_len=50):
    if line == '':
        return False

    mid = int(len(line)/2)
    if line[:mid].upper() == line[:mid]: # more than half of the string is only uppercase considered not informative
        return False

    if is_date(line): # the line describes the date of the discurso
        return False

    if len(line) < min_len: # too short to be useful
        return False

    if frequency > 0:
        if word_counts == None:
            raise Exception('No word count provided')

        voc_size = len(word_counts)
        line_avg = 0
        words = re.split(re_chars_for_splitting,line.strip())
        for word in words:
            line_avg += word_counts[word]
        line_avg = line_avg / len(words) / len(word_counts)
        if line_avg < frequency:
            return False


    for banned_prefix in banned_prefixes:
        if line.lower().startswith(banned_prefix.lower()):
            return False

    return True


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('base_directory', metavar='D', type=str,
                        help='Base directory')
    parser.add_argument('-fC', '--frequencyCleaning', metavar='F', type=float, default=0.19,
                        help='Discard paragraphs with average frequency of words below F (this is to keep out non Spanish discursos).')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='Show in detail what the script is doing.')
    parser.add_argument('-mC', '--minUsefulChars', metavar='MC', type=int, default=1000, 
                        help='Minimum number of useful characters in a discurso to consider it.')
    parser.add_argument('-f', '--fullProcessing', default=False, action='store_true',
                        help='Make full processing of text.')
    parser.add_argument('-d', '--duplicateDeletion', default=False, action='store_true',
                        help='Try to delete duplicates.')
    parser.add_argument('-lA', '--lookAhead', metavar='LA', type=int, default=10, 
                        help='Number of discursos to check for duplicates (for each discurso, after the date of the discurso).')
    parser.add_argument('-nE', '--numEquals', metavar='NE', type=int, default=300, 
                        help='Number of charactes to be verbatim equal between two discursos to be consider duplicates.')

    args = parser.parse_args()
    base_directory = args.base_directory
    frequency = args.frequencyCleaning
    duplicate_deletion = args.duplicateDeletion
    full = args.fullProcessing
    min_useful_chars = args.minUsefulChars
    look_ahead = args.lookAhead
    n_equals = args.numEquals
    verbose = args.verbose
    word_counts = None

    txt_directory = os.path.join(base_directory, 'raw_text/')
    processed_directory = os.path.join(base_directory, 'processed_text/')
    clean_d_directory = os.path.join(processed_directory,'discursos_limpios')


    shutil.rmtree(clean_d_directory)
    shutil.rmtree(processed_directory)

    os.makedirs(processed_directory)
    os.makedirs(clean_d_directory)

    if frequency > 0:
        ### for now we are computing internal word frequencies
        ### it would be better to rely in some external word frequency corpus
        if verbose:
            print('Computing word frequency statistics for cleaning...')
        # genera una tabla de frecuencia de palabras
        all_lines = []
        all_words = []

        for filename in os.listdir(txt_directory):
            if filename == 'meta.txt':
                continue
            raw_text = open(os.path.join(txt_directory,filename)).read()
            raw_lines = raw_text.split('\n')
            clean_lines = [clean_text(l) for l in raw_lines]
            list_of_lists_of_words = [re.split(re_chars_for_splitting,line.strip()) for line in clean_lines]
            for list_of_words in list_of_lists_of_words:
                all_lines.append(list_of_words)
                all_words += list_of_words

        word_counts = Counter(all_words)
        # compute average frequency per paragraph


    # ahora limpia el texto y guarda uno a uno en archivos distintos
    if verbose:
        print('Begin cleaning...')
    for filename in os.listdir(txt_directory):
        if filename == 'meta.txt':
            continue

        raw_text = open(os.path.join(txt_directory,filename)).read()
        raw_lines = raw_text.split('\n')

        useful_lines = []

        for line in raw_lines:
            clean_line = clean_text(line)
            if is_useful_line(clean_line, word_counts=word_counts, frequency=frequency):
                useful_lines.append(clean_line)

        paragraphs = '\n'.join(useful_lines)
        if len(paragraphs) < min_useful_chars:
            if verbose:
                print('Discarding:',filename[:25],'Not enough useful characters. Total useful characters:',len(paragraphs))
            continue

        with open(os.path.join(clean_d_directory,filename),'w') as outfile_discurso:
            outfile_discurso.write(paragraphs)


    ### now heavy processing
    if duplicate_deletion:
        check_duplicates(
            clean_d_directory,
            n_equals=n_equals,
            look_ahead=look_ahead,
            verbose=verbose)


    if full:
        # primero junta todos los nombres y ordénalos
        filenames = []
        for filename in os.listdir(txt_directory):
            if filename == 'meta.txt':
                continue
            if filename.endswith(".txt"):
                filenames.append(filename)

        filenames = sorted(filenames)

        with \
            open(os.path.join(processed_directory,'all_text_single_line.txt'),'w') as outfile_single_line, \
            open(os.path.join(processed_directory,'all_text_file_names_plus_content.txt'),'w') as outfile_name_line, \
            open(os.path.join(processed_directory,'all_text_per_paragraphs.txt'),'w') as outfile_todo_por_parrafo:

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
