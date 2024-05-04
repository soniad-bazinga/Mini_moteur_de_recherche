
from frequency_score import frequence_score
from flask import Flask, render_template, request
import nltk
import csv
import re 
import urllib.parse
from nltk.corpus import stopwords
nltk.download('stopwords')


csv.field_size_limit(100000000)

#fonction qui convertit les titres des pages en vrais liens wikipedia 
def convert_to_wikipedia_links(result_pages):
    with open('filtered_pages.csv', mode = 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        id_to_title = {row['ID']: row['Title'] for row in reader}
    real_page_links = {}  #dictionanire des vrais liens wikipedia 
    for page_data in result_pages: #liste de dictionnaires
        page_id = page_data['page_id'] 
        if page_id in id_to_title:
            page_title = id_to_title[page_id]
            cleaned_title = page_title.replace(' ', '_')
            encoded_title = urllib.parse.quote(cleaned_title)
            wiki_link = f'https://fr.wikipedia.org/wiki/{encoded_title}'
            real_page_links[page_id] = (page_title, wiki_link)
    return real_page_links

def cleanRequestWords(text) : 
    #1. supprimer les chiffres ou caractères spéciaux
    newtext = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    #5. remplacer les ponctuations par des espaces
    newtext = re.sub(r'[^\w\s]', ' ', newtext) 
    return newtext



# pour nettoyer la requete: enlever les 'stop' words et les doublons
def remove_stopwords_and_duplicates_as_list(text):
    stop_words = set(stopwords.words('french'))
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    filtered_text = ' '.join(filtered_words)
    unique_words = []
    for word in filtered_text.split():
        if word not in unique_words:
            cleaned_word = cleanRequestWords(word)
            unique_words.append(cleaned_word)
    return unique_words



app = Flask(__name__)  #instance 


#traitement de la requete
def process_request(request):
    clean_request = remove_stopwords_and_duplicates_as_list(request)  #traitement de la requete
    #calcul des scores 
    result = frequence_score(clean_request)
    wiki_links = convert_to_wikipedia_links(result)
    return result, wiki_links



#chemin de la page d'accueil 
@app.route('/')
def index():
    return render_template('index.html')

#chemin pour les traitement des requetes 
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    page_scores, page_links = process_request(query)
    results = []  #on combine tout les résultats 
    for page_data in page_scores:
        page_id = page_data['page_id']
        score = page_data['score']
        if page_id in page_links:
            link = page_links[page_id]
            results.append({'page_id': page_id,'score': score,'link': link})
    return render_template('search_results.html', search_results=results)  #on les envoie à la page d'affichage des résultats


if __name__ == '__main__':
    app.run(debug=True)

    























