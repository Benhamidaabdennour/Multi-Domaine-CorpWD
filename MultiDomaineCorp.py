#You may need to enable these two commandes if your punkt isn't installed
#once dowloaded and installed nltk will work perfectly fine
#import nltk
#nltk.download('punkt')

'''
Next Imports are tools we need for our code to work properly
-Wikipedia: API for wiki articles, installation is required (pip install wikipedia or pip3 if doesn't work)
-re.sub: function that alllow as to delete portions of text that are or not in the text
-word_tokenize: we use to tokenize (split) our texts into a list of words
-request exception to handle connection errors and timeouts
-sleep for time out exeptions handling
-langdetect: a tool that detects languages, so that we don't return any article that is not 
written in the language we want
'''
import wikipedia #https://wikipedia.readthedocs.io/en/latest/code.html#api
import os
import json
from re import sub #https://docs.python.org/3/library/re.html
from nltk import ngrams
from nltk.tokenize import word_tokenize
from requests import exceptions as RExceptions
from time import sleep
from langdetect import detect

Corpora = {} #variable returned as context in django

def getGrams(KeyChain):

    NewKeyChains = []
    Splited = KeyChain.split()
    Grams = list(ngrams(Splited,3))
    for Gram in Grams:
        NewKey = ""
        for item in Gram:
            NewKey = NewKey + item + " "
        NewKey = NewKey[:len(NewKey)-1]
        NewKeyChains.append(NewKey)
    
    if NewKeyChains == []:
        return KeyChain.replace(" "," ")
    else:
        return NewKeyChains

def BuildCorp(Domaines, Name):
    Lang = detect(Domaines)
    wikipedia.set_lang(Lang)#setting the language of search
    Domaines = getGrams(Domaines)
    Count = 0
    Count2 = 0
    Articles = {}
    GroupedText = ""

    for Domaine in Domaines: #each domaine on the list will have it's own search on the wiki dump

        Tags = wikipedia.search(Domaine, results = 200) #this fuction returns a list of keywords related to our domain

        for Article in Tags:
            try:
                #creating a key value couple as "title": "content" and retreiving only arabic from the wiki page (no numbers, no special caracters or punctuation)
                if Lang == "ar":
                    Articles[wikipedia.page(Article).title] = sub(r'[^\u0600-\u06ff\u0750-\u077f\ufb50-\ufbc1\ufbd3-\ufd3f\ufd50-\ufd8f\ufd50-\ufd8f\ufe70-\ufefc\uFDF0-\uFDFD]+',' ',wikipedia.page(Article).content)
                else:
                    Articles[wikipedia.page(Article).title] = sub(r'[^A-Za-z]+', ' ',wikipedia.page(Article).content)
                Count = Count + len(word_tokenize(Articles[wikipedia.page(Article).title]))
                Count2 = Count2 + 1
                print(Count2)
                GroupedText = GroupedText + " " + Articles[wikipedia.page(Article).title]
                #exceptions handling ..
            except wikipedia.exceptions.DisambiguationError as DE:
                '''
                this exception is raised whenever the wiki server can't determin which keyword is the best
                for our domaine, so in order to avoid any ambiguations, the programme will pop that tag from 
                the list for now (19/06/2020)
                '''
                Tags.pop(Tags.index(Article))
            except wikipedia.exceptions.HTTPTimeoutError as TE:
                #if a timeout exception is raised we will wait 5seconds and then it will automatically re-run
                sleep(3)
                continue
            except RExceptions.ConnectionError as CE:
                print("ConnextionFailed")
                continue
            except wikipedia.exceptions.PageError as PE:
                #if a "PageError" was raised, we ignore it and continue to next page
                continue
    #Computing the number of diffrent words in the corp we just created
    GlobalWolrdsList = word_tokenize(GroupedText)
    DIffWordsList = []
    for Word in GlobalWolrdsList:
        if Word in DIffWordsList:
            continue
        else:
            DIffWordsList.append(Word)

    #Finihing other key value couples that might be needed
    Corpora["Articles"] = Articles
    Corpora["ArticlesCount"] = len(Articles)
    Corpora["WordsCount"] = Count
    Corpora["DiffWordsCount"] = len(DIffWordsList)
    Corpora["Name"] = Name
    Corpora["Type"] = "MultiDomaine"

    #Saving into a json file
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_file = os.path.join(THIS_FOLDER, Name + '.json')

    write_file = open(my_file, "w")
    json.dump(Corpora, write_file, indent=2)
    write_file.close()
