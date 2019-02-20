#The way this program works is that it decides whether a blog entry is "useful"
#or garbage, and depending on that it classifies them

#In order to this it samples about 12 useful and 13 useless blog posts

#And then it looks at blog posts from a given range:

#X to Y

#These are specified in config.txt

#import urllib
from fractions import Fraction
import requests
import os,sys
import tkinter as tk
import json
#import html.parser
#install bs4 and 
from SPLIT import SPLIT 
from CLEAN import CLEAN
#from bs4 import UnicodeDammit

root = tk.Tk()
root.title('Crawling Chaos')
filesProcessed=tk.StringVar()

pause=0
eps=1e-6
contentCheckSample=100
minWordCount=20

#index=1
#currentBlogCount=56193

index=1
currentBlogCount = 100

smoothingValues  = [1,1,1]
types = 2


vocabulary = []
titleVocabulary = []
tagVocabulary = []
users = []

notKeyword = set()

#Type 1
#Tips/Tricks
#Type 2
#Others/Uncertain advice

#Prior
totalRead=0
occurences = [0 for t in range(0,types+1)]

wordCount=0
wordCounts = [0 for t in range(0,types+1)]

#Known Tags
totalTagCount=0
tagCounts = [0 for t in range(0,types+1)]


totalUserCount=0
userCounts = [0 for t in range(0,types+1)]

prior = {}
for t in range(1,types+1):
	prior[t] = Fraction(1,types)


occurencesWord = {}
occurencesTitle = {}
occurencesUser = {}
occurencesTag = {}

#P(word|type)
#Likelihood
likelihoodW = {}

#P(type|word)
#Posterior
posteriorW = {}


#P(user|type)
#Likelihood
likelihoodU = {}

#P(type|user)
#Posterior
posteriorU = {}


#P(user|type)
#Likelihood
likelihoodU = {}

#P(type|user)
#Posterior
posteriorU = {}


#P(tags|type)
#Likelihood
likelihoodT = {}

#P(type|tags)
#Posterior
posteriorUT= {}

def learn(stuff,classNumber,V,Occurences,totalWordCount,wordCounts,CaseDoesntMatter=False):
	for word in stuff:
		if not CaseDoesntMatter:
			word=word.upper()
		if not word in Occurences:
			Occurences[word] = dict()
			for t in range(0,types+1):
				Occurences[word][t] = 0
			V.append(word)
			totalWordCount+=1

		if not word in notKeyword:
			Occurences[word][classNumber] += 1
			Occurences[word][0]+=1
			wordCounts[classNumber]+=1
			
	return V,Occurences,totalWordCount,wordCounts

def calculatePosterior(a,b,c,d):
	return Fraction(a*b,a*b + c*d)

def train(classNumber):
	#print(classNumber)
	global totalRead, occurencesWord, notKeyword,wordCount,vocabulary,occurencesWord,wordCount,wordCounts
	global tagVocabulary,tagCounts,tagWords,occurencesTag,totalTagCount
	global users,userCounts,occurencesUser,totalUserCount

	with open("OOPS{}.txt".format(classNumber),"wb") as DEBUGGING: 
		for trainingData in os.listdir(str(classNumber))[1:]:
			with open(str(classNumber)+"/"+trainingData,"rb") as T: 

				if trainingData == ".DS_Store":
					continue

				occurences[classNumber]+=1
				totalRead+=1


				TD = T.read()
				DATA = json.loads(TD.decode("UTF-8").replace("\xa0", " ").replace("\xc2", " "))


				#DATA["result"]["content"]
				#DATA["result"]["tags"]
				#DATA["result"]["user"]
				#DATA["result"]["rating"]

				titleWords = SPLIT(CLEAN(DATA["result"]["title"]))
				tagWords = DATA["result"]["tags"]
				USER = DATA["result"]["authorHandle"]

				lotsOfWords=SPLIT(CLEAN(DATA["result"]["content"]))

				vocabulary,occurencesWord,wordCount,wordCounts=learn(titleWords,classNumber,vocabulary,occurencesWord,wordCount,wordCounts)
				vocabulary,occurencesWord,wordCount,wordCounts=learn(lotsOfWords,classNumber,vocabulary,occurencesWord,wordCount,wordCounts)
				tagVocabulary,occurencesTag,totalTagCount,tagCounts=learn(titleWords,classNumber,tagVocabulary,occurencesTag,totalTagCount,tagCounts)
				users,occurencesUser,totalUserCount,userCounts=learn(USER,classNumber,users,occurencesUser,totalUserCount,userCounts)


	if(classNumber<types):
		root.after(100,train(classNumber+1))
	else:
		root.after(100,progress)


