        #with open ('C:/Users/Valued Client/Desktop/html/springerBooks.html', 'r', errors='ignore') as html_file:
        #content = html_file.read()
        #print(content)
        #soup = BeautifulSoup(content, 'html.parser')
        #
import bs4
from bs4 import BeautifulSoup
import os, sys
import requests
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
import random
import time
import json
from fake_useragent import UserAgent
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
import statistics
import requests
# session= HTMLSession()
# from .models import *
import re
def modes(allBookmarks,userID):
    title = ""
   

  
    allBookmarksdf = pd.DataFrame(allBookmarks)
    notOwnedBookmarks = allBookmarksdf[allBookmarksdf["isOwn"] == 0]
    notOwnedBookmarks = notOwnedBookmarks[notOwnedBookmarks["isMyRemoved"] == 0]
    ownedBookmarks = allBookmarksdf[allBookmarksdf["isOwn"] == 1 ]

    maxCount= ownedBookmarks["count"].max()
    mode = ownedBookmarks[ownedBookmarks["count"] == maxCount]
    # print(allBookmarksdf)

    if len(notOwnedBookmarks.index) == 0:
        print("empty not owned bookmarks")
        return []
    if len(mode.index) == 0:
        print("nothing  mode")
        return []

    elif len(mode.index) > 1:
        # print("modes", modes)
        highest = -1
        tfidf = TfidfVectorizer(stop_words='english')
        # mode['title'] = mode['title'].fillna('')
        tfidf_matrix = tfidf.fit_transform(mode['title'])
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

        
        # return []
        for i, row in enumerate(cosine_sim):
            summ=0
            for column in row:
                if column != 1.0 or column != 1:
                    summ = summ + column

            average = summ/(len(row))
            # print(average)
            if average >= highest:
                highest = average
                indexOfHighest_cosinesim = i
                # print(indexOfHighest_cosinesim)


        # for i, item in enumerate(modes['bookmark__title']):
        title = mode.iloc[indexOfHighest_cosinesim]

        # print("to find recommendation: (multiple  mode)", type(title["title"]),title["title"])
    else:
        title = mode
        # print("to find recommendation: (single mode)", title["title"])


    # a = allBookmarksdf 
    # b= a.append(mode)
    # c = b.drop_duplicates('title', keep='last')
    # d = c.iloc[:-len(mode) , :]
    # e= d.append(title)
    # # print("b:",b)
    # # print("c:",c)
    # print(e)
    # listFormat = e.to_dict('records')
    notOwnedBookmarks = notOwnedBookmarks.append(title)
    listFormat = notOwnedBookmarks.to_dict('records')
    bookmarks = pd.DataFrame(listFormat)

    return recommend(bookmarks, title)

def recommend(metadata, title):

    # metadata = bookmarkFrame 
    # print(bookmarkFrame)
    # print(metadata)
    tfidf = TfidfVectorizer(stop_words='english')

    tfidf_matrix = tfidf.fit_transform(metadata['title'])
  

    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    
    indices = pd.Series(metadata.index, index=metadata['title'])
    
    try:
        idx = indices[title["title"]]
        print("not dict")
    except:
        idx = indices[title["title"].to_dict()]
        print("to dict")
    # Get the pairwsie similarity scores of all movies with that movie
    try:
        sim_scores = list(enumerate(cosine_sim[idx[0]]))
    except:
        sim_scores = list(enumerate(cosine_sim[idx]))

    # # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    # Get top 5 similarity scores
    dataframe = pd.DataFrame(sim_scores)

    removeLowScores = dataframe[dataframe[1] > .20]

    cleanScores  = removeLowScores[removeLowScores[1] <= 0.80].values.tolist()
    # print(cleanScores)
    # Get the movie indices
    # print("dataframe",dataframe)

    # print("cleanScores:", cleanScores)
    movie_indices = [i[0] for i in cleanScores]
    meta = metadata.iloc[movie_indices]
    # print("metadata:", metadata)
    # print("movie_indices:",movie_indices)
    # print(meta)

    return meta.to_dict("records")







def scrape(word, refType, site, header, pageNumber):
    
  
    if site == 'Springeropen':
        return springer(word, refType,pageNumber)
    elif site == 'UNESCO_Digital_Library':
        return UNESCO(word, refType, pageNumber)
    elif site == 'Open_Textbook_Library':
        return OTL(word, refType, pageNumber)

    elif site == 'OER_Commons':
        return OER(word, refType, pageNumber)





# def render_html():
#     url = 'https://ocw.mit.edu/search/ocwsearch.htm?q=war'
#     r = session.get(url,headers=headers())
#     r.html.render(sleep=1,keep_page=True)
#     soup = BeautifulSoup(r.html.html, 'html.parser')
#     title = soup.findAll('div', class_='gsc-cursor-page', attrs={'class':'gsc-cursor-page', 'aria-label':'Page 3'})
#     title.click()
#     print(title)
#     # for i,a in enumerate(title):
#     #     print(a.text, i)



    

