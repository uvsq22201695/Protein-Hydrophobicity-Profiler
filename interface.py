import flet as ft
import pyperclip


class FletApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Protein Hydrophobicity Profiler"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.theme = ft.Theme(color_scheme_seed=ft.colors.PINK, use_material3=True)

        self.second_row = ft.Row(
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
                text="Nouveau profil d'hydrophobicité",
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
                    ft.Column([self.second_row], alignment=ft.MainAxisAlignment.CENTER, expand=True, spacing=20),
                ],
                expand=True
            )
        )

    def close_banner(self, e):
        self.page.banner.open = False
        self.page.update()

    def show_banner_click(self, e, icon=ft.icons.WARNING_AMBER_ROUNDED, text=""):
        self.close_banner(e)
        self.page.banner.content = ft.Text(text)
        self.page.banner.leading = ft.Icon(icon, size=40)
        self.page.banner.open = True
        self.page.update()

    def close_dlg(self, e):
        self.dlg.open = False
        self.dlg.update()

        self.reset_values()

    def open_dlg(self):
        self.dlg.open = True
        self.dlg.update()

    def reset_values(self):
        self.weighting.value = "50.0"
        self.window_size.value = "9"
        self.model.value = None
        self.validate_button.disabled = True

        self.validate_button.update()
        self.weighting.update()
        self.window_size.update()
        self.model.update()

    def on_weighting_changed(self, e):
        self.validate_input(e, self.weighting, 0, 100, float)

    def on_window_size_changed(self, e):
        self.validate_input(e, self.window_size, 1, None, int)

    def validate_input(self, e, field, min_val, max_val, value_type):
        if not field.value:
            self.validate_button.disabled = True
        else:
            try:
                value = value_type(field.value)
                if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                    field.value = field.value[:-1]
                else:
                    self.check_parameters(e)
            except ValueError:
                field.value = field.value[:-1]

        field.update()
        self.validate_button.update()

    def check_parameters(self, e):
        self.validate_button.disabled = not all([self.weighting.value, self.window_size.value, self.model.value])
        self.validate_button.update()

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.path = e.files[0].path
            self.open_dlg()

    def validate_pressed(self, e):

        if True:
            self.create_profile(e)
        else:
            self.show_banner_click(
                e,
                icon=ft.icons.WARNING_AMBER_ROUNDED,
                text="Un problème est survenu avec le fichier sélectionné."
            )

    def create_profile(self, e):
        self.second_row.controls = [ft.Column(
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

        self.second_row.update()

    def name_prot_clicked(self, e):
        pyperclip.copy(self.protein_name.spans[0].text)
        self.show_banner_click(
            e,
            icon=ft.icons.CHECK_CIRCLE_ROUNDED,
            text="Nom de la protéine copié dans le presse-papier."
        )
