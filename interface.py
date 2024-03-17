import flet as ft
import pyperclip


class FletApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Protein Hydrophobicity Profiler"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.theme = ft.Theme(color_scheme_seed=ft.colors.PINK, use_material3=True)

        self.main_container = ft.Row(
            [
                ft.Text("Aucun fichier sélectionné", disabled=True)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

        self.weighting = ft.TextField(
            label="Pondérations aux extrémités",
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9\.]", replacement_string=""),
            keyboard_type=ft.KeyboardType.NUMBER,
            value="50.0",
            bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLACK),
            max_lines=1,
            min_lines=1,
            tooltip="Valeur comprise entre 0 et 100.",
            suffix_icon=ft.icons.PERCENT_ROUNDED,
            on_change=self.on_weighting_changed
        )

        self.window_size = ft.TextField(
            label="Taille de la fenêtre",
            input_filter=ft.NumbersOnlyInputFilter(),
            keyboard_type=ft.KeyboardType.NUMBER,
            value="9",
            bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLACK),
            max_lines=1,
            min_lines=1,
            tooltip="Valeur entière supérieure à 0.",
            on_change=self.on_window_size_changed
        )

        self.model = ft.Dropdown(
            label="Modèle",
            hint_text="Choisir un modèle",
            options=[
                ft.dropdown.Option("0", "Kyte & Doolittle"),
                ft.dropdown.Option("1", "Hopp-Woods"),
                ft.dropdown.Option("2", "Eisenberg"),
                ft.dropdown.Option("4", "Engelman - GES"),
            ],
            color=ft.colors.ON_SECONDARY_CONTAINER,
            bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLACK),
            filled=True,
            on_change=self.check_parameters
        )

        self.rail = ft.NavigationRail(
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            leading=ft.FloatingActionButton(
                icon=ft.icons.UPLOAD_FILE_ROUNDED,
                text="Nouveau profil d'hypdrophobicité",
                on_click=lambda _: self.pick_files_dialog.pick_files(
                    allow_multiple=False,
                    allowed_extensions=["pdb"],
                    dialog_title="Sélectionner un fichier PDB",
                    file_type=ft.FilePickerFileType.CUSTOM,
                )),
            group_alignment=-0.9,
        )

        self.protein_name = ft.Text(
            size=30,
            weight=ft.FontWeight.BOLD,
            selectable=True,
            spans=[ft.TextSpan(text="Nom de la protéine", on_click=self.name_prot_clicked)]
        )

        self.pick_files_dialog = ft.FilePicker(
            on_result=self.pick_files_result
        )

        self.validate_button = ft.FilledButton(
            text="Valider",
            on_click=self.validate_pressed,
            disabled=True
        )

        self.dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Choisissez vos paramètres"),
            content=ft.Column(
                [
                    self.weighting,
                    self.window_size,
                    self.model
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True
            ),
            actions=[
                ft.TextButton(
                    text="Annuler",
                    on_click=self.close_dlg
                ),
                self.validate_button
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.pb = ft.Banner(
            actions=[
                ft.TextButton(icon=ft.icons.CLOSE_ROUNDED, on_click=self.close_banner),
            ]
        )

        self.page.overlay.append(self.pick_files_dialog)
        self.page.dialog = self.dlg
        self.page.banner = self.pb

        self.path = None

        self.page.add(
            ft.Row(
                [
                    self.rail,
                    ft.VerticalDivider(width=1),
                    ft.Column([self.main_container], alignment=ft.MainAxisAlignment.CENTER, expand=True, spacing=20),
                ],
                expand=True
            )
        )

    def close_banner(self, e):
        """ Ferme la bannière. """
        self.page.banner.open = False
        self.page.update()

    def show_banner_click(self, e, icon=ft.icons.WARNING_AMBER_ROUNDED, text=""):
        """ Affiche une bannière avec un message et une icône. """
        self.page.banner.leading = ft.Icon(icon, size=40)
        self.page.banner.content = ft.Text(text)
        self.page.banner.open = True
        self.page.update()

    def close_dlg(self, e):
        """ Ferme la boîte de dialogue pour choisir les paramètres et réinitialise les valeurs. """
        self.dlg.open = False
        self.dlg.update()

        self.reset_values()

    def open_dlg(self):
        """ Ouvre la boîte de dialogue pour choisir les paramètres. """
        self.dlg.open = True
        self.dlg.update()

    def reset_values(self):
        """ Réinitialise les valeurs des champs de texte et le bouton de validation. """

        self.weighting.value = "50.0"
        self.window_size.value = "9"
        self.model.value = None
        self.validate_button.disabled = True

        self.validate_button.update()
        self.weighting.update()
        self.window_size.update()
        self.model.update()

    def on_weighting_changed(self, e):
        """ Vérifie si la valeur entrée est valide et met à jour le bouton de validation. """
        self.validate_input(e, 0, 100, float)

    def on_window_size_changed(self, e):
        """ Vérifie si la valeur entrée est valide et met à jour le bouton de validation. """
        self.validate_input(e, 1, None, int)

    def validate_input(self, e, min_val: int, max_val: [int, float], value_type: [int, float]):
        """
        Vérifie si la valeur entrée est valide et met à jour le bouton de validation.
        :param min_val: Valeur minimale autorisée.
        :param max_val: Valeur maximale autorisée.
        :param value_type: Type de la valeur attendue.
        """

        # Si le champ est vide, on désactive le bouton de validation sinon on vérifie la valeur.
        if not e.control.value:
            self.validate_button.disabled = True
        else:
            # On essaie de convertir la valeur en le type attendu.
            try:
                value = value_type(e.control.value)

                # Si la valeur est hors des bornes, on la supprime.
                if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                    e.control.value = e.control.value[:-1]

                # Sinon, on vérifie les autres champs.
                else:
                    self.check_parameters(e)

            # Si la valeur n'est pas du bon type, on la supprime.
            except ValueError:
                e.control.value = e.control.value[:-1]

        e.control.update()  # On met à jour le champ de texte.
        self.validate_button.update()  # On met à jour le bouton de validation.

    def check_parameters(self, e):
        """ Vérifie si les paramètres sont valides pour activer le bouton de validation. """
        self.validate_button.disabled = not all([self.weighting.value, self.window_size.value, self.model.value])
        self.validate_button.update()

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        """ Récupère le chemin du fichier sélectionné et ouvre la boîte de dialogue pour choisir les paramètres. """
        if e.files:
            self.path = e.files[0].path
            self.open_dlg()

    def validate_pressed(self, e):
        """ Vérifie si le fichier sélectionné est valide et crée le profil d'hydrophobicité. """

        if True:
            self.create_profile(e)
        else:
            self.show_banner_click(
                e,
                icon=ft.icons.WARNING_AMBER_ROUNDED,
                text="Un problème est survenu avec le fichier sélectionné."
            )

    def create_profile(self, e):
        """ Crée le profil d'hydrophobicité de la protéine. """

        weight = float(self.weighting.value)
        window_size = int(self.window_size.value)
        model = int(self.model.value)
        path = self.path

        self.close_dlg(e)

        self.main_container.controls = [ft.Column(
            [
                self.protein_name,
                ft.Tabs(
                    selected_index=1,
                    animation_duration=300,
                    tabs=[
                        ft.Tab(
                            text="Tab 1",
                            content=ft.Container(
                                content=ft.Text("This is Tab 1"), alignment=ft.alignment.center
                            ),
                        )]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )]

        self.main_container.update()

    def name_prot_clicked(self, e):
        """ Copie le nom de la protéine dans le presse-papier lorsqu'il est cliqué et affiche une bannière. """

        pyperclip.copy(self.protein_name.spans[0].text)
        self.show_banner_click(
            e,
            icon=ft.icons.CHECK_CIRCLE_ROUNDED,
            text="Nom de la protéine copié dans le presse-papier."
        )
