#!/usr/bin/python3
from bs4 import BeautifulSoup
from io import BytesIO
import re, datetime, pycurl, time, sys
from urllib.parse import urlencode

# Login to the webpage
def login(u, p):
	
	post_data = {'cid':'45','save':'1','loginphrase':u,'password':p,'x':'38','y':'7'}

	b = BytesIO()
	curl = pycurl.Curl()
	curl.setopt(curl.URL, 'https://services.jsatech.com/login.php?cid=45')
	curl.setopt(curl.POSTFIELDS, urlencode(post_data))
	curl.setopt(curl.WRITEDATA, b)
	curl.perform()
	curl.close()
	skey = b.getvalue().decode('iso-8859-1').split('skey=')[1].split('&')[0] # Bad practice

	# Not necessary?
	curl = pycurl.Curl()
	url = 'https://services.jsatech.com/login.php?cid=45&skey='+skey+'&fullscreen=1&wason='
	curl.setopt(curl.URL, url)
	curl.setopt(curl.WRITEDATA, b)
	curl.perform()
	curl.close()

	# Necessary
	curl = pycurl.Curl()
	url = 'https://services.jsatech.com/login-check.php?skey='+skey
	curl.setopt(curl.URL, url)
	curl.setopt(curl.WRITEDATA, b)
	curl.perform()
	curl.close()

	return skey

# Get the webpage with the list of mealswipes
def get_page(skey):
	time.sleep(1)
	post_data = {'save':'1','skey':skey,'cid':'45','accto':'106','month':str(month),'x':'38','y':'7'}

	b = BytesIO()
	curl = pycurl.Curl()
	curl.setopt(curl.URL, 'https://services.jsatech.com/statement.php?skey='+skey+'&cid=45&acctto=106')
	curl.setopt(curl.POSTFIELDS, urlencode(post_data))
	curl.setopt(curl.WRITEDATA, b)
	curl.perform()
	curl.close()

	return b.getvalue().decode('iso-8859-1')

# Print out usage information
def usage():
	print("Usage: main.py STUDENT_ID PASSWORD [WAIT_TIME]")
	quit()

wait = 0

# Check for arguments; needs to be improved (perhaps with argparse)
if len(sys.argv)!=3:
	if len(sys.argv)==4:
		try:
			wait = float(sys.argv[3])
		except Exception:
			print("Invalid wait time.")
			usage()
	else:
		usage()


now = datetime.datetime.now()

## Read in local list of mealswipes
# file = open("meals.html",'r')
# html = file.read()
# file.close()

month = now.month
low = now.day-(now.weekday()+2)
high = low+6


tot = 0
week = 0
swipes = 0

try:
	html = get_page(login(sys.argv[1],sys.argv[2]))
except Exception:
	print("There was an error accessing the page. Verify that your student ID and password were typed in correctly and try again later; if the problem persists, please submit a bug report.")
	quit()

try:
	soup = BeautifulSoup(html, 'html.parser')
	ex = str(month)+"\/%d+"
	for i in soup.find_all("td", "tablefirstcol"):
			name = i.next_sibling.next_sibling.string
			day = int(i.string.split("/")[1].split(" ")[0]) # Bad practice
			if day>=low and day<=high:
				week+=1
				if re.match("(Fountain|Clark|Case)",i.next_sibling.next_sibling.string)==None:
					swipes+=1
			tot += 1

except Exception:
	print("An unknown error occured. Please submit a bug report.")
print("You've used %d mealswipes this month, %d this week, and %d at restaurants this week." % (tot, week, swipes))