from bs4 import BeautifulSoup
import urllib2
import re
import csv
import os

def get_data(filename):
	data_list = []
	with open('movie_data/'+filename,mode='rU') as datafile:
		reader = csv.reader(datafile)
   		data_item = {}
   		headers = reader.next()
   		for row in reader:
   			# print  row
   			data_item = {headers[i]:row[i] for i in xrange(len(headers))}
   			data_item['year'] = re.sub('\.csv','',filename)
   			data_list.append(data_item);
   	return data_list

def get_all_filenames():
	file_names = []
	for f in os.listdir('movie_data/'):
		if re.search('csv',f):
			file_names.append(f)
	return file_names

def clean_data(data_list):
	final_data = []
	for row in data_list:
		if row['Budget'] == '0' or 'Unknown' in row['Budget']:
			continue
		elif row['Revenue'] == '0' or 'Unknown' in row['Revenue']:
			continue
		final_data.append(row)
	return final_data

def write_list_of_hash_to_file(input_list,filename):
	with open('data/'+filename+'.csv', 'wb') as csvfile:
		fwriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
		fwriter.writerow(input_list[0].keys())
		for row in input_list:
			fwriter.writerow(row.values())

if __name__ == "__main__":
	files = get_all_filenames()
	all_data = []
	for f in files:
		all_data.extend(get_data(f))
	print len(all_data)
	# print all_data[0]
	final_data = clean_data(all_data)
	count = 0
	for row in final_data:
		if len(row['Contributors']) == 0:
			count +=1
	print len(final_data)
	print count
	write_list_of_hash_to_file(final_data,'final_data')
