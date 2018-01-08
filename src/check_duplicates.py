import os
import re
import sys
from suffix_array import longest_common_substring

def check_duplicates(
    p_txt_directory,
    filenames=[],
    n_equals=300,
    look_ahead=10,
    manual_duplicates=[],
    verbose=True,
    ):
    ### Chequea repetidos
    ### Usa un suffix array
    ### Método: si alguno de los siguientes 'look_ahead' discursos en orden cronológico 
    ### tienen un overlap textual de 'n_equals' símbolos, lo considera un duplicado
    ### Sería mejor chequear todos los pares de discursos para encontrar overlap pero la 
    ### complejidad sería prohibitiva: en total sería O(N^2*MlogM) con 
    ### N=1500 discursos y M=12000 caracteres por discurso ~ 3 * 10^11
    ### La complejidad del proceso actual es O(N*look_ahead*M*logM) con los valores por defecto

    duplicates = set()

    if filenames == []:
        for filename in os.listdir(p_txt_directory):
            filenames.append(filename)

    filenames = sorted(filenames)
    if verbose:
        print('Checking duplicates for',len(filenames),'files.')

    for i in range(len(filenames)-1):
        if verbose:
            sys.stdout.write("Checking file:{} of {} \r".format(i,len(filenames)))
            sys.stdout.flush()
        current_file = filenames[i]
        current_date = current_file[:10]
        current_text = re.sub('( |\n)+','',open(os.path.join(p_txt_directory, current_file)).read()).lower()

        j = i+1

        checking_file = filenames[j]
        checking_date = checking_file[:10]

        while j < len(filenames) and j < i+look_ahead: 
            checking_text = re.sub('( |\n)+','',open(os.path.join(p_txt_directory, checking_file)).read()).lower()

            l = min(len(checking_text),len(current_text))
            lcs = longest_common_substring(checking_text + current_text)

            if len(list(lcs.keys())[0]) > n_equals: #d_factor*l:ç
                if verbose:
                    print('found duplicate',current_file[:25],'=',checking_file[:25])
                if len(current_text) < len(checking_text):
                    duplicates.add(current_file[:-4])
                    if verbose:
                        print('will delete',current_file)
                else:
                    duplicates.add(checking_file[:-4])
                    if verbose:
                        print('will delete',checking_file)
                

            j += 1
            if j == len(filenames):
                break
            checking_file = checking_file = filenames[j]
            checking_date = checking_file[:10]

    # some manual duplicates:
    for dup in manual_duplicates:
        duplicates.add(dup)

    if verbose:
        print()
        print('duplicates found:',duplicates)
        print('deleting duplicates...')

    # elimina archivos repetidos
    for dup in duplicates:
        os.remove(os.path.join(p_txt_directory, dup + '.txt'))
    
    if verbose:
        print('done.')
