'''
Backup includes capability to save and load JSON

Requires 
pip install wikipedia
OR
pip install git+https://github.com/lucasdnd/Wikipedia.git

Helpful:
https://stackabuse.com/getting-started-with-pythons-wikipedia-api/

ToDO:
- Should first set page not search 
- Let user choose starting node if there is disambiguation
- Error Handling with API
	- starting article not existent
	- No options


'''


import wikipedia as wiki

class WikipediaArticle():
	"""
	-- An Wikipedia Article --
	
	initialize with 
	WikipediaArticle(ARTICLE_NAME_HERE)

	to use given PAGE_NAME call 
	search_and_set_page() 

	then all attributes seen below in __init__ are usable:
	"""


	def __init__(self, search_term, language = "en", \
		page_name = None, links = None, links_filtered = None, page = None, content = None, \
		content_filtered = None, title = None, url = None, references = None, \
		references_filtered = None, categories = None, categories_filtered = None, \
		summary = None, error = False): 
		# Weird init attributes are needed to recreate article from JSON
		# Because of the "keywords arguments" (**kwargs)
		
		wiki.set_lang(language) 

		self.search_term = search_term 
		self.page_name = page_name
		self.page = page

		self.links = links
		self.links_filtered = links_filtered
		self.references = references
		self.references_filtered = references_filtered
		self.categories = categories
		self.categories_filtered = categories_filtered
		self.content = content
		self.content_filtered = content_filtered

		self.title = title
		self.url = url
		self.summary = summary

		self.error = error

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
		
		self.remove_page_attr() 
		# self.page Object cannot be converted to JSON, so we have to delete it


	def set_page(self): # Can be used directly if there is no disambiguation for sure
		self.page = wiki.page(self.page_name, auto_suggest=False) 
		self.summary = wiki.summary(self.page_name, auto_suggest=False)
		# Auto suggestion causes weird errors. Like "Dog" turning to "Do" in the search

	def filter(self, num): # Filter out data
		self.filter_links(num)
		self.filter_content(num)
		self.filter_references(num)
		self.filter_categories(num)

	def filter_links(self, num):
		self.links_filtered = self.links[:num] # Get first ... links

	def filter_content(self, num):
		self.content_filtered = self.content[:num]

	def filter_references(self, num):
		self.references_filtered = self.references[:num]

	def filter_categories(self, num):
		self.categories_filtered = self.categories[:num]

	def remove_page_attr(self): 
		# self.page Object cannot be converted to JSON, so we have to delete it and reassign
		self.links = self.page.links
		self.content = self.page.content
		self.title = self.page.title
		self.url = self.page.url
		self.references = self.page.references
		self.categories = self.page.categories

		self.page = None


