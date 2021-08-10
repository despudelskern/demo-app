'''
Requires 
pip install wikipedia
OR
pip install git+https://github.com/lucasdnd/Wikipedia.git

Helpful:
https://stackabuse.com/getting-started-with-pythons-wikipedia-api/

ToDO:
- Let user choose starting node if there is disambiguation
- Error Handling with API
	- starting article not existent
'''


import wikipedia as wiki
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

	def __init__(self, search_term, language = "en"): 
		wiki.set_lang(language) 
		self.search_term = search_term

		self.page_name = None
		self.page = None

		self.links = None
		self.links_filtered = None
		self.references = None
		self.references_filtered = None
		self.categories = None
		self.categories_filtered = None
		self.content = None
		self.content_filtered = None

		self.title = None
		self.url = None
		self.summary = None

		self.error = False

	def search_and_set_page(self):
		self.page_name = self.search_term 

		try:
			print("TRYING: ", self.page_name, end=' ')	
			self.set_page()
			print("{*} SUCCESS")

		except wiki.DisambiguationError as e:
			best_guess = e.options[1] #Take the first of the options
			print("GUESSING: ", best_guess)

			self.page_name = best_guess
			self.set_page()

		except wiki.PageError as e:
			print("ERROR! Page doesnt exist:", self.page_name)
			self.error = True
			return

	def set_page(self): # Can be used directly if there is no disambiguation for sure
		self.page = wiki.page(self.page_name, auto_suggest=False) 
		self.summary = wiki.summary(self.page_name, auto_suggest=False)
		# Auto suggestion causes weird errors. Like "Dog" turning to "Do" in the search

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



