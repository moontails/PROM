import os
import json
import snap
import csv
from collections import defaultdict
import numpy
import matplotlib.pyplot as plt


def add_to_dict(map,deg):
	# when the degree of th node is passed, add count++# Get the degree distribution for the nodes
	# hash = {
	# 	"d1" => "f1",
	# 	"d2" => "f2",
	# 	.
	# 	.
	# 	.
	#	"dn" => "fn"
	# }
	# for each node, get the degree and count++ for tha node
	if deg in map:
		map[deg] += 1
	else:
		map[deg] = 1

def get_degree_dist_map(gr):
	#Takes an un-directed graph and returns a dictionary with {"degree" => "freq"}
	map_deg = {}
	for ni in gr.Nodes():
		add_to_dict(map_deg,ni.GetOutDeg())

	return map_deg

def draw_degree_distribution_curve(gr,filename, desc="Plot for the graph"):
    #Given a graph draw a distribution curve of d"Degree of node" vs. "Frequency"
    desc = desc + ' ' + filename
    degree_dist = get_degree_dist_map(gr)

    print "degree_dist"+str(degree_dist)

    x_values = degree_dist.keys()
    y_values = degree_dist.values()
    plt.plot(x_values,y_values)
    plt.xlabel('Number of Actors (Degree of the node)')
    plt.ylabel('Frequency')
    plt.title('Degree Distribution')
    plt.grid(True)
    plt.savefig(filename)
    print "Generated file using Matplotlib"
    
data = {}
actor = defaultdict(list)

datafiles = os.listdir('data/')

for file in datafiles:
    print file
    infile = open('data/' + file, "r")
    temp = csv.reader(infile)
    for row in temp:
        movie = row[0]
        data[movie] = row[2]
        actors = row[2].replace(',',';').split(';')
        actors = [ x.strip() for x in actors ]
        for i in range(0,len(actors)):
            actor[actors[i]].extend(actors[:i] + actors[i+1:])
        #print actor
        #break
    #break   
print "\nTotal number of movies processed: " + str(len(data))

G1 = snap.TUNGraph.New()

ids = actor.keys()

for i in ids:
    G1.AddNode( ids.index(i) )
    
for i in actor:
    for j in set(actor[i]):
        G1.AddEdge(ids.index(i),ids.index(j))
        
print str(G1.GetNodes()), str(G1.GetEdges())

#snap.PlotOutDegDistr(G1, 'degreeDistribution1.png', "Plot for the graph")
draw_degree_distribution_curve(G1, 'degreeDistribution.png' )


degrees = snap.TIntV()
snap.GetDegSeqV(G1, degrees)
degrees = numpy.array(degrees)
"""
print sorted(degrees)[:10]
degD = {} #dictionary for degree distribution

for n in G1.Nodes():
	if n.GetOutDeg() in degD.keys():
		degD[n.GetOutDeg()] += n.GetOutDeg() #increment the node count for that degree
	else:
		degD[n.GetOutDeg()] = 1 #new degree found 

for x in degD:
	print "Degree: " + str(x) + " Nodes: " + str(degD[x])
	
print "\nPlotting the degree distribution"
"""
fig = plt.figure()
plt.plot(degrees)
fig.suptitle('Actors Degrees')
plt.xlabel('Actors')
plt.ylabel('Degree')
plt.grid(True)
fig.savefig('ActordegreeDistribution.png') #could save only in .png format
#plt.show() #to display the graph

labels = snap.TIntStrH()
for NI in G1.Nodes():
    labels[NI.GetId()] = str(NI.GetId())
snap.DrawGViz(G1, snap.gvlDot, "output.png", " ", labels)

print str(snap.GetClustCf(G1))
#with open('actors.json', 'w') as outfile:
#    json.dump(actor, outfile)