def UNESCO(word, refType, pageNumber):
    # isbn is for 
    rows =[]
    headers = {
        'authority': 'unesdoc.unesco.org',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"',
        'x-inmedia-authorization': 'Bearer null e2229ff2-73dd-498c-8c52-3f8694622c7b 310378718',
        'x-microsite-id': 'mainSite',
        'content-type': 'application/json',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34',
        'sec-ch-ua-platform': '"Windows"',
        'accept': '*/*',
        'origin': 'https://unesdoc.unesco.org',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://unesdoc.unesco.org/search/2bc5c5b6-62ce-4b5f-aa27-4679499c1830',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'consent_cookie_usage=agreed; _ga=GA1.3.1917778646.1638009010; _ga=GA1.2.1917778646.1638009010; _gid=GA1.3.155193290.1638167610; _gid=GA1.2.155193290.1638167610; JSESSIONID=8E242AEF08998954AA5D8316AD325D42; _gat_UA60257183=1',
    }
    x= False
    data = {}
    # print(refType)
    # return []
    while(x == False):
        try:
            if refType == 'article':
                data = '{"includeFacets":true,"order":"score_DESC;id_DESC","query":["'+word+'"],"queryid":"eecdadaf-edec-4c69-bc64-a5cd63ad754c","sf":"+TypeOfDocumentFacet:UnescoPhysicalDocument","mappedFQ":{"ZMATFacet":{"SER":false,"BKP":false,"STI":false,"ISS":false,"BKS":false,"DGN":false,"CIR":false,"PGD":false,"DEP":false,"MOV":false}},"pageNo":'+ str(pageNumber)+',"locale":"en"}'
            elif refType == 'book':
                data = '{"includeFacets":true,"order":"score_DESC;id_DESC","query":["'+word+'"],"queryid":"eecdadaf-edec-4c69-bc64-a5cd63ad754c","sf":"+TypeOfDocumentFacet:UnescoPhysicalDocument","mappedFQ":{"ZMATFacet":{"SER":false,"ART":false,"BKP":false,"STI":false,"ISS":false,"DGN":false,"CIR":false,"PGD":false,"DEP":false,"MOV":false}},"pageNo":'+ str(pageNumber)+',"locale":"en"}'
            elif refType == 'Programme_and_meeting_document':
                print("nisulod")
                # data = '{includeFacets:true,order:score_DESC;id_DESC,query:['+word+'],queryid:50276496-3adb-4f23-b494-df651f82d88d,sf:+TypeOfDocumentFacet:UnescoPhysicalDocument,mappedFQ:{ZMATFacet:{SER:false,ART:false,BKP:false,STI:false,ISS:false,BKS:false,DGN:false,CIR:false,DEP:false,MOV:false}},pageNo:'+ str(pageNumber)+',locale:en}'
                data = '{"includeFacets":true,"order":"score_DESC;id_DESC","query":["'+word+'"],"queryid":"eecdadaf-edec-4c69-bc64-a5cd63ad754c","sf":"+TypeOfDocumentFacet:UnescoPhysicalDocument","mappedFQ":{"ZMATFacet":{"SER":false,"ART":false,"BKP":false,"STI":false,"ISS":false,"BKS":false,"DGN":false,"CIR":false,"DEP":false,"MOV":false}},"pageNo":'+ str(pageNumber)+',"locale":"en"}'
            
            x = True
        except ConnectionError:
            print('Connection Error')

        except ConnectTimeout:
            print('Connect Timeout')
            
        except ReadTimeout:
            print('except')

    
    
    response = requests.post('https://unesdoc.unesco.org/in/rest/api/search', headers=headers, data=data)
    b = response.json()

    # for x in b:
    #     print(x,"\n\n\n")
    # # print(b['resultSet'])
    # return []
    for c in b['resultSet']:
        z=[]
        array = []
        title = c['title'][0]['value']  
        author = 'Author:  '
        link = 'https://unesdoc.unesco.org/ark:/' + c['ark'][0]['value']
        language = 'Language:  '
        dateYear = 'Year of Publication:  '
        isbn = 'ISBN:  '
        collation = 'Collation:  '

        try:
            if len(c['meta']['authorPerson']) > 1:
                for d in c['meta']['authorPerson']:
                    author = author+", " + d['value']
            else:
                author = author + c['meta']['authorPerson'][0]['value']
            
        except KeyError:
            try:
                if len(c['meta']['authorCorporate']) > 1 :
                    for d in c['meta']['authorCorporate']:
                        author = author+", " + d['value']
                else:
                    author = author + c['meta']['authorCorporate'][0]['value']
            except KeyError:
                author = 'Conference:  '
                try:
                    if len(c['meta']['authorEvent']) > 1 :
                        for d in c['meta']['authorEvent']:
                            author = author+", " + d['value']
                    else:
                        author = author + c['meta']['authorEvent'][0]['value']
                except:
                    author = None
        except:
            author=None


        try:
            if len(c['meta']['language']) > 1:
                for d in c['meta']['language']:
                    language = language+", "+ d['value']
            else:
                language = language+ c['meta']['language'][0]['value']
         
        except KeyError:
            language =''

        if len(c['meta']['dateYear']) > 1:
            for d in c['meta']['dateYear']:
                dateYear = dateYear+", "+ d['value']
        else:
            dateYear = dateYear+ c['meta']['dateYear'][0]['value']



        if refType == 'article':
            z.append(title)
            z.append(author)
            z.append(language)
            z.append(dateYear)
            z.append(link)
            rows.append(z)


        elif refType == 'book':
            try:
                if len(c['meta']['isbn']) > 1:
                    for d in c['meta']['isbn']:
                        isbn = isbn+", "+ d['value']
                else:
                     isbn = isbn + d['value']
            except:
                try:
                    isbn = "Document Code:  "
                    if len(c['meta']['callnumber']) > 1:
                        for d in c['meta']['callnumber']:
                            isbn = isbn +", "+ d['value']
                    else:
                         isbn = isbn + d['value']
               
                except:
                    isbn = ''

            try:
                if len(c['meta']['descriptionPhysical']) > 1:
                    for d in c['meta']['descriptionPhysical']:
                        collation =collation+ ", " + d['value']
                else:
                    collation =collation + d['value']
            except:
                collation = ''

            z.append(title)
            z.append(author)
            z.append(collation)
            z.append(language)
            z.append(isbn)
            z.append(dateYear)
            z.append(link)
            
            rows.append(z)

        elif refType == 'Programme_and_meeting_document': 
            isbn = "Document Code:  "
            try:
                
                if len(c['meta']['callnumber']) > 1:
                    for d in c['meta']['callnumber']:
                        isbn = isbn+", "+ d['value']
                else:
                     isbn = isbn + d['value']
            except:
                isbn = ''

            z.append(title)
            z.append(author)
            z.append(isbn)
            z.append(collation)
            z.append(language)
            
            z.append(dateYear)
            z.append(link)
            rows.append(z)

    return rows    
        

        # try:
        #     isbn ="ISBN: "+c['meta']['isbn'][0]['value']
        # except KeyError:
        #     isbn ="Document Code: "+c['meta']['callnumber'][0]['value']

        
        
        
         
       

        

    # headers = { # for next page 2 and so on
    # 'authority': 'unesdoc.unesco.org',
    # 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"',
    # 'x-inmedia-authorization': 'Bearer null 5e0790bc-ca31-40d3-9a28-3687b0b04d01 307434452',
    # 'x-microsite-id': 'mainSite',
    # 'content-type': 'application/json',
    # 'sec-ch-ua-mobile': '?0',
    # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34',
    # 'sec-ch-ua-platform': '"Windows"',
    # 'accept': '*/*',
    # 'origin': 'https://unesdoc.unesco.org',
    # 'sec-fetch-site': 'same-origin',
    # 'sec-fetch-mode': 'cors',
    # 'sec-fetch-dest': 'empty',
    # 'referer': 'https://unesdoc.unesco.org/search/b3f5ddbf-3e97-4641-8e07-97ab959cc31c',
    # 'accept-language': 'en-US,en;q=0.9',
    # 'cookie': 'consent_cookie_usage=agreed; _ga=GA1.3.1917778646.1638009010; _ga=GA1.2.1917778646.1638009010; JSESSIONID=C32D5FCB4761AF6EC52DC9E9E1423742; _gid=GA1.3.155193290.1638167610; _gat_UA60257183=1',
    # }

    ## for books:
    # data = '{"includeFacets":false,"order":"score_DESC;id_DESC","query":["war"],"queryid":"b3f5ddbf-3e97-4641-8e07-97ab959cc31c","sf":"+TypeOfDocumentFacet:UnescoPhysicalDocument","mappedFQ":{:{"ZMATFacet":{"SER":false,"ART":false,"BKP":false,"STI":false,"ISS":false,"DGN":false,"CIR":false,"PGD":false,"DEP":false,"MOV":false}},"pageNo":2,"pageSize":8,"locale":"en"}' 

    # response = requests.post('https://unesdoc.unesco.org/in/rest/api/search', headers=headers, data=data) 8 items per page, page start @ index 1



