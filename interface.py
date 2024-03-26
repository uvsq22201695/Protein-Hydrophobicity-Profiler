import flet as ft


def _close_banner(e):
    """ Ferme la bannière. """
    e.open = False
    e.update()


def _show_banner_click(e: ft.Banner, icon: ft.icons, text: str):
    """ Affiche une bannière avec une icône et un texte. """

    e.leading = ft.Icon(name=icon, size=40)
    e.content = ft.Text(value=text, size=15)
    e.open = True
    e.update()


def _open_dlg(e):
    """ Ouvre la boîte de dialogue pour choisir les paramètres. """
    e.open = True
    e.update()


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
            on_change=self._on_weighting_changed
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
            on_change=self._on_window_size_changed
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
            on_change=self._check_parameters
        )

        self.rail = ft.NavigationRail(
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            leading=ft.FloatingActionButton(
                icon=ft.icons.UPLOAD_FILE_ROUNDED,
                text="Nouveau profil d'hypdrophobicité",
                on_click=lambda _: pick_files_dialog.pick_files(
                    allow_multiple=False,
                    allowed_extensions=["pdb"],
                    dialog_title="Sélectionner un fichier PDB",
                    file_type=ft.FilePickerFileType.CUSTOM,
                )),
            group_alignment=-0.9,
        )

        pick_files_dialog = ft.FilePicker(on_result=self._pick_files_result)
        self.page.overlay.append(pick_files_dialog)

        self.protein_name = ft.Text(
            size=30,
            weight=ft.FontWeight.BOLD,
            selectable=True,
            spans=[ft.TextSpan(text="Nom de la protéine", on_click=self._copy_to_clipboard)]
        )

        self.validate_button = ft.FilledButton(
            text="Valider",
            on_click=self._validate_pressed,
            disabled=True
        )

        self.pd = ft.AlertDialog(
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
                    on_click=lambda _: self._close_dlg(self.pd)
                ),
                self.validate_button
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        self.page.dialog = self.pd

        self.pb = ft.Banner(
            actions=[
                ft.IconButton(icon=ft.icons.CLOSE_ROUNDED, on_click=lambda _: _close_banner(self.pb)),
            ]
        )
        self.page.banner = self.pb

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

    def _close_dlg(self, e):
        """ Ferme la boîte de dialogue pour choisir les paramètres et réinitialise les valeurs. """
        e.open = False
        e.update()

        self._reset_values()

    def _reset_values(self):
        """ Réinitialise les valeurs des champs de texte et le bouton de validation. """

        self.weighting.value = "50.0"
        self.window_size.value = "9"
        self.model.value = None
        self.validate_button.disabled = True

        self.validate_button.update()
        self.weighting.update()
        self.window_size.update()
        self.model.update()

    def _on_weighting_changed(self, e):
        """ Vérifie si la valeur entrée est valide et met à jour le bouton de validation. """
        self._validate_input(e, 0, 100, float)

    def _on_window_size_changed(self, e):
        """ Vérifie si la valeur entrée est valide et met à jour le bouton de validation. """
        self._validate_input(e, 1, None, int)

    def _validate_input(self, e, min_val: int, max_val: [int, float], value_type: [int, float]):
        """
        Vérifie si la valeur entrée est valide et met à jour le bouton de validation.
        :param min_val: Valeur minimale autorisée.
        :param max_val: Valeur maximale autorisée.
        :param value_type: Type de la valeur attendue.
        """

        if not e.control.value:
            self.validate_button.disabled = True
        else:
            try:
                value = value_type(e.control.value)

                if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                    e.control.value = e.control.value[:-1]
                else:
                    self._check_parameters(e)

            except ValueError:
                e.control.value = e.control.value[:-1]

        e.control.update()
        self.validate_button.update()

    def _check_parameters(self, _):
        """ Vérifie si les paramètres sont valides pour activer le bouton de validation. """
        self.validate_button.disabled = not all([self.weighting.value, self.window_size.value, self.model.value])
        self.validate_button.update()

    def _pick_files_result(self, e: ft.FilePickerResultEvent):
        """ Récupère le chemin du fichier sélectionné et ouvre la boîte de dialogue pour choisir les paramètres. """
        if e.files:
            self.path = e.files[0].path
            _open_dlg(self.pd)

    def _validate_pressed(self, _):
        """ Vérifie si le fichier sélectionné est valide et crée le profil d'hydrophobicité. """

        if True:
            self._create_profile()
        else:
            self.show_banner_click(
                self.pb,
                icon=ft.icons.WARNING_AMBER_ROUNDED,
                text="Un problème est survenu avec le fichier sélectionné."
            )

    def _create_profile(self):
        """ Crée le profil d'hydrophobicité de la protéine. """
        self._close_dlg(self.pd)

        weight = float(self.weighting.value)
        window_size = int(self.window_size.value)
        model = str(self.model.value)
        path = self.path

        self.main_container.controls = [ft.Column(
            [
                self.protein_name,
                ft.Tabs(
                    selected_index=0,
                    animation_duration=300,
                    tabs=[
                        ft.Tab(
                            text="Profil d'hydrophobicité",
                            content=ft.Container(
                                content=ft.Text("This is Tab 1"), alignment=ft.alignment.center
                            ),
                        ),
                        ft.Tab(
                            text="Détails",
                            content=ft.Container(
                                content=ft.Text("This is Tab 2"), alignment=ft.alignment.center
                            ),
                        ),]
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )]

        self.main_container.update()

    def _copy_to_clipboard(self, e):
        """ Copie le texte dans le presse-papiers. """

        self.page.set_clipboard(e.control.text)
        _show_banner_click(
            self.pb,
            icon=ft.icons.CHECK_CIRCLE_ROUNDED,
            text="Texte copié dans le presse-papiers."
        )
