package main



import(
	"fmt"
	"os"
)

func main(){

	//open XML file 
	xmlFile, err := os.Open("frwiki10000.xml")
	//if it returns an error 
	if err != nil{
		fmt.Println(err)
	}

	fmt.Println("Success!")
	//defer the closing for pasing later on
	defer xmlFile.Close()
}


