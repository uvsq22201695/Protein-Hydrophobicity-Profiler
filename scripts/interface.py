import flet as ft

from scripts.profile_generation import HydrophobicityProfile
from scripts.pdb import PDBFile


class FletApp:
    def __init__(self, page):
        # Initialisation de l'instance avec la page de l'application.
        self.page = page
        # Définir le titre de la page web.
        self.page.title = "Protein Hydrophobicity Profiler"
        # Centrer les contrôles dans la page verticalement.
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER

        # Configurer le thème de l'application avec une couleur de base et utiliser Material Design 3.
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.colors.PINK,
            use_material3=True
        )

        # Créer des références pour les divers contrôles qui seront manipulés.
        page_dialog = ft.Ref[ft.AlertDialog]()
        weighting = ft.Ref[ft.TextField]()
        window_size = ft.Ref[ft.TextField]()
        model = ft.Ref[ft.Dropdown]()
        validate_button = ft.Ref[ft.FilledButton]()
        pick_files_dialog = ft.Ref[ft.FilePicker]()
        err_dialog = ft.Ref[ft.SnackBar]()

        # Configuration de la boîte de dialogue pour sélectionner des fichiers avec un callback spécifié.
        self.page.overlay.append(
            ft.FilePicker(
                on_result=lambda e: self._pick_files_result(e, page_dialog),
                ref=pick_files_dialog
            )
        )

        # Obtenir les noms des modèles d'hydrophobicité disponibles pour le choix de l'utilisateur.
        models_name = HydrophobicityProfile.get_models_names()

        # Définir une fonction callback pour gérer le retour en arrière dans l'interface.
        self.page.on_view_pop = self.view_pop

        # Ajouter une vue principale avec divers contrôles.
        self.page.views.append(
            ft.View(
                "/",  # Route de la vue principale.
                controls=[
                    ft.Row(
                        [
                            # Image/logo de l'application.
                            ft.Image(
                                src="../assets/icon.png",
                                width=500,
                                height=500
                            ),
                            ft.Column(
                                [
                                    # Message de bienvenue en gras et centré.
                                    ft.Text(
                                        size=30,
                                        weight=ft.FontWeight.BOLD,
                                        selectable=True,
                                        spans=[ft.TextSpan(text="Welcome to the Protein Hydrophobicity Profiler")],
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    # Bouton pour lancer la sélection de fichier PDB.
                                    ft.FilledButton(
                                        icon=ft.icons.FILE_UPLOAD_ROUNDED,
                                        text="Select a PDB file to begin",
                                        on_click=lambda _: pick_files_dialog.current.pick_files(
                                            allow_multiple=False,
                                            allowed_extensions=["pdb"],
                                            dialog_title="Select a PDB file to begin",
                                            file_type=ft.FilePickerFileType.CUSTOM,
                                        )
                                    )
                                ]
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    # Configuration de la boîte de dialogue pour saisir les paramètres.
                    ft.AlertDialog(
                        ref=page_dialog,
                        modal=True,
                        title=ft.Text("Choose your parameters"),
                        content=ft.Column(
                            [
                                # Champ de saisie pour le poids aux extrémités avec des contraintes.
                                ft.TextField(
                                    border_radius=20,
                                    ref=weighting,
                                    label="Weighting at the ends",
                                    input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9\.]",
                                                                replacement_string=""),
                                    keyboard_type=ft.KeyboardType.NUMBER,
                                    value="100.0",
                                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                                    max_lines=1,
                                    min_lines=1,
                                    tooltip="Value between 0 and 100.",
                                    suffix_icon=ft.icons.PERCENT_ROUNDED,
                                    on_change=lambda e: self._validate_input(e, 0, 100, float, validate_button,
                                                                             weighting, window_size, model)
                                ),
                                # Champ de saisie pour la taille de la fenêtre.
                                ft.TextField(
                                    border_radius=20,
                                    ref=window_size,
                                    label="Window size",
                                    input_filter=ft.InputFilter(allow=True, regex_string=r"^[1-9]\d*$",
                                                                replacement_string=""),
                                    keyboard_type=ft.KeyboardType.NUMBER,
                                    value="4",
                                    bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                                    max_lines=1,
                                    min_lines=1,
                                    tooltip="Integer value greater than 0.",
                                    on_change=lambda e: self._check_parameters(validate_button, weighting, window_size,
                                                                               model)
                                ),
                                # Liste déroulante pour choisir le modèle hydrophobicité.
                                ft.Dropdown(
                                    border_radius=20,
                                    ref=model,
                                    label="Model",
                                    hint_text="Choose a model",
                                    options=[
                                        ft.dropdown.Option(str(i), models_name[i]) for i in range(len(models_name))
                                    ],
                                    color=ft.colors.ON_SECONDARY_CONTAINER,
                                    filled=True,
                                    on_change=lambda _: self._check_parameters(validate_button, weighting, window_size,
                                                                               model)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            tight=True
                        ),
                        actions=[
                            # Bouton d'annulation dans la boîte de dialogue.
                            ft.TextButton(
                                text="Cancel",
                                on_click=lambda _: self._switch_dialog(page_dialog, weighting, window_size, model,
                                                                       validate_button)
                            ),
                            # Bouton de validation pour générer le profil.
                            ft.FilledButton(
                                ref=validate_button,
                                text="Validate",
                                on_click=lambda _: self._generate_profile(page_dialog, weighting, window_size, model,
                                                                          validate_button, err_dialog),
                                disabled=True
                            )
                        ],
                        actions_alignment=ft.MainAxisAlignment.END
                    ),
                    # Configuration de la boîte de dialogue pour afficher des erreurs.
                    ft.SnackBar(
                        ref=err_dialog,
                        bgcolor=ft.colors.RED_900,
                        show_close_icon=True,
                        close_icon_color=ft.colors.WHITE,
                        content=ft.Text("The window size is greater than the sequence length.", color=ft.colors.WHITE),
                        duration=5000
                    )
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
            )
        )

        # Charger la route initiale.
        self.page.go("/")

    def view_pop(self, _: ft.ViewPopEvent):
        """Cette méthode gère l'événement de retour arrière dans l'application. Elle supprime la vue actuelle de la
        pile et charge la vue précédente."""

        self.page.views.pop()   # Retire la vue actuelle de la pile.
        self.page.go(self.page.views[-1].route)  # Navigue à la vue précédente.

    @staticmethod
    def _check_parameters(validate_button: ft.Ref[ft.FilledButton], weighting: ft.Ref[ft.TextField],
                          window_size: ft.Ref[ft.TextField], model: ft.Ref[ft.Dropdown]):
        """ Vérifie si tous les paramètres nécessaires sont remplis pour activer le bouton de validation. """

        # Le bouton de validation est désactivé si un des champs est vide.
        validate_button.current.disabled = not all(
            [weighting.current.value, window_size.current.value, model.current.value]
        )

        validate_button.current.update()  # Met à jour l'état du bouton dans l'interface.


    @staticmethod
    def _reset_values(weighting: ft.Ref[ft.TextField], window_size: ft.Ref[ft.TextField],
                      model: ft.Ref[ft.Dropdown], validate_button: ft.Ref[ft.FilledButton]):
        """ Réinitialise les valeurs des champs de saisie et le bouton de validation. """

        if weighting is not None or window_size is not None or model is not None or validate_button is not None:
            weighting.current.value = "100.0"  # Réinitialise les champs de saisie.
            window_size.current.value = "4"  # Réinitialise les champs de saisie.
            model.current.value = None  # Réinitialise la liste déroulante.
            validate_button.current.disabled = True  # Désactive le bouton de validation.

    def _switch_dialog(self, page_dialog: ft.Ref[ft.AlertDialog], weighting: ft.Ref[ft.TextField] = None,
                       window_size: ft.Ref[ft.TextField] = None, model: ft.Ref[ft.Dropdown] = None,
                       validate_button: ft.Ref[ft.FilledButton] = None):
        """ Gère l'ouverture et la fermeture de la boîte de dialogue des paramètres. """

        # Alterne l'état ouvert/fermé de la boîte de dialogue.
        page_dialog.current.open = not page_dialog.current.open
        page_dialog.current.update()  # Met à jour la boîte de dialogue dans l'interface.

        # Réinitialise les valeurs des champs si la boîte de dialogue est fermée.
        self._reset_values(weighting, window_size, model, validate_button)

    def _validate_input(self, e: ft.ControlEvent, min_val: int, max_val: [int, float], value_type: [int, float],
                        validate_button: ft.Ref[ft.FilledButton], *args):
        """ Vérifie la validité de l'entrée de l'utilisateur et met à jour le bouton de validation. """
        # Si l'entrée est vide, le bouton de validation est désactivé.
        if not e.control.value:
            validate_button.current.disabled = True
        else:
            try:
                # Convertit la valeur entrée au type spécifié (int ou float).
                value = value_type(e.control.value)

                # Vérifie si la valeur est dans les limites spécifiées.
                if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                    # Si la valeur est hors des limites, enlève le dernier caractère entré.
                    e.control.value = e.control.value[:-1]
                else:
                    # Si la valeur est valide, vérifie l'état des autres paramètres.
                    self._check_parameters(validate_button, *args)

            except ValueError:
                # En cas d'erreur de conversion, enlève le dernier caractère entré.
                e.control.value = e.control.value[:-1]

        # Met à jour l'état de l'entrée et du bouton dans l'interface.
        e.control.update()
        validate_button.current.update()

    def _pick_files_result(self, e: ft.FilePickerResultEvent, page_dialog: ft.Ref[ft.AlertDialog]):
        """ Gère le résultat de la sélection de fichiers et ouvre la boîte de dialogue des paramètres. """

        # Si un fichier a été sélectionné, stocke le chemin du fichier.
        if e.files is not None:
            self.path = e.files[0].path
            # Ouvre la boîte de dialogue pour entrer les paramètres.
            self._switch_dialog(page_dialog)

    def _generate_profile(self, page_dialog: ft.Ref[ft.AlertDialog], weighting: ft.Ref[ft.TextField],
                          window_size: ft.Ref[ft.TextField], model: ft.Ref[ft.Dropdown],
                          validate_button: ft.Ref[ft.FilledButton], err_dialog: ft.Ref[ft.SnackBar]):
        """ Génère un profil d'hydrophobicité à partir des paramètres choisis. """

        # Copie des valeurs des contrôles d'entrée pour assurer l'utilisation de types de données corrects.
        model_copy = int(model.current.value)  # Convertit la valeur du modèle en entier.
        window_size_copy = int(window_size.current.value)  # Convertit la taille de la fenêtre en entier.
        weighting_copy = float(weighting.current.value) / 100  # Convertit le poids en flottant et normalise par 100.

        # Ferme la boîte de dialogue de paramètres une fois que les valeurs sont récupérées.
        self._switch_dialog(page_dialog, weighting, window_size, model, validate_button)

        # Crée une instance de PDBFile pour traiter le fichier PDB sélectionné.
        pdb_file = PDBFile(self.path)

        # Vérifie si la taille de la séquence est adéquate pour la taille de fenêtre choisie.
        for chain, sequence in pdb_file.seqres.items():
            if len(sequence) < window_size_copy:
                # Si une séquence est trop courte, affiche une erreur et cesse le traitement.
                err_dialog.current.open = True
                err_dialog.current.update()
                return

        profile_list = []
        # Génère des profils pour chaque chaîne de protéine trouvée dans le fichier PDB.
        for chain, sequence in pdb_file.seqres.items():
            profile = HydrophobicityProfile(sequence, model_copy, window_size_copy, weighting_copy)
            profile_list.append((chain, profile))

        data_list = []
        # Prépare les données pour le graphique de ligne de chaque profil généré.
        for chain, profile in profile_list:
            data_list.append(
                ft.LineChartData(
                    data_points=profile.points,
                    stroke_width=2,
                    curved=True,
                    stroke_cap_round=True,
                    color=self._get_color_by_chain(chain),
                    data=chain,
                    below_line_cutoff_y=0,
                    below_line_bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLUE)
                )
            )

        # Références aux éléments d'interface qui seront actualisés ou manipulés.
        switch_ref = ft.Ref[ft.Row]()
        line_chart_ref = ft.Ref[ft.LineChart]()
        list_view_ref = ft.Ref[ft.ListView]()

        # Ajoute une nouvelle vue au gestionnaire de vue qui affiche les résultats.
        self.page.views.append(
            ft.View(
                route="/profile",
                controls=[
                    # Barre d'applications avec le titre du journal.
                    ft.AppBar(title=ft.Text(value=f"{pdb_file.journal.title}")),

                    ft.Column(
                        [

                            # Conteneur pour la barre de navigation.
                            ft.Container(
                                content=ft.NavigationBar(
                                    destinations=[
                                        # Option de profil d'hydrophobicité.
                                        ft.NavigationDestination(icon=ft.icons.STACKED_LINE_CHART_ROUNDED,
                                                                 label="Hydrophobicity Profile"),

                                        # Option de détails.
                                        ft.NavigationDestination(icon=ft.icons.INFO_ROUNDED,
                                                                 label="Details")
                                    ],
                                    on_change=lambda e: self._switch_content(e, line_chart_ref, switch_ref,
                                                                             list_view_ref),
                                    width=self.page.width / 2
                                ),
                                border_radius=20
                            ),

                            # Liste de commutateurs pour afficher/masquer les chaînes.
                            ft.ListView(
                                [ft.Switch(
                                    label=f"Show chain {chain}",
                                    active_color=self._get_color_by_chain(chain),
                                    value=True,
                                    on_change=lambda e: self._show_hide_chains(e, data_list)
                                ) for chain, _ in profile_list],
                                ref=switch_ref,
                                horizontal=True,
                                height=0.1 * self.page.height,
                            ),

                            # Graphique de ligne pour afficher le profil d'hydrophobicité.
                            ft.LineChart(
                                data_series=data_list,
                                tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
                                min_y=min(profile.ordinate_axe.min_value for _, profile in profile_list),
                                max_y=max(profile.ordinate_axe.max_value for _, profile in profile_list),
                                min_x=min(profile.abscissa_axe.min_value for _, profile in profile_list),
                                max_x=max(profile.abscissa_axe.max_value for _, profile in profile_list),
                                horizontal_grid_lines=ft.ChartGridLines(
                                    interval=1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
                                ),
                                vertical_grid_lines=ft.ChartGridLines(
                                    interval=5, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
                                ),
                                left_axis=ft.ChartAxis(
                                    title=ft.Text("Hydrophobicity", size=25),
                                    title_size=50,
                                    labels_interval=1,
                                    labels_size=50
                                ),
                                bottom_axis=ft.ChartAxis(
                                    title=ft.Text("Amino acids", size=25),
                                    title_size=50,
                                    labels_interval=25,
                                    labels_size=50
                                ),
                                border=ft.border.all(3, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
                                expand=True,
                                ref=line_chart_ref
                            ),

                            # Liste de détails pour afficher les informations sur le journal, le fichier PDB,
                            # les paramètres et les profils.
                            ft.ListView([
                                # Liste d'ExpansionPanel pour organiser et afficher des informations détaillées dans un format repliable.
                                ft.ExpansionPanelList(
                                    expand_icon_color=ft.colors.BLUE_GREY,  # Couleur de l'icône d'expansion.
                                    spacing=20,  # Espace entre chaque panneau.
                                    elevation=8,  # Effet de profondeur visuelle des panneaux.
                                    divider_color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE),
                                    # Couleur du séparateur entre les panneaux.
                                    controls=[
                                        # Premier panneau d'expansion : Informations du journal associé à la structure PDB.
                                        ft.ExpansionPanel(
                                            header=ft.ListTile(
                                                leading=ft.Icon(ft.icons.NEWSPAPER_ROUNDED),  # Icône pour le panneau.
                                                title=ft.Text("Journal Information")  # Titre du panneau.
                                            ),
                                            can_tap_header=True,
                                            # Permet d'ouvrir/fermer le panneau en tapant sur l'entête.
                                            content=ft.ListTile(
                                                title=ft.Markdown(
                                                    value=f"**Title:** {pdb_file.journal.title if pdb_file.journal.title else 'Not available'}\n\n" +
                                                          f"**Authors:** {', '.join(pdb_file.journal.authors) if pdb_file.journal.authors else 'Not available'}\n\n" +
                                                          f"**PubMed Link:** [{pdb_file.journal.pubmed_link if pdb_file.journal.pubmed_link else 'Not available'}]" +
                                                          f"({pdb_file.journal.pubmed_link if pdb_file.journal.pubmed_link else '#'})\n\n" +
                                                          f"**PubMed ID:** {pdb_file.journal.pubmed_id if pdb_file.journal.pubmed_id else 'Not available'}\n\n" +
                                                          f"**DOI:** {pdb_file.journal.digital_object_identifier if pdb_file.journal.digital_object_identifier else 'Not available'}\n\n" +
                                                          f"**ISSN:** {pdb_file.journal.international_standard_serial_number if pdb_file.journal.international_standard_serial_number else 'Not available'}\n\n" +
                                                          f"**Publisher:** {pdb_file.journal.publisher if pdb_file.journal.publisher else 'Not available'}\n\n" +
                                                          f"**Year:** {pdb_file.journal.reference.year if pdb_file.journal.reference.year else 'Not available'}\n\n" +
                                                          f"**Volume:** {pdb_file.journal.reference.volume if pdb_file.journal.reference.volume else 'Not available'}\n\n" +
                                                          f"**Page:** {pdb_file.journal.reference.page if pdb_file.journal.reference.page else 'Not available'}\n\n" +
                                                          f"**Publication Name:** {pdb_file.journal.reference.pub_name if pdb_file.journal.reference.pub_name else 'Not available'}",
                                                    auto_follow_links=True,
                                                    selectable=True
                                                )
                                            )
                                        ),

                                        # Deuxième panneau d'expansion : Informations détaillées du fichier PDB.
                                        ft.ExpansionPanel(
                                            header=ft.ListTile(
                                                leading=ft.Icon(ft.icons.ATTACH_FILE_ROUNDED),  # Icône pour le panneau.
                                                title=ft.Text("PDB Information")  # Titre du panneau.
                                            ),
                                            can_tap_header=True,
                                            # Permet d'ouvrir/fermer le panneau en tapant sur l'entête.
                                            content=ft.ListTile(
                                                title=ft.Column([
                                                    # Affichage des informations principales du fichier PDB en Markdown.
                                                    ft.Markdown(
                                                        value=f"**Author(s):** {', '.join(pdb_file.authors) if pdb_file.authors else 'Not available'}\n\n" +
                                                              f"**PDB Link:** [{pdb_file.header.pdb_link if pdb_file.header.pdb_link else 'Not available'}]({pdb_file.header.pdb_link if pdb_file.header.pdb_link else '#'})\n\n" +
                                                              f"**Date:** {pdb_file.header.date if pdb_file.header.date else 'Not available'}\n\n" +
                                                              f"**Classification:** {pdb_file.header.classification if pdb_file.header.classification else 'Not available'}\n\n" +
                                                              f"**ID:** {pdb_file.header.id if pdb_file.header.id else 'Not available'}",
                                                        auto_follow_links=True,
                                                        selectable=True
                                                    ),
                                                    # Sous-section pour lister les séquences de chaque chaîne de la protéine.
                                                    ft.ExpansionTile(
                                                        title=ft.Text("Séquence"),
                                                        controls=[
                                                            ft.ExpansionTile(
                                                                title=ft.Text(f"Chain {chain}"),
                                                                subtitle=ft.Text(f"Length: {len(sequence)}"),
                                                                leading=ft.Icon(ft.icons.CIRCLE,
                                                                                color=self._get_color_by_chain(chain)),
                                                                controls=[
                                                                    ft.ListTile(
                                                                        title=ft.Markdown(
                                                                            value=f"{' '.join(sequence)}",
                                                                            selectable=True
                                                                        )
                                                                    )
                                                                ]
                                                            ) for chain, sequence in pdb_file.seqres.items()
                                                        ]
                                                    )
                                                ])
                                            )
                                        ),

                                        # Troisième panneau d'expansion : Analyse de l'hydrophobicité pour chaque chaîne.
                                        ft.ExpansionPanel(
                                            header=ft.ListTile(
                                                leading=ft.Icon(ft.icons.ANALYTICS),  # Icône pour le panneau.
                                                title=ft.Text("Hydrophobicity analysis")  # Titre du panneau.
                                            ),
                                            can_tap_header=True,
                                            # Permet d'ouvrir/fermer le panneau en tapant sur l'entête.
                                            content=ft.ListTile(
                                                title=ft.Column(
                                                    [
                                                        ft.ExpansionTile(
                                                            title=ft.Text(f"Chain {chain}"),
                                                            leading=ft.Icon(ft.icons.CIRCLE,
                                                                            color=self._get_color_by_chain(chain)),
                                                            subtitle=ft.Text(
                                                                f"{len(profile.picks)} predicted transmembrane domains"),
                                                            controls=[
                                                                ft.ExpansionTile(
                                                                    title=ft.Text(f"Pick {i + 1}"),
                                                                    controls=[
                                                                        ft.ListTile(
                                                                            title=ft.Markdown(
                                                                                value=f"**Start:** {pick.start}\n\n" +
                                                                                      f"**End:** {pick.start + pick.length}\n\n" +
                                                                                      f"**Length:** {pick.length}\n\n" +
                                                                                      f"**Maximum:** {pick.maximum:.2f}\n\n" +
                                                                                      f"**Minimum:** {pick.minimum:.2f}\n\n",
                                                                                selectable=True
                                                                            ),
                                                                            subtitle=ft.LineChart(
                                                                                data_series=[
                                                                                    ft.LineChartData(
                                                                                        data_points=profile.points[
                                                                                                    pick.start - window_size_copy:pick.start + pick.length - window_size_copy + 1],
                                                                                        stroke_width=2,
                                                                                        curved=True,
                                                                                        stroke_cap_round=True,
                                                                                        color=self._get_color_by_chain(
                                                                                            chain),
                                                                                        data=chain,
                                                                                    )
                                                                                ],
                                                                                tooltip_bgcolor=ft.colors.with_opacity(
                                                                                    0.8, ft.colors.BLUE_GREY),
                                                                                min_y=pick.minimum - 0.5,
                                                                                max_y=pick.maximum + 0.5,
                                                                                min_x=pick.start,
                                                                                max_x=pick.start + pick.length,
                                                                                horizontal_grid_lines=ft.ChartGridLines(
                                                                                    interval=1,
                                                                                    color=ft.colors.with_opacity(0.2,
                                                                                                                 ft.colors.ON_SURFACE),
                                                                                    width=1),
                                                                                vertical_grid_lines=ft.ChartGridLines(
                                                                                    interval=5,
                                                                                    color=ft.colors.with_opacity(0.2,
                                                                                                                 ft.colors.ON_SURFACE),
                                                                                    width=1),
                                                                                left_axis=ft.ChartAxis(
                                                                                    title=ft.Text("Hydrophobicity"),
                                                                                    labels_interval=1, labels_size=50),
                                                                                bottom_axis=ft.ChartAxis(
                                                                                    title=ft.Text("Amino acids"),
                                                                                    labels_interval=50, labels_size=50),
                                                                                border=ft.border.all(3,
                                                                                                     ft.colors.with_opacity(
                                                                                                         0.2,
                                                                                                         ft.colors.ON_SURFACE)),
                                                                                expand=True
                                                                            )
                                                                        )
                                                                    ]
                                                                ) for i, pick in enumerate(profile.picks)
                                                            ]
                                                        ) for chain, profile in profile_list
                                                    ]
                                                ),
                                            )
                                        ),

                                        # Quatrième panneau d'expansion : Paramètres utilisés pour l'analyse.
                                        ft.ExpansionPanel(
                                            header=ft.ListTile(
                                                leading=ft.Icon(ft.icons.SETTINGS_ROUNDED),  # Icône pour le panneau.
                                                title=ft.Text("Parameters")  # Titre du panneau.
                                            ),
                                            can_tap_header=True,
                                            # Permet d'ouvrir/fermer le panneau en tapant sur l'entête.
                                            content=ft.ListTile(
                                                title=ft.Markdown(
                                                    value=f"**Model:** {model.current.options[model_copy].text if model.current.options[model_copy].text else 'Not available'}\n\n" +
                                                          f"**Window size:** {window_size_copy if window_size_copy else 'Not available'}\n\n" +
                                                          f"**Weighting:** {weighting_copy * 100 if weighting_copy else 'Not available'}%",
                                                    selectable=True
                                                )
                                            )
                                        )
                                    ]
                                )],
                                padding=20,
                                expand=True,
                                visible=False,
                                ref=list_view_ref
                            )],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True
                    )
                ]
            )
        )

        # Redirige vers la nouvelle vue de profil.
        self.page.go("/profile")

    @staticmethod
    def _show_hide_chains(e, data_list):
        """ Affiche ou masque les chaînes sélectionnées en fonction de l'état d'un contrôle Switch. """

        for data in data_list:
            # Vérifie si l'étiquette du contrôle correspond à la donnée actuellement manipulée.
            if data.data == e.control.label[-1]:  # Accède au dernier caractère de l'étiquette qui représente la chaîne.
                data.visible = e.control.value  # Définit la visibilité de la série de données en fonction de l'état du Switch.
                data.update()  # Met à jour les données pour refléter les changements dans l'interface utilisateur.
                break  # Quitte la boucle une fois la chaîne correspondante trouvée et mise à jour.

    def _switch_content(self, e: ft.ControlEvent, chart: ft.Ref[ft.LineChart],
                        checkboxes: ft.Ref[ft.Row], list_view_ref: ft.Ref[ft.ListView]):
        """ Change le contenu de la page en fonction de l'onglet sélectionné dans une barre de navigation. """

        # Vérifie l'index de l'onglet sélectionné.
        if e.control.selected_index == 0:
            # Si l'index est 0, cela indique généralement le premier onglet.
            chart.current.visible = True  # Rend le graphique visible.
            checkboxes.current.visible = True  # Rend les checkboxes (contrôles de type Switch pour les chaînes) visibles.
            list_view_ref.current.visible = False  # Masque la vue de liste détaillée.

        else:
            # Pour tout autre onglet sélectionné,
            chart.current.visible = False  # Masque le graphique.
            checkboxes.current.visible = False  # Masque les checkboxes.
            list_view_ref.current.visible = True  # Affiche la vue de liste détaillée.

        # Met à jour la vue actuelle pour refléter les changements.
        self.page.views[-1].update()

    @staticmethod
    def _get_color_by_chain(chain: str):
        """ Retourne la couleur associée à la chaîne. """
        return {
            "A": ft.colors.RED,
            "B": ft.colors.GREEN,
            "C": ft.colors.BLUE,
            "D": ft.colors.YELLOW,
            "E": ft.colors.PURPLE,
            "F": ft.colors.ORANGE,
            "G": ft.colors.CYAN,
            "H": ft.colors.PINK,
            "I": ft.colors.LIGHT_GREEN,
            "J": ft.colors.LIGHT_BLUE,
            "K": ft.colors.RED_200,
            "L": ft.colors.GREEN_200,
            "M": ft.colors.BLUE_200,
            "N": ft.colors.YELLOW_200,
            "O": ft.colors.PURPLE_200,
            "P": ft.colors.ORANGE_200,
            "Q": ft.colors.CYAN_200,
            "R": ft.colors.PINK_200,
            "S": ft.colors.LIGHT_GREEN_200,
            "T": ft.colors.LIGHT_BLUE_200,
            "U": ft.colors.RED_400,
            "V": ft.colors.GREEN_400,
            "W": ft.colors.BLUE_400,
            "X": ft.colors.YELLOW_400,
            "Y": ft.colors.PURPLE_400,
            "Z": ft.colors.ORANGE_400,
            "a": ft.colors.CYAN_400,
            "b": ft.colors.PINK_400,
            "c": ft.colors.LIGHT_GREEN_400,
            "d": ft.colors.LIGHT_BLUE_400,
            "e": ft.colors.RED_600,
            "f": ft.colors.GREEN_600,
            "g": ft.colors.BLUE_600,
            "h": ft.colors.YELLOW_600,
            "i": ft.colors.PURPLE_600,
            "j": ft.colors.ORANGE_600,
            "k": ft.colors.CYAN_600,
            "l": ft.colors.PINK_600,
            "m": ft.colors.LIGHT_GREEN_600,
            "n": ft.colors.LIGHT_BLUE_600,
            "o": ft.colors.RED_800,
            "p": ft.colors.GREEN_800,
            "q": ft.colors.BLUE_800,
            "r": ft.colors.YELLOW_800,
            "s": ft.colors.PURPLE_800,
            "t": ft.colors.ORANGE_800,
            "u": ft.colors.CYAN_800,
            "v": ft.colors.PINK_800,
            "w": ft.colors.LIGHT_GREEN_800,
            "x": ft.colors.LIGHT_BLUE_800,
            "y": ft.colors.RED_900,
            "z": ft.colors.GREEN_900
        }[chain]
