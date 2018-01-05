import os
import re
from suffix_array import longest_common_substring

def check_duplicates_and_store_meta(
    meta_to_write,
    txt_directory,
    p_txt_directory,
    n_equals=300,
    look_ahead=10,
    manual_duplicates=[],
    ):
    ### Chequea repetidos
    ### Usa un suffix array
    ### Método: si alguno de los siguientes 'look_ahead' discursos en orden cronológico 
    ### tienen un overlap textual de 'n_equals' símbolos, lo considera un duplicado
    ### Sería mejor chequear todos los pares de discursos para encontrar overlap pero la 
    ### complejidad sería prohibitiva: en total sería O(N^2*MlogM) con 
    ### N=1500 discursos y M=12000 caracteres por discurso ~ 3 * 10^11
    ### La complejidad del proceso actual es O(N*look_ahead*M*logM) con los valores por defecto
    print('checking duplicates...')

    meta_to_write_sorted = sorted(meta_to_write)

    duplicates = set()

    for i in range(len(meta_to_write_sorted)-1):
        current_file = meta_to_write_sorted[i].split('\t')[0] + '.txt'
        current_date = current_file[:10]
        current_text = re.sub('( |\n)+','',open(os.path.join(txt_directory, current_file)).read()).lower()

        j = i+1

        checking_file = meta_to_write_sorted[j].split('\t')[0] + '.txt'
        checking_date = checking_file[:10]

        while j < len(meta_to_write_sorted) and j < i+look_ahead: 
            checking_text = re.sub('( |\n)+','',open(os.path.join(txt_directory, checking_file)).read()).lower()

            l = min(len(checking_text),len(current_text))
            lcs = longest_common_substring(checking_text + current_text)

            if len(list(lcs.keys())[0]) > n_equals: #d_factor*l:ç
                print('found duplicate',current_file,'=',checking_file)
                if len(current_text) < len(checking_text):
                    duplicates.add(current_file[:-4])
                    print('deleting',current_file)
                else:
                    duplicates.add(checking_file[:-4])
                    print('deleting',checking_file)
                

            j += 1
            if j == len(meta_to_write_sorted):
                break
            checking_file = meta_to_write_sorted[j].split('\t')[0] + '.txt'
            checking_date = checking_file[:10]

    # some manual duplicates:
    for dup in manual_duplicates:
        duplicates.add(dup)

    print('duplicates found:',duplicates)

    print('writting meta...')
    os.makedirs(p_txt_directory, exist_ok=True)
    with open(os.path.join(p_txt_directory, 'meta.txt'), 'w') as out_meta:
        for line in meta_to_write_sorted:
            if line.split('\t')[0] not in duplicates:
                out_meta.write(line)

    print('deleting duplicates...')
    # elimina archivos repetidos
    for dup in duplicates:
        os.remove(os.path.join(txt_directory, dup + '.txt'))
    print('done.')
