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
"""

import json
import flet


class Axe:
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value


class ModelFormatError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class HydrophobicityProfile:
    def __init__(self, sequence, model_id, frame_size, edge_proportion):
        with open('models.json') as f:
            data = json.load(f)
        model = data[model_id]
        HydrophobicityProfile._check_model_integrity(model)
        del data
        hydrophobicity_values = [model[amino_acid] for amino_acid in sequence]
        del model, sequence
        self.points = []
        self.abscissa_axe = Axe(frame_size, len(hydrophobicity_values) - frame_size)
        self.ordinate_axe = Axe(min(hydrophobicity_values), max(hydrophobicity_values))
        for i in range(frame_size, len(hydrophobicity_values) - frame_size):
            frame = hydrophobicity_values[i - frame_size:i + frame_size + 1]
            # edge of the frame count for 0% of the average and the center counts for 100% of the average
            for j in range(len(frame)):
                frame[j] = frame[j] * (1 / frame_size * -(abs(j - frame_size) * (1 - edge_proportion)) + 1)

            self.points.append(flet.LineChartDataPoint(i, sum(frame) / len(frame)))

    @staticmethod
    def get_models_names():
        with open('models.json') as f:
            data = json.load(f)
        models = []
        for model in data:
            HydrophobicityProfile._check_model_integrity(model)
            models.append(model['name'])
        return models

    @staticmethod
    def _check_model_integrity(model):
        if not isinstance(model, dict):
            raise ModelFormatError("Model in models.json must be a dictionary")
        if 'name' not in model:
            raise ModelFormatError("Model in models.json must have a name")
        for amino_acide in ['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE', 'LEU', 'LYS', 'MET',
                            'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL']:
            if amino_acide not in model:
                raise ModelFormatError(f"Model '{model['name']}' in models.json must have a value for '{amino_acide}'")
        amino_acides = list(model.keys())
        amino_acides.remove('name')
        for amino_acide in amino_acides:
            if amino_acide not in ['ALA', 'ARG', 'ASN', 'ASP', 'CYS', 'GLN', 'GLU', 'GLY', 'HIS', 'ILE', 'LEU', 'LYS',
                                   'MET', 'PHE', 'PRO', 'SER', 'THR', 'TRP', 'TYR', 'VAL']:
                raise ModelFormatError(f"Amino acide '{amino_acide}' in model '{model['name']}' is not a valid amino "
                                       f"acide name")
            if not isinstance(model[amino_acide], (int, float)):
                raise ModelFormatError(f"Value for '{amino_acide}' in model '{model['name']}' must be a number")
