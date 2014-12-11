from bs4 import BeautifulSoup as BS
from urllib2 import urlopen
from collections import defaultdict
import json
import sys
import csv

years = ['1990','1991','1992','1993','1994','1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013']

base_wiki = "http://en.wikipedia.org"


def getLinks(year, debug=False):
    base_url = "http://en.wikipedia.org/wiki/" + year + "_in_film"
    if debug:
        print base_url
       
    page =  urlopen(base_url)
    html = page.read()
    soup = BS(html)
    temp = []
    movie_links = defaultdict()
    print "\nAccessing the data\n"
    for items in soup.find_all('table', { 'class' : 'wikitable'}  ):
        temp.append(items)
    
    result = temp[-4:]

    for row in result:
        movie_data = row.findAll('tr')
        print "\n Processing quarterly Movie Segments \n"
        for items in movie_data:
            if items.find('i'):
                #print items.find('i')
                if items.find('i').find('a'):
                    temp = items.find('i').find('a')
                    movie_links[temp.text.encode('ascii', 'ignore')] = temp.get('href')
   
    print "\nProcessed: " + str(len(movie_links)) + " movies in " + year +"\n"
    writeLinks(year,movie_links)    
  
def writeLinks(year,results):
    csvfile = open("movie_links/"+ year + ".csv", "wb")
    movie_writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
    movie_writer.writerow(['movie_name','movie_link'])
    for movie in results:
        #print [movie,results[movie]]
        movie_writer.writerow([movie,results[movie]])

    csvfile.close()
    print "\nFinished extracting the data and storing in file\n"
        
if __name__ == "__main__":
	# Pass the city
    debug = False
    #if len(sys.argv) == 3:
    for year in years:
        getLinks(year)
    
    #for year 1998
    print "\nProcessing:  movies in 1998\n"
    infile = open('1998.html','r')
    csvfile = open("movie_links/1998.csv", "wb")
    movie_writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
    movie_writer.writerow(['Movie_Name','Movie_Link'])
    html = infile.read()
    soup = BS(html)
    data = soup.findAll('a')
    for item in data:
        movie_writer.writerow([item.text.encode('ascii', 'ignore'),item.get('href')])
