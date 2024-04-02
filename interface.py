import math

import flet as ft

from profile_generation import HydrophobicityProfile
from pdb import PDBFile


class FletApp:
    def __init__(self, page):
        self.page = page
        self.path = None

        self.page.title = "Protein Hydrophobicity Profiler"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.theme = ft.Theme(color_scheme_seed=ft.colors.PINK, use_material3=True)

        main_content = ft.Ref[ft.Column]()
        page_dialog = ft.Ref[ft.AlertDialog]()
        weighting = ft.Ref[ft.TextField]()
        window_size = ft.Ref[ft.TextField]()
        model = ft.Ref[ft.Dropdown]()
        validate_button = ft.Ref[ft.FilledButton]()

        pick_files_dialog = ft.FilePicker(on_result=lambda e: self._pick_files_result(e, page_dialog))
        self.page.overlay.append(pick_files_dialog)

        models_name = HydrophobicityProfile.get_models_names()

        self.page.dialog = ft.AlertDialog(
            ref=page_dialog,
            modal=True,
            title=ft.Text("Choose your parameters"),
            content=ft.Column(
                [
                    ft.TextField(
                        border_radius=20,
                        ref=weighting,
                        label="Weighting at the ends",
                        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9\.]", replacement_string=""),
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
                    ft.TextField(
                        border_radius=20,
                        ref=window_size,
                        label="Window size",
                        input_filter=ft.NumbersOnlyInputFilter(),
                        keyboard_type=ft.KeyboardType.NUMBER,
                        value="9",
                        bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                        max_lines=1,
                        min_lines=1,
                        tooltip="Integer value greater than 0.",
                        on_change=lambda e: self._validate_input(e, 1, None, int, validate_button,
                                                                 weighting, window_size, model)
                    ),
                    ft.Dropdown(
                        border_radius=20,
                        ref=model,
                        label="Model",
                        hint_text="Choose a model",
                        options=[
                            ft.dropdown.Option(str(i), models_name[i]) for i in range(len(models_name))
                        ],
                        color=ft.colors.ON_SECONDARY_CONTAINER,
                        # bgcolor=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                        filled=True,
                        on_change=lambda _: self._check_parameters(validate_button, weighting, window_size, model)
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True
            ),
            actions=[
                ft.TextButton(
                    text="Cancel",
                    on_click=lambda _: self._switch_dialog(page_dialog, weighting, window_size, model, validate_button)
                ),
                ft.FilledButton(
                    ref=validate_button,
                    text="Validate",
                    on_click=lambda _: self._generate_profile(page_dialog, weighting, window_size, model,
                                                              validate_button, main_content),
                    disabled=True
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.add(
            ft.Row([
                ft.Container(
                    ft.FilledButton(icon=ft.icons.FILE_UPLOAD_ROUNDED,
                                    text="Select a PDB file",
                                    on_click=lambda _: pick_files_dialog.pick_files(
                                        allow_multiple=False,
                                        allowed_extensions=["pdb"],
                                        dialog_title="Select a PDB file",
                                        file_type=ft.FilePickerFileType.CUSTOM,
                                    )),
                    padding=20
                ),
                ft.VerticalDivider(width=20),
                ft.Column([
                    ft.Text("No file selected", disabled=True),
                ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                    ref=main_content
                )],
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True
            )
        )

    @staticmethod
    def _check_parameters(validate_button: ft.Ref[ft.FilledButton], weighting: ft.Ref[ft.TextField],
                          window_size: ft.Ref[ft.TextField], model: ft.Ref[ft.Dropdown]):
        """ Vérifie si les paramètres sont valides pour activer le bouton de validation. """
        validate_button.current.disabled = not all(
            [weighting.current.value, window_size.current.value, model.current.value]
        )
        validate_button.current.update()

    @staticmethod
    def _reset_values(weighting: ft.Ref[ft.TextField], window_size: ft.Ref[ft.TextField],
                      model: ft.Ref[ft.Dropdown], validate_button: ft.Ref[ft.FilledButton]):
        """ Réinitialise les valeurs des champs de saisie et le bouton de validation. """
        if weighting is not None or window_size is not None or model is not None or validate_button is not None:
            weighting.current.value = "100.0"
            window_size.current.value = "9"
            model.current.value = None
            validate_button.current.disabled = True

    def _switch_dialog(self, page_dialog: ft.Ref[ft.AlertDialog], weighting: ft.Ref[ft.TextField] = None,
                       window_size: ft.Ref[ft.TextField] = None, model: ft.Ref[ft.Dropdown] = None,
                       validate_button: ft.Ref[ft.FilledButton] = None):
        """ Ouvre ou ferme la boîte de dialogue. """
        page_dialog.current.open = False if page_dialog.current.open else True
        page_dialog.current.update()

        self._reset_values(weighting, window_size, model, validate_button)

    def _validate_input(self, e: ft.ControlEvent, min_val: int, max_val: [int, float], value_type: [int, float],
                        validate_button: ft.Ref[ft.FilledButton], *args):
        """Vérifie si la valeur entrée est valide et met à jour le bouton de validation."""

        if not e.control.value:
            validate_button.current.disabled = True
        else:
            try:
                value = value_type(e.control.value)

                if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                    e.control.value = e.control.value[:-1]
                else:
                    self._check_parameters(validate_button, *args)

            except ValueError:
                e.control.value = e.control.value[:-1]

        e.control.update()
        validate_button.current.update()

    def _pick_files_result(self, e: ft.FilePickerResultEvent, page_dialog: ft.Ref[ft.AlertDialog]):
        """ Récupère le chemin du fichier sélectionné et ouvre la boîte de dialogue pour choisir les paramètres. """
        if e.files is not None:
            self.path = e.files[0].path
            self._switch_dialog(page_dialog)

    def _generate_profile(self, page_dialog: ft.Ref[ft.AlertDialog], weighting: ft.Ref[ft.TextField],
                          window_size: ft.Ref[ft.TextField], model: ft.Ref[ft.Dropdown],
                          validate_button: ft.Ref[ft.FilledButton], main_content: ft.Ref[ft.Column]):
        """ Génère un profil d'hydrophobicité à partir des paramètres choisis. """
        model_copy = int(model.current.value)
        window_size_copy = int(window_size.current.value) // 2
        weighting_copy = float(weighting.current.value) / 100

        self._switch_dialog(page_dialog, weighting, window_size, model, validate_button)

        pdb_file = PDBFile(self.path)

        profile_list = []
        for chain, sequence in pdb_file.seqres.items():
            profile = HydrophobicityProfile(sequence, model_copy, window_size_copy, weighting_copy)
            profile_list.append((chain, profile))

        color_by_chain = {
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
            "K": ft.colors.YELLOW_200,
            "L": ft.colors.PURPLE_200,
            "M": ft.colors.ORANGE_200,
            "N": ft.colors.CYAN_200,
            "O": ft.colors.PINK_200,
            "P": ft.colors.RED_200,
            "Q": ft.colors.GREEN_200,
            "R": ft.colors.BLUE_200,
            "S": ft.colors.YELLOW_400,
            "T": ft.colors.PURPLE_400,
            "U": ft.colors.ORANGE_400,
            "V": ft.colors.CYAN_400,
            "W": ft.colors.PINK_400,
            "X": ft.colors.RED_400,
            "Y": ft.colors.GREEN_400,
            "Z": ft.colors.BLUE_400,
        }

        data_list = []
        for chain, profile in profile_list:
            data_list.append(
                ft.LineChartData(
                    data_points=profile.points,
                    stroke_width=8,
                    curved=True,
                    stroke_cap_round=True,
                    color=color_by_chain[chain],
                    data=chain
                )
            )

        min_y = math.inf
        max_y = -math.inf
        min_x = math.inf
        max_x = -math.inf
        for _, profile in profile_list:
            if profile.abscissa_axe.min_value < min_x:
                min_x = profile.abscissa_axe.min_value
            if profile.abscissa_axe.max_value > max_x:
                max_x = profile.abscissa_axe.max_value
            if profile.ordinate_axe.min_value < min_y:
                min_y = profile.ordinate_axe.min_value
            if profile.ordinate_axe.max_value > max_y:
                max_y = profile.ordinate_axe.max_value

        chart = ft.LineChart(
            data_series=data_list,
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
            min_y=min_y,
            max_y=max_y,
            min_x=min_x,
            max_x=max_x,
            horizontal_grid_lines=ft.ChartGridLines(
                interval=1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
            ),
            vertical_grid_lines=ft.ChartGridLines(
                interval=5, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
            ),
            left_axis=ft.ChartAxis(
                title=ft.Text("Hydrophobicity"),
                labels_interval=1,
                labels_size=50
            ),
            bottom_axis=ft.ChartAxis(
                title=ft.Text("Amino acids"),
                labels_interval=50,
                labels_size=50
            ),
            border=ft.border.all(3, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
            expand=True
        )

        main_content.current.controls.clear()

        main_content.current.controls.append(
            ft.Text(
                size=30,
                weight=ft.FontWeight.BOLD,
                selectable=True,
                spans=[ft.TextSpan(text=f"{pdb_file.journal.title}")],
                text_align=ft.TextAlign.CENTER
            )
        )

        main_content.current.alignment = ft.MainAxisAlignment.START

        navigation_bar = ft.Ref[ft.NavigationBar]()

        main_content.current.controls.append(
            ft.Container(
                content=ft.Column(
                    [ft.NavigationBar(
                        destinations=[
                            ft.NavigationDestination(icon=ft.icons.STACKED_LINE_CHART_ROUNDED,
                                                     label="Hydrophobicity Profile"),
                            ft.NavigationDestination(icon=ft.icons.INFO_ROUNDED, label="Details")
                        ],
                        on_change=lambda e: self._switch_content(e, main_content, profile_list, data_list, chart,
                                                                 model, model_copy, window_size_copy, weighting_copy,
                                                                 pdb_file, navigation_bar),
                        width=self.page.width / 2,
                        ref=navigation_bar,
                        data=0
                    )]
                ),
                border_radius=20,
            )
        )

        main_content.current.controls.append(
            ft.Row(
                [ft.Checkbox(
                    label=f"Show chain {chain}",
                    value=True,
                    on_change=lambda e: self._show_hide_chains(e, data_list)
                ) for chain, _ in profile_list],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

        main_content.current.controls.append(chart)

        main_content.current.update()

    @staticmethod
    def _show_hide_chains(e, data_list):
        """ Affiche ou masque les chaînes sélectionnées. """
        if e.control.value:
            for data in data_list:
                if data.data == e.control.label[-1]:
                    data.visible = True
                    data.update()
                    break
        else:
            for data in data_list:
                if data.data == e.control.label[-1]:
                    data.visible = False
                    data.update()
                    break

    def _switch_content(self, e: ft.ControlEvent, main_content: ft.Ref[ft.Column], profile_list: list,
                        data_list: list, chart: ft.LineChart, model: ft.Ref[ft.Dropdown], model_copy: int,
                        window_size_copy: int, weighting_copy: float, pdb_file: PDBFile,
                        navigation_bar: ft.Ref[ft.NavigationBar]):
        """ Change le contenu de la page en fonction de l'onglet sélectionné. """
        if e.control.selected_index == navigation_bar.current.data:
            return
        else:
            navigation_bar.current.data = e.control.selected_index

        if e.control.selected_index == 0:
            main_content.current.controls.pop(2)
            main_content.current.controls.append(
                ft.Row(
                    [ft.Checkbox(
                        label=f"Show chain {chain}",
                        value=True,
                        on_change=lambda e: self._show_hide_chains(e, data_list)
                    ) for chain, _ in profile_list],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )
            main_content.current.controls.append(chart)

        else:
            main_content.current.controls.pop(3)
            main_content.current.controls.pop(2)
            main_content.current.controls.append(
                ft.ListView([
                    ft.ExpansionPanelList(
                        expand_icon_color=ft.colors.BLUE_GREY,
                        spacing=20,
                        elevation=8,
                        divider_color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE),
                        controls=[
                            ft.ExpansionPanel(
                                header=ft.ListTile(leading=ft.Icon(ft.icons.NEWSPAPER_ROUNDED),
                                                   title=ft.Text("Journal Information")),
                                can_tap_header=True,
                                content=ft.ListTile(
                                    title=ft.Markdown(
                                        value=f"**Title:** {pdb_file.journal.title if pdb_file.journal.title else 'Not available'}\n\n" +
                                              f"**Authors:** {', '.join(pdb_file.journal.authors) if pdb_file.journal.authors else 'Non disponible'}\n\n" +
                                              f"**PubMed Link:** [{pdb_file.journal.pubmed_link if pdb_file.journal.pubmed_link else 'Non disponible'}]" +
                                              f"({pdb_file.journal.pubmed_link if pdb_file.journal.pubmed_link else '#'})\n\n" +
                                              f"**PubMed ID:** {pdb_file.journal.pubmed_id if pdb_file.journal.pubmed_id else 'Non disponible'}\n\n" +
                                              f"**DOI:** {pdb_file.journal.digital_object_identifier if pdb_file.journal.digital_object_identifier else 'Non disponible'}\n\n" +
                                              f"**ISSN:** {pdb_file.journal.international_standard_serial_number if pdb_file.journal.international_standard_serial_number else 'Non disponible'}\n\n" +
                                              f"**Publisher:** {pdb_file.journal.publisher if pdb_file.journal.publisher else 'Non disponible'}\n\n" +
                                              f"**Year:** {pdb_file.journal.reference.year if pdb_file.journal.reference.year else 'Non disponible'}\n\n" +
                                              f"**Volume:** {pdb_file.journal.reference.volume if pdb_file.journal.reference.volume else 'Non disponible'}\n\n" +
                                              f"**Page:** {pdb_file.journal.reference.page if pdb_file.journal.reference.page else 'Non disponible'}\n\n" +
                                              f"**Publication Name:** {pdb_file.journal.reference.pub_name if pdb_file.journal.reference.pub_name else 'Non disponible'}",
                                        auto_follow_links
                                        =True,
                                        selectable=True)
                                )
                            ),

                            ft.ExpansionPanel(
                                header=ft.ListTile(leading=ft.Icon(ft.icons.ATTACH_FILE_ROUNDED),
                                                   title=ft.Text("PDB Information")),
                                can_tap_header=True,
                                content=ft.ListTile(
                                    title=ft.Column([
                                        ft.Markdown(
                                            value=f"**Author(s):** {', '.join(pdb_file.authors) if pdb_file.authors else 'Non disponible'}\n\n" +
                                                  f"**PDB Link:** [{pdb_file.header.pdb_link if pdb_file.header.pdb_link else 'Non disponible'}]({pdb_file.header.pdb_link if pdb_file.header.pdb_link else '#'})\n\n" +
                                                  f"**Date:** {pdb_file.header.date if pdb_file.header.date else 'Non disponible'}\n\n" +
                                                  f"**Classification:** {pdb_file.header.classification if pdb_file.header.classification else 'Non disponible'}\n\n" +
                                                  f"**ID:** {pdb_file.header.id if pdb_file.header.id else 'Non disponible'}",
                                            auto_follow_links=True,
                                            selectable=True),
                                        ft.ExpansionPanelList(
                                            controls=[
                                                ft.ExpansionPanel(
                                                    header=ft.ListTile(leading=ft.Icon(ft.icons.LIST_ROUNDED),
                                                                       title=ft.Text("Sequence")),
                                                    can_tap_header=True,
                                                    content=ft.ListTile(
                                                        title=ft.Column([
                                                            ft.Markdown(
                                                                value=f"**Chain {chain}**\n\n{' '.join(sequence)}",
                                                                selectable=True) for chain, sequence in
                                                            pdb_file.seqres.items()
                                                        ])
                                                    )
                                                ),
                                                # ft.ExpansionPanel(
                                                #     header=ft.ListTile(leading=ft.Icon(ft.icons.EDIT_ROUNDED),
                                                #                        title=ft.Text("Remarks")),
                                                #     can_tap_header=True,
                                                #     content=ft.ListTile(
                                                #         title=ft.Markdown(
                                                #             value=f"**Remarks:** {pdb_file.remarks if pdb_file.remarks else 'Non disponible'}",
                                                #             selectable=True)
                                                #     )
                                                # )
                                            ]
                                        )
                                    ])
                                )
                            ),

                            ft.ExpansionPanel(
                                header=ft.ListTile(leading=ft.Icon(ft.icons.SETTINGS_ROUNDED),
                                                   title=ft.Text("Parameters")),
                                can_tap_header=True,
                                content=ft.ListTile(
                                    title=ft.Markdown(
                                        value=f"**Model:** {model.current.options[model_copy].text if model.current.options[model_copy].text else 'Non disponible'}\n\n" +
                                              f"**Window size:** {window_size_copy if window_size_copy else 'Non disponible'}\n\n" +
                                              f"**Weighting:** {weighting_copy * 100 if weighting_copy else 'Non disponible'}%",
                                        selectable=True))
                            )

                        ]
                    )],
                    auto_scroll=True,
                    padding=20,
                    expand=True
                )
            )

        main_content.current.update()
