import random
import gradio as gr

# On choisit un thème aléatoire parmi les thèmes disponibles
THEME = random.choice(["Base", "Monochrome", "Glass", "Soft"])

# On définit le titre de l'interface
TITLE = "HydroProfileR"

# On crée l'interface graphique avec le thème et le titre choisis précédemment
with gr.Blocks(theme=THEME, title=TITLE) as iface:

    def hydrophobicity(pdb_file):

        if pdb_file is None:
            return {
                file_input: file_input,
                accor: gr.Accordion(visible=False),
                file_output: gr.Plot(value=None)
            }

        # TODO : remplacer par le traitement du fichier PDB et le calcul de l'hydrophobicité

        err = random.choice([True, False])

        if err:  # TODO : remplacer par le test de non-erreur

            return {
                file_input: file_input,
                accor: gr.Accordion(label="PROT", visible=True),  # TODO : remplacer par la vraie protéine
                file_output: gr.Plot(value=None),  # TODO : remplacer par le vrai graphique
            }

        else:

            return {
                file_input: gr.File(value=None),
                accor: accor,
                file_output: file_output
            }


    # On crée un onglet pour le calcul de l'hydrophobicité avec comme nom "Profil d'hydrophobicité"
    with gr.Tab(label="Profil d'hydrophobicité"):

        # On crée un composant pour uploader un seul fichier PDB.
        file_input = gr.File(label="Fichier PDB", file_count="single", file_types=["pdb"])

        # On crée un bloc pour afficher le résultat du calcul de l'hydrophobicité
        with gr.Accordion(visible=False) as accor:
            # On crée un composant pour afficher le fichier PDB uploadé par l'utilisateur
            file_output = gr.Plot(label="Hydrophobicité")

        # On détecte le changement de fichier PDB et on lance le calcul de l'hydrophobicité
        file_input.change(fn=hydrophobicity, inputs=file_input, outputs=[file_input, accor, file_output])
