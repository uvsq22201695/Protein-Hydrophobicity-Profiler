# Profil d'Hydrophobicité des Protéines

Ce projet est développé par les étudiants :
- BOISSERIE Baptiste, 22200450
- FRANÇOIS Alexandre, 22201695

Il utilise la bibliothèque Flet pour générer des profils d'hydrophobicité de séquences protéiques à partir de fichiers PDB. Le système permet aux utilisateurs de visualiser des graphiques de l'hydrophobicité le long de la chaîne de protéines, en utilisant différents modèles hydrophobiques disponibles.

## Fonctionnalités

- **Sélection de fichiers PDB :** Permet à l'utilisateur de sélectionner un fichier PDB pour l'analyse.
- **Configuration des paramètres :** Offre la possibilité de configurer les paramètres d'hydrophobicité, y compris le choix du modèle hydrophobique, la taille de la fenêtre de calcul, et la pondération aux extrémités.
- **Visualisation graphique :** Affiche un graphique représentant le profil d'hydrophobicité de la protéine (possibilité de cacher ou d'afficher les différentes chaînes).
- **Informations détaillées :** Fournit des informations détaillées sur la publication liée au fichier PDB, y compris les références, les auteurs, et les liens vers les bases de données.

## Composants

### Interface principale (`interface.py`)
L'interface utilisateur est conçue pour faciliter l'interaction avec l'application. Elle permet aux utilisateurs de charger des fichiers PDB, de choisir parmi différents modèles hydrophobiques et de paramétrer des options comme la taille de la fenêtre de calcul et la pondération aux extrémités. L'interface rend également possible la visualisation des résultats sous forme graphique, où les valeurs d'hydrophobicité le long de la chaîne protéique sont affichées clairement, permettant une analyse rapide et intuitive.

### Génération de profil (`profile_generation.py`)
Ce module central traite les données entrées par l'utilisateur pour calculer l'hydrophobicité des séquences protéiques. Il utilise les données extraites du fichier PDB pour former une séquence d'acides aminés, puis applique le modèle hydrophobique sélectionné pour produire un profil d'hydrophobicité. Ce profil est calculé en tenant compte de la fenêtre de calcul spécifiée et de toute pondération appliquée aux extrémités de la chaîne protéique, ce qui permet une analyse précise de l'hydrophobicité locale et globale.

- **Classe `HydrophobicityProfile`** : Responsable de calculer le profil d'hydrophobicité à partir de la séquence d'acides aminés. Utilise les données du modèle hydrophobique chargées depuis `models.json` pour appliquer le calcul hydrophobique à la séquence. Prend en compte la taille de la fenêtre spécifiée et applique une pondération pour les acides aminés aux extrémités afin de générer un profil précis.
- **Validation des modèles** : Assure que les modèles hydrophobiques chargés du fichier JSON sont valides et bien formatés, évitant ainsi des erreurs lors des calculs d'hydrophobicité.

### Gestion des fichiers PDB (`pdb.py`)
Ce module est responsable de la gestion des fichiers de structure de protéines (PDB). Il parse les fichiers pour en extraire des informations cruciales comme les séquences d'acides aminés et les métadonnées associées aux publications et aux auteurs. Ce module assure également que les références aux bases de données externes et les citations sont correctement intégrées pour une référence facile par les utilisateurs.

- **Classe `Header`** : Traite les informations de classification, la date, l'identifiant de la structure PDB, et fournit des liens vers des ressources externes comme la page RCSB.
- **Classe `Journal`** : Extrait et organise les informations de publication associées aux structures PDB, incluant les auteurs, le titre de l'article, l'éditeur, le numéro PubMed, et le DOI.
- **Classe `PDBFile`** : Agit comme le gestionnaire principal pour les fichiers PDB, organisant l'extraction et le stockage des séquences d'acides aminés, des informations d'auteurs, des remarques, et des références du journal pour un accès facile.

### Modèles hydrophobiques (`models.json`)
Ce fichier JSON sert de base de données pour les différents modèles hydrophobiques disponibles pour l'analyse. Chaque modèle est défini avec des valeurs spécifiques d'hydrophobicité pour chaque acide aminé, ce qui permet de varier les analyses selon les besoins de recherche spécifiques ou les préférences des utilisateurs. Les modèles disponibles incluent Kyte & Doolittle, Eisenberg, Engelman GES, et Hopp-Woods, chacun ayant ses propres caractéristiques et applications recommandées.

### Application principale (`main.py`)
Le fichier `main.py` agit comme le point d'entrée de l'application. Il initialise l'interface utilisateur et lie tous les modules ensemble, permettant ainsi à l'application de fonctionner de manière fluide et intégrée. Ce fichier configure également les dépendances nécessaires et s'assure que l'application est prête à être exécutée dès son lancement.

## Prérequis
- Python 3.11
- Package Flet : `pip install flet`

## Installation
Assurez-vous d'avoir Python 3.11 installé sur votre machine, puis installez le package Flet en utilisant la commande suivante :
```bash
pip install flet
```

Ce package est également listé dans les ``requirements.txt`` du projet.

## Exécution

Pour lancer l'application, exécutez le fichier `main.py` en utilisant Python 3.11 :
```bash
python main.py
```

L'interface utilisateur s'ouvrira, vous permettant de charger un fichier PDB, de configurer les paramètres d'hydrophobicité, et de visualiser les profils générés. Suivez les instructions à l'écran pour interagir avec l'application et explorer les profils d'hydrophobicité des protéines.
