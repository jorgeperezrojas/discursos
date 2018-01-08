import os
import bs4
import re

html_directory = 'data/piñera_1/crawl/htm/'
txt_directory = 'data/piñera_1/raw_text/'
prefix_site = 'http://2010-2014.gob.cl'

meta_to_write = []

months = {'ENE':1,'FEB':2,'MAR':3,'ABR':4,'MAY':5,'JUN':6,'JUL':7,'AGO':8,'SEP':9,'OCT':10,'NOV':11,'DIC':12}

print('extracting text...')

os.makedirs(txt_directory)
for filename in os.listdir(html_directory):
    if filename.endswith('.htm'):
        
        # abre y parsea el archivo
        with open(os.path.join(html_directory, filename)) as infile:
            html = bs4.BeautifulSoup(infile,'lxml')

        data = {}

        content = html.find('section',{'id':'content'})
        pre_date = content.article.header.find('time').get("datetime")
        data['date'] = re.sub('-','_',pre_date)
        data['title'] = content.article.header.h2.text

        body = html.find('section',{'class':'body'})
        picture = body.find('img')
        if picture:
            data['picture'] = prefix_site + picture.get('src').strip()
        else:
            data['picture'] = 'None'

        pars = body.find_all('p')
        text = '\n'.join([par.text for par in pars])
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