def OTL(word, refType, pageNumber): # pagination starts with index 1 diri
    rows =[]

    x = False
    while(x == False):
        try:
            if refType == 'Text_book':
                response = requests.get('https://open.umn.edu/opentextbooks/textbooks?term='+word+'&commit=Go&page='+str(pageNumber), headers = headers(), timeout=2) #articles 

            x = True
        except ConnectionError:
            print('Connection Error')

        except ConnectTimeout:
            print('Connect Timeout')
            
        except ReadTimeout:
            print('except')

    if refType == 'Text_book':
        soup = BeautifulSoup(response.content, 'html.parser')

        rowsss = soup.findAll('div', class_='col-sm-9 info')

        for row in rowsss:
            z=[]
            title = row.h2.text #title
            link = "https://open.umn.edu"+row.h2.a['href']
            author = row.p.text.replace('\n','  ') # 
            publisher = row.p.find_next().text.replace('\n','  ')
            description = row.p.find_next().find_next().text.replace('\n','  ')
            z.append(title)
            z.append(author)
            z.append(description)
            z.append(publisher)
            z.append(link)
            
        
            rows.append(z)

    return rows


def OER(word, refType, pageNumber): # paginattion diri ky sumpay walay page-page, by 10, 20,50,100 ang makita sa screen
    rows =[]
    
    pageNumber = int(pageNumber)

    # primary source
    # text book
    # teaching/learning startegy
    batch_start = 0
    batch_size = 10

    if (pageNumber)*10 > 10:
        batch_size = 20
    elif pageNumber*10 > 20:
        batch_size = 50
    elif pageNumber*10 > 50:
        batch_size = 100
    elif pageNumber*10 > 100:
        batch_start = 100
    elif pageNumber*10 > 200:
        batch_start = 200

    x = False
    while(x == False):
        try:
            response = requests.get('https://www.oercommons.org/search?batch_size='+str(batch_size)+'&batch_start='+str(batch_start)+'&sort_by=search&view_mode=summary&f.search='+ word+'&f.material_types=textbook&f.sublevel=college-upper-division&f.sublevel=graduate-professional&f.sublevel=career-technical&f.sublevel=community-college-lower-division', headers=headers(), timeout=3)
            x = True
            
        except ConnectionError:
            print('Connection Error')

        except ConnectTimeout:
            print('Connect Timeout')
            
        except ReadTimeout:
            print('except')


    soup = BeautifulSoup(response.content, 'html.parser')
    
    rowsss = soup.findAll('div', class_='item-details col-md-8 col-xs-11')
    
    for i,row in enumerate(rowsss):
        if i >= (pageNumber*10)-10: # get first 10 results in the page
            z=[]
            title = row.div.a.text # title
            link = row.div.a['href'] # link
            description = row.find('div', class_='abstract-short').p.text.replace('\n','').replace('  ','') # short description
            x = row.find('dl', class_='item-info visible-md-block visible-lg-block').dt
            array =[]
            
            try:
                while(x != None):
                    y = x.find_next_sibling()
                    array.append(x.text+" "+ y.text)
                    
                    x= y.find_next_sibling()
            except: 
                pass
                
            z.append(title)
            z.append(description)
            
            for item in array:
                z.append(item)
            
            z.append(link)
            
            rows.append(z)

        if i >= (pageNumber*10)-1:
            break
        
    return rows
   


