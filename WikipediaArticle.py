'''
Requires:
pip install wikipedia
OR
pip install git+https://github.com/lucasdnd/Wikipedia.git

Helpful:
https://stackabuse.com/getting-started-with-pythons-wikipedia-api/

Issues:
- Is "wikipedia-api" API faster?
- Filter smartly
	- By links in summary => parse HTML 
	- Maybe with "Backlinks" or "links point to this site"
- Let user choose starting node if there is disambiguation -JUP-
- starting article not existent -JUP-
'''

import wikipedia as wiki

from bs4 import BeautifulSoup
import requests
import urllib.parse

def suggest_article(text):
	return wiki.search(text)


class WikipediaArticle():
	"""
	-- An Wikipedia Article --
	
	Use it like this:
	
	article = WikipediaArticle(ARTICLE_NAME_HERE)

	article.get_wikipedia_object() 
	#This way access links, links_filtered e.g.
		article.page.links_filtered
	#and summary
		article.summary
	

	article.get_links_in_summary()
	#Very fast way to access important links and summary as html
		article.links_from_summary
		article.summary_html


	"""

	def __init__(self, search_term, language = "en", is_starting_article = False): 
		wiki.set_lang(language) 
		self.search_term = search_term
		self.page_name = self.search_term 

		self.language = language
		self.is_starting_article = is_starting_article

		#These will be set through 'get_wikipedia_object()'
		self.links_filtered = None
		self.summary = None
		self.page = type('', (), {})() #This somehow just creates an empty object
		self.page.links = None
		# Access links, references, content, title and url through 
		# self.page.links
		
		#These will be set through 'get_links_in_summary()'
		self.summary_html = None
		self.links_from_summary = None

		#Error thrown if article couldn't be found
		self.error = False

	def get_wikipedia_object(self):

		try:
			print("[*] TRYING (api): ", self.page_name)	
			self._set_page()

		except wiki.DisambiguationError as e:
			if self.is_starting_article == True: # User input for starting article
				self._solve_disambiguation(e.options)

			else:
				print("[*] GUESSING: ", best_guess)
				best_guess = e.options[1] # Take the first of the options
				self.page_name = best_guess

		except wiki.PageError as e:
			print("[!] ERROR! Page doesnt exist:", self.page_name)
			self.error = True
			return

	def _set_page(self): # Can be used directly if there is no disambiguation for sure
		self.page = wiki.page(self.page_name, auto_suggest = False, preload=False) 
		self.summary = wiki.summary(self.page_name, auto_suggest = False)
		# Auto suggestion causes weird errors. Like "Dog" turning to "Do" in the search

	def get_links_in_summary(self): # Via "requests" and HTML parsing
		phrase_formatted = self.search_term.replace(" ", "_")
		phrase_formatted = urllib.parse.quote(phrase_formatted)

		self.url = "https://" + self.language + ".wikipedia.org/wiki/" + phrase_formatted
		print("[*] TRYING (html): ", self.url)	
		
		raw_html = requests.get(self.url)
		html = BeautifulSoup(raw_html.text, 'html.parser') 
		# This is the page in HTML in parseable format
		parent = html.find('div', class_ = "mw-parser-output")
		
		if parent == None: #Parent is None if the page isnt found
			self.error = True
			print("[!] ERROR! Page doesnt exist:", self.search_term)

		else:
			summary = []
			links_filtered = []
			
			reached_summary = False
			for child in parent.children:
				if child.name == "p" and child.text.strip() != "": #There can be empty <p> tags
					reached_summary = True
					summary.append(child)
			
				elif reached_summary == True: #Then the end of summary is reached
					break
			
			for part in summary: #Extract links of painfully found <a> tags
				links = part.find_all("a")
				for link in links:
					try:
						link_string = link["href"].replace("/wiki/", "")
						#This takes the 'href' attribute of the <p> and removes "/wiki/"
						#And sometimes it just doesnt work
					except KeyError as e:
						print(e)
					link_string = urllib.parse.unquote(link_string) 
					# This will replace %27 with ' and %E2%80%93 with - and so on

					if self._is_real_link(link_string) and link_string not in links_filtered:
						links_filtered.append(link_string)

			print("[+] success, links found: " + str(len(links_filtered)))
			self.links_from_summary = links_filtered
			
	def _is_real_link(self, link_string):
		if link_string[0:11] == "#cite_note-":
			return False

		if link_string[0:5] == "Help:":
			return False

		if link_string[0:5] == "File:":
			return False
		
		return True			

	def solve_disambiguation(self, options):
		print("Did you mean:")

		for numbered_option in enumerate(options): 
			# enumerate gives key value pairs like (0, "African Dog")
			print(numbered_option[0], ":", numbered_option[1])

		given = input("(Type number or just enter to take the first): ")

		if given == '':
			self.page_name = options[0]

		else:
			try:
				given_index = int(given)
				self.page_name = options[given_index]
				print("[*] CHOOSE: ", self.page_name)

			except:
				print("[!] ERROR! Option doesnt exist:", given)
				self.error = True
				return
		self._set_page()

	def filter(self, num): 
		# Filter links
		if self.page.links != None:
			self.links_filtered = self.page.links[:num] # Get first ... links

		#self.links_filtered = numpy.array(self.page.links)[:num] 
		# Using numpy should be faster but isnt ... hmmm
