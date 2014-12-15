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
import matplotlib.pyplot as plt
from scipy.stats.mstats import mquantiles
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
        influence_score[contributor] = (alpha*award_score[contributor]) + (beta*contributor_score[contributor])
    print 'Tom Hanks:',contributor_score['Tom Hanks'],award_score['Tom Hanks'],influence_score['Tom Hanks']
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

    hub_score = normalize(numpy.append(numpy.array(influence_score.values()),numpy.zeros(mov_len)))
    # Not required
    auth_score = normalize(numpy.dot(adj_matrix.T,hub_score))
    # print "shapes: ",hub_score.shape,auth_score.shape,
    # print len(adj_matrix),len(influence_score),len(auth_score)
    return [adj_matrix,hub_score,contributors_list,movies]

def dance_at_the_prom(adj_matrix,hub_score):
    print "Dance with the date..."
    return hits_algo(adj_matrix,hub_score)

def normalize(vector):
    return vector/sum(vector)
    
def hits_algo(adj_matrix,hub_score):  
    # INPUT: Initial hub_score, authorities score and adjacency matrix.
    # OUTPUT: Converged
    print "Running HITS algorithm..."
    graph = nx.to_networkx_graph(adj_matrix)
    # print graph
    nstart = dict([(i, hub_score[i]) for i in xrange(len(hub_score))])
    # print nstart
    # return nx.hits(graph)
    return nx.hits(graph,nstart=nstart)

def the_final_dance(contributors,hub_score,temp_hub_score):
    init_hub_score_map = {}
    final_hub_score_map = {}
    for i in xrange(len(contributors)):
        init_hub_score_map[contributors[i]] = hub_score[i]
        final_hub_score_map[contributors[i]] = temp_hub_score[i]
    return [init_hub_score_map,final_hub_score_map]

def execute_prom(movies_data,awards_data,alpha=0.5,beta=0.5):
    # To do:
    #   -   Read movie data and awards data
    #   -   Initialize scores for the contributors as hubs and keep movies as authorities
    #   -   Calculate the initial authorities score
    #   -   Normalize scores
    #   -   Run the HITS algo and return the scores
    print alpha,beta
    adj_matrix,hub_score,contributors,movies = init_prom(movies_data,awards_data,alpha,beta)
    temp_hub_score, temp_auth_score = dance_at_the_prom(adj_matrix,hub_score)
    init_hub_score, final_auth_score = the_final_dance(contributors,hub_score,temp_hub_score)
    # print final_hub_score
    return [init_hub_score, final_auth_score]

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

def save_scores_to_db(final_hub_score,final_result):
    cl = connect()
    for name in final_hub_score:
        print "Updating hub score "+name
        cl.command('Update Contributor set hub_score='+str(final_hub_score[name])+' where name=\''+name+'\'')

    for movie in final_result:
        # print movie
        print "Updating auth score "+movie[0]
        try:
            movie_record = cl.command('select from Movie  where name="'+movie[0]+'" and year='+movie[1])[0]
        except Exception, e:
            raise e
        else:
            cl.command('Update Movie set predicted_revenue='+str(final_result[movie]['pred_rev'])+',error_score='+str(final_result[movie]['error'])+' where @rid='+movie_record.rid)

def sort_dict_by_value(map):
    sorted_map = sorted(map.items(), key=operator.itemgetter(0),reverse=True)
    return sorted_map

def calculate_constant(movie_data,final_hub_score,k_year=2000):
    print 'Calculating constant'
    # Covert movie data into hash[movie] = data format
    # now calculate score for each movie as the sum of contributor score
    # keep the factor K in the 
    # new_movie_data = {}
    bad_score_list = []
    good_score_list = []
    bad_constant_list = []
    good_constant_list = []
    for movie in movie_data:
        # print movie
        if True:
            # new_movie_data[movie['Movie_Name']] = movie
            contributors = movie['Contributors'].split(',')
            t_sum = 0
            for con in contributors:
                try:
                    t_sum += final_hub_score[con.strip()]
                except Exception, e:
                     t_sum = t_sum
            prediction_score = t_sum*float(movie['Budget'])
            # new_movie_data[movie['Movie_Name']]['prediction_score'] = prediction_score
            # print 'score: ',prediction_score
            if prediction_score <=0:
                print movie
                continue
            temp_constant = float(movie['Revenue'])/prediction_score
            if float(movie['Revenue'])<float(movie['Budget']):
                bad_score_list.append(prediction_score)
                bad_constant_list.append(temp_constant)
            else:
                good_score_list.append(prediction_score)
                good_constant_list.append(temp_constant)
            # new_movie_data[movie['Movie_Name']]['prediction_constant'] = temp_constant
            # prediction_constant_list.append(temp_constant)
    # print len(prediction_constant_list)
    print 'Bad Score:(',min(bad_score_list),',',max(bad_score_list),')'
    print 'Good Score:(',min(good_score_list),',',max(good_score_list),')'
    bad_score_median = numpy.median(bad_score_list)
    good_score_median = numpy.median(good_score_list)
    bad_k_median = mquantiles(bad_score_median)[0]#numpy.median(mquantiles)
    good_k_median = mquantiles(good_constant_list)[0]#numpy.median(good_constant_list)
    print 'bad_k_median:',bad_k_median,'good_k_median:',good_k_median,'bad_score_median:',bad_score_median,'good_score_median:',good_score_median
    return [bad_k_median,good_k_median,bad_score_median,good_score_median]

