import os
import bs4
import re
from check_duplicates import check_duplicates_and_store_meta

html_directory = 'data/bachelet_2/crawl/html/'
txt_directory = 'data/bachelet_2/raw_text/'
p_txt_directory = 'data/bachelet_2/processed_text/'
prefix_site = 'https://prensa.presidencia.cl'

meta_to_write = []

months = {'ENE':1,'FEB':2,'MAR':3,'ABR':4,'MAY':5,'JUN':6,'JUL':7,'AGO':8,'SEP':9,'OCT':10,'NOV':11,'DIC':12}

print('extracting text...')

os.makedirs(txt_directory, exist_ok=True)
for filename in os.listdir(html_directory):
    if filename.endswith('.html'):
        # abre y parsea el archivo
        with open(os.path.join(html_directory, filename)) as infile:
            html = bs4.BeautifulSoup(infile,'lxml')

        spans =  html.find_all('span')
        data = {}
        for span in spans:
            if span.get('id') == 'main_ltTitulo':
                data['title'] = span.text.strip()
            if span.get('id') == 'main_ltFEcha':
                pre_date_list = span.text.strip().split()
                day_s = pre_date_list[0].zfill(2)
                month_s = str(months[pre_date_list[1]]).zfill(2)
                year_s = pre_date_list[2]
                data['date'] = '_'.join([year_s,month_s,day_s])
            if span.get('id') == 'main_ltFotoDestacada':
                picture = span.find('img')
                if (picture):
                    data['picture'] = prefix_site + picture.get('src').strip().replace('\\','/')
                else:
                    data['picture'] = 'None'
            if span.get('id') == 'main_ltBajada':
                data['subtitle'] = span.text.strip()
            if span.get('id') == 'main_ltContenido':
                data['content'] = span.text.strip()

        if 'content' not in data:
            print('no data in file',filename)
            continue

        outfilename_pref = data['date'] + '_' + filename[:-5]
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

check_duplicates_and_store_meta(
    meta_to_write,
    txt_directory,
    p_txt_directory,
    n_equals=300,
    look_ahead=5,
    manual_duplicates=['2014_10_23_9048','2015_10_13_21664'])


