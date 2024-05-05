## MAAIN: programmer un moteur de recherche 



Le but de ce projet est de programmer un moteur de recherche simple mais fonctionnel.

Un moteur de recherche basique fonctionne sur ce principe très simple :
— calculer « une fois pour toutes » l’importance de chaque page d’internet, et la fréquence
de chaque mot dans ces pages ;
— lors d’une requête, trouver toutes les pages qui contiennent les mots cherchés, calculer
leur « score » et renvoyer ces pages triées par score décroissant.


Le score d’une page pour une requête va dépendre à la fois de l’importance de la page dans
l’absolu, et de la fréquence d’apparition dans la page des mots de la requête. La pertinence
du moteur de recherche dépend évidemment de ce score attribué à chaque page. Pour évaluer
l’importance d’une page dans l’absolu, nous allons utiliser le pagerank qui a fait le succès de
Google. Celui-ci attribue un score plus élevé aux pages qui reçoivent plus de liens importants,
l’idée étant qu’une page reçoit d’autant plus de liens qu’elle est plus populaire.



Pour concevoir notre moteur de recherche, nous allons procéder en différentes étapes :
**(TP1)** programmer un « collecteur » (en anglais : web
crawler) qui indexera les pages Wikipédia en suivant les liens des pages.
Ce collecteur aura deux tâches :
— « apprendre » le graphe orienté G des pages visitées (un sommet = une page ; un
arc = un lien),
— associer à chacun des mots français les plus fréquents la liste des pages dans
lesquelles il apparaît, avec sa fréquence d’apparition ;


**(TP2)**  à partir du graphe G obtenu, calculer le pagerank
de chaque sommet.


**(TP3)**  programmer le serveur de sorte que, sur une
requête de l’utilisateur, il affiche l’ensemble des pages contenant tous les mots de la
requête, par score décroissant.



