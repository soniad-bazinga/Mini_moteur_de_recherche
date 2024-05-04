import math
import csv
import nltk
import json
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# Télécharger les ressources nécessaires de NLTK
nltk.download('punkt')
nltk.download('wordnet')

# Increase the CSV field size limit
csv.field_size_limit(100000000)  # Set it to a sufficiently large value

# Fonction pour enlever les stop words
def remove_stop_words(words):
    stop_words = set(stopwords.words('french'))
    return [word for word in words if word.lower() not in stop_words]

# Fonction pour effectuer la lemmatisation des mots
def lemmatize_words(words):
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(word) for word in words]

def main():
    word_freq = {}  # Initialize a dictionary to store word frequencies
    total_documents = 0  # Initialize total number of documents
    
    # Ouvrir le fichier CSV
    with open('filtered_pages.csv', 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        total_documents = sum(1 for _ in csv_reader) - 1  # Total number of lines excluding header
        csv_file.seek(0)  # Reset file pointer to the beginning
        next(csv_reader)  # Ignorer l'en-tête
        
        for i, row in enumerate(csv_reader, start=1):
            # Extraire le texte de la troisième colonne (indice 2)
            text = row[2]
            # Tokeniser le texte en mots (séparés par des espaces)
            words = nltk.word_tokenize(text)
            
            # Enlever les stop words et lemmatiser les mots
            filtered_words = lemmatize_words(remove_stop_words(words))
            
            # Mettre à jour la fréquence des mots pour chaque page
            for word in filtered_words:
                page_id = row[0]  # Assuming the page ID is in the first column
                if word in word_freq:
                    # If the word is already in the dictionary, update its frequency list
                    if page_id in word_freq[word]:
                        word_freq[word][page_id] += 1
                    else:
                        word_freq[word][page_id] = 1
                else:
                    # If the word is not in the dictionary, add it with the page ID and frequency
                    word_freq[word] = {page_id: 1}
            
            # Print a message indicating processing of each line
            print(f"Processing line {i}...")
    
    # Calculate total frequency for each word
    total_word_freq = {}
    for word, page_freqs in word_freq.items():
        total_freq = sum(page_freqs.values())
        total_word_freq[word] = {'total_frequency': total_freq, 'page_frequency': page_freqs}
    
    # Keep only the top 20,000 most frequent words
    sorted_word_freq = dict(sorted(total_word_freq.items(), key=lambda item: item[1]['total_frequency'], reverse=True)[:20000])
    
    print("Total number of documents:", total_documents)
    return total_documents , sorted_word_freq

if __name__ == "__main__":
    total_documents, word_freq = main()
    #print(word_freq)
    


def calculate_idf_and_tf(total_documents, word_freq):
    for word, page_freqs in word_freq.items():
        num_pages_containing_word = len(page_freqs['page_frequency'])
        idf = math.log10(total_documents / num_pages_containing_word)
        word_freq[word]['idf'] = idf
        
        # Calculate TF for each word within each page
        for page_id, freq in page_freqs['page_frequency'].items():
            tf = 1 + math.log10(freq)
            word_freq[word]['page_frequency'][page_id] = tf
            
    return word_freq


# Calculate IDF and TF values and update word_freq dictionary
word_freq_with_idf_and_tf = calculate_idf_and_tf(total_documents, word_freq)

#print (word_freq_with_idf_and_tf)


def calculate_Nd(total_documents, word_freq_with_idf_and_tf):
    Nd = [0] * total_documents  # Initialize Nd with zeros for each page
    
    # Iterate through each word and its frequency data
    for word_data in word_freq_with_idf_and_tf.values():
        page_frequency = word_data['page_frequency']
        
        # Iterate through each page and update Nd
        for page_id, tf in page_frequency.items():
            Nd[int(page_id) - 1] += tf ** 2  # Subtracting 1 to convert page_id to 0-based index
    
    # Take the square root of each element in Nd
    Nd = [math.sqrt(x) for x in Nd]
    
    #print (Nd)
    return Nd
Nd= calculate_Nd(total_documents, word_freq_with_idf_and_tf)




def update_word_freq(word_freq_with_idf_and_tf, Nd):
    for word_data in word_freq_with_idf_and_tf.values():
        page_frequency = word_data['page_frequency']
        idf = word_data['idf']
        
        # Update TF-IDF values for each page
        for page_id, tf in page_frequency.items():
            tf_idf = (idf * tf) / Nd[int(page_id) - 1]  # Subtracting 1 to convert page_id to 0-based index
            word_data['page_frequency'][page_id] = tf_idf

# Assuming you already have obtained total_documents, word_freq_with_idf_and_tf, and Nd
update_word_freq(word_freq_with_idf_and_tf, Nd)

#print (word_freq_with_idf_and_tf)

#RAJOUTER LE ALPHA ET BETA 

def update_word_freq(word_freq_with_idf_and_tf, Nd):
    for word, word_data in word_freq_with_idf_and_tf.items():
        page_frequency = word_data.pop('page_frequency', {})  # Remove 'page_frequency' key
        idf = word_data.pop('idf', None)  # Remove 'idf' key
        
        # Update TF-IDF values for each page
        updated_page_frequency = {}
        for page_id, tf in page_frequency.items():
            tf_idf = (idf * tf) / Nd[int(page_id) - 1]  # Subtracting 1 to convert page_id to 0-based index
            updated_page_frequency[page_id] = tf_idf
        
        word_data.update(updated_page_frequency)
        
        # Remove 'total_frequency' key
        word_data.pop('total_frequency', None)
        
        # Remove 'idf' key
        word_data.pop('idf', None)
        
# Assuming you already have obtained total_documents, word_freq_with_idf_and_tf, and Nd
update_word_freq(word_freq_with_idf_and_tf, Nd)


def save_dict_to_json_stream(dictionary, filename):
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(dictionary, json_file, ensure_ascii=False)

# Assuming word_freq_with_idf_and_tf is your dictionary
save_dict_to_json_stream(word_freq_with_idf_and_tf, 'word_freq_with_idf_and_tf.json')

