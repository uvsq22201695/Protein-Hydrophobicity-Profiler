import flet as ft
import time


class FletApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Protein Hydrophobicity Profiler"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.theme = ft.Theme(color_scheme_seed=ft.colors.PINK, use_material3=True)
        page.banner = ft.Banner(
            leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, size=40),
            actions=[
                ft.TextButton(icon=ft.icons.CLOSE_ROUNDED, on_click=self.close_banner),
            ],
        )

        main_container = [ft.Text("Aucun fichier sélectionné", disabled=True)]

        self.weighting = ft.TextField(
            label="Pondérations aux extrémités",
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9\.]", replacement_string=""),
            keyboard_type=ft.KeyboardType.NUMBER,
            max_lines=1,
            min_lines=1,
            value="50.0",
            suffix_icon=ft.icons.PERCENT_ROUNDED,
            on_change=self.weighting_changed,
            bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLACK),
        )

        self.window_size = ft.TextField(
            label="Taille de la fenêtre",
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""),
            keyboard_type=ft.KeyboardType.NUMBER,
            bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLACK),
            max_lines=1,
            min_lines=1,
        )

        self.model = ft.Dropdown(label="Modèle", hint_text="Choisir un modèle",
                                 options=[ft.dropdown.Option("0", "Kyte & Doolittle"),
                                          ft.dropdown.Option("1", "Hopp-Woods"),
                                          ft.dropdown.Option("2", "Eisenberg"),
                                          ft.dropdown.Option("4", "Engelman - GES"),
                                          ],
                                 color=ft.colors.ON_SECONDARY_CONTAINER,
                                 bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                                 filled=True)

        self.pick_files_dialog = ft.FilePicker(on_result=self.pick_files_result)
        page.overlay.append(self.pick_files_dialog)

        self.dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Choisissez vos paramètres"),
            content=ft.Column([self.weighting, self.window_size, self.model], alignment=ft.MainAxisAlignment.CENTER,
                              tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=self.close_dlg),
                ft.FilledButton("Valider", on_click=self.close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.rail = ft.NavigationRail(
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            leading=ft.FloatingActionButton(icon=ft.icons.UPLOAD_FILE_ROUNDED,
                                            text="Nouveau profil d'hydrophobicité",
                                            on_click=lambda _: self.pick_files_dialog.pick_files(
                                                allow_multiple=False,
                                                allowed_extensions=["pdb"],
                                                dialog_title="Sélectionner un fichier PDB",
                                                file_type=ft.FilePickerFileType.CUSTOM,

                                            )),
            group_alignment=-0.9,
        )

        page.add(
            ft.Row(
                [
                    self.rail,
                    ft.VerticalDivider(width=1),
                    ft.Column([
                        ft.Row(main_container,
                               alignment=ft.MainAxisAlignment.CENTER)
                    ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True),
                ],
                expand=True,
            )
        )

    def close_banner(self, e):
        self.page.banner.open = False
        self.page.update()

    def show_banner_click(self, e, *args, **kwargs):
        self.close_banner(e)
        self.page.banner.content = ft.Text(*args, **kwargs)
        self.page.banner.open = True
        self.page.update()

        time.sleep(5)
        self.close_banner(e)

    def close_dlg(self, e):
        self.dlg.open = False
        self.page.update()

    def open_dlg(self):
        self.page.dialog = self.dlg
        self.dlg.open = True
        self.page.update()

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            with open(e.files[0].path, "r") as f:
                pass

            if True:
                self.open_dlg()

    def weighting_changed(self, e):
        if not self.weighting.value:
            return

        if float(self.weighting.value) < 0 or float(self.weighting.value) > 100:
            self.weighting.value = self.weighting.value[:-1]
            self.weighting.update()
            self.show_banner_click(e, "Veuillez entrer un nombre compris entre 0 et 100.")
