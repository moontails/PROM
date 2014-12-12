from bs4 import BeautifulSoup
import urllib2
import re
import csv
import os
from connect_db import *

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
                data_item['year'] = re.sub('\D','',filename)
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
	regex = ' \D+[\d\.,]*|Budget|[bB]ox office|\(.*\)|,|\)|\[.*\]|-\d*|\]|m|Share'
	for row in data_list:
		if re.search('Unknown|N/A',row['Budget']) > 0 or row['Budget']=='0':
			continue
		elif re.search('Unknown',row['Revenue']) > 0 or row['Revenue']=='0':
			continue
		if 'billion' in row['Revenue']:
			row['Revenue'] = str(float(re.sub(regex,'',row['Revenue']))*1000000000)
		row['Budget'] = re.sub(regex,'',row['Budget'])
		row['Revenue'] = re.sub(regex,'',row['Revenue'])

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

def insert_into_db(data_list):
	#Need to get all actors and movies list and insert it.
	movie_contributor_hash = {}
	contributors = []
	for row in final_data:
		row['Contributors'] = re.sub('\[|\]|\'','',row['Contributors'])
		row['Contributors'] = re.sub('\n',',',row['Contributors'])
		temp_contributor_list = row['Contributors'].split(', ')
		movie_contributor_hash[row['Movie_Name']] = temp_contributor_list
		contributors.extend(temp_contributor_list)

	contributor_set = set(contributors)
	cl = connect()
	# Insert all contributors
	for name in contributor_set:
		name = re.sub('^"|"$','',name).strip()
		if len(name)>0:
			print 'Inserting '+name
			cl.command('Create vertex Contributor set name="'+name+'",awards=[], award_count=0')
	# Insert the movies
	weird_movies = []
	for movie in data_list:
		print 'Inserting movie '+movie['Movie_Name']
		try:
			cl.command('Create vertex Movie set year='+movie['year']+',budget='+movie['Budget']+',revenue='+movie['Revenue']+',name="'+movie['Movie_Name']+'",impact_score='+str(float(movie['Revenue'])/float(movie['Budget'])))
		except Exception, e:
			weird_movies.append(movie)
	print weird_movies
	print len(weird_movies)
	# for movie in movie_contributor_hash:
		# 
if __name__ == "__main__":
	files = get_all_filenames()
	all_data = []
	for f in files:
		all_data.extend(get_data('movie_data/'+f))
	# print len(all_data)
	final_data = clean_data(all_data)
	# print len(final_data)
	write_list_of_hash_to_file(final_data,'final_data')
	insert_into_db(final_data)
	# awards_data = get_data()




