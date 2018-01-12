import os
import bs4
import re

html_directory = 'data/macri/crawl/html/'
txt_directory = 'data/macri/raw_text/'
prefix_site = 'http://'

meta_to_write = []

months = {'ENE':1,'FEB':2,'MAR':3,'ABR':4,'MAY':5,'JUN':6,'JUL':7,'AGO':8,'SEP':9,'OCT':10,'NOV':11,'DIC':12}
months_large = {'enero':1,'febrero':2,'marzo':3,'abril':4,'mayo':5,'junio':6,'julio':7,'agosto':8,'septiembre':9,'octubre':10,'noviembre':11,'diciembre':12}

print('extracting text...')

os.makedirs(txt_directory)
for filename in os.listdir(html_directory):
    if filename.endswith('.html'):
    # if filename.endswith('35538-palabras-del-presidente-mauricio-macri-y-del-primer-mi.html'):    
        # abre y parsea el archivo
        with open(os.path.join(html_directory, filename)) as infile:
            html = bs4.BeautifulSoup(infile,'lxml')

        data = {}
        pre_date = html.find('time').text.strip()
        list_data = re.split(' +',pre_date)
        day = list_data[1].zfill(2)
        month = str(months_large[list_data[3]]).zfill(2)
        year = list_data[5]
        if year == '-0001': ### limpieza particular del año, asume 2016
            year = '2016'
        data['date'] = '_'.join([year,month,day])
        data['title'] = html.find('meta', {'property':'og:title'}).get('content').strip() 
        picture = None
        if picture:
            data['picture'] = prefix_site + picture.get('src').strip()
        else:
            data['picture'] = 'None'

        data['content'] = html.find('article').text.strip()

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


