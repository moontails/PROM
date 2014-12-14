import BeautifulSoup
from collections import defaultdict
from connect_db import *
import urllib2
import re
import csv
import os
import numpy
import networkx as nx
import operator
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

def init_prom(final_data,award_data,alpha=0.5,beta=0.5):
    # Running the prom Initialization.
    print "Setting up tunes and dances floor for the PROM... "
    influence_score = defaultdict(float) #Initial values of hub
    contributor_score = defaultdict(float)
    award_score = defaultdict(float)
    movie_contributor_hash = {}
    
    for row in final_data:
        profit_score = float(row['Revenue']) / float(row['Budget'])
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
    # print contributor_score['Tom Hanks'],award_score['Tom Hanks'],influence_score['Tom Hanks']
    #print len(influence_score)

    contributors_list = influence_score.keys() 
    movies = movie_contributor_hash.keys()
    con_len = len(contributors_list)
    mov_len = len(movies)
    matrix_size = con_len+mov_len
    adj_matrix = numpy.zeros((matrix_size,matrix_size)) #Initial values
    
    #Loop over contributors (keys of influence_score hash) 
    for key in movies:
        j = movies.index(key)
        contributor_list = movie_contributor_hash[key]
        for contributor in contributor_list:
            if len(contributor.strip()) > 0 :
                i = contributors_list.index(contributor)
                adj_matrix[i][con_len+j] = 1

    hub_score = numpy.append(numpy.array(influence_score.values()),numpy.zeros(mov_len))
    auth_score = normalize(numpy.dot(adj_matrix.T,hub_score))
    # print "shapes: ",hub_score.shape,auth_score.shape,
    # print len(adj_matrix),len(influence_score),len(auth_score)
    return [adj_matrix,hub_score,auth_score,contributors_list,movies]

def dance_at_the_prom(adj_matrix,hub_score,auth_score):
    print "Dance with the date..."
    return hits_algo(adj_matrix,hub_score,auth_score)

def normalize(vector):
    return vector/sum(vector)
    
def hits_algo(adj_matrix,hub_score,auth_score):  
    # INPUT: Initial hub_score, authorities score and adjacency matrix.
    # OUTPUT: Converged
    print "Running HITS algorithm..."
    graph = nx.to_networkx_graph(adj_matrix)
    # print graph
    nstart = dict([(i, hub_score[i]) for i in xrange(len(hub_score))])
    return nx.hits(graph,nstart=nstart)

def the_final_dance(contributors,movies,temp_hub_score,temp_auth_score):
    contributor_score_map = {}
    movie_score_map = {}
    for i in xrange(len(contributors)):
        contributor_score_map[contributors[i]] = temp_hub_score[i]
    for i in xrange(len(movies)):
        movie_score_map[movies[i]] = temp_auth_score[len(contributors)+i]
    return [contributor_score_map,movie_score_map]

def execute_prom(movies_data,awards_data):
    # To do:
    #   -   Read movie data and awards data
    #   -   Initialize scores for the contributors as hubs and keep movies as authorities
    #   -   Calculate the initial authorities score
    #   -   Normalize scores
    #   -   Run the HITS algo and return the scores
    alpha = 0.5
    beta = 0.5
    adj_matrix,hub_score,auth_score,contributors,movies = init_prom(movies_data,awards_data,alpha,beta)
    temp_hub_score, temp_auth_score = dance_at_the_prom(adj_matrix,hub_score,auth_score)
    final_hub_score, final_auth_score = the_final_dance(contributors,movies,temp_hub_score,temp_auth_score)
    # print final_hub_score
    return [final_hub_score, final_auth_score]

def what_is_interesting(final_hub_score, final_auth_score):
    sorted_hubs = sort_dict_by_value(final_hub_score)
    sorted_auths = sort_dict_by_value(final_auth_score)
    count = 0
    for key,value in sorted_hubs:
        if count < 10:
            print key,':',value
        else:
            break
        count+=1
    count = 0
    for key,value in sorted_auths:
        if count < 10:
            print key,':',value
        else:
            break
        count+=1

def save_scores_to_db(final_hub_score, final_auth_score):
    cl = connect()
    for name in final_hub_score:
        print "Updating hub score "+name
        cl.command('Update Contributor set hub_score='+str(final_hub_score[name])+' where name=\''+name+'\'')

    for movie in final_auth_score:
        print "Updating auth score "+movie[0]
        movie_record = cl.command('select from Movie  where name="'+movie[0]+'" and year='+movie[1])[0]
        try:
            award_count = cl.command('select sum(award_count) from Contributor where @rid in (select expand(in()) from Movie where @rid='+movie_record.rid+')')[0].sum
        except Exception, e:
            award_count = 0
        cl.command('Update Movie set auth_score='+str(final_auth_score[movie])+',award_count='+str(award_count)+' where @rid='+movie_record.rid)

def sort_dict_by_value(map):
    sorted_map = sorted(map.items(), key=operator.itemgetter(0),reverse=True)
    return sorted_map

if __name__ == "__main__":
    final_data = get_data('training_data.csv')
    awards_data = get_data('awards.csv')
    print "Movie data: " + str(len(final_data))
    print "Awards data: " + str(len(awards_data))
    final_hub_score, final_auth_score  = execute_prom(final_data,awards_data)
    save_scores_to_db(final_hub_score, final_auth_score)
    what_is_interesting(final_hub_score, final_auth_score)



