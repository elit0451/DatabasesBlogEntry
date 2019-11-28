import os
import rdflib
import csv

from pymongo import MongoClient, TEXT, GEOSPHERE
from pprint import pprint
from rdflib import URIRef, Graph
from geotext import GeoText

booksDir = './Resources/Books'
catalogueDir = './Resources/Offline_Catalogue'
citiesFile = './Resources/cities5000.csv'

def runImport():
    bookPaths = os.listdir(booksDir)
    booksData = []

    for bookFile in bookPaths:
        bookId = bookFile[:-4]
        bookCataloguePath = catalogueDir + '/' + bookId + '/pg' + bookId + '.rdf'
        
        try:
            with open(booksDir + '/' + bookFile, 'r', encoding='utf-8') as content_file:
                content = content_file.read()
                cities = extractCities(content)
            
            graph = Graph()
            graph.parse(bookCataloguePath, format = 'xml')
            
            booksData.append((extractGraphInfo(graph), cities))
        except:
            print('Error in ' + booksDir + '/' + bookFile)
            
    
    #OLD SCHEMA METHODS
    importCityDataOld(citiesFile)
    importBooksDataOld(booksData)

    #NEW SCHEMA METHODS
    cities = readCitiesToMemory()
    importBooksDataNew(booksData, cities)
    



#IMPORTING AND DEFINING OLD SCHEMA

def importCityDataOld(path):
    db.geodata.delete_many({})
    db.geodata.drop_indexes()
    db.geodata.create_index([('city', TEXT)], name='city_index', default_language='english')
    db.geodata.create_index([('location', GEOSPHERE)], name='location_index')
    # '../Resources/cities5000.csv'
    with open(path,'r',encoding='utf-8', errors='replace') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        geodata = []
        for row in csv_reader:
            if(row[4] != '' and row[5] != ''):
            # coordinates: [longitude, latitude]
                datum = {
                    'city':str(row[2]),
                    'location':{
                        'type': 'Point',
                        'coordinates': [float(row[5]), float(row[4])]
                    }
                }
                geodata.append(datum)
                if(len(geodata) > 500):
                    db.geodata.insert_many(geodata)
                    geodata.clear()
        db.geodata.insert_many(geodata)
        print ('Finished importing cities //OLD SCHEMA')

def importBooksDataOld(booksData):
    db.books.delete_many({})
    db.books.drop_indexes()
    db.books.create_index([('author', TEXT)], name='author_index', default_language='english')
    books = []
    for data in booksData:
        book = {
            # data - tuple of (tuple of title and author) and cities
            'title': data[0][0],
            'author': data[0][1],
            'cities': list(data[1])
        }
        books.append(book)
        if(len(books) > 500):
            db.books.insert_many(books)
            books.clear()
    db.books.insert_many(books)
    
    print ('Finished importing books //OLD SCHEMA')




#IMPORTING AND DEFINING NEW SCHEMA

def readCitiesToMemory():
    # '../Resources/cities5000.csv'
    with open(citiesFile,'r',encoding='utf-8', errors='replace') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        cities = {}
        for row in csv_reader:
            if(row[4] != '' and row[5] != ''):
            # coordinates: [longitude, latitude]
                cities[str(row[2])] = (float(row[5]), float(row[4]))

        return cities

client = MongoClient('mongodb://localhost:27017/')
db=client.gutenberg


def importBooksDataNew(booksData, cities):
    db.newbooks.delete_many({})
    db.newbooks.drop_indexes()
    db.newbooks.create_index([('author', TEXT)], name='author_index', default_language='english')
    books = []
    # data - tuple of (tuple of title and author) and cities
    for data in booksData:
        bookCities = []
        for city in list(data[1]):
            try:
                bookCities.append({'name': city, 'location': cities[city]})
            except:
                pass
        
        newBook = {
            'title': data[0][0],
            'author': data[0][1],
            'cities': bookCities
        }
        books.append(newBook)
        if(len(books) > 500):
            db.newbooks.insert_many(books)
            books.clear()
    db.newbooks.insert_many(books)
    print('Finished importing books/cities //NEW SCHEMA')


#HELPER METHODS

def extractCities(text):
    places = set(GeoText(text).cities)
    return places

def extractGraphInfo(graph):
    title = ''
    agent = ''
    author = ''
    
    uri = rdflib.term.URIRef(u'http://purl.org/dc/terms/title')
    for o in graph.objects(subject=None, predicate=uri):
        title = o.replace('\r\n', ' ').replace('\n', ' ')
    
    uri = rdflib.term.URIRef(u'http://purl.org/dc/terms/creator')
    for o in graph.objects(subject=None, predicate=uri):
        agent = o
    
    uri = rdflib.term.URIRef(u'http://www.gutenberg.org/2009/pgterms/name')
    for o in graph.objects(subject=agent, predicate=uri):
        author = o.replace('\r\n', ' ').replace('\n', ' ')

    if(author == ''):
        author = 'Unknown'

    bookDetails = (title, author)
    return bookDetails

runImport()