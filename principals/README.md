# New York City public schools principals
Web scraper for NYC public schools principal email addresses. Code details:

- parser.py: parse XML public NYC school data into a pandas DataFrame. The XML data are obtained through http://schools.nyc.gov/default.htm

- getEmails.py: web scraping tools (regular HTML and WIX Javascript pages supported)
- editDistance.py: approximate string matching (Levenshtein distance) for identifying the correct email address from the principal's name 
- main.py: SMTP client to deliver email messages to each principal
