"""
Utilisation de la classe HydrophobicityProfile:
    - Pour créer un profil d'hydrophobicité, il faut instancier la classe HydrophobicityProfile avec les paramètres
        suivants:
        - sequence: une chaîne de caractères contenant la séquence d'acides aminés
        - model_id: une chaîne de caractères contenant le nom du modèle à utiliser
        - frame_size: un entier positif représentant la taille du cadre à utiliser pour calculer la moyenne
        - edge_proportion: un flottant entre 0 et 1 représentant la proportion de la moyenne que les acides aminés aux
            extrémités du cadre doivent compter
    - La classe HydrophobicityProfile a les attributs suivants:
        - points: une liste de points de données de type LineChartDataPoint
        - abscissa_axe: un objet de type Axe représentant l'axe des abscisses
        - ordinate_axe: un objet de type Axe représentant l'axe des ordonnées
    - La classe HydrophobicityProfile a les méthodes suivantes:
        - get_models_names: une méthode statique qui retourne une liste de chaînes de caractères contenant les noms des
            modèles disponibles
    - La classe HydrophobicityProfile lève l'exception ModelFormatError si le fichier models.json est mal formaté
    - La classe Axe a les attributs suivants:
        - min_value: un entier représentant la valeur minimale de l'axe
        - max_value: un entier représentant la valeur maximale de l'axe
    - La classe Pick a les attributs suivants:
        - maximum: un flottant représentant la valeur maximale du pic
        - minimum: un flottant représentant la valeur minimale du pic
        - length: un entier représentant la longueur du pic
        - start: un entier représentant l'indice de départ du pic
"""

import json
import flet


class Axe:
    def __init__(self, min_value, max_value):
        """
        Détermine les valeurs minimales et maximales pour un axe du graphique.
        """
        self.min_value = min_value
        self.max_value = max_value


class ModelFormatError(Exception):
    def __init__(self, message):
        """
        Exception levée lorsqu'un modèle dans models.json est mal formaté.
        """
        self.message = message
        super().__init__(self.message)


class Pick:
    def __init__(self, start):
        """
        Représente un pic / zone hydrophobe dans le profil d'hydrophobicité.
        """
        self.maximum = None
        self.minimum = None
        self.length = -1
        self.start = start

    def add(self, value) -> None:
        """
        Ajoute un acide aminé.
        """

        # met à jour les valeurs maximales et minimales si nécessaire
        if not self.maximum or value > self.maximum:
            self.maximum = value
        if not self.minimum or value < self.minimum:
            self.minimum = value

        # met à jour la longueur du pic
        self.length += 1

    def __repr__(self) -> str:
        """
        Représentation de l'objet Pick.
        """
        return f"Pick({self.start}, {self.start + self.length}, max: {self.maximum}, min: {self.minimum})"


class HydrophobicityProfile:
    def __init__(self, sequence, model_id, frame_size, edge_proportion):
        """
        Crée un profil d'hydrophobicité à partir d'une séquence d'acides aminés.
        """
        # charge le modèle depuis le fichier models.json
        with open('data/models.json') as f:
            data = json.load(f)
        model = data[model_id]

        # vérifie l'intégrité du modèle
        HydrophobicityProfile._check_model_integrity(model)

        # libère la mémoire utilisée par models.json
        del data

        # initialise les valeurs d'hydrophobicité pour chaque acide aminé
        hydrophobicity_values = [model[amino_acid] for amino_acid in sequence]

        # libère la mémoire utilisée par le modèle et la séquence d'acides aminés
        del model, sequence

        # initialise les variables nécessaires pour le profil d'hydrophobicité
        self.points = []
        self.abscissa_axe = Axe(frame_size, len(hydrophobicity_values) - frame_size)
        self.ordinate_axe = Axe(min(hydrophobicity_values), max(hydrophobicity_values))
        self.picks = []
        previous_value = 0
        for i in range(frame_size, len(hydrophobicity_values) - frame_size):

            # isole une fenêtre de taille frame_size autour de l'acide aminé i
            frame = hydrophobicity_values[i - frame_size:i + frame_size + 1]
            # applique une fonction de poids à la fenêtre en fonction de la distance à l'acide aminé i et de
            # edge_proportion
            for j in range(len(frame)):
                frame[j] = frame[j] * (1 / frame_size * -(abs(j - frame_size) * (1 - edge_proportion)) + 1)

            # calcule la moyenne des valeurs d'hydrophobicité dans la fenêtre
            value = sum(frame) / len(frame)

            # tentative de détection de zone hydrophobe
            if value >= 0.5:
                if previous_value < 0.5:
                    # si la valeur est supérieure à 0.5 et que la valeur précédente est inférieure à 0.5, commence un
                    # nouveau pic
                    self.picks.append(Pick(i))
                # ajoute la valeur à la zone hydrophobe actuelle
                self.picks[-1].add(value)
            else:
                if previous_value > 0.5:
                    # si la valeur est inférieure à 0.5 et que la valeur précédente est supérieure à 0.5, termine le pic
                    if self.picks[-1].length < 10:
                        # si le pic est trop court (moins de 10 acides aminés), il est supprimé
                        self.picks.pop()
            previous_value = value

            # ajoute la valeur à la liste des points de données
            self.points.append(flet.LineChartDataPoint(i, value, tooltip=str(round(value, 4))))

    @staticmethod
    def get_models_names() -> list:
        """
        Retourne une liste de chaînes de caractères contenant les noms des modèles disponibles dans models.json.
        """

        # charge les modèles depuis le fichier models.json
        with open('data/models.json') as f:
            data = json.load(f)

        # initialise la liste des noms des modèles
        models = []

        # pour chaque modèle
        for model in data:
            # vérifie l'intégrité du modèle
            HydrophobicityProfile._check_model_integrity(model)
            # si le modèle est valide, ajoute son nom à la liste
            models.append(model['name'])

        # retourne la liste des noms des modèles
        return models

    @staticmethod
    def _check_model_integrity(model):
        """
        Vérifie l'intégrité d'un modèle.
        """
        # vérifie que le modèle est un dictionnaire
        if not isinstance(model, dict):
            raise ModelFormatError("Model in models.json must be a dictionary")
        # vérifie que le modèle a un nom
        if 'name' not in model:
            raise ModelFormatError("Model in models.json must have a name")
        # vérifie que le modèle a une valeur pour chaque acide aminé
        for amino_acide in ['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE', 'LEU', 'LYS', 'MET',
                            'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL']:
            if amino_acide not in model:
                raise ModelFormatError(f"Model '{model['name']}' in models.json must have a value for '{amino_acide}'")
        amino_acides = list(model.keys())
        amino_acides.remove('name')
        for amino_acide in amino_acides:
            # vérifie que l'acide aminé acide est valide
            if amino_acide not in ['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE', 'LEU', 'LYS',
                                   'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL']:
                raise ModelFormatError(f"Amino acide '{amino_acide}' in model '{model['name']}' is not a valid amino "
                                       f"acide name")
            # vérifie que la valeur associée à l'acide aminé est un nombre
            if not isinstance(model[amino_acide], (int, float)):
                raise ModelFormatError(f"Value for '{amino_acide}' in model '{model['name']}' must be a number")
