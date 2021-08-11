#Backup includes capability to save and load JSON

from WikipediaArticle import WikipediaArticle
import json #For exporting

all_articles = []

#start = "Barack Obama" #input("What do you want to start with? eg. 'Barack Obama'")
start = input("What do you want to start with? (eg. 'Dog'): ")

print("START OF SEARCH:", start)

starting_article = WikipediaArticle(start)
starting_article.search_and_set_page()
starting_article.filter(10)
all_articles.append(starting_article)

print("PARSING LINKS OF:", starting_article.page_name)
for link in starting_article.links_filtered:
	curr_article = WikipediaArticle(link)
	curr_article.search_and_set_page()


	if not curr_article.error: # Throws error when search doesn't deliver results
		curr_article.filter(2)
		all_articles.append(curr_article)


#Saving JSON to file
with open("data.json", "wt") as data_file:   #data.txt should exist, "wt" for writing and text
	all_articles_dict = [article.__dict__ for article in all_articles]
	# List comprehension: newlist = [expression for item in iterable if condition == True]
	# WikipediaArticle Object cannot be stored directly
	# .__dict__ Converts to dictionary which can be saved

	json_articles = json.dumps(all_articles_dict) 

	data_file.write(json_articles)
	print("SAVING:", "with len", len(all_articles_dict))


#Reading JSON from file
with open("data.json", "rt") as data_file:   #data.txt should exist, "rt" for reading and text
	opened_json_articles = data_file.read()

	opened_dict_articles = json.loads(opened_json_articles) # Is dictionary
	print("OPENED:", "with len", len(opened_dict_articles))

	all_articles = [WikipediaArticle(**article) for article in opened_dict_articles]
	print("IMPORTED ARTICLES:", "with len", len(opened_dict_articles))

	# List comprehension: newlist = [expression for item in iterable if condition == True]
	#And using "keywords arguments" (**kwargs)


