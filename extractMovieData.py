from bs4 import BeautifulSoup as BS
from urllib2 import urlopen
from collections import defaultdict
import json
import sys
import csv

years = ['1990','1991','1992','1993','1994','1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013']
base_wiki = "http://en.wikipedia.org"

def readLinks(year, debug=False):
    csvfile = open("movie_links/"+year+".csv","r")
    reader = csv.reader(csvfile)
    headers = reader.next()
    movie_links = defaultdict()
    for line in reader:
        movie_links[line[0]] = line[-1]
    print "\nProcessed: " + str(len(movie_links)) + " movies in " + year +"\n"
    csvfile.close()
    getData(year,movie_links)

def getData(year,movie_links):
    movie_db = defaultdict()
    for movie in movie_links:
        movie_db[movie] = defaultdict()
        movie_url = base_wiki + movie_links[movie]
        print movie_url
        
        page =  urlopen(movie_url)
        html = page.read()
        soup = BS(html)
        #print movie
        movie_infobox = soup.find('table')
        #print movie_infobox
        movie_data = movie_infobox.findAll('tr')
        
        #Variables to extract
        movie_db[movie]['contributor'] = []
        movie_db[movie]['budget'] = 0
        movie_db[movie]['revenue'] = 0
        
        for row in movie_data:
            #Contributors
            if 'Directed' in row.text or 'Starring' in row.text or 'Written' in row.text:
                temp = row.find('td')
                #print temp
                items = temp.findAll('a')
                
                for item in items:
                    #print item.text
                    movie_db[movie]['contributor'].append(item.text.encode('ascii', 'ignore'))
            
            #Budget
            if 'Budget' in row.text:
                temp = row.text.encode('ascii', 'ignore')
                #print temp
                temp = temp.strip()
                temp = temp.replace('\n','')
                if 'million' in temp:
                    temp = temp.split('$')[-1].split('[')[0].replace('million','').strip()
                    temp = temp 
                elif '$' in temp:
                    temp = temp.split('$')[-1].split('[')[0].replace(',','')
                #print temp
                movie_db[movie]['budget'] = temp
            #Revenue
            if 'Box' in row.text:
                temp = row.text.encode('ascii', 'ignore')
                #print temp
                temp = temp.strip()
                temp = temp.replace('\n','')
                if 'million' in temp:
                    temp = temp.split('$')[-1].split('[')[0].replace('million','').strip()
                    temp = temp
                elif '$' in temp:
                    temp = temp.split('$')[-1].split('[')[0].replace(',','')
                #print temp
                movie_db[movie]['revenue'] = temp
    writeData(year,movie_db)        
        
def writeData(year,results):
    csvfile = open("movie_data/" + year + ".csv", "wb")
    movie_writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
    movie_writer.writerow(['Movie_Name','Contributors','Budget','Revenue'])
    for movie in results:
        #print [movie,results[movie]]
        movie_writer.writerow([movie,results[movie]['contributor'],results[movie]['budget'],results[movie]['revenue']])
    csvfile.close()
    print "\nFinished extracting the data and storing in file\n"
        
if __name__ == "__main__":
	# Pass the city
    debug = False
    #if len(sys.argv) == 3:
    for year in years:
        readLinks(year)