def springer(word,refType, pageNumber): # INDEX 1 STARTING SA PAGINATION DIRI
    
    springers = []
    
    
    
    x = False
    while(x == False):
        try:
            if refType == 'article':
                response = requests.get('https://www.springeropen.com/search?searchType=publisherSearch&sort=Relevance&query=' + word +'&page='+ str(pageNumber), headers = headers(), timeout=2) #articles         
            elif refType == 'book':
                response = requests.get('https://link.springer.com/search/page/'+ str(1) +'?facet-content-type=%22Book%22&query='+word, headers = headers(), timeout=2) #books
            x = True
        except ConnectionError:
            print('Connection Error')

        except ConnectTimeout:
            print('Connect Timeout')
            
        except ReadTimeout:
            print('except')
        

    if refType == 'article':
        soup = BeautifulSoup(response.content, 'html.parser')
        a= soup.find('ol', class_='c-list-group c-list-group--bordered c-list-group c-list-group--md')

        if a != None: #find ol tag where naa ang rows sa list
            bb = a.findAll('li') #find li tag where nag contain sa rows

            for b in bb:
            
                            
                article = b.find('article') #find article tag
                if article != None:

                    div = article.find('div', class_='u-mb-16') #find div tag
                    a = div.h3  # extract title
                    p = div.find('p', class_='c-listing__authors u-mb-0') #extract authors
                    z = []
                                        
                    z.append(a.text.replace('\n','')) # store title to list
                    z.append(p.text) # store author to list
                    z.append(div.p.text) # store description of link to list
                    div2 = article.find('div',class_='c-meta')
                    z.append(div2.text) # store date&type to list
                    z.append("https:"+a.a['href'])
                   # extract link and store to list
                    
                    springers.append(z)
        return springers
    elif refType == 'book':
        # response = requests.get(' https://link.springer.com/search/page/'+ str(pageNumber) +'?query='+ word, headers = headers(), timeout=2) #books
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.findAll('a', class_="title")
        
        titles = soup.find_all('a', class_="title")

        
        for title in titles:
            z= []
            
            subtitle = title.findNext("p", class_="subtitle")
            p_tag__meta = title.parent.findNext("p", class_="meta")
            # print(i,p_tag__meta.span.a , p_tag__meta.findNext("span", class_="year"))

            try:
                author = p_tag__meta.span.a.text +"  " +p_tag__meta.findNext("span", class_="year").text
            except:
                author = p_tag__meta.span.span.text +"  " +p_tag__meta.findNext("span", class_="year").text

            z.append(title.text)
            if subtitle.text != "" and not subtitle.text.isspace() and len(subtitle.text) > 5:
                z.append(subtitle.text)

            
            if author != "" or not author.isspace() or len(author) > 5:
                z.append(author)
            
            z.append("https://link.springer.com"+title["href"])


            springers.append(z)

        return springers

def details(link, proxy,website, refType ):
   

    if website == "Springeropen":
        # with open ('C:/Users/Valued Client/Desktop/html/sprigner DETAILS.html', 'r', errors='ignore') as html_file:
        #     content = html_file.read()
            # soup = BeautifulSoup(content, 'html.parser')
        if refType == 'article':
            try:
                response = requests.get('https://'+link, headers=headers())
            except:
                response = requests.get(link, headers=headers())

            soup = BeautifulSoup(response.content, 'html.parser')
            descrip = soup.find('div', class_='c-article-section__content').p.text
            description = descrip[:500]
            # print(len(description))
            # if len(description) > 1000:
            #     a = soup.find('h3', text='Conclusion')
            #     print(a.next)
            abbr_tag = soup.find('abbr', text = "DOI")
            doi = abbr_tag.findNext('span', class_="c-bibliographic-information__value").text

            
            details={
                'websiteTitle': website,
                'itemType': refType,
                'author': soup.find('div', class_='c-article-header').find('ul', class_='c-article-author-list js-etal-collapsed').text,
                'description': description,
                'journalItBelongs': soup.find('i', attrs={'data-test':'journal-title'}).text,
                'volume': soup.find('b', attrs={'data-test':'journal-volume'}).text[7:],
                'publishYear': soup.find('span', class_="c-bibliographic-information__value").text,
                'doi': doi, 
                'subtitle':'',
                'citation':'',
                'downloads':'',
                'publisher':'',
                'edition':'',
                'pages':''
                
            }
            

                
            # websiteTitle = refType[0]
            # itemType = refType[1]
            
            return details


        elif refType == 'book':
            response = requests.get(link + '#about',headers=headers())
            soup = BeautifulSoup(response.content, 'html.parser')


            if soup.find('div', class_='unique-selling-points unique-selling-points--collapsed u-mb-36') == None:
                description = ''
            else:
                description = soup.find('div', class_='unique-selling-points unique-selling-points--collapsed u-mb-36').text

            if soup.find('span', id='bookcitations-count-number') == None:
                cite = ''
            else:
                cite = soup.find('span', id='bookcitations-count-number').text
            
            if soup.find('h2', class_='page-title__subtitle') == None:
                subtitle = ''
            else:
                subtitle = soup.find('h2', class_='page-title__subtitle').text

            if soup.find('h1', attrs={"itemprop":"name"}) == None:
                if soup.find('h1', class_='app-journal-header__title') == None:
                    title = ''
                else:
                    title= soup.find('h1', class_='app-journal-header__title').text
            else:
                title= soup.find('h1', attrs={"itemprop":"name"}).text
            details={
                'websiteTitle': website,
                'itemType': refType,
                'title': title,
                'subtitle': subtitle,
                'description': description,
                'citation': cite,
                'downloads': soup.find('span', class_='test-metric-count article-metrics__views').text,
                'author': soup.find('ul', class_='test-contributor-names').text,
                'publisher': soup.find('span', attrs={"itemprop":"name"}).text,
                'edition': soup.find('span', id='edition-number').text,
                'pages': soup.find('span', id='number-of-pages').text,
                'doi': soup.find('span', id='doi-url').text,
                'journalItBelongs': '',
                'volume': '',
                'publishYear': '',
            }

            return details

   
    elif website == "UNESCO_Digital_Library":
        cookies = {
            '_ga': 'GA1.2.1337792028.1638176102',
            'JSESSIONID': 'F458670F72A749861CFD2B7ED4F08D6E',
            '_gid': 'GA1.2.682840214.1643440906',
        }

        

        params = (
            ('ark', link.replace("https://unesdoc.unesco.org","")),
            ('_', '1643445318321'),
        )

        response = requests.get('https://unesdoc.unesco.org/in/rest/api/resolveArk', headers=headers(), params=params, cookies=cookies)
        responseData = response.json()
        detail = responseData["collectionData"]
        author = ""
        # if refType == "Programme_and_meeting_document":
        try:
            author = detail["authorCorporate"]
        except:
            try:
                author = detail["authorPerson"]["Answer"]
            except:
                pass

        try:
            abstract = detail["abstract"]
        except:
            try:
                abstract = detail["noteGeneral"]
            except:
                abstract = ""

        
        details={
            'websiteTitle': website.replace("_", " "),
            'itemType': refType.replace("Programme_and_meeting_", " "),
            'author': author,
            'description': abstract,
            'journalItBelongs': '',
            'volume': '',
            'publishYear': detail["dateYear"],
            'doi': detail["identifierILS"], 
            'subtitle':'',
            'citation':'',
            'downloads':'',
            'publisher':'',
            'edition':'',
            'pages':''
            
        }
        return details

    elif website == "Open_Textbook_Library":
        response = requests.get(link,headers=headers())
        soup = BeautifulSoup(response.content, 'html.parser')

        description = soup.find('section', id = "AboutBook").p.text
        author = ""
        # if soup.find('section', id = "Contributors") != None:
        authors = soup.find('section', id = "Contributors").find_all("strong")
        for a in authors:
            author = author + ", "+a.text
        print(author)
        try:
            isbn = soup.find('p', text = re.compile("ISBN 13:")).text.replace("ISBN 13:","")
        except:
            isbn = ""
        details={
                'websiteTitle': website.replace("_"," "),
                'itemType': refType,
                'subtitle': "",
                'description': description,
                'citation': '',
                'downloads': '',
                'author': author,
                'publisher': '',
                'edition': '',
                'pages': '',
                'doi': '',
                'journalItBelongs': '',
                'volume': '',
                'publishYear': soup.find('p', text = re.compile("Copyright Year")).text.replace("Copyright Year:",""),
                'ISSN': isbn
            }

        return details
    elif website == "OER_Commons":
        response = requests.get(link,headers=headers())
        soup = BeautifulSoup(response.content, 'html.parser')

        description = soup.find("dl", class_="materials-details-abstract").dd

        all__dd_tag = soup.find("dl", class_="materials-details-first-part").find_all("dd")
        # subtitle = dl_tag.dd
        subtitle = all__dd_tag[0].text
        author = all__dd_tag[3].text
        print(website)

        details={
                'websiteTitle': website.replace("_"," "),
                'itemType': refType,
                'subtitle': subtitle,
                'description': description.text,
                'citation': '',
                'downloads': '',
                'author': author,
                'publisher': '',
                'edition': '',
                'pages': '',
                'doi': '',
                'journalItBelongs': '',
                'volume': '',
                'publishYear': '' ,
                'ISSN': ''
            }

        return details
