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

#import numpy # For Runtime purposes

class WikipediaArticle():
	"""
	-- An Wikipedia Article --
	
	initialize with 
	WikipediaArticle(ARTICLE_NAME_HERE)

	to use given PAGE_NAME call 
	search_and_set_page() 

	then all attributes seen below in __init__ are usable:
	"""

	def __init__(self, search_term, language = "en", is_starting_article = False): 
		wiki.set_lang(language) 
		self.search_term = search_term
		self.language = language

		self.page_name = None
		self.page = None
		# Access links, references, content, title and url through 
		# self.page.links

		self.links_filtered = None
		self.references_filtered = None
		self.categories_filtered = None
		self.content_filtered = None

		self.summary = None

		self.is_starting_article = is_starting_article
		self.error = False

	def search_and_set_page(self):
		self.page_name = self.search_term 

		try:
			print("[*wiki] TRYING: ", self.page_name)	
			self.set_page()

		except wiki.DisambiguationError as e:
			if self.is_starting_article == True: # User input for starting article
				self.solve_disambiguation(e)

			else:
				print("[*] GUESSING: ", best_guess)
				best_guess = e.options[1] # Take the first of the options
				self.page_name = best_guess

		except wiki.PageError as e:
			print("[!] ERROR! Page doesnt exist:", self.page_name)
			self.error = True
			return

	def get_links_in_summary(self): # Via "requests" and HTML parsing

		phrase_formatted = self.search_term.replace(" ", "_")

		self.url = "https://" + self.language + ".wikipedia.org/wiki/" + phrase_formatted
		print("[*html] TRYING: ", self.url)	
		
		raw_html = requests.get(self.url)
		html = BeautifulSoup(raw_html.text, 'html.parser')
		
		parent = html.find('div', class_ = "mw-parser-output")
		
		if parent == None: #Parent is None if the page isnt found
			self.error = True
			print("[!] ERROR! Page doesnt exist:", self.search_term)

		else:
			summary = []
			links_filtered = []
			
			reached_summary = False
			for child in parent.children:
				if child.name == "p" and child.text.strip() != "":
					reached_summary = True
					summary.append(child)
			
				elif reached_summary == True: #Then the end of summary is reached
					break
			
			for part in summary: #Extract links of painfully found <a> tags
				links = part.find_all("a")
				for link in links:
					link_string = (link["href"]).replace("/wiki/", "")
					if "#cite_note-" not in link_string:
						links_filtered.append(link_string)
			
			print(links_filtered)
			self.links_filtered = links_filtered
			self.page = type('', (), {})() #This somehow just creates an empty object
			self.page.links = links_filtered



	def set_page(self): # Can be used directly if there is no disambiguation for sure
		self.page = wiki.page(self.page_name, auto_suggest = False, preload=False) 
		self.summary = wiki.summary(self.page_name, auto_suggest = False)
		# Auto suggestion causes weird errors. Like "Dog" turning to "Do" in the search

	def solve_disambiguation(self, e):
		print("Did you mean:")

		for numbered_option in enumerate(e.options): 
			# enumerate gives key value pairs like (0, "African Dog")
			print(numbered_option[0], ":", numbered_option[1])

		given = input("(Type number or just enter to take the first): ")

		if given == '':
			self.page_name = e.options[0]

		else:
			try:
				given_index = int(given)
				self.page_name = e.options[given_index]
				print("[*] CHOSE: ", self.page_name)

			except:
				print("[!] ERROR! Option doesnt exist:", given)
				self.error = True
				return
		self.set_page()

	def filter(self, num): # Filter out data
		self.filter_links(num)
		#self.filter_content(num)
		#self.filter_references(num)
		#self.filter_categories(num)

	def filter_links(self, num):
		self.links_filtered = self.page.links[:num] # Get first ... links

		#self.links_filtered = numpy.array(self.page.links)[:num] 
		# Using numpy should be faster but isnt ... hmmm
	
	def filter_content(self, num):
		self.content_filtered = self.page.content[:num]

	def filter_references(self, num):
		self.references_filtered = self.page.references[:num]

	def filter_categories(self, num):
		self.categories_filtered = self.page.categories[:num]



