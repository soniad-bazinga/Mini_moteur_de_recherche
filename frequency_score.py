import json

#TP3 EXO2


#calculer la moyenne des scores de fréquences pour déterminer les paramètres alpha et beta 
def calculer_moyenne_scores_frequence(scores_frequence):
    somme_scores = sum(scores_frequence.values())
    nombre_pages = len(scores_frequence)
    moyenne_scores = somme_scores / nombre_pages
    
    return moyenne_scores

requetes = []



def frequence_score(request):
    """algorithme efficace, qui à partir de la relation mots-pages, énumère toutes les pages contenant tous les mots de la requete (un seul parcours des listes concernant les mots de la requete)"""

    #chargement du dictionnaire des score TF-IDF de chaque mot par page
    with open("word_freq_with_idf_and_tf.json", "r") as tfidf_file:
        tfidf_scores = json.load(tfidf_file)

    #chargement du dictionnaire des scores de PageRanks de chaque page 
    with open("pagerank_scores.json", "r") as pagerank_file:
        pagerank_scores = json.load(pagerank_file)

    ############# VERSION SIMPLE

    """1. calcul du score d'une page d par rapport à la requete r
    2. énumérer les pages contenant TOUS les mots de la requete


    ** algorithme efficace pour récupérer toutes les pages qui contiennent TOUS les mots de la requete: 
    - pour ne faire qu'un seul parcours de la liste des mots de la requete: on récupère toutes les pages qui contiennet chaque mot de la requete, puis on fait l'intersection 
    """
    frequency_scores = {}  #score de fréquence pour chaque page du corpus par rapport à la liste de mots de request

    #tfidf_file is relation mots-pages

    #on mets dans une liste tous les identifiants des pages qui contienent chaque mot de la requete 
    pages_containing_request_words = {word: set(tfidf_scores.get(word, {}).keys()) for word in request}

    #faire l'intersection des pages_pertinentes 
    pages_pertinentes = set.intersection(*pages_containing_request_words.values())
    #pages_pertinentes= pages_containing_request_words

    #calcul des scores pour les pages pertinentes
    for page_id in pages_pertinentes:
        page_freq = sum(tfidf_scores[word][page_id] for word in request) + pagerank_scores.get(page_id)
        frequency_scores[page_id] = page_freq

    #tri des résultats de fréquences par ordre décroissant 
    sorted_pages = sorted(frequency_scores.items(), key = lambda x: x[1], reverse=True)

    print("calcul des scores de fréquences terminé avec succès.")
    #envoyer les résultats au serveur pour etre affichée sur la page du moteur de recherche
    result = [{'page_id': page_id, 'score': score} for page_id, score in sorted_pages]
    return result



