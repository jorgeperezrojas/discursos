import os
import bs4
import re

html_directory = 'data/bachelet_2/crawl/html/'
txt_directory = 'data/bachelet_2/raw_text/'
prefix_site = 'https://prensa.presidencia.cl'

meta_to_write = []

months = {'ENE':1,'FEB':2,'MAR':3,'ABR':4,'MAY':5,'JUN':6,'JUL':7,'AGO':8,'SEP':9,'OCT':10,'NOV':11,'DIC':12}

print('extracting text...')

os.makedirs(txt_directory)
for filename in os.listdir(html_directory):
    if filename.endswith('.html'):
        # abre y parsea el archivo
        with open(os.path.join(html_directory, filename)) as infile:
            html = bs4.BeautifulSoup(infile,'lxml')

        spans =  html.find_all('span')
        data = {}

        pre_date_list = html.find('span',{'id':'main_ltFEcha'}).text.strip().split()
        day_s = pre_date_list[0].zfill(2)
        month_s = str(months[pre_date_list[1]]).zfill(2)
        year_s = pre_date_list[2]
        data['date'] = '_'.join([year_s,month_s,day_s])

        picture = html.find('span',{'id':'main_ltFotoDestacada'}).find('img')
        if (picture):
            data['picture'] = prefix_site + picture.get('src').strip().replace('\\','/')
        else:
            data['picture'] = 'None'

        data['title'] = html.find('span',{'id':'main_ltTitulo'}).text.strip()
        data['subtitle'] = html.find('span',{'id':'main_ltBajada'}).text.strip()
        data['content'] = html.find('span',{'id':'main_ltContenido'}).text.strip()

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
print('writting meta...')

meta_to_write_sorted = sorted(meta_to_write)
os.makedirs(txt_directory, exist_ok=True)
with open(os.path.join(txt_directory, 'meta.txt'), 'w') as out_meta:
    for line in meta_to_write_sorted:
        out_meta.write(line)

print('done')