def scienceDirect(word,proxy, refType, pageNumber, header):
    scienceDirects = []
    scienceLinks = []
    #ua = random.choice(userAgents) 
    headers = {
    'authority': 'www.sciencedirect.com',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Microsoft Edge";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://id.elsevier.com/',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': 'EUID=80a39c81-5643-43a6-a14d-dbdeb3ff56f9; utt=ae01-efa25bdbb71478802a627452c2319959fc3-A; AMCVS_4D6368F454EC41940A4C98A6%40AdobeOrg=1; __gads=ID=cbccebd4b239d1b9:T=1634873619:S=ALNI_MbKgsfwajTBcaYJMjf-VEiMK5cN_g; mboxes=%7B%22universal-view-pdf%22%3A%7B%22variation%22%3A%22A%22%7D%2C%22login-intermediate-page%22%3A%7B%22variation%22%3A%22B%22%7D%7D; SD_ART_LINK_STATE=%3Ce%3E%3Cq%3Escience%3C%2Fq%3E%3Corg%3Erslt_list%3C%2Forg%3E%3Cz%3Erslt_list_item%3C%2Fz%3E%3CsrcFr%3Erslt_list_item%3C%2FsrcFr%3E%3Crdt%3E2021%2F10%2F31%2F13%3A02%3A47%3A933%3C%2Frdt%3E%3Cenc%3EN%3C%2Fenc%3E%3C%2Fe%3E; __cf_bm=YrisfCns8p2z8ZZHzzjsm5nrdSeQ24kgyTez1vjjlw4-1636341385-0-AfO28+touQnJ+aAFzCvzn6WCJUyzI06yFSVTDr21BWQ8TwxF0PGr4qHLLNrFUQR6jQgFMiZrmpfHT27QDBKdcfz9hq/Cf/dUeVvo9FX21lk6; acw=4736891373ac114c545b5af0416165e484ddgxrqa%7C%24%7CC7567E508BB27F0AD5635AC3D279072A6E49DE75273610E54C84238FDA27FE09DAC91C7CC2088AD67DC4507B13AC5E7DDC1CE1FFCC1DF7F03FBA44D1BD4E4F2EB0469A67597464825D387A21AFA2E514; fingerPrintToken=298693a32e804ab0b2513bc3a48802f9; mbox=session%23a16c9dd3c28146179d4e14055ed5c400%231636343500%7CPC%23a16c9dd3c28146179d4e14055ed5c400.34_0%231699586440; sd_access=eyJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..XY8C06otiUe0iCqt41nacw.f9hu3we5h6QHt-39HS1f7iTu0L_bYiyszOObB6jFKwGJ0QH-M12-_QDN8AEgSkXhSiAEVXTSLVN4uftBJXpxGhJoBeiWMljtYT8fDBee9nyJScBEDHxdzTAyXA64Bi2yNqWz42ZRhz7m2xKr8VB8kA.gVqctdV9io2lBtpUkOUP6w; sd_session_id=7013f5299d49c04a76895ef7d9cfb5d83787gxrqa; id_ab=IDP; has_multiple_organizations=true; MIAMISESSION=c99c2c87-1a5d-4301-bb44-4aab50adf504:3813794463; SD_REMOTEACCESS=eyJhY2NvdW50SWQiOiI3MzA5NCIsInRpbWVzdGFtcCI6MTYzNjM0MTY2Mzk5M30=; AMCV_4D6368F454EC41940A4C98A6%40AdobeOrg=-2121179033%7CMCIDTS%7C18940%7CMCMID%7C81261105090677501200180261852203688591%7CMCAID%7CNONE%7CMCOPTOUT-1636348869s%7CNONE%7CMCAAMLH-1636946469%7C3%7CMCAAMB-1636946469%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CvVersion%7C5.3.0%7CMCCIDH%7C-388222836; s_pers=%20v8%3D1636341673263%7C1730949673263%3B%20v8_s%3DLess%2520than%25207%2520days%7C1636343473263%3B%20c19%3Dsd%253Ahome%253Ahpx%7C1636343473269%3B%20v68%3D1636341664028%7C1636343473274%3B; s_sess=%20s_cpc%3D0%3B%20e78%3Dqs%253Dcancer%3B%20c21%3Dqs%253Dtsunami%3B%20e13%3Dqs%253Dtsunami%253A1%3B%20c13%3Drelevance-desc%3B%20s_sq%3D%3B%20s_ppvl%3Dsd%25253Ahome%25253Ahpx%252C21%252C21%252C969%252C1239%252C969%252C1920%252C1080%252C1%252CP%3B%20s_cc%3Dtrue%3B%20e41%3D1%3B%20s_ppv%3Dsd%25253Ahome%25253Ahpx%252C21%252C21%252C969%252C1239%252C969%252C1920%252C1080%252C1%252CP%3B',
    }
    
    x = False
    while(x == False):
        try:
            if refType == 'journal':
                response = requests.get('https://www.sciencedirect.com/browse/journals-and-books?contentType=JL&searchPhrase='+ word, headers=headers, proxies={'https:': proxy}, timeout= 5)
                x = True
            else:
                response = requests.get('https://www.sciencedirect.com/browse/journals-and-books?contentType=BK&searchPhrase='+ word, headers=headers, proxies={'https:': proxy}, timeout= 5) # books
                x = True
        except ConnectionError:
                print('Connection Error')
                return False

        except ConnectTimeout:
            print('Connect Timeout')
                
        except ReadTimeout:
            print('except')
        
    
    soup = BeautifulSoup(response.content, 'html.parser')
    lli= soup.findAll('li', class_='publication branded u-padding-xs-ver js-publication')

    for li in lli:
        z = []
                    
        z.append(li.a.text)
        p = li.div.p
        pp = li.div.find('p', class_='u-display-inline u-clr-grey8') 

        if refType == 'journal':
            if pp != None:
                ppp = pp.find('span')
                            
                z.append( "Journal ● " + ppp.text)
            else:
                z.append( "Journal")
        else:
            if(li.p.text != 'Book'):
                z.append(li.p.text)
            z.append(li.div.text)



        scienceLinks.append('https://www.sciencedirect.com/' + li.a['href'])
        scienceDirects.append(z)

    if(soup.find('a', text='Sign in')):
        print("Cookies expired")
    else:
        print("Cookies not expired")
   
    return scienceDirects, scienceLinks