def calculate_predict(data,bad_k,good_k,bad_m,good_m):
    final_predition = {}
    total_score = 0
    contributor_count = 0
    for movie in data:
        contributors = movie['Contributors'].split(',')
        for con in contributors:
            try:
                contributor_count+=1
                total_score+=final_hub_score[con.strip()]
            except Exception, e:
                # print e
                total_score = total_score
    mean_score = total_score/contributor_count
    # print 'mean_score:',mean_score
    for movie in data:
        t_sum = 0
        for con in contributors:
            try:
                if final_hub_score[con.strip()]<=0:
                    t_sum += mean_score
                else:
                    t_sum += final_hub_score[con.strip()]
            except Exception, e:
                # print e
                t_sum = t_sum
        pred_score = (t_sum/contributor_count)*float(movie['Budget'])
        if pred_score<good_k:
            pred_rev = bad_k*pred_score
        else:
            pred_rev = good_k*pred_score
        final_predition[movie['Movie_Name'],movie['year']] = {'pred_rev':pred_rev, 'rev':float(movie['Revenue'])}
    # print final_predition
    return final_predition

def draw_plot_given_x_y_list(x_values,xlabel='Degree of the node',ylabel='Frequency',filename='plot',title='Degree Distribution'):
    print 'generating '+title
    plt.plot(x_values)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    # plt.xscale('log')
    plt.yscale('log')
    plt.savefig(filename+'_matplotlib.png')
    plt.close()

if __name__ == "__main__":
    training_data = get_data('training_data.csv')
    training_awards_data = get_data('training_awards.csv')
    testing_data = get_data('testing_data.csv')
    print "Movie data: " + str(len(training_data))
    print "Awards data: " + str(len(training_awards_data))
    # print '\n\n--------------------------------\nAlpha='+str(alpha)+'\n--------------------------------'
    init_hub_score, final_hub_score = execute_prom(training_data,training_awards_data,0,1)
    # base_k = calculate_constant(training_data,init_hub_score)
    final_bad_k,final_good_k,final_bad_m,final_good_m = calculate_constant(training_data,final_hub_score)

    # base_result = calculate_predict(testing_data,base_k)
    final_result = calculate_predict(testing_data,final_bad_k,final_good_k,final_bad_m,final_good_m)

    # base_errors = []
    final_errors = []

    # for movie in base_result:
    #     t_pred = 100*numpy.absolute(base_result[movie]['pred_rev']-base_result[movie]['rev'])/base_result[movie]['rev']
    #     base_errors.append(t_pred)
    # base_errors = numpy.sort(base_errors)

    for movie in final_result:
        t_pred = 100*numpy.absolute(final_result[movie]['pred_rev']-final_result[movie]['rev'])/final_result[movie]['rev']
        final_result[movie]['error'] = t_pred
        final_errors.append(t_pred)
    final_errors = numpy.sort(final_errors)

    # print 'Error Rate - Base:(',min(base_errors),',',max(base_errors),')'
    print 'Error Rate - Final:(',min(final_errors),',',max(final_errors),')'
    print 'Tom Hanks:',init_hub_score['Tom Hanks'],final_hub_score['Tom Hanks']

    # draw_plot_given_x_y_list(base_errors,'Index of the Movie','Error','base','Base Hubs')
    draw_plot_given_x_y_list(final_errors,'Index of the Movie','Error','final','Final Hubs')

    # save_scores_to_db(final_hub_score,final_result)



