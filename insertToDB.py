from bs4 import BeautifulSoup
import urllib2
import re
import csv
import os

def get_data(filename):
    data_list = []
    with open('data/'+filename,mode='rU') as datafile:
        reader = csv.reader(datafile)
        data_item = {}
        headers = reader.next()
        for row in reader:
            # print  row
            data_item = {headers[i]:row[i] for i in xrange(len(headers))}
            if 'year' not in data_item:
                data_item['year'] = re.sub('\.csv','',filename)
            data_list.append(data_item);
    return data_list

def get_all_filenames():
	file_names = []
	for f in os.listdir('data/movie_data/'):
		if re.search('csv',f):
			file_names.append(f)
	return file_names

def clean_data(data_list):
	final_data = []
	for row in data_list:
		if re.search('Unknown|N/A',row['Budget']) > 0 or row['Budget']=='0':
			continue
		elif re.search('Unknown',row['Revenue']) > 0 or row['Revenue']=='0':
			continue
		if 'billion' in row['Revenue']:
			row['Revenue'] = str(float(re.sub('[^0-9\.?]','',row['Revenue']))*1000000000)
		row['Budget'] = re.sub('[^0-9\.?]','',row['Budget'])
		row['Revenue'] = re.sub('[^0-9\.?]','',row['Revenue'])

		try:
			if float(row['Budget']) < 1000:
				row['Budget'] = str(float(row['Budget'])*1000000)
			if float(row['Revenue']) < 1000:
				row['Revenue'] = str(float(row['Revenue'])*1000000)
		except Exception, e:
			print row
		final_data.append(row)
	return final_data

def write_list_of_hash_to_file(input_list,filename):
	with open('data/'+filename+'.csv', 'wb') as csvfile:
		fwriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
		fwriter.writerow(input_list[0].keys())
		for row in input_list:
			fwriter.writerow(row.values())

#def insert_into_db(data_list):



if __name__ == "__main__":
    files = get_all_filenames()
    all_data = []
    for f in files:
        all_data.extend(get_data('movie_data/' + f))
    # print len(all_data)
    final_data = clean_data(all_data)
    # print len(final_data)
    write_list_of_hash_to_file(final_data,'final_data')
    award_data = get_data('awards.csv')
    print award_data[0]
    print len(award_data)
    #insert_into_db(final_data)
    #Need to get all actors and movies list and insert it.
    contributors = []
    for row in final_data:
        contributors.extend(re.sub('\[|\]|\'','',row['Contributors']).split(', '))
    contributor_set = set(contributors)
    