def scirp(word, refType, pageNumber):
    
    scirp = []
    scirpLinks = []         
    
    # x = False
    # while(x == False):
    #     try:
    #         if refType == 'article':
    #             response = requests.get('https://www.scirp.org/journal/articles.aspx?searchcode='+ word+'&searchfield=All&page=1', headers = headers(),  timeout=2) # article                   #
    #             x = True
    #         else:
    #             response = requests.get('https://www.scirp.org/journal/articles.aspx?searchcode='+ word +'&searchfield=jname&page=1&skid=0', headers = headers(), timeout=2) #journal
    #             x = True
    #     except ConnectionError:
    #         print('Connection Error')
    #         return False

    #     except ConnectTimeout:
    #         print('Connect Timeout')
                
    #     except ReadTimeout:
    #         print('ReadTimeout')
        
    if refType == 'article':
        response = requests.get('https://www.scirp.org/journal/articles.aspx?searchcode='+ word+'&searchfield=All&page=1', headers = headers(),  timeout=2) # article                   #
        
    else:
        response = requests.get('https://www.scirp.org/journal/articles.aspx?searchcode='+ word +'&searchfield=jname&page=1&skid=0', headers = headers(), timeout=2) #journal
    soup = BeautifulSoup(response.content, 'html.parser')
    a=soup.find('ul', class_='list-unstyled list_link').findAll('li')
   
    for i in a:
        z = []
        x = i.find('div', class_='list_unit') #get container of rows
        z.append(i.div.text) # get title
        z.append(i.find('div', class_='txt5').text) #author 
        z.append(i.find('div', class_='list_unit').text.replace('¼Œ', ' ')) #get other info
        z.append(i.find('div', class_='list_doi').text) 
        scirp.append(z)

        
        scirpLinks.append('https://www.scirp.org/journal/' + i.div.span.a['href'])

    return scirp, scirpLinks








