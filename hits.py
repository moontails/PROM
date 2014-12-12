from bs4 import BeautifulSoup
from collections import defaultdict
from connect_db import *
import urllib2
import re
import csv
import os
import numpy


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

def initialize(final_data,award_data):
    alpha = 1
    beta = 1
    influence_score = defaultdict(float) #Initial values of hub
    contributor_score = defaultdict(float)
    award_score = defaultdict(float)
    movie_contributor_hash = {}
    
    for row in final_data:
        profit_score = float(row['Revenue']) / float(row['Budget'])
        row['Contributors'] = re.sub('\[|\]|\'','',row['Contributors'])
        row['Contributors'] = re.sub('\\n',',',row['Contributors'])
        temp_contributor_list = row['Contributors'].split(', ')
        movie_contributor_hash[row['Movie_Name'],row['year']] = temp_contributor_list
        for contributor in temp_contributor_list:
            if len(contributor.strip()) > 0 :
                contributor_score[contributor] += (profit_score / len(temp_contributor_list))
    #print len(movie_contributor_hash)
    
    for row in award_data:
        award_type = row['award_type']
        contributor = row['contributor_name']
        win_type = row['win_type']
        if win_type == 'winner':
            award_score[contributor] += 1
        elif win_type == 'nominee':
            award_score[contributor] += 0.5
               
    for contributor in contributor_score:
        influence_score[contributor] = (alpha*contributor_score[contributor]) + (beta*award_score[contributor])
    print contributor_score['Tom Hanks'],award_score['Tom Hanks'],influence_score['Tom Hanks']
    #print len(influence_score)

    contributors_list = influence_score.keys() 
    movies = movie_contributor_hash.keys()
    adj_matrix = numpy.zeros((len(contributors_list),len(movies))) #Initial values
    
    #Loop over contributors (keys of influence_score hash) 
    for key in movies:
        j = movies.index(key)
        contributor_list = movie_contributor_hash[key]
        for contributor in contributor_list:
            if len(contributor.strip()) > 0 :
                i = contributors_list.index(contributor)
                adj_matrix[i,j] = 1
                
    #Initial values
    hub_score = numpy.array(influence_score.values())
    hub_score = normalize(hub_score)
    auth_score = numpy.transpose(adj_matrix)*hub_score
    auth_score = normalize(auth_score)
    #print len(adj_matrix),len(influence_score),len(auth_score)
    
    hits_algo(adj_matrix,hub_score,auth_score)

def normalize(vector):
    return vector/sum(vector)
    
def hits_algo(adj_matrix,hub_score,auth_score):     
    print "Begin Regression"
    
    
        
    
    
if __name__ == "__main__":
    final_data = get_data('final_data.csv')
    award_data = get_data('awards.csv')
    print "Movie data: " + str(len(final_data))
    print "Awards data: " + str(len(award_data))
    initialize(final_data,award_data)