def UnicodeConfoundIt(x):
	return UnicodeDammit(x)
def getData(x):
	#req = urllib.request.Request(x)
	#print (x)
	#with urllib.request.urlopen(x) as response:
		#received_data = response.read()
	#received_data  = requests.get(x, auth=('user', 'pass'))
	#received_data  = requests.get(x, auth=('user', 'pass'))
	received_data  = requests.get(x)
	return received_data
	#return "<html></html>"
def getComments(x):
	#with urllib.request.urlopen(x) as response:
		#received_data = response.read()
	#return received_data
	received_data  = requests.get(x)
	return received_data

def DataFormat(x,language="en"):
	return 'http://codeforces.com/api/blogEntry.view?blogEntryId={}&lang={}'.format(index,language)
def CommentFormat(x,language="en"):
	return 'http://codeforces.com/api/blogEntry.comments?blogEntryId={}&lang={}'.format(index,language)

def markHTML(HTML):
	return HTML.replace("trick","<color=#FF0000>trick</color>")

def checkData(HTML):
	return (HTML.find("trick")!=-1)

def progress():
	global pause, index, totalRead, occurencesW, notKeyword, wordCount, vocabulary,occurencesWord,wordCount,wordCounts
	global totalRead, occurencesWord, notKeyword,wordCount,vocabulary,occurencesWord,wordCount,wordCounts
	global tagVocabulary,tagCounts,tagWords,occurencesTag,totalTagCount
	global users,userCounts,occurencesUser,totalUserCount
	#print (index)
	if pause != 0:
		pause-=1
		return
		
	if(index <= currentBlogCount):
		try:
			blogDataEnglish = getData(DataFormat(index,"en"))
			blogCommentsEnglish = getComments(CommentFormat(index,"en"))
			blogDataRussian = getData(DataFormat(index,"ru"))
			blogCommentsRussian = getComments(CommentFormat(index,"ru"))
		except (Exception) as ex:
			filesProcessed.set("Something Went Wront At: {}".format(index))
			with open("errors.txt","ab") as T:
				T.write( ( "A(n) error occured while processing http://codeforces.com/blog/entry/{}:\n{};{}\n".format( str(index),type(ex).__name__, ex.args)+"\n").encode('utf-8') )
			if(index!=currentBlogCount):
				root.after(100,progress)

			return

		oneLanguage=False

		if(blogDataEnglish.status_code == 200) and (blogDataRussian.status_code == 200):
			if(json.loads( blogDataEnglish.text.replace("\xa0", " ").replace("\xc2", " ") )["status"]!="OK"):
				index+=1
				root.after(100,progress)
				return
			critPoint=blogDataRussian.text.find("title")
			#oneLanguage=False
			language="ru"
			if (blogDataRussian.text[critPoint+8]==blogDataEnglish.text[critPoint+8]):
				oneLanguage=True
				#print("Only one language available: {} {} {} {}".format(blogDataRussian.content[critPoint+8],blogDataRussian.content[critPoint+9],blogDataRussian.content[critPoint+10],blogDataRussian.content[critPoint+11]))
				if(blogDataRussian.content[critPoint+8] > 128):
					language="ru"
					#print ("RUSSIAN ONLY")
				else:
					language="en"
					#print ("ENGLISH ONLY")
		else:
			index+=1
			root.after(100,progress)
			return
		try:
			if not oneLanguage:
				#print ("Available in 2 languages")

				#For Blogs:
				BlogEnJSON=json.loads( blogDataEnglish.text.replace("\xa0", " ").replace("\xc2", " ") )["result"]
				BlogEnTitle = BlogEnJSON["title"] 
				BlogEnTagWords = BlogEnJSON["tags"]
				USER = BlogEnJSON["authorHandle"]
				BlogEnContent = SPLIT(CLEAN(BlogEnJSON["content"]) )
				BlogEnRating = BlogEnJSON["rating"] 
				
				BlogRuJSON=json.loads( blogDataRussian.text.replace("\xa0", " ").replace("\xc2", " ") )["result"]
				BlogRuTitle = BlogRuJSON["title"] 
				BlogRuTagWords = BlogRuJSON["tags"]
				#BlogRuUSER = BlogEnJSON["result"]["authorHandle"] Same as above
				BlogRuContent = SPLIT(CLEAN(BlogRuJSON["content"]) )
				BlogRuRating = BlogEnJSON["rating"] 

				titleWordsEn = SPLIT(BlogEnTitle)
				titleWordsRu = SPLIT(BlogRuTitle)

				if BlogEnRating < 0 or BlogRuRating < 0 or len(titleWordsEn)+len(BlogEnContent) < minWordCount  or len(titleWordsRu)+len(BlogRuContent) < minWordCount  :
					#EVERYTHING IS Type 2!
					vocabulary,occurencesWord,wordCount,wordCounts=learn(titleWordsEn,2,vocabulary,occurencesWord,wordCount,wordCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(BlogEnContent,2,vocabulary,occurencesWord,wordCount,wordCounts)
					tagVocabulary,occurencesTag,totalTagCount,tagCounts=learn(BlogEnTagWords,2,tagVocabulary,occurencesTag,totalTagCount,tagCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(titleWordsRu,2,vocabulary,occurencesWord,wordCount,wordCounts)
					tagVocabulary,occurencesTag,totalTagCount,tagCounts=learn(BlogRuTagWords,2,tagVocabulary,occurencesTag,totalTagCount,tagCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(BlogRuContent,2,vocabulary,occurencesWord,wordCount,wordCounts)
					users,occurencesUser,totalUserCount,userCounts=learn(USER,2,users,occurencesUser,totalUserCount,userCounts,True)
					
					with open("garbage.txt","ab") as T:
						Decision=0
						if(Decision<0.5):
							#T.write( (BlogEnTitle+": http://codeforces.com/blog/entry/{}".format(str(index))+"\n").encode('utf-8') )
							T.write( (BlogEnTitle+": http://codeforces.com/blog/entry/{} [Probability: {}]\n".format(str(index), str(round(1-float(Decision),4)) )).encode('utf-8'))

					filesProcessed.set("Currently At: {}".format(index))
					index+=1
					if(index!=currentBlogCount):
						root.after(100,progress)
					else:
						filesProcessed.set("Done!")
					return

				A1=Fraction(occurences[1] + smoothingValues[0],totalRead + smoothingValues[0]*2)
				A2=Fraction(occurences[2] + smoothingValues[0],totalRead + smoothingValues[0]*2)

				#English
				#Title
				for word in titleWordsEn[0:contentCheckSample]:
					word=word.upper()
					if word in occurencesWord:
						A1*=Fraction(occurencesWord[word][1]  + smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction(occurencesWord[word][2]  + smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
					else:
						A1*=Fraction( smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction( smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
				#Tag
				for tag in BlogEnTagWords:
					tag=tag.upper()
					if tag in occurencesTag:
						A1*=Fraction(occurencesTag[tag][1]  + smoothingValues[1] ,tagCounts[1] + totalTagCount*smoothingValues[1])
						A2*=Fraction(occurencesTag[tag][2]  + smoothingValues[1] ,tagCounts[2] + totalTagCount*smoothingValues[1])
					else:
						A1*=Fraction( smoothingValues[1] ,wordCounts[1] + totalTagCount*smoothingValues[1])
						A2*=Fraction( smoothingValues[1] ,wordCounts[2] + totalTagCount*smoothingValues[1])

				#Content
				for word in BlogEnContent[0:contentCheckSample]:
					word=word.upper()
					if word in occurencesWord:
						A1*=Fraction(occurencesWord[word][1]  + smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction(occurencesWord[word][2]  + smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
					else:
						A1*=Fraction( smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction( smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
				#Russian	
				#Title
				for word in titleWordsRu:
					word=word.upper()
					if word in occurencesWord:
						A1*=Fraction(occurencesWord[word][1]  + smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction(occurencesWord[word][2]  + smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
					else:
						A1*=Fraction( smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction( smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
				#Tag
				for tag in BlogRuTagWords:
					tag=tag.upper()
					if tag in occurencesTag:
						A1*=Fraction(occurencesTag[tag][1]  + smoothingValues[1] ,tagCounts[1] + totalTagCount*smoothingValues[1])
						A2*=Fraction(occurencesTag[tag][2]  + smoothingValues[1] ,tagCounts[2] + totalTagCount*smoothingValues[1])
					else:
						A1*=Fraction( smoothingValues[1] ,wordCounts[1] + totalTagCount*smoothingValues[1])
						A2*=Fraction( smoothingValues[1] ,wordCounts[2] + totalTagCount*smoothingValues[1])	

				#Content
				for word in BlogRuContent[0:contentCheckSample]:
					word=word.upper()
					if word in occurencesWord:
						A1*=Fraction(occurencesWord[word][1]  + smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction(occurencesWord[word][2]  + smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
					else:
						A1*=Fraction( smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction( smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
				#Common
				#User
				if USER in occurencesUser:
					A1*=Fraction(occurencesUser[USER][1]  + smoothingValues[2] ,userCounts[1] + totalUserCount*smoothingValues[2])
					A2*=Fraction(occurencesUser[USER][2]  + smoothingValues[2] ,userCounts[2] + totalUserCount*smoothingValues[2])
				else:
					A1*=Fraction( smoothingValues[2] ,userCounts[1] + totalUserCount*smoothingValues[2])
					A2*=Fraction( smoothingValues[2] ,userCounts[2] + totalUserCount*smoothingValues[2])

				#Decide
				Decision=Fraction(A1,A1+A2)
				#print(Decision)
				if(Decision>=0.5):
					vocabulary,occurencesWord,wordCount,wordCounts=learn(titleWordsEn,1,vocabulary,occurencesWord,wordCount,wordCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(BlogEnContent,1,vocabulary,occurencesWord,wordCount,wordCounts)
					tagVocabulary,occurencesTag,totalTagCount,tagCounts=learn(BlogEnTagWords,1,tagVocabulary,occurencesTag,totalTagCount,tagCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(titleWordsRu,1,vocabulary,occurencesWord,wordCount,wordCounts)
					tagVocabulary,occurencesTag,totalTagCount,tagCounts=learn(BlogRuTagWords,1,tagVocabulary,occurencesTag,totalTagCount,tagCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(BlogRuContent,1,vocabulary,occurencesWord,wordCount,wordCounts)
					users,occurencesUser,totalUserCount,userCounts=learn(USER,1,users,occurencesUser,totalUserCount,userCounts,True)
				else:
					vocabulary,occurencesWord,wordCount,wordCounts=learn(titleWordsEn,2,vocabulary,occurencesWord,wordCount,wordCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(BlogEnContent,2,vocabulary,occurencesWord,wordCount,wordCounts)
					tagVocabulary,occurencesTag,totalTagCount,tagCounts=learn(BlogEnTagWords,2,tagVocabulary,occurencesTag,totalTagCount,tagCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(titleWordsRu,2,vocabulary,occurencesWord,wordCount,wordCounts)
					tagVocabulary,occurencesTag,totalTagCount,tagCounts=learn(BlogRuTagWords,2,tagVocabulary,occurencesTag,totalTagCount,tagCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(BlogRuContent,2,vocabulary,occurencesWord,wordCount,wordCounts)
					users,occurencesUser,totalUserCount,userCounts=learn(USER,2,users,occurencesUser,totalUserCount,userCounts,True)

				with open("niceSources.txt","ab") as T:
					if(Decision>=0.5):
						#T.write( (BlogEnTitle+": http://codeforces.com/blog/entry/{}".format(str(index))+"\n").encode('utf-8') )
						T.write( (BlogEnTitle+": http://codeforces.com/blog/entry/{} [Probability: {}]\n".format(str(index),str(round(float(Decision),4)) )).encode('utf-8'))


				with open("garbage.txt","ab") as T:
					if(Decision<0.5):
						#T.write( (BlogEnTitle+": http://codeforces.com/blog/entry/{}".format(str(index))+"\n").encode('utf-8') )
						T.write( (BlogEnTitle+": http://codeforces.com/blog/entry/{} [Probability: {}]\n".format(str(index),str(round(1-float(Decision),4)) )).encode('utf-8'))

				#Check Title


				#Check Tags

				#Check Rating

				#Check Wording of ALL AVAILABLE LANGUAGES

				#Check User


				#Do Comments Later
				#Check Rating

				#For Comments:

				#Check Wording
				#Check User

			elif language == "en":
				#print ("Available in English exclusively")

				#For Blogs:
				BlogEnJSON=json.loads( blogDataEnglish.text.replace("\xa0", " ").replace("\xc2", " ") )["result"]
				BlogEnTitle = BlogEnJSON["title"] 
				BlogEnTagWords = BlogEnJSON["tags"]
				USER = BlogEnJSON["authorHandle"]
				BlogEnContent = SPLIT(CLEAN(BlogEnJSON["content"]) )
				BlogEnRating = BlogEnJSON["rating"] 

				titleWordsEn = SPLIT(BlogEnTitle)

				#print("{}: {}+{}".format(index,len(titleWordsEn),len(BlogEnContent) ))
				if BlogEnRating < 0  or len(titleWordsEn)+len(BlogEnContent) < minWordCount :
					#EVERYTHING IS Type 2!

					vocabulary,occurencesWord,wordCount,wordCounts=learn(titleWordsEn,2,vocabulary,occurencesWord,wordCount,wordCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(BlogEnContent,2,vocabulary,occurencesWord,wordCount,wordCounts)
					tagVocabulary,occurencesTag,totalTagCount,tagCounts=learn(BlogEnTagWords,2,tagVocabulary,occurencesTag,totalTagCount,tagCounts)
					users,occurencesUser,totalUserCount,userCounts=learn(USER,2,users,occurencesUser,totalUserCount,userCounts,True)

					with open("garbage.txt","ab") as T:
						Decision=0
						if(Decision<0.5):
							#T.write( (BlogEnTitle+": http://codeforces.com/blog/entry/{}".format(str(index))+"\n").encode('utf-8') )
							T.write( (BlogEnTitle+": http://codeforces.com/blog/entry/{} [Probability: {}]\n".format(str(index),str(round(1-float(Decision),4)) )).encode('utf-8'))
					filesProcessed.set("Currently At: {}".format(index))
					index+=1
					if(index!=currentBlogCount):
						root.after(100,progress)
					else:
						filesProcessed.set("Done!")
					return

				A1=Fraction(occurences[1] + smoothingValues[0],totalRead + smoothingValues[0]*2)
				A2=Fraction(occurences[2] + smoothingValues[0],totalRead + smoothingValues[0]*2)

				#English
				#Title
				for word in titleWordsEn:
					word=word.upper()
					if word in occurencesWord:
						A1*=Fraction(occurencesWord[word][1]  + smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction(occurencesWord[word][2]  + smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
					else:
						A1*=Fraction( smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction( smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
				#Tag
				for tag in BlogEnTagWords:
					tag=tag.upper()
					if tag in occurencesTag:
						A1*=Fraction(occurencesTag[tag][1]  + smoothingValues[1] ,tagCounts[1] + totalTagCount*smoothingValues[1])
						A2*=Fraction(occurencesTag[tag][2]  + smoothingValues[1] ,tagCounts[2] + totalTagCount*smoothingValues[1])
					else:
						A1*=Fraction( smoothingValues[1] ,wordCounts[1] + totalTagCount*smoothingValues[1])
						A2*=Fraction( smoothingValues[1] ,wordCounts[2] + totalTagCount*smoothingValues[1])
				#Content
				for word in BlogEnContent[0:contentCheckSample]:
					word=word.upper()
					if word in occurencesWord:
						A1*=Fraction(occurencesWord[word][1]  + smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction(occurencesWord[word][2]  + smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
					else:
						A1*=Fraction( smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction( smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
				#Common
				#User
				if USER in occurencesUser:
					A1*=Fraction(occurencesUser[USER][1]  + smoothingValues[2] ,userCounts[1] + totalUserCount*smoothingValues[2])
					A2*=Fraction(occurencesUser[USER][2]  + smoothingValues[2] ,userCounts[2] + totalUserCount*smoothingValues[2])
				else:
					A1*=Fraction( smoothingValues[2] ,userCounts[1] + totalUserCount*smoothingValues[2])
					A2*=Fraction( smoothingValues[2] ,userCounts[2] + totalUserCount*smoothingValues[2])

				#Decide
				Decision=Fraction(A1,A1+A2)
				#print(Decision)

				if(Decision>=0.5):
					vocabulary,occurencesWord,wordCount,wordCounts=learn(titleWordsEn,1,vocabulary,occurencesWord,wordCount,wordCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(BlogEnContent,1,vocabulary,occurencesWord,wordCount,wordCounts)
					tagVocabulary,occurencesTag,totalTagCount,tagCounts=learn(BlogEnTagWords,1,tagVocabulary,occurencesTag,totalTagCount,tagCounts)
					users,occurencesUser,totalUserCount,userCounts=learn(USER,1,users,occurencesUser,totalUserCount,userCounts,True)
				else:
					vocabulary,occurencesWord,wordCount,wordCounts=learn(titleWordsEn,2,vocabulary,occurencesWord,wordCount,wordCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(BlogEnContent,2,vocabulary,occurencesWord,wordCount,wordCounts)
					tagVocabulary,occurencesTag,totalTagCount,tagCounts=learn(BlogEnTagWords,2,tagVocabulary,occurencesTag,totalTagCount,tagCounts)
					users,occurencesUser,totalUserCount,userCounts=learn(USER,2,users,occurencesUser,totalUserCount,userCounts,True)

				with open("niceSources.txt","ab") as T:
					if(Decision>=0.5):
						#T.write( (BlogEnTitle+": http://codeforces.com/blog/entry/{}".format(str(index))+"\n").encode('utf-8') )
						T.write( (BlogEnTitle+": http://codeforces.com/blog/entry/{} [Probability: {}]\n".format(str(index),str(round(float(Decision),4)) )).encode('utf-8'))

				with open("garbage.txt","ab") as T:
					if(Decision<0.5):
						#T.write( (BlogEnTitle+": http://codeforces.com/blog/entry/{}".format(str(index))+"\n").encode('utf-8') )
						T.write( (BlogEnTitle+": http://codeforces.com/blog/entry/{} [Probability: {}]\n".format(str(index),str(round(1-float(Decision),4)) )).encode('utf-8'))


			else:
				#print("Available in Russian")
				#For Blogs:
				BlogRuJSON=json.loads( blogDataRussian.text.replace("\xa0", " ").replace("\xc2", " ") )["result"]
				BlogRuTitle = BlogRuJSON["title"] 
				BlogRuTagWords = BlogRuJSON["tags"]
				USER = BlogRuJSON["authorHandle"]
				#BlogRuUSER = BlogRuJSON["result"]["user"] Same as above
				BlogRuContent = SPLIT( CLEAN(BlogRuJSON["content"] ))
				BlogRuRating = BlogRuJSON["rating"] 

				titleWordsRu = SPLIT(BlogRuTitle)

				if BlogRuRating < 0  or len(titleWordsRu)+len(BlogRuContent) < minWordCount  :
					#EVERYTHING IS Type 2!
					vocabulary,occurencesWord,wordCount,wordCounts=learn(titleWordsRu,2,vocabulary,occurencesWord,wordCount,wordCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(BlogRuContent,2,vocabulary,occurencesWord,wordCount,wordCounts)
					tagVocabulary,occurencesTag,totalTagCount,tagCounts=learn(BlogRuTagWords,2,tagVocabulary,occurencesTag,totalTagCount,tagCounts)
					users,occurencesUser,totalUserCount,userCounts=learn(USER,2,users,occurencesUser,totalUserCount,userCounts,True)

					filesProcessed.set("Currently At: {}".format(index))

					index+=1
					if(index!=currentBlogCount):
						root.after(100,progress)
					else:
						filesProcessed.set("Done!")
					return

				A1=Fraction(occurences[1] + smoothingValues[0],totalRead + smoothingValues[0]*2)
				A2=Fraction(occurences[2] + smoothingValues[0],totalRead + smoothingValues[0]*2)

				#Russian	
				#Title
				for word in titleWordsRu:
					word=word.upper()
					#if (word=="ПЛОХО"):
						#print(index)
						#print( occurencesWord.get('ПЛОХО', "MISSING") )
					if word in occurencesWord:
						A1*=Fraction(occurencesWord[word][1]  + smoothingValues[0] , wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction(occurencesWord[word][2]  + smoothingValues[0] , wordCounts[2] + wordCount*smoothingValues[0])
					else:
						#if (word=="ПЛОХО"):
							#print(index)
							#print( occurencesWord.get('ПЛОХО', "MISSING") )
						A1*=Fraction( smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction( smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
				#Tag
				#print(index)
				for tag in BlogRuTagWords:
					#print(tag.encode("UTF-8"))
					tag=tag.upper()
					if tag in occurencesTag:
						A1*=Fraction(occurencesTag[tag][1]  + smoothingValues[1] ,tagCounts[1] + totalTagCount*smoothingValues[1])
						A2*=Fraction(occurencesTag[tag][2]  + smoothingValues[1] ,tagCounts[2] + totalTagCount*smoothingValues[1])
					else:
						A1*=Fraction( smoothingValues[1] ,wordCounts[1] + totalTagCount*smoothingValues[1])
						A2*=Fraction( smoothingValues[1] ,wordCounts[2] + totalTagCount*smoothingValues[1])	
				#Content
				for word in BlogRuContent[0:contentCheckSample]:
					word=word.upper()

					if word in occurencesWord:
						A1*=Fraction(occurencesWord[word][1]  + smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction(occurencesWord[word][2]  + smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
					else:
						A1*=Fraction( smoothingValues[0] ,wordCounts[1] + wordCount*smoothingValues[0])
						A2*=Fraction( smoothingValues[0] ,wordCounts[2] + wordCount*smoothingValues[0])
		
				#Common
				#User
				if USER in occurencesUser:
					A1*=Fraction(occurencesUser[USER][1]  + smoothingValues[2] ,userCounts[1] + totalUserCount*smoothingValues[2])
					A2*=Fraction(occurencesUser[USER][2]  + smoothingValues[2] ,userCounts[2] + totalUserCount*smoothingValues[2])
				else:
					A1*=Fraction( smoothingValues[2] ,userCounts[1] + totalUserCount*smoothingValues[2])
					A2*=Fraction( smoothingValues[2] ,userCounts[2] + totalUserCount*smoothingValues[2])

				#Decide
				Decision=Fraction(A1,A1+A2)
				#print(Decision)
				if(Decision>=0.5):
					vocabulary,occurencesWord,wordCount,wordCounts=learn(titleWordsRu,1,vocabulary,occurencesWord,wordCount,wordCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(BlogRuContent,1,vocabulary,occurencesWord,wordCount,wordCounts)
					tagVocabulary,occurencesTag,totalTagCount,tagCounts=learn(BlogRuTagWords,1,tagVocabulary,occurencesTag,totalTagCount,tagCounts)
					users,occurencesUser,totalUserCount,userCounts=learn(USER,1,users,occurencesUser,totalUserCount,userCounts,True)
				else:
					vocabulary,occurencesWord,wordCount,wordCounts=learn(titleWordsRu,2,vocabulary,occurencesWord,wordCount,wordCounts)
					vocabulary,occurencesWord,wordCount,wordCounts=learn(BlogRuContent,2,vocabulary,occurencesWord,wordCount,wordCounts)
					tagVocabulary,occurencesTag,totalTagCount,tagCounts=learn(BlogRuTagWords,2,tagVocabulary,occurencesTag,totalTagCount,tagCounts)
					users,occurencesUser,totalUserCount,userCounts=learn(USER,2,users,occurencesUser,totalUserCount,userCounts,True)

		except (Exception) as ex:
			with open("errors.txt","ab") as T:
				T.write( ( "A(n) error occured while processing http://codeforces.com/blog/entry/{}:\n{}\n".format( str(index),str(ex))+"\n").encode('utf-8') )

			"""
			with open("niceSources.txt","ab") as T:
				if(Decision>=0.5):
					T.write( (BloRuTitle+": http://codeforces.com/blog/entry/{}".format(str(index))+"\n").encode('utf-8') )

			with open("garbage.txt","ab") as T:
				if(Decision<0.5):
					T.write( (BlogRuTitle+": http://codeforces.com/blog/entry/{}".format(str(index))+"\n").encode('utf-8') )

			"""
		filesProcessed.set("Currently At: {}".format(index))

		index+=1
		if(index!=currentBlogCount):
			root.after(100,progress)
		else:
			filesProcessed.set("Done!")

def main():
    global index
    global currentBlogCount

    with open("config.txt","r") as CONFIG: 
        a = str(CONFIG.read()).split(" ")
        index, currentBlogCount = int(a[0]), int(a[1])

    print ("{}, {}".format(index, currentBlogCount))

    CurrentIndex=tk.Label(textvariable=filesProcessed)
    CurrentIndex.grid(row=0,column=0)

    filesProcessed.set("Initiating Training...")

    root.after(100,train(1))

    #root.after(100,read2)

    #root.after(100,progress)


    root.mainloop()


if __name__ == "__main__":
    main()