def tandFOnline(word, proxy, refType, pageNumber): # INDEX ZERO MAG START ILANG PAGE

    results= []
    links = []
        
    
    
    if refType == 'article':
        x = False
        while(x == False):
            
            try:
                response = requests.get('https://www.tandfonline.com/action/doSearch?AllField='+ word +'&pageSize=10&subjectTitle=&startPage='+ str(pageNumber), headers = headers(), proxies={'https:': proxy}, timeout=3) # article
                x = True
            except ConnectionError:
                print('Connection Error')
                return False

            except ConnectTimeout:
                print('Connect Timeout')
                
            except ReadTimeout:
                print('except')
                
        soup = BeautifulSoup(response.content, 'html.parser')
        rows = soup.findAll('article', class_='searchResultItem')

        for row in rows:
            z=[]
            z.append(row.find('a', class_='ref nowrap').text) #title
            z.append(row.find('div', class_='author').text) #author
            z.append(row.find('div', class_='publication-meta').text) #others
            z.append(row.find('span', class_='publication-year').text) #date

            
            results.append(z)
            links.append('https://www.tandfonline.com' + row.find('a', class_='ref nowrap')['href'])
        return results, links

    elif refType == 'journal':
        x = False
        while(x == False):
            
            try:
                response = requests.get('https://www.tandfonline.com/action/doSearch?AllField='+ word +'&target=titleSearch&content=title&pageSize=10&subjectTitle=&startPage='+str(pageNumber) , headers = headers(), proxies={'https:': proxy}, timeout=3) # journals
                x = True
            except ConnectionError:
                print('Connection Error')
                return False

            except ConnectTimeout:
                print('Connect Timeout')
                
            except ReadTimeout:
                print('Read Timeout')

        soup = BeautifulSoup(response.content, 'html.parser')
        rows =soup.findAll('li', class_='searchResultItem browse-result')

        for row in rows:
            z = []
            z.append(row.find('a', class_='ref').text) #title
            z.append(row.find('h3').text)

            results.append(z)
            links.append('https://www.tandfonline.com' + row.find('a', class_='ref')['href'])
        return results, links

    elif refType == 'database':
        x = False
        while(x == False):
            
            try:
                response = requests.get('https://www.tandfonline.com/action/doSearch?AllField='+ word +'&content=db&target=database&pageSize=10&subjectTitle=&startPage='+ str(pageNumber) , headers = headers(), proxies={'https:': proxy}, timeout=3) # journals
                x = True
            except ConnectionError:
                print('Connection Error')
                return False

            except ConnectTimeout:
                print('Connect Timeout')
                
            except ReadTimeout:
                print('except')

        soup = BeautifulSoup(response.content, 'html.parser')
        rows =soup.findAll('article', class_='searchResultItem')

        for row in rows:
            z = []
            z.append(row.find('a', class_='ref').text) #title
            z.append(row.find('span', class_='entryAuthor search-link hlFld-ContribAuthor').text) # author
            z.append(row.find('div', class_='publication-meta').text) # source

            results.append(z)
            links.append('https://www.tandfonline.com' + row.find('a', class_='ref')['href'])
        return results, links


    



        
def herdin(word, proxy,refType, pageNumber): # INDEX ZERO ANG STARTING SA ILA PAGINATION
    results = []
    links = []
    x = False
    while(x == False):
        try:
            if refType == 'journal':
                response = requests.get('https://www.herdin.ph/index.php?option=com_herdin&view=publiclistowp&layout=list&type=researches&searchstr='+ word +'&res_source=journal&start=' + pageNumber, headers = headers(), proxies={'https:': proxy}, timeout=3) #article                                       
                x = True
            elif refType == 'book' :
                
                response = requests.get('https://www.herdin.ph/index.php?option=com_herdin&view=publiclistowp&layout=list&type=researches&searchstr='+ word + '&res_source=book&start=' + pageNumber, headers = headers(), proxies={'https:': proxy}, timeout=3) #books 
                x = True
            elif refType == 'research project' :
                response = requests.get('https://www.herdin.ph/index.php?option=com_herdin&view=publiclistowp&layout=list&type=researches&searchstr='+ word + '&res_source=research_project&start=' + pageNumber, headers = headers(), proxies={'https:': proxy}, timeout=3) #books 
                x = True
            elif refType == 'resident research' :
                response = requests.get('https://www.herdin.ph/index.php?option=com_herdin&view=publiclistowp&layout=list&type=researches&searchstr='+ word + '&res_source=resident_research&start=0'+ pageNumber, headers = headers(), proxies={'https:': proxy}, timeout=3) #books 
                x = True
            elif refType == 'thesis' :
                response = requests.get('https://www.herdin.ph/index.php?option=com_herdin&view=publiclistowp&layout=list&type=researches&searchstr='+ word + '&res_source=thesis/dissertation&start=0' + pageNumber, headers = headers(), proxies={'https:': proxy}, timeout=3) #books 
                x = True

        except ConnectionError:
            print('Connection Error')
            return False

        except ConnectTimeout:
            print('Connect Timeout')
                
        except ReadTimeout:
            print('Read timeout')

    soup = BeautifulSoup(response.content, 'html.parser')
    rows = soup.findAll('div',attrs={'style':'overflow: hidden; padding-left: 5px;'})

    
    for row in rows:
        z = []
        z.append(row.find('h4', attrs={'style':'line-height:1.5; text-align:justify;'}).text) # title

        if row.find('div', attrs={'name':'opt1'}) != None:
            z.append(row.find('div', attrs={'name':'opt1'}).text.replace('\n','').replace('\xa0','')) # author

        z.append(row.find('div', attrs={'name':'opt2'}).text.replace('\n','').replace('\xa0','')) # source

        if row.find('div', attrs={'name':'opt3'}) != None:
            z.append(row.find('div', attrs={'name':'opt3'}).text.replace('\n','').replace('\xa0','')) # abstract

        z.append(row.find('div', attrs={'name':'opt4'}).text.replace('\n','').replace('\xa0','')) # others
        z.append(row.find('div', attrs={'name':'opt5'}).text.replace('\n','').replace('\xa0','')) # author

        results.append(z)

        links.append('https://www.herdin.ph' + row.find('h4', attrs={'style':'line-height:1.5; text-align:justify;'}).a['href'])
            
    return results, links


