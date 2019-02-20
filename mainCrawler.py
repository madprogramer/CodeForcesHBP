import re, cgi, sys, os, requests


# UTILIY
#
#

#Adapted From: https://stackoverflow.com/a/19730306/2089784
#Cleans HTML TAGS
def CLEAN(mess):
	tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
	no_tags = tag_re.sub('', mess)
	ready = cgi.escape(no_tags)
	return ready
#Adapted From: https://stackoverflow.com/a/3801846/2089784
#Splits strings into words, but also splits Chinese sentences into characters
def SPLIT(s):
    regex = []
    # Match a whole word:
    regex += [r'\w+']

    # Chinese Characters
    regex += [r'[\u4e00-\ufaff]']
    
    #Thai Characters
    #regex += [r'[\u0e00–\u0e7f]']

    # Match one of anything else, except for spaces:
    regex += [r'[^\s]']

    regex = "|".join(regex)
    r = re.compile(regex)

    return r.findall(s)


# String Formatting Utilies
#
#

def BlogDataURL(x,language="en"):
	return 'http://codeforces.com/api/blogEntry.view?blogEntryId={}&lang={}'.format(x,language)

def saveFileFor(x, target="/saves", language = "en")
	return target+'/{}{}'.format(language,x)

# Error Handling
#
#

#Checks Range
def checkRange(r):
	try:
		start,end = r[0],[1]
		if end<start:
			raise ValueError('Error: Invalid Range')
	except:
		print("Error: Invalid Range")
		sys.exit(2)


#Check Crawled File CAN BE Saved
def checkCanSave(f):
	try:
		print("not implemented yet")
		pass
	except:
		print("Error: Can't Save File: {}".format(f))
		raise ValueError("won't save")

#Check Crawled File WAS Saved
def checkWasSaved(f):
	try:
		print("not implemented yet")
		pass
	except:
		print("Error: Unable to Locate Saved File {}".format(f))
		raise ValueError("wasn't saved")

# SUBTASKS
#
#

def grab(index):
	address = BlogDataURL(index)
	return requests.get(address)

def saveToFile(index,data,language='en',path=''):
	with open(saveFileFor(index),"w") as F:
		F.write(data)

# MAIN
#
#

def main(argv):
	checkRange(argv)
	start,end = argv[0],argv[1]
	for i in range(start,end+1):
		try: 
			data = grab(i)
			saveToFile(i,data)
		except:
			print('An error occured at index {}\n Skipping...'.format(i))
	print('done.')


if __name__ == "__main__":
    main(sys.argv[1:])
