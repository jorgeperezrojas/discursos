import os
import bs4
import re
import shutil
# procesa los archivos de texto de discursos
# almacena la info procesándolos en orden segun el nombre del archivo

months_large = {'enero':1,'febrero':2,'marzo':3,'abril':4,'mayo':5,'junio':6,'julio':7,'agosto':8,'septiembre':9,'octubre':10,'noviembre':11,'diciembre':12}


html_directory = 'data/allende/crawl/htm/'
txt_directory = 'data/allende/raw_text/'
prefix_site = 'https://www.marxists.org/espanol/allende/'

meta_to_write = []

print('extracting text...')

shutil.rmtree(txt_directory,ignore_errors=True)
os.makedirs(txt_directory)

for filename in os.listdir(html_directory):
    # if filename == '1972_octubre07.htm':
    if filename.endswith('.htm'):
        
        # abre y parsea el archivo
        with open(os.path.join(html_directory, filename)) as infile:
            html = bs4.BeautifulSoup(infile,'lxml')

        data = {}

        text_title = html.find('title').text.strip()
        text_title = re.sub('\n',' ',text_title)
        data['title'] = text_title.strip()

        content = html.find('section',{'id':'content'})
        span = html.findAll('span',{'class':'info'})[0]
        
        pre_date = span.next_element.next_element.strip()
        list_data = re.split('[ \.\,]+',pre_date)

        if len(list_data) <= 4:
            day = '01'
            month = str(months_large[list_data[0].lower()]).zfill(2)
            year = list_data[2]
        elif len(list_data) <= 6 and list_data[-1] == '':    
            day = list_data[0].zfill(2)
            month = str(months_large[list_data[2].lower()]).zfill(2)
            year = list_data[3]
        else:
            day = list_data[1].zfill(2)
            month = str(months_large[list_data[3].lower()]).zfill(2)
            year = list_data[5]

        data['date'] = '_'.join([year,month,day])

        data['subtitle'] = data['title']
        data['picture'] = 'None'

        body = html.find('body')
        pars = body.find_all('p')

        text_list = []
        for par in pars:
            if not par.find('strong') and not par.find('span'):
                to_append = re.sub('\n',' ',par.text.strip())
                text_list.append(to_append)

        text = '\n'.join(text_list)
        data['content'] = text.strip()        

        if data['content'] == '':
            print('no data in file',filename)
            continue

        outfilename_pref = data['date'] + '_' + filename[:-4]
        outfile_txt = outfilename_pref + '.txt'
        with open(os.path.join(txt_directory, outfile_txt), 'w') as outfile:
            outfile.write(data['content'])

        out_line_meta = outfilename_pref + '\t' 
        out_line_meta += data['date'] + '\t'
        out_line_meta += data['title'] + '\t'
        out_line_meta += data['subtitle'] + '\t'
        out_line_meta += data['picture'] + '\n'

        meta_to_write.append(out_line_meta)

print('done extracting text...')
print('writting meta...')

meta_to_write_sorted = sorted(meta_to_write)
os.makedirs(txt_directory, exist_ok=True)
with open(os.path.join(txt_directory, 'meta.txt'), 'w') as out_meta:
    for line in meta_to_write_sorted:
        out_meta.write(line)

print('done')