def zLibrary(word, proxy,refType, pageNumber):

    results = []
    links = []

    x = False
    while(x == False):
        try:
            if refType == 'article':
                response = requests.get('https://booksc.org/s/'+ word, headers = headers(), proxies={'https:': proxy}, timeout=2) # article
                x = True
            elif refType == 'book':
                response = requests.get('https://1lib.ph/s/'+ word, headers = headers(), proxies={'https:': proxy}, timeout=2) #books 
                x = True
        except ConnectionError:
            print('Connection Error')
            return False

        except ConnectTimeout:
            print('Connect Timeout')
                
        except ReadTimeout:
            print('Read Timeout')
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    if refType == 'book':
        rows = soup.findAll('td', attrs={'style':'vertical-align: top;'})

        for row in rows:
            z= []
            z.append(row.find('h3', attrs={'itemprop':'name'} ).text.replace('\n','')) # title
            z.append(row.find('div', class_='authors' ).text) #author
            if row.find('div', attrs={'title':'Publisher'} ) != None:
                z.append(row.find('div', attrs={'title':'Publisher'} ).text) # publisher
            z.append(row.find('div', class_='bookDetailsBox').text)
            
            results.append(z)
            links.append('https://1lib.ph' + row.find('h3', attrs={'itemprop':'name'}).a['href'])

        return results, links


    elif refType == 'article':
        rows = soup.findAll('tr',class_='bookRow')

        for row in rows:
            z= []
            z.append(row.find('h3', attrs={'itemprop':'name'} ).text.replace('\n','').replace('â€“','-')) # title

            z.append(row.find('div', class_='authors' ).text) #author

            if row.find('div', attrs={'title':'Publisher'} ) != None:
                z.append(row.find('div', attrs={'title':'Publisher'} ).text) # publisher

            z.append(row.find('div', class_='bookDetailsBox').div.text.replace('\n',' ')) # journal of the 

            stringPosition = row.find('div', class_='bookDetailsBox').text.find('Year')
            z.append(row.find('div', class_='bookDetailsBox').text[stringPosition:].replace('\n',' ')) # journal of the 

            results.append(z)
            links.append('https://booksc.org' + row.find('h3', attrs={'itemprop':'name'}).a['href'])
            
            
        return results, links

            






    



def proxy_generator1():

    response = requests.get('https://www.proxynova.com/proxy-server-list/country-ph/', headers = headers())
    soup = BeautifulSoup(response.content, 'html.parser')
    
        
    page= soup.find('textarea', class_='form-control')
    a =page.text
    proxies = a[75:].split("\n")
    #print(proxies)
    print(proxies)
    return proxies


def proxy_generator2():
    proxies = []
    
    for x in range(2):
        
        headers = {
        'authority': 'www.proxyhub.me',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="94", "Microsoft Edge";v="94", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 Edg/94.0.992.50',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.proxyhub.me/en/ph-https-proxy-list.html',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '__gads=ID=6c6661a0f109efd0-2246a8b0b9cc0070:T=1634804154:RT=1634804154:S=ALNI_MZZ5TnlvEI8S1B6-41Yln5ggLyG4A; page='+ str(x+1) +'; anonymity=all',
        }

        response = requests.get('https://www.proxyhub.me/en/ph-https-proxy-list.html', headers = headers)
        soup = BeautifulSoup(response.content, 'html.parser')
     
        rows = soup.find('tbody').findAll('tr')
         
        for row in rows:
            z = []
            x = 0
            columns = row.findAll('td')
            for column in columns:
                if x >= 2:
                    break
                
                z.append(column.text.replace(' ', '').replace('\n', ''))
                if(z[0] != '' and len(z) == 1):
                    z.append(":")
                x += 1
           
            if len(z) > 1: 
                proxies.append(''.join(z)) 
        print("Number of proxies extracted: ",len(proxies))
        time.sleep(10)
       

    proxyList = list(dict.fromkeys(proxies))
    # print(proxyList[91])

    return proxyList
    

   

    

    #with open('C:/Users/Valued Client/Desktop/proxies.txt', 'w') as file:    / writing in a file /
    
    #with open ('C:/Users/Valued Client/Desktop/free proxy.html', 'r', errors='ignore') as html_file:   / opening a file /
            #content = html_file.read()
            #soup = BeautifulSoup(content, 'html.parser')

        #response = requests.get("https://free-proxy-list.net/")
        #soup = BeautifulSoup(response.content, 'html.parser')
        ##mylist = list(dict.fromkeys(mylist))
        #print(a.readline())   / reading a line in the file/
        #rows = page.text
        
        #tr = page.findAll('tr')
        #rowCtr = 0
        
        #for row in tr:
            #columnCtr = 0
            #temp =[]
            #if rowCtr > 0 and rowCtr < 21:
                #for column in row:
                    #temp.append(column.text)
                    #columnCtr = columnCtr + 1

            #if len(temp) != 0:
                #if (temp[4] == 'elite proxy' and temp[6] == 'yes'):
                    #file.write('https://' + temp[0] + ':' + temp[1] + "\n")
            
            #rowCtr = rowCtr + 1





def headers(): 
    ua = UserAgent()

    headers = {
                    'user-agent': ua.random,
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'accept-language': 'en-US,en;q=0.9',
                    'referer': 'https://ocw.mit.edu/',
                    'Upgrade-Insecure-Requests': '1',          
    }
    return headers


    

def testProxy(proxies, ptype):
    a = False

    while a == False:

        if ptype == 1:
            try:
                p = random.choice(proxies)
                print(p.proxy + ': ')
                response = requests.get('https://google.com', proxies={'https:':p.proxy} ,timeout=1)
                print('new proxy assigned')
                a = True
                return p.proxy
            except:
                print( "                   Connection error ")
                pass
        else:
            try:
                response = requests.get('https://google.com', proxies={'https:':proxies} ,timeout=1)
                print(proxies + ' working\n')
                a = True
                return proxies
            except:
                print(proxies,' not working\n')
                return False
        
            
            # if the request is successful, no exception is raised
       
        




def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]



