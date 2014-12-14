from bs4 import BeautifulSoup
import urllib2
import re
import csv

def get_content(url):
	content = open(url,'r').read()
	return content

def process_content(content,award_type):
	# Need to process content and return a hash of the form:
	# {"type" : "actor", "win_type":True, "name":"some_name","movie":"movie name"}
	acadamy_awards = []
	soup = BeautifulSoup(content)
	all_divs = soup.find_all('div',class_='nomHangIndent')
	all_trs = []
	for div in all_divs:
		all_trs.append(div.parent.parent)
	# print all_trs
	for tr in all_trs:
		temp_row = {}
		st, win_star, person_details  = tr.contents
		div, st = person_details.contents
		hrefs = div.find_all('a')
		for href in hrefs:
			if href.parent.name == 'div':
				name = href.string
				name = re.sub('Written| by|Screenplay|Original|Story','',name)
				name = re.sub('&|;| and',',',name)
				name = re.sub('\[[0-9]*\]|\[|\]|\'|novel|see Cast|original screenplay|Adapted for the screen|','',name)
				name = re.sub(r'\\n',',',name)
				name = re.sub(',\s*,',',',name)
				name = re.sub(', Jr.',' Jr.',name)
		for tag in tr.parent.parent.previous_elements:
			if tag.name == 'dt':
				dt = tag
				try:
					year = dt.u.a.string
				except Exception, e:
					year = dt.a.string
				finally:
					year = re.sub(" \([0-9]+[a-z]+\)",'',year)
				break
		temp_row['year'] = year.encode("utf8")
		temp_row['movie'] = div.i.a.string.encode("utf8")
		temp_row['name'] = name.encode("utf8")
		temp_row['award_type'] = award_type.encode("utf8")
		temp_row['win_type'] = 'winner' if win_star.string == u'*' else 'nominee'
		acadamy_awards.append(temp_row)
	return acadamy_awards


if __name__ == "__main__":
	urls = ['actress', 'actors','writing','directing','picture','supporting_actor','supporting_actress']
	awards_list = []
	for url in urls:
		content = get_content('data/awards_data/'+url+'.html')
		temp_list = process_content(content,url)
		print temp_list[0]
		awards_list.extend(temp_list)
	with open('data/awards.csv', 'wb') as csvfile:
		award_writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
		award_writer.writerow(['year','award_type','win_type','contributor_name','movie_name'])
		for temp_hash in awards_list:
			award_writer.writerow([temp_hash['year'],temp_hash['award_type'],temp_hash['win_type'],temp_hash['name'],temp_hash['movie']])


	

