package main

import (
	"encoding/csv"
	"encoding/xml"
	"fmt"
	"os"
	"regexp"
	"strings"
)

type Page struct {
	Title string `xml:"title"`         //title of the page
	Text  string `xml:"revision>text"` //text of the page
	ID    int    //id of the page
}

func countWords(text string) int {
	words := strings.Fields(text)
	return len(words)
}

func replaceInternLinks(text string, pageIDs map[string]int) string {
	//remplacer les liens internes par les ID des pages référencées: [[Article]] ou [[Article|textede remplacement]]
	linkregexp := regexp.MustCompile(`INTERNLINK(.*?)INTERNLINK`)
	newText := linkregexp.ReplaceAllStringFunc(text, func(link string) string {
		//extraire le titre de la page reférencée
		referenced_title := strings.Trim(link, "INTERNLINK")

		pipeIndex := strings.Index(referenced_title, "|")
		if pipeIndex != -1 {
			referenced_title = referenced_title[:pipeIndex] //ne sert à rien je pense
		}
		//on remplace mnt ce lien par l'id de la page correspondante
		if id, exists := pageIDs[referenced_title]; exists {
			return fmt.Sprintf("%d", id)
		}
		//si l'id n'existe pas, on le retourne tel quel
		return link
	})

	return newText
}

func cleanText(text string) string {
	//pour éviter que les démarcation des liens internes ne soitent effacées lors du nettoyagen on les remplace par une chaine temporaire
	linkregexp := regexp.MustCompile(`\[\[([^|\]]+?)(?:\s*\|\s*([^]]+?))?\]\]`)
	links := linkregexp.FindAllStringSubmatch(text, -1)
	for _, match := range links {
		text = strings.ReplaceAll(text, match[0], fmt.Sprintf("INTERNLINK%sINTERNLINK", match[1]))
	}

	//1. supprimer le contenu entre doubles accolades '{{..}}'
	newtext := regexp.MustCompile("\\{\\{.*?\\}\\}").ReplaceAllString(text, "")

	//2. supprimer les liens externes (balises ref, &lt; , &gt; )
	newtext = regexp.MustCompile("<ref.*?>.*?</ref>").ReplaceAllString(newtext, "")

	//3. supprimer les entetes, titres d'une section entourés par des "==","===" ou plus
	newtext = regexp.MustCompile("(=+.*?=+)").ReplaceAllString(newtext, "")

	//4. supprimer les chiffres ou caractères spéciaux
	newtext = regexp.MustCompile("[^a-zA-Z0-9\\s]").ReplaceAllString(newtext, "")
	// Supprimer les grands nombres
	re := regexp.MustCompile("[0-9]+")
	newtext = re.ReplaceAllString(newtext, " ")

	//5. remplacer les ponctuations par des espaces
	newtext = regexp.MustCompile("[[:punct:]]").ReplaceAllString(newtext, " ")

	//6. supprimer les espaces superflus, ne garder que ceux entre les mots, les remplacer par un seul espace
	newtext = regexp.MustCompile("\\s+").ReplaceAllString(newtext, " ")

	return newtext
}

func main() {
	//open XML file
	xmlFile, err := os.Open("..\\frwiki-latest-pages-articles\\frwiki-latest-pages-articles.xml")
	//if it returns an error
	if err != nil {
		fmt.Println("Error opening xml file: ", err)
		return
	}

	//defer the closing for pasing later on
	defer xmlFile.Close()

	//création du fichier csv en écriture
	csvFile, err := os.Create("filtered_pages.csv")
	if err != nil {
		fmt.Println("Error opening csv file: ", err)
		return
	}

	defer csvFile.Close()

	//create the writer
	writer := csv.NewWriter(csvFile)
	defer writer.Flush()

	//writing the file header {ID, TITLE, TEXT, INTERNALLINKS}
	header := []string{"ID", "Title", "Text"}
	err = writer.Write(header)
	if err != nil {
		fmt.Println("Error writing header: ", err)
		return
	}

	var pages []Page

	//pour garder les IDs correspondant à chaque titre,
	pageIDs := make(map[string]int)

	//selectionner les pages qui contiennent un certain mot clé (ex: Histoire)
	keyword := "histoire"

	//creating an XML decoder
	decoder := xml.NewDecoder(xmlFile)

	//le nombre minimal de mots que doit contenir une page après nettoyage
	minWordsCount := 600

	//id des pages
	//alternative: utiliser une fonction de hachage ?
	id := 0 //première page

	page_limit := 200000

	//parsing
	for id <= page_limit {
		//reading the token
		token, err := decoder.Token()
		if err != nil {
			break //end of file
		}

		//we check the token's type
		switch se := token.(type) { //on vérifie le type de token généré par le décodeur XML
		case xml.StartElement:
			//checking if the start element is page
			if se.Name.Local == "page" {
				var page Page //current page

				err := decoder.DecodeElement(&page, &se)
				if err != nil {
					fmt.Println("Error while decoding page: ", err)
					continue

				}
				//lower case
				page.Text = strings.ToLower(page.Text)
				page.Title = strings.ToLower(page.Title)
				//filtering
				if strings.Contains(page.Text, strings.ToLower(keyword)) {
					//cleaning
					cleanedText := cleanText(page.Text)

					//verify word count after cleaning
					if countWords(cleanedText) >= minWordsCount {
						pages = append(pages, Page{
							Title: page.Title,
							Text:  cleanedText,
							ID:    id,
						})

						fmt.Printf("%d: %s\n", id, page.Title)
						pageIDs[page.Title] = id //on peut s'en passer mais bon
						id++
					}
				}
			}
		}
	}

	//on remplace les liens internes et on sauvegarde dans le CSV
	for i := range pages {
		pages[i].Text = replaceInternLinks(pages[i].Text, pageIDs)
		//write page to CSV
		record := []string{fmt.Sprintf("%d", pages[i].ID), pages[i].Title, pages[i].Text}
		err := writer.Write(record)
		if err != nil {
			fmt.Println("Error writing in the CSV: ", err)
			return
		}
	}

	fmt.Println("Nombre de pages sélectionnées: ", id)
	writer.Flush()
}
