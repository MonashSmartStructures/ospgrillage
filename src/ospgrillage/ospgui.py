import sys
import os
import logging

logger = logging.getLogger(__name__)

try:
    from PyQt6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QTabWidget,
        QVBoxLayout,
        QHBoxLayout,
        QFormLayout,
        QGroupBox,
        QLineEdit,
        QDoubleSpinBox,
        QSpinBox,
        QComboBox,
        QPushButton,
        QLabel,
        QScrollArea,
        QMenuBar,
        QToolBar,
        QStatusBar,
        QTextEdit,
        QCheckBox,
        QMessageBox,
        QRadioButton,
        QFileDialog,
        QStackedWidget,
    )
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QAction, QIcon

    _PYQT6_AVAILABLE = True

    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView

        _WEBENGINE_AVAILABLE = True
    except ImportError:
        _WEBENGINE_AVAILABLE = False

except ModuleNotFoundError:
    _PYQT6_AVAILABLE = False
    _WEBENGINE_AVAILABLE = False

    # Stub base classes so the class definitions below don't raise NameError at
    # import time.  Actual functionality is blocked by the check in main().
    class QWidget:
        pass  # type: ignore[assignment]

    class QMainWindow:
        pass  # type: ignore[assignment]

    class QApplication:
        pass  # type: ignore[assignment]


class BridgeInputWidget(QWidget):
    """Tabbed input form for bridge geometry, materials, sections, and members.

    Provides a structured form with separate tabs for each category of bridge
    model inputs.  This widget is embedded inside :class:`BridgeAnalysisGUI`
    and is not intended to be instantiated directly by users.

    .. note::
        Requires PyQt6.  Install with ``pip install "ospgrillage[gui]"``.
    """

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create tab widget for different input categories
        self.tabs = QTabWidget()

        # Add input tabs
        self.create_geometry_tab()
        self.create_materials_tab()
        self.create_sections_tab()
        self.create_members_tab()
        # self.create_loads_tab()
        # self.create_analysis_tab()

        # Add tabs to main layout
        main_layout.addWidget(self.tabs)

        # Add control buttons
        button_layout = QHBoxLayout()
        self.btn_apply = QPushButton("Apply Changes")
        self.btn_run = QPushButton("Create Geometry")
        button_layout.addWidget(self.btn_apply)
        button_layout.addWidget(self.btn_run)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def create_geometry_tab(self):
        """Geometry input tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Basic Geometry Group (unchanged)
        basic_group = QGroupBox("Basic Geometry")
        basic_form = QFormLayout()

        self.bridge_name = QLineEdit("My Bridge")
        self.bridge_length = QDoubleSpinBox()
        self.bridge_length.setRange(1, 1000)
        self.bridge_length.setValue(30)
        self.bridge_length.setSuffix(" m")

        self.bridge_width = QDoubleSpinBox()
        self.bridge_width.setRange(1, 100)
        self.bridge_width.setValue(10)
        self.bridge_width.setSuffix(" m")

        self.left_skew_angle = QDoubleSpinBox()
        self.left_skew_angle.setRange(-89, 89)
        self.left_skew_angle.setValue(5)
        self.left_skew_angle.setSuffix(" °")

        self.right_skew_angle = QDoubleSpinBox()
        self.right_skew_angle.setRange(-89, 89)
        self.right_skew_angle.setValue(5)
        self.right_skew_angle.setSuffix(" °")

        basic_form.addRow("Bridge Name", self.bridge_name)
        basic_form.addRow("Length", self.bridge_length)
        basic_form.addRow("Width", self.bridge_width)
        basic_form.addRow("Left Skew Angle", self.left_skew_angle)
        basic_form.addRow("Right Skew Angle", self.right_skew_angle)
        basic_group.setLayout(basic_form)

        # Mesh Settings Group
        mesh_group = QGroupBox("Mesh Settings")
        mesh_form = QFormLayout()

        self.bridge_type = QComboBox()
        self.bridge_type.addItems(["Straight", "Multi-Span Straight", "Curved"])

        self.long_beams = QSpinBox()
        self.long_beams.setRange(2, 20)
        self.long_beams.setValue(7)

        self.trans_beams = QSpinBox()
        self.trans_beams.setRange(2, 100)
        self.trans_beams.setValue(10)

        self.mesh_type = QComboBox()
        self.mesh_type.addItems(["Oblique", "Ortho"])

        self.opensees_file = QRadioButton("Opensees Command File")
        self.visualize = QRadioButton("Visualization")
        self.visualize.setChecked(True)

        # Add widgets to form
        mesh_form.addRow("Bridge Type", self.bridge_type)
        ##        mesh_form.addRow("Radius", self.bridge_radius)  # Added but hidden
        mesh_form.addRow("Longitudinal Beams", self.long_beams)
        mesh_form.addRow("Transverse Beams", self.trans_beams)
        mesh_form.addRow("Mesh Type", self.mesh_type)
        mesh_form.addRow(self.opensees_file)
        mesh_form.addRow(self.visualize)
        mesh_group.setLayout(mesh_form)

        # Create radius input but hide it initially
        self.radius_label = QLabel("Radius:")  # Store as instance variable
        self.bridge_radius = QDoubleSpinBox()
        self.bridge_radius.setRange(10, 10000)  # Adjust range as needed
        self.bridge_radius.setValue(100)
        self.bridge_radius.setSuffix(" m")
        self.bridge_radius.setVisible(False)  # Hidden by default
        mesh_form.addRow(self.radius_label, self.bridge_radius)
        self.radius_label.setVisible(False)
        self.bridge_radius.setVisible(False)

        # Create and hide multi span inputs:
        self.multi_span_dist_list_label = QLabel("Multi Span \nList")
        self.multi_span_dist_list = QLineEdit()
        self.multi_span_dist_list.setPlaceholderText(
            "[span1, span2, span3,..]"
        )  # Hint text
        self.multi_span_dist_list.setMaxLength(100)
        self.nl_multi_label = QLabel("List of transv. \nmembers in \nevery span")
        self.nl_multi = QLineEdit()
        self.nl_multi.setPlaceholderText(
            "[transv. members in span1, span2, span3,..]"
        )  # Hint text
        self.nl_multi.setMaxLength(100)
        self.continuous = QCheckBox("Continuous spans", checked=True)
        self.stitch_slab_x_spacing_label = QLabel("Spacing in spans")
        self.stitch_slab_x_spacing = QDoubleSpinBox()
        self.stitch_slab_x_spacing.setRange(0, 10)  # Adjust range as needed
        self.stitch_slab_x_spacing.setValue(0.5)
        self.stitch_slab_x_spacing.setSuffix(" m")

        mesh_form.addRow(self.multi_span_dist_list_label, self.multi_span_dist_list)
        mesh_form.addRow(self.nl_multi_label, self.nl_multi)
        mesh_form.addRow(self.continuous)
        mesh_form.addRow(self.stitch_slab_x_spacing_label, self.stitch_slab_x_spacing)
        self.stitch_slab_x_spacing_label.setVisible(False)
        self.multi_span_dist_list.setVisible(False)
        self.multi_span_dist_list_label.setVisible(False)
        self.nl_multi.setVisible(False)
        self.nl_multi_label.setVisible(False)
        self.continuous.setVisible(False)
        self.stitch_slab_x_spacing.setVisible(False)

        # Connect bridge type change to show/hide radius
        self.bridge_type.currentTextChanged.connect(self.toggle_radius_visibility)
        self.bridge_type.currentTextChanged.connect(self.toggle_multi_span_visibility)

        layout.addWidget(basic_group)
        layout.addWidget(mesh_group)
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Geometry")

    def toggle_radius_visibility(self, bridge_type):
        """Show radius input only for curved bridges"""
        show = self.bridge_type.currentText() == "Curved"
        self.radius_label.setVisible(show)
        self.bridge_radius.setVisible(show)

    def toggle_multi_span_visibility(self, bridge_type):
        show = self.bridge_type.currentText() == "Multi-Span Straight"
        self.multi_span_dist_list_label.setVisible(show)
        self.multi_span_dist_list.setVisible(show)
        self.nl_multi.setVisible(show)
        self.continuous.setVisible(show)
        self.stitch_slab_x_spacing.setVisible(show)
        self.nl_multi_label.setVisible(show)
        self.multi_span_dist_list.setVisible(show)
        self.stitch_slab_x_spacing_label.setVisible(show)

    def create_materials_tab(self):
        """Material properties tab with nested group boxes"""
        tab = QWidget()
        main_layout = QVBoxLayout()

        # Outer group box - Material Properties
        outer_group = QGroupBox("Material Properties")
        outer_layout = QVBoxLayout()

        # Material Type selection
        self.material_type = QComboBox()
        self.material_type.addItems(["Concrete", "Steel"])
        self.material_type.currentTextChanged.connect(self.update_material_fields)

        # Inner group box - Grade Options
        inner_group = QGroupBox("Standard Code Options")
        inner_layout = QFormLayout()

        # Grade of material
        self.grade_box = QComboBox()
        self.update_grade_fields(
            "AS5100-2017", "Concrete"
        )  # Initialize with concrete options
        self.grade_box.setCurrentText("65MPa")

        # Code of Material
        self.material_fc = QComboBox()
        self.update_material_fields("Concrete")  # Initialize with concrete options
        self.material_fc.currentTextChanged.connect(
            lambda: self.update_grade_fields(
                self.material_fc.currentText(), self.material_type.currentText()
            )
        )

        # Use Preset radio buttons
        self.use_preset_yes = QRadioButton("Use Preset")
        self.use_preset_no = QRadioButton("Custom Values")
        self.use_preset_yes.setChecked(True)

        # Custom material properties (hidden by default)
        self.custom_props_group = QGroupBox("Custom Material Properties")
        custom_props_layout = QFormLayout()

        self.material_ec = QDoubleSpinBox()
        self.material_ec.setRange(10000, 500000)
        self.material_ec.setValue(30000)
        self.material_ec.setSuffix(" MPa")

        self.material_density = QDoubleSpinBox()
        self.material_density.setRange(1000, 10000)
        self.material_density.setValue(2400)
        self.material_density.setSuffix(" kg/m³")

        self.material_poisson = QDoubleSpinBox()
        self.material_poisson.setRange(0.1, 0.5)
        self.material_poisson.setValue(0.2)
        self.material_poisson.setSingleStep(0.01)

        # Add widgets to inner layout
        inner_layout.addRow("Standard Code (Preset):", self.material_fc)
        inner_layout.addRow("Grade of material:", self.grade_box)
        inner_layout.addRow("Use Preset?:", self.use_preset_yes)
        inner_layout.addRow("", self.use_preset_no)

        # Add widgets to custom properties layout
        custom_props_layout.addRow("Elastic Modulus (E):", self.material_ec)
        custom_props_layout.addRow("Density:", self.material_density)
        custom_props_layout.addRow("Poisson's Ratio:", self.material_poisson)
        self.custom_props_group.setLayout(custom_props_layout)
        self.custom_props_group.setVisible(False)  # Hidden by default

        # Set inner group layout
        inner_group.setLayout(inner_layout)

        # Add widgets to outer layout
        outer_layout.addWidget(QLabel("Material Type:"))
        outer_layout.addWidget(self.material_type)
        outer_layout.addWidget(inner_group)
        outer_layout.addWidget(self.custom_props_group)

        # Set outer group layout
        outer_group.setLayout(outer_layout)

        # Add outer group to main layout
        main_layout.addWidget(outer_group)
        main_layout.addStretch()

        # Connect radio buttons to toggle custom properties
        self.use_preset_no.toggled.connect(
            lambda: self.custom_props_group.setVisible(self.use_preset_no.isChecked())
        )

        tab.setLayout(main_layout)
        self.tabs.addTab(tab, "Materials")

    def update_material_fields(self, material):
        """Update the compressive strength options based on material type"""
        self.material_fc.clear()

        if material == "Concrete":
            # AS5100-2017 concrete strength options
            self.material_fc.addItems(["AS5100-2017", "AASHTO-LRFD-8th"])
        elif material == "Steel":
            # Steel strength options
            self.material_fc.addItems(["AS5100.6-2004", "AASHTO-LRFD-8th"])

    def update_grade_fields(self, code, material):
        """Update the grade options based on code selected"""
        self.grade_box.clear()

        if code == "AS5100-2017":
            # AS5100-2017 concrete strength options
            self.grade_box.addItems(
                ["32MPa", "40MPa", "50MPa", "65MPa", "80MPa", "100MPa"]
            )
        if material == "Concrete":
            if code == "AASHTO-LRFD-8th":
                # AASHTO-LRFD-8th concrete strength options
                self.grade_box.addItems(
                    [
                        "2.4ksi",
                        "3.0ksi",
                        "3.6ksi",
                        "4.0ksi",
                        "5.0ksi",
                        "6.0ksi",
                        "7.5ksi",
                        "10.0ksi",
                        "15.0ksi",
                    ]
                )
        if material == "Steel":
            if code == "AASHTO-LRFD-8th":
                # AASHTO-LRFD-8th steel strength options
                self.grade_box.addItems(
                    ["A615-40", "A615-60", "A615-75", "A615-80", "A615-100", "A615-100"]
                )
        if code == "AS5100.6-2004":
            # Steel strength options
            self.grade_box.addItems(["R250N", "D500N", "D500L"])

    def create_sections_tab(self):
        """Cross-section input tab with specific properties"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)  # Set layout directly on the tab widget

        # Create a container widget for the scroll area
        container = QWidget()
        layout = QVBoxLayout(container)

        # Edge Longitudinal Section
        edge_long_group = QGroupBox("Edge Longitudinal Section")
        edge_long_form = QFormLayout(edge_long_group)  # Set layout directly on group

        self.edge_long_A = QDoubleSpinBox()
        self.edge_long_A.setRange(0.1, 10)
        self.edge_long_A.setValue(0.934)
        self.edge_long_A.setSingleStep(0.01)
        self.edge_long_A.setSuffix(" m²")

        self.edge_long_J = QDoubleSpinBox()
        self.edge_long_J.setRange(0.001, 1)
        self.edge_long_J.setValue(0.1857)
        self.edge_long_J.setSingleStep(0.01)
        self.edge_long_J.setSuffix(" m³")

        self.edge_long_Iz = QDoubleSpinBox()
        self.edge_long_Iz.setRange(0.001, 1)
        self.edge_long_Iz.setValue(0.3478)
        self.edge_long_Iz.setSingleStep(0.01)
        self.edge_long_Iz.setSuffix(" m⁴")

        self.edge_long_Iy = QDoubleSpinBox()
        self.edge_long_Iy.setRange(0.001, 1)
        self.edge_long_Iy.setValue(0.213602)
        self.edge_long_Iy.setSuffix(" m⁴")

        self.edge_long_Az = QDoubleSpinBox()
        self.edge_long_Az.setRange(0.001, 1)
        self.edge_long_Az.setValue(0.444795)
        self.edge_long_Az.setSuffix(" m²")

        self.edge_long_Ay = QDoubleSpinBox()
        self.edge_long_Ay.setRange(0.001, 1)
        self.edge_long_Ay.setValue(0.258704)
        self.edge_long_Ay.setSuffix(" m²")

        edge_long_form.addRow("Area (A)", self.edge_long_A)
        edge_long_form.addRow("Torsional Constant (J)", self.edge_long_J)
        edge_long_form.addRow("Moment of Inertia (Iz)", self.edge_long_Iz)
        edge_long_form.addRow("Moment of Inertia (Iy)", self.edge_long_Iy)
        edge_long_form.addRow("Shear Area (Az)", self.edge_long_Az)
        edge_long_form.addRow("Shear Area (Ay)", self.edge_long_Ay)

        # Longitudinal Section
        long_group = QGroupBox("Longitudinal Section")
        long_form = QFormLayout()

        self.long_A = QDoubleSpinBox()
        self.long_A.setRange(0.1, 10)
        self.long_A.setValue(1.025)
        self.long_A.setSuffix(" m²")

        self.long_J = QDoubleSpinBox()
        self.long_J.setRange(0.001, 1)
        self.long_J.setValue(0.1878)
        self.long_J.setSuffix(" m³")

        self.long_Iz = QDoubleSpinBox()
        self.long_Iz.setRange(0.001, 1)
        self.long_Iz.setValue(0.3694)
        self.long_Iz.setSuffix(" m⁴")

        self.long_Iy = QDoubleSpinBox()
        self.long_Iy.setRange(0.001, 1)
        self.long_Iy.setValue(0.3634)
        self.long_Iy.setSuffix(" m⁴")

        self.long_Az = QDoubleSpinBox()
        self.long_Az.setRange(0.001, 1)
        self.long_Az.setValue(0.4979)
        self.long_Az.setSuffix(" m²")

        self.long_Ay = QDoubleSpinBox()
        self.long_Ay.setRange(0.001, 1)
        self.long_Ay.setValue(0.309)
        self.long_Ay.setSuffix(" m²")

        long_form.addRow("Area (A)", self.long_A)
        long_form.addRow("Torsional Constant (J)", self.long_J)
        long_form.addRow("Moment of Inertia (Iz)", self.long_Iz)
        long_form.addRow("Moment of Inertia (Iy)", self.long_Iy)
        long_form.addRow("Shear Area (Az)", self.long_Az)
        long_form.addRow("Shear Area (Ay)", self.long_Ay)
        long_group.setLayout(long_form)

        # Transverse Section
        trans_group = QGroupBox("Transverse Section")
        trans_form = QFormLayout()

        self.trans_A = QDoubleSpinBox()
        self.trans_A.setRange(0.1, 10)
        self.trans_A.setValue(0.504)
        self.trans_A.setSuffix(" m²")

        self.trans_J = QDoubleSpinBox()
        self.trans_J.setRange(0.001, 1)
        self.trans_J.setValue(5.22303e-3)
        self.trans_J.setSuffix(" m³")

        self.trans_Iy = QDoubleSpinBox()
        self.trans_Iy.setRange(0.001, 1)
        self.trans_Iy.setValue(0.32928)
        self.trans_Iy.setSuffix(" m⁴")

        self.trans_Iz = QDoubleSpinBox()
        self.trans_Iz.setRange(0.001, 1)
        self.trans_Iz.setValue(1.3608e-3)
        self.trans_Iz.setSuffix(" m⁴")

        self.trans_Ay = QDoubleSpinBox()
        self.trans_Ay.setRange(0.001, 1)
        self.trans_Ay.setValue(0.42)
        self.trans_Ay.setSuffix(" m²")

        self.trans_Az = QDoubleSpinBox()
        self.trans_Az.setRange(0.001, 1)
        self.trans_Az.setValue(0.42)
        self.trans_Az.setSuffix(" m²")

        self.trans_unit_width = QCheckBox()
        self.trans_unit_width.setChecked(True)

        trans_form.addRow("Area (A)", self.trans_A)
        trans_form.addRow("Torsional Constant (J)", self.trans_J)
        trans_form.addRow("Moment of Inertia (Iy)", self.trans_Iy)
        trans_form.addRow("Moment of Inertia (Iz)", self.trans_Iz)
        trans_form.addRow("Shear Area (Ay)", self.trans_Ay)
        trans_form.addRow("Shear Area (Az)", self.trans_Az)
        trans_form.addRow("Unit Width", self.trans_unit_width)
        trans_group.setLayout(trans_form)

        # End Transverse Section
        end_trans_group = QGroupBox("End Transverse Section")
        end_trans_form = QFormLayout()

        self.end_trans_A = QDoubleSpinBox()
        self.end_trans_A.setRange(0.1, 10)
        self.end_trans_A.setValue(0.252)
        self.end_trans_A.setSuffix(" m²")

        self.end_trans_J = QDoubleSpinBox()
        self.end_trans_J.setRange(0.001, 1)
        self.end_trans_J.setValue(2.5012e-3)
        self.end_trans_J.setSuffix(" m³")

        self.end_trans_Iy = QDoubleSpinBox()
        self.end_trans_Iy.setRange(0.001, 1)
        self.end_trans_Iy.setValue(0.04116)
        self.end_trans_Iy.setSuffix(" m⁴")

        self.end_trans_Iz = QDoubleSpinBox()
        self.end_trans_Iz.setRange(0.001, 1)
        self.end_trans_Iz.setValue(0.6804e-3)
        self.end_trans_Iz.setSuffix(" m⁴")

        self.end_trans_Ay = QDoubleSpinBox()
        self.end_trans_Ay.setRange(0.001, 1)
        self.end_trans_Ay.setValue(0.21)
        self.end_trans_Ay.setSuffix(" m²")

        self.end_trans_Az = QDoubleSpinBox()
        self.end_trans_Az.setRange(0.001, 1)
        self.end_trans_Az.setValue(0.21)
        self.end_trans_Az.setSuffix(" m²")

        end_trans_form.addRow("Area (A)", self.end_trans_A)
        end_trans_form.addRow("Torsional Constant (J)", self.end_trans_J)
        end_trans_form.addRow("Moment of Inertia (Iy)", self.end_trans_Iy)
        end_trans_form.addRow("Moment of Inertia (Iz)", self.end_trans_Iz)
        end_trans_form.addRow("Shear Area (Ay)", self.end_trans_Ay)
        end_trans_form.addRow("Shear Area (Az)", self.end_trans_Az)
        end_trans_group.setLayout(end_trans_form)

        # Add all section groups to the scrollable layout
        layout.addWidget(edge_long_group)
        layout.addWidget(long_group)
        layout.addWidget(trans_group)
        layout.addWidget(end_trans_group)
        layout.addStretch()

        # Set up scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        # Add scroll area to main layout
        main_layout.addWidget(scroll)

        self.tabs.addTab(tab, "Sections")

    def create_members_tab(self):
        """Member assignment tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Beam Spacing Group
        beam_spacing_group = QGroupBox("Beam Spacing (optional)")
        beam_spacing_form = QFormLayout()

        self.beam_spacing_input = QLineEdit()
        self.beam_spacing_input.setPlaceholderText("e.g. 1.0, 2.5, 2.5, 2.5, 1.0")
        self.beam_spacing_input.setToolTip(
            "Comma-separated list of transverse spacings (m). "
            "First and last entries are edge overhangs; middle entries "
            "are between-beam distances. Leave blank for uniform spacing."
        )

        beam_spacing_form.addRow("Spacings (m)", self.beam_spacing_input)
        beam_spacing_group.setLayout(beam_spacing_form)

        # Edge Beams Group
        edge_beam_group = QGroupBox("Edge Beams")
        edge_beam_form = QFormLayout()

        self.edge_beam_offset = QDoubleSpinBox()
        self.edge_beam_offset.setRange(0.1, 5)
        self.edge_beam_offset.setValue(0.5)
        self.edge_beam_offset.setSingleStep(0.1)
        self.edge_beam_offset.setSuffix(" m")

        edge_beam_form.addRow("Edge Offset", self.edge_beam_offset)
        edge_beam_group.setLayout(edge_beam_form)

        layout.addWidget(beam_spacing_group)
        layout.addWidget(edge_beam_group)
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Members")

    def create_loads_tab(self):
        """Load cases tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Dead Load Group
        dl_group = QGroupBox("Dead Load")
        dl_form = QFormLayout()

        self.dl_magnitude = QDoubleSpinBox()
        self.dl_magnitude.setRange(0, 100)
        self.dl_magnitude.setValue(5)
        self.dl_magnitude.setSuffix(" kN/m²")

        self.dl_direction = QComboBox()
        self.dl_direction.addItems(["-Y (Downward)", "+Y (Upward)", "-Z", "+Z"])

        dl_form.addRow("Magnitude", self.dl_magnitude)
        dl_form.addRow("Direction", self.dl_direction)
        dl_group.setLayout(dl_form)

        # Live Load Group
        ll_group = QGroupBox("Live Load")
        ll_form = QFormLayout()

        self.ll_magnitude = QDoubleSpinBox()
        self.ll_magnitude.setRange(0, 100)
        self.ll_magnitude.setValue(10)
        self.ll_magnitude.setSuffix(" kN/m²")

        self.ll_direction = QComboBox()
        self.ll_direction.addItems(["-Y (Downward)", "+Y (Upward)", "-Z", "+Z"])

        ll_form.addRow("Magnitude", self.ll_magnitude)
        ll_form.addRow("Direction", self.ll_direction)
        ll_group.setLayout(ll_form)

        layout.addWidget(dl_group)
        layout.addWidget(ll_group)
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Loads")

    def create_analysis_tab(self):
        """Analysis settings tab (simplified)"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Output Settings Group
        output_group = QGroupBox("Output Settings")
        output_form = QFormLayout()

        self.output_displacements = QComboBox()
        self.output_displacements.addItems(["Yes", "No"])
        self.output_displacements.setCurrentIndex(0)

        self.output_forces = QComboBox()
        self.output_forces.addItems(["Yes", "No"])
        self.output_forces.setCurrentIndex(0)

        self.output_stresses = QComboBox()
        self.output_stresses.addItems(["Yes", "No"])

        output_form.addRow("Output Displacements", self.output_displacements)
        output_form.addRow("Output Forces", self.output_forces)
        output_form.addRow("Output Stresses", self.output_stresses)
        output_group.setLayout(output_form)

        layout.addWidget(output_group)
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Analysis")


class ResultsControlWidget(QWidget):
    """Left-panel controls for results-viewer mode.

    Shows the loaded file name, a loadcase dropdown, and member-filter
    checkboxes.  Signals are emitted when the user changes a control so
    that :class:`BridgeAnalysisGUI` can refresh the plot tabs.
    """

    _MEMBER_FLAGS = [
        ("EDGE_BEAM", "Edge Beam"),
        ("EXTERIOR_MAIN_BEAM_1", "Exterior Main Beam 1"),
        ("INTERIOR_MAIN_BEAM", "Interior Main Beam"),
        ("EXTERIOR_MAIN_BEAM_2", "Exterior Main Beam 2"),
        ("START_EDGE", "Start Edge"),
        ("END_EDGE", "End Edge"),
        ("TRANSVERSE_SLAB", "Transverse Slab"),
    ]

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # --- File info ---
        file_group = QGroupBox("Results File")
        file_layout = QVBoxLayout()
        self.file_label = QLabel("No file loaded")
        self.file_label.setWordWrap(True)
        file_layout.addWidget(self.file_label)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # --- Loadcase dropdown ---
        lc_group = QGroupBox("Load Case")
        lc_layout = QFormLayout()
        self.loadcase_combo = QComboBox()
        self.loadcase_combo.addItem("(no results loaded)")
        lc_layout.addRow("Select:", self.loadcase_combo)
        lc_group.setLayout(lc_layout)
        layout.addWidget(lc_group)

        # --- Member filter checkboxes ---
        members_group = QGroupBox("Member Filter")
        members_layout = QVBoxLayout()
        self.member_checkboxes = {}
        for flag_name, display_name in self._MEMBER_FLAGS:
            cb = QCheckBox(display_name)
            cb.setChecked(True)
            members_layout.addWidget(cb)
            self.member_checkboxes[flag_name] = cb
        members_group.setLayout(members_layout)
        layout.addWidget(members_group)

        # --- Shell contour controls ---
        self.contour_group = QGroupBox("Shell Contour")
        contour_layout = QFormLayout()
        self.contour_component_combo = QComboBox()
        for comp in (
            "Mx",
            "My",
            "Mz",
            "Vx",
            "Vy",
            "Vz",
            "Dx",
            "Dy",
            "Dz",
            "N11",
            "N22",
            "N12",
            "M11",
            "M22",
            "M12",
            "Q13",
            "Q23",
        ):
            self.contour_component_combo.addItem(comp)
        contour_layout.addRow("Component:", self.contour_component_combo)
        self.contour_colorscale_combo = QComboBox()
        for cs in ("RdBu_r", "Viridis", "Plasma", "Cividis", "Turbo"):
            self.contour_colorscale_combo.addItem(cs)
        contour_layout.addRow("Colorscale:", self.contour_colorscale_combo)
        self.contour_overlay_combo = QComboBox()
        for ov in ("None", "BMD", "SFD", "TMD", "Deflection"):
            self.contour_overlay_combo.addItem(ov)
        contour_layout.addRow("Overlay:", self.contour_overlay_combo)
        self.contour_group.setLayout(contour_layout)
        self.contour_group.setVisible(False)  # shown only for shell_beam
        layout.addWidget(self.contour_group)

        # --- Back button ---
        self.btn_back = QPushButton("Back to Wizard")
        layout.addWidget(self.btn_back)

        layout.addStretch()
        self.setLayout(layout)

    def populate_loadcases(self, loadcase_names):
        """Fill the combo box from a list of loadcase name strings."""
        self.loadcase_combo.blockSignals(True)
        self.loadcase_combo.clear()
        for name in loadcase_names:
            self.loadcase_combo.addItem(str(name))
        self.loadcase_combo.blockSignals(False)

    def update_available_members(self, proxy):
        """Enable/disable checkboxes based on which members have elements."""
        for flag_name, cb in self.member_checkboxes.items():
            member_name = flag_name.lower()
            has_elements = False
            info = proxy._members.get(member_name, {})
            for group in info.get("elements", []):
                if group:
                    has_elements = True
                    break
            cb.setEnabled(has_elements)
            cb.setChecked(has_elements)

    def set_file_info(self, filename, summary):
        """Update the file info label."""
        self.file_label.setText(f"<b>{filename}</b><br>{summary}")

    def selected_loadcase(self):
        """Return the currently selected loadcase name, or None."""
        text = self.loadcase_combo.currentText()
        if text and text != "(no results loaded)":
            return text
        return None

    def selected_members(self):
        """Return a Members bitflag from the checked boxes, or None for all."""
        try:
            import ospgrillage as og
        except ImportError:
            return None
        result = None
        for flag_name, cb in self.member_checkboxes.items():
            if cb.isChecked():
                flag = getattr(og.Members, flag_name)
                result = flag if result is None else (result | flag)
        return result if result is not None else og.Members.ALL

    def set_shell_contour_visible(self, visible):
        """Show or hide the shell contour controls based on model type."""
        self.contour_group.setVisible(visible)

    def set_shell_contour_enabled(self, enabled):
        """Enable or disable shell contour controls based on active tab."""
        self.contour_component_combo.setEnabled(enabled)
        self.contour_colorscale_combo.setEnabled(enabled)
        self.contour_overlay_combo.setEnabled(enabled)
        # Visual feedback: dim the title when disabled
        self.contour_group.setStyleSheet(
            "" if enabled else "QGroupBox { color: #999; }"
        )


class BridgeAnalysisGUI(QMainWindow):
    """Main window for the *ospgui* bridge geometry generator.

    Provides an interactive graphical interface for defining a bridge deck
    grillage model, previewing the generated *ospgrillage* Python code, and
    running the model directly within the same session.

    The window is divided into three panels:

    * **Left** — :class:`ospgrillage.ospgui.BridgeInputWidget` with tabbed input forms.
    * **Centre** — live code view showing the generated Python source.
    * **Right** — interactive 3-D mesh preview rendered via *Plotly*.

    Typical usage is through the ``ospgui`` console entry-point or
    programmatically::

        from ospgrillage.ospgui import main
        main()

    .. note::
        Requires PyQt6.  Install with ``pip install "ospgrillage[gui]"``.
    """

    def __init__(self):
        super().__init__()
        # self.setWindowIcon(QIcon("ospgrillage_logo.png"))  # Add your icon file
        # Add this stylesheet
        self.setStyleSheet(
            """
            /* Force light theme regardless of desktop settings */
            QWidget {
                background-color: #f0f0f0;
                color: #1a1a1a;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 1ex;
                font-weight: bold;
                color: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                top: -1px;
            }
            QTabBar::tab {
                background: #e0e0e0;
                color: #1a1a1a;
                border: 1px solid #cccccc;
                padding: 8px;
                min-width: 60px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom-color: #ffffff;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                background-color: #ffffff;
                color: #1a1a1a;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 3px;
                min-height: 20px;
            }
            QComboBox:disabled, QLineEdit:disabled,
            QSpinBox:disabled, QDoubleSpinBox:disabled {
                background-color: #e8e8e8;
                color: #999999;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #1a1a1a;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
            }
            QCheckBox {
                color: #1a1a1a;
            }
            QRadioButton {
                color: #1a1a1a;
            }
            QLabel {
                color: #1a1a1a;
            }
            QMenuBar {
                background-color: #f0f0f0;
                color: #1a1a1a;
            }
            QMenuBar::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QMenu {
                background-color: #ffffff;
                color: #1a1a1a;
            }
            QMenu::item:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QToolBar {
                background-color: #f0f0f0;
                border: none;
            }
            QStatusBar {
                background-color: #f0f0f0;
                color: #1a1a1a;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #006cbd;
            }
            QScrollArea {
                background-color: #f0f0f0;
            }
        """
        )
        self.setWindowTitle("ospgui")
        self.setGeometry(100, 100, 1400, 900)

        # Initialize variables to store user inputs
        self.bridge_params = {}
        self.generated_code = ""

        # Results viewer state
        self._mode = "wizard"  # "wizard" or "results"
        self._model_proxy = None  # _ModelProxy from loaded results
        self._results = None  # xarray Dataset
        self._stale_tabs = set()  # result tab names needing re-render

        # Create UI components
        self.create_menu_bar()
        self.create_status_bar()
        self.create_main_content()

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Python Script",
            "",
            "Python Files (*.py);;All Files (*)",
        )

        if file_name:
            try:
                with open(file_name, "r") as f:
                    content = f.read()
                    self.code_tab.setPlainText(content)
                    self.statusbar.showMessage(
                        f"Loaded: {os.path.basename(file_name)}", 3000
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file:\n{str(e)}")

    def show_about(self):
        QMessageBox.about(
            self,
            "About ospgui",
            "ospgui — GUI for ospgrillage\n\n"
            "Wizard mode: define bridge grillage geometry\n"
            "Results mode: view BMD/SFD/TMD/Deflection from .nc files\n\n"
            "ospgrillage v"
            + getattr(__import__("ospgrillage"), "__version__", "unknown"),
        )

    def create_menu_bar(self):
        """Create the main menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction(QIcon.fromTheme("document-new"), "New", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)

        open_results_action = QAction(
            QIcon.fromTheme("document-open"), "Open Results (.nc)", self
        )
        open_results_action.setShortcut("Ctrl+O")
        open_results_action.triggered.connect(self._open_results_file)
        file_menu.addAction(open_results_action)

        open_script_action = QAction("Open Script (.py)", self)
        open_script_action.triggered.connect(self.open_file)
        file_menu.addAction(open_script_action)

        save_action = QAction(QIcon.fromTheme("document-save"), "Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_code)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction(QIcon.fromTheme("application-exit"), "Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        ##        # Tools menu
        ##        tools_menu = menubar.addMenu("Tools")
        ##
        ##        settings_action = QAction("Settings", self)
        ##        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        help_menu.addAction(about_action)
        about_action.triggered.connect(self.show_about)

    def create_tool_bar(self):
        """Create the main toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Run Analysis action
        self.run_action = QAction(
            QIcon.fromTheme("media-playback-start"), "Create Geometry", self
        )
        self.run_action.setShortcut("F5")
        self.run_action.triggered.connect(self.run_analysis)
        toolbar.addAction(self.run_action)

        # Separator
        toolbar.addSeparator()

        # Zoom tools

    ##        zoom_in = QAction(QIcon.fromTheme("zoom-in"), "Zoom In", self)
    ##        zoom_out = QAction(QIcon.fromTheme("zoom-out"), "Zoom Out", self)
    ##        toolbar.addAction(zoom_in)
    ##        toolbar.addAction(zoom_out)

    def create_status_bar(self):
        """Create the status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

    def create_main_content(self):
        """Create the main content area with two-mode stacked layout.

        **Wizard mode** (page 0): left = BridgeInputWidget, right = Code + 3D tabs.
        **Results mode** (page 1): left = ResultsControlWidget, right = BMD/SFD/TMD/Def tabs.
        """
        from PyQt6.QtWidgets import QSplitter

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # ---- Left stacked widget ----
        self.left_stack = QStackedWidget()

        # Page 0: Wizard input panel
        self.input_panel = BridgeInputWidget()
        self.input_panel.btn_apply.clicked.connect(self.apply_changes)
        self.input_panel.btn_run.clicked.connect(self.run_analysis)
        self.left_stack.addWidget(self.input_panel)  # index 0

        # Page 1: Results controls
        self.results_panel = ResultsControlWidget()
        self.results_panel.loadcase_combo.currentIndexChanged.connect(
            self._on_results_control_changed
        )
        for cb in self.results_panel.member_checkboxes.values():
            cb.stateChanged.connect(self._on_results_control_changed)
        self.results_panel.contour_component_combo.currentIndexChanged.connect(
            self._on_results_control_changed
        )
        self.results_panel.contour_colorscale_combo.currentIndexChanged.connect(
            self._on_results_control_changed
        )
        self.results_panel.contour_overlay_combo.currentIndexChanged.connect(
            self._on_results_control_changed
        )
        self.results_panel.btn_back.clicked.connect(self._switch_to_wizard)
        self.left_stack.addWidget(self.results_panel)  # index 1

        self.left_stack.setMinimumWidth(200)
        splitter.addWidget(self.left_stack)
        splitter.setCollapsible(0, True)

        # ---- Right stacked widget ----
        self.right_stack = QStackedWidget()

        # Page 0: Wizard — code view + 3D view
        self.right_panel = QTabWidget()
        if _WEBENGINE_AVAILABLE:
            self.viz_tab = QWebEngineView()
            self.viz_tab.setHtml(
                "<html><body style='display:flex;align-items:center;"
                "justify-content:center;height:100vh;font-family:sans-serif;"
                "color:#888'><p>Click <b>Create Geometry</b> to see "
                "the 3-D model here.</p></body></html>"
            )
        else:
            self.viz_tab = QLabel(
                "Install PyQtWebEngine for interactive 3D visualization:\n"
                "  pip install PyQtWebEngine"
            )
            self.viz_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.code_tab = QTextEdit()
        self.code_tab.setStyleSheet("font-family: monospace; font-size: 10pt;")
        self.code_tab.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.right_panel.addTab(self.code_tab, "Code View")
        self.right_panel.addTab(self.viz_tab, "3D View")
        self.right_stack.addWidget(self.right_panel)  # index 0

        # Page 1: Results — BMD / SFD / TMD / Deflection tabs
        self.results_tabs = QTabWidget()
        _placeholder = (
            "<html><body style='display:flex;align-items:center;"
            "justify-content:center;height:100vh;font-family:sans-serif;"
            "color:#888'><p>Open a results file (.nc) to see "
            "diagrams here.</p></body></html>"
        )
        self._result_tab_widgets = {}
        for label in ("Deflection", "BMD", "SFD", "TMD", "Shell Contour"):
            if _WEBENGINE_AVAILABLE:
                tab = QWebEngineView()
                tab.setHtml(_placeholder)
            else:
                tab = QLabel("Install PyQtWebEngine for result plots")
                tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_tabs.addTab(tab, label)
            self._result_tab_widgets[label] = tab
        self.results_tabs.currentChanged.connect(self._on_result_tab_changed)
        self.right_stack.addWidget(self.results_tabs)  # index 1

        splitter.addWidget(self.right_stack)
        splitter.setStretchFactor(0, 1)  # left panel
        splitter.setStretchFactor(1, 2)  # right panel

    def apply_changes(self):
        """Handle Apply Changes button click"""
        try:
            # Collect all parameters from input fields
            self.collect_parameters()

            # Generate the ospgrillage code
            self.generate_ospgrillage_code()

            # Update code view
            self.code_tab.setPlainText(self.generated_code)

            # Update status bar
            self.statusbar.showMessage("Parameters applied successfully", 3000)

        except Exception as e:
            self.statusbar.showMessage(f"Error applying changes: {(e)}", 5000)
            logger.exception("Error in apply_changes: %s", e)

    def collect_parameters(self):
        """Collect all parameters from input fields"""
        self.bridge_params = {
            "geometry": {
                "name": self.input_panel.bridge_name.text(),
                "length": self.input_panel.bridge_length.value(),
                "width": self.input_panel.bridge_width.value(),
                "left_skew_angle": self.input_panel.left_skew_angle.value(),
                "right_skew_angle": self.input_panel.right_skew_angle.value(),
                #'num_spans': self.input_panel.num_spans.value(),
                "long_beams": self.input_panel.long_beams.value(),
                "trans_beams": self.input_panel.trans_beams.value(),
                "mesh_type": self.input_panel.mesh_type.currentText(),
                "need_command_file": self.input_panel.opensees_file.isChecked(),
                "bridge_type": self.input_panel.bridge_type.currentText(),
                "radius": self.input_panel.bridge_radius.value(),
                "multi_span_dist_list": self.input_panel.multi_span_dist_list.text(),
                "nl_multi": self.input_panel.nl_multi.text(),
                "continuous": self.input_panel.continuous.isChecked(),
                "stitch_slab_x_spacing": self.input_panel.stitch_slab_x_spacing.value(),
            },
            "materials": {
                "type": self.input_panel.material_type.currentText(),
                "ec": self.input_panel.material_ec.value(),
                "density": self.input_panel.material_density.value(),
                "poisson": self.input_panel.material_poisson.value(),
                "preset_yes": self.input_panel.use_preset_yes.isChecked(),
                "preset_no": self.input_panel.use_preset_no.isChecked(),
                "code": self.input_panel.material_fc.currentText(),
                "grade": self.input_panel.grade_box.currentText(),
            },
            "sections": {
                "edge_longitudinal": {
                    "A": self.input_panel.edge_long_A.value(),
                    "J": self.input_panel.edge_long_J.value(),
                    "Iz": self.input_panel.edge_long_Iz.value(),
                    "Iy": self.input_panel.edge_long_Iy.value(),
                    "Az": self.input_panel.edge_long_Az.value(),
                    "Ay": self.input_panel.edge_long_Ay.value(),
                },
                "longitudinal": {
                    "A": self.input_panel.long_A.value(),
                    "J": self.input_panel.long_J.value(),
                    "Iz": self.input_panel.long_Iz.value(),
                    "Iy": self.input_panel.long_Iy.value(),
                    "Az": self.input_panel.long_Az.value(),
                    "Ay": self.input_panel.long_Ay.value(),
                },
                "transverse": {
                    "A": self.input_panel.trans_A.value(),
                    "J": self.input_panel.trans_J.value(),
                    "Iy": self.input_panel.trans_Iy.value(),
                    "Iz": self.input_panel.trans_Iz.value(),
                    "Ay": self.input_panel.trans_Ay.value(),
                    "Az": self.input_panel.trans_Az.value(),
                    "unit_width": self.input_panel.trans_unit_width.isChecked(),
                },
                "end_transverse": {
                    "A": self.input_panel.end_trans_A.value(),
                    "J": self.input_panel.end_trans_J.value(),
                    "Iy": self.input_panel.end_trans_Iy.value(),
                    "Iz": self.input_panel.end_trans_Iz.value(),
                    "Ay": self.input_panel.end_trans_Ay.value(),
                    "Az": self.input_panel.end_trans_Az.value(),
                },
            },
            ##            'loads': {
            ##                'dead_load': {
            ##                    'magnitude': self.input_panel.dl_magnitude.value(),
            ##                    'direction': self.input_panel.dl_direction.currentText()
            ##                },
            ##                'live_load': {
            ##                    'magnitude': self.input_panel.ll_magnitude.value(),
            ##                    'direction': self.input_panel.ll_direction.currentText()
            ##                }
            ##            },
            ##            'analysis': {
            ##                'output_displacements': self.input_panel.output_displacements.currentText(),
            ##                'output_forces': self.input_panel.output_forces.currentText(),
            ##                'output_stresses': self.input_panel.output_stresses.currentText()
            ##            }
        }

    def generate_ospgrillage_code(self):
        if self.bridge_params["geometry"]["need_command_file"] == True:
            plot_or_save = f"""model.create_osp_model(pyfile=True)"""
        else:
            plot_or_save = f"""model.create_osp_model(pyfile=False)
og.plot_model(model, figsize=(8, 8), show=True)
"""

        ##Define material(Preset or custom)
        if self.bridge_params["materials"]["preset_yes"] == False:
            material_code = f"""material = og.create_material(
    material='{self.bridge_params['materials']['type'].lower()}',
    E={self.bridge_params['materials']['ec']}*GPa,
    v= {self.bridge_params['materials']['poisson']},
    rho={self.bridge_params['materials']['density']}*kN/m3 
)"""
        else:
            material_code = f"""material = og.create_material(material="{self.bridge_params['materials']['type'].lower()}",
code="{self.bridge_params['materials']['code']}", grade="{self.bridge_params['materials']['grade']}")"""
        """Generate ospgrillage Python code from collected parameters"""

        if self.bridge_params["geometry"]["bridge_type"] == "Curved":
            create_model = f"""model = og.create_grillage(
    bridge_name="{self.bridge_params['geometry']['name']}",
    long_dim={self.bridge_params['geometry']['length']} * m,
    width={self.bridge_params['geometry']['width']} * m,
    skew=[{self.bridge_params['geometry']['left_skew_angle']},{self.bridge_params['geometry']['right_skew_angle']}],
    num_long_grid={self.bridge_params['geometry']['long_beams']},  # Number of grid lines
    num_trans_grid={self.bridge_params['geometry']['trans_beams']},
    mesh_type="{self.bridge_params['geometry']['mesh_type']}",  # ('Ortho' or 'Oblique')
    mesh_radius={self.bridge_params['geometry']['radius']},
)"""
        if self.bridge_params["geometry"]["bridge_type"] == "Straight":
            # Build optional beam_spacing kwarg from user input
            _bs_text = self.input_panel.beam_spacing_input.text().strip()
            if _bs_text:
                _bs_line = f"\n    beam_spacing=[{_bs_text}],"
            else:
                _bs_line = (
                    f"\n    num_long_grid={self.bridge_params['geometry']['long_beams']},"
                    f"  # Number of grid lines"
                    f"\n    edge_beam_dist={self.input_panel.edge_beam_offset.value()} * m,"
                )
            create_model = f"""# Create grillage model
model = og.create_grillage(
    bridge_name="{self.bridge_params['geometry']['name']}",
    long_dim={self.bridge_params['geometry']['length']} * m,
    width={self.bridge_params['geometry']['width']} * m,
    skew=[{self.bridge_params['geometry']['left_skew_angle']},{self.bridge_params['geometry']['right_skew_angle']}],{_bs_line}
    num_trans_grid={self.bridge_params['geometry']['trans_beams']},
    mesh_type="{self.bridge_params['geometry']['mesh_type']}"  # ('Ortho' or 'Oblique')
)"""
        if self.bridge_params["geometry"]["bridge_type"] == "Multi-Span Straight":
            create_model = f"""model = og.create_grillage(
        bridge_name="{self.bridge_params['geometry']['name']}",
        long_dim={self.bridge_params['geometry']['length']} * m,
        width={self.bridge_params['geometry']['width']} * m,
        skew=[{self.bridge_params['geometry']['left_skew_angle']},{self.bridge_params['geometry']['right_skew_angle']}],
        num_long_grid={self.bridge_params['geometry']['long_beams']},  # Number of grid lines
        num_trans_grid={self.bridge_params['geometry']['trans_beams']},
        edge_beam_dist={self.input_panel.edge_beam_offset.value()} * m,
        mesh_type="{self.bridge_params['geometry']['mesh_type']}",  # ('Ortho' or 'Oblique')
        multi_span_dist_list={self.bridge_params['geometry']['multi_span_dist_list']},
        multi_span_num_points={self.bridge_params['geometry']['nl_multi']},
        continuous={self.bridge_params['geometry']['continuous']},
        non_cont_spacing_x={self.bridge_params['geometry']['stitch_slab_x_spacing']},
    )"""
        # Unit definitions
        units_code = """# Unit definitions
kilo = 1e3
milli = 1e-3
N = 1
m = 1
mm = milli * m
m2 = m ** 2
m3 = m ** 3
m4 = m ** 4
kN = kilo * N
MPa = N / ((mm) ** 2)
GPa = kilo * MPa
"""

        # Material definition
        material_code = f"""
# Material definition
{material_code}
"""

        # Section definitions
        sections_code = f"""
# Section definitions
edge_longitudinal_section = og.create_section(
    A={self.bridge_params['sections']['edge_longitudinal']['A']} * m2,
    J={self.bridge_params['sections']['edge_longitudinal']['J']} * m3,
    Iz={self.bridge_params['sections']['edge_longitudinal']['Iz']} * m4,
    Iy={self.bridge_params['sections']['edge_longitudinal']['Iy']} * m4,
    Az={self.bridge_params['sections']['edge_longitudinal']['Az']} * m2,
    Ay={self.bridge_params['sections']['edge_longitudinal']['Ay']} * m2
)

longitudinal_section = og.create_section(
    A={self.bridge_params['sections']['longitudinal']['A']} * m2,
    J={self.bridge_params['sections']['longitudinal']['J']} * m3,
    Iz={self.bridge_params['sections']['longitudinal']['Iz']} * m4,
    Iy={self.bridge_params['sections']['longitudinal']['Iy']} * m4,
    Az={self.bridge_params['sections']['longitudinal']['Az']} * m2,
    Ay={self.bridge_params['sections']['longitudinal']['Ay']} * m2
)

transverse_section = og.create_section(
    A={self.bridge_params['sections']['transverse']['A']} * m2,
    J={self.bridge_params['sections']['transverse']['J']} * m3,
    Iy={self.bridge_params['sections']['transverse']['Iy']} * m4,
    Iz={self.bridge_params['sections']['transverse']['Iz']} * m4,
    Ay={self.bridge_params['sections']['transverse']['Ay']} * m2,
    Az={self.bridge_params['sections']['transverse']['Az']} * m2,
    unit_width={str(self.bridge_params['sections']['transverse']['unit_width'])}
)


end_transverse_section = og.create_section(
    A={self.bridge_params['sections']['end_transverse']['A']} * m2,
    J={self.bridge_params['sections']['end_transverse']['J']} * m3,
    Iy={self.bridge_params['sections']['end_transverse']['Iy']} * m4,
    Iz={self.bridge_params['sections']['end_transverse']['Iz']} * m4,
    Ay={self.bridge_params['sections']['end_transverse']['Ay']} * m2,
    Az={self.bridge_params['sections']['end_transverse']['Az']} * m2
)

longitudinal_beam = og.create_member(section=longitudinal_section, material=material)

edge_longitudinal_beam = og.create_member(
    section=edge_longitudinal_section, material=material
)
transverse_slab = og.create_member(section=transverse_section, material=material)

end_transverse_slab = og.create_member(
    section=end_transverse_section, material=material
)


"""

        # Create grillage model
        model_code = f"""{create_model}
"""

        # Member assignments
        members_code = f"""
# Member assignments
model.set_member(longitudinal_beam, member="interior_main_beam")
model.set_member(longitudinal_beam, member="exterior_main_beam_1")
model.set_member(longitudinal_beam, member="exterior_main_beam_2")
model.set_member(edge_longitudinal_beam, member="edge_beam")
model.set_member(transverse_slab, member="transverse_slab")
model.set_member(end_transverse_slab, member="start_edge")
model.set_member(end_transverse_slab, member="end_edge")
"""

        visualization_code = f"""{plot_or_save}
"""
        ##        # Load cases
        ##        loads_code = f"""
        ### Load cases
        ##dead_load_case = og.load.create_load_case(name='DeadLoad')
        ##live_load_case = og.load.create_load_case(name='LiveLoad')
        ##
        ### Create load vertices (example for uniform load)
        ##load_area = og.load.create_area(
        ##    x1=0, z1=0,  # Start point
        ##    x2={self.bridge_params['geometry']['length']} * m,
        ##    z2={self.bridge_params['geometry']['width']} * m,  # End point
        ##    p={self.bridge_params['loads']['dead_load']['magnitude']} * kN/m2
        ##)
        ##
        ### Add loads to load cases
        ##dead_load_case.add_load(
        ##    og.load.create_load(
        ##        name='DeadLoad',
        ##        load_type='Area',
        ##        points=[load_area],
        ##        direction='{self.bridge_params['loads']['dead_load']['direction'][0:2]}'  # Just the direction part
        ##    )
        ##)
        ##
        ##live_load_case.add_load(
        ##    og.load.create_load(
        ##        name='LiveLoad',
        ##        load_type='Area',
        ##        points=[load_area],
        ##        magnitude={self.bridge_params['loads']['live_load']['magnitude']} * kN/m2,
        ##        direction='{self.bridge_params['loads']['live_load']['direction'][0:2]}'
        ##    )
        ##)
        ##
        ### Add load cases to model
        ##model.add_load_case(dead_load_case)
        ##model.add_load_case(live_load_case)
        ##"""
        ##
        ##        # Analysis and results
        ##        output_lines = []
        ##
        ##        if self.bridge_params['analysis']['output_displacements'] == 'Yes':
        ##            output_lines.append("displacements = results.get_displacements()")
        ##        if self.bridge_params['analysis']['output_forces'] == 'Yes':
        ##            output_lines.append("forces = results.get_forces()")
        ##        if self.bridge_params['analysis']['output_stresses'] == 'Yes':
        ##            output_lines.append("stresses = results.get_stresses()")
        ##
        ##        summary_lines = [
        ##            'print()',
        ##            'print("- Number of nodes: {}".format(len(results.node)))',
        ##            'print("- Number of elements: {}".format(len(results.element)))'
        ##        ]
        ##
        ##        if self.bridge_params['analysis']['output_displacements'] == 'Yes':
        ##            summary_lines.append('print("- Maximum displacement: {:.6f} m".format(displacements.max().values))')
        ##        if self.bridge_params['analysis']['output_forces'] == 'Yes':
        ##            summary_lines.append('print("- Maximum bending moment: {:.2f} kN·m".format(forces.sel(component=\'Mz\').max().values))')
        ##        if self.bridge_params['analysis']['output_stresses'] == 'Yes':
        ##            summary_lines.append('print("- Maximum stress: {:.2f} MPa".format(stresses.max().values))')
        ##
        ##        analysis_code = f"""
        ### Analysis and results
        ##model.analyze()
        ##
        ### Get results
        ##results = model.get_results()
        ##print("Analysis completed successfully!")
        ##
        ### Initialize variables for results
        ##displacements = None
        ##forces = None
        ##stresses = None
        ##
        ### Store requested results
        ##{chr(10).join(output_lines)}
        ##
        ### Print summary of results
        ##{chr(10).join(summary_lines)}
        ##"""

        # Combine all code sections
        self.generated_code = f"""# Bridge Geometry Script
# Generated by ospgui

import ospgrillage as og
from math import *

{units_code}
{material_code}
{sections_code}
{model_code}
{members_code}
{visualization_code}
"""

    ##{loads_code}
    ##{analysis_code}

    def save_code(self):
        """Save the generated code to a file with proper error handling"""
        if not hasattr(self, "generated_code") or not self.generated_code:
            QMessageBox.warning(
                self, "Warning", "No code to save. Please generate code first."
            )
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Python Script",
            "",  # Start in current directory
            "Python Files (*.py);;All Files (*)",
            options=options,
        )

        if not file_name:  # User cancelled the dialog
            return

        try:
            # Ensure .py extension
            if not file_name.lower().endswith(".py"):
                file_name += ".py"

            # Create parent directories if needed
            os.makedirs(os.path.dirname(file_name), exist_ok=True)

            # Write with proper encoding and line endings
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(self.generated_code)

            # Show success message
            self.statusbar.showMessage(
                f"Script successfully saved to {os.path.abspath(file_name)}", 5000
            )

        except PermissionError:
            QMessageBox.critical(
                self, "Error", f"Permission denied. Could not save to:\n{file_name}"
            )
        except OSError as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Unexpected error saving file:\n{str(e)}"
            )

    # ------------------------------------------------------------------
    # Mode switching
    # ------------------------------------------------------------------
    def _switch_to_wizard(self):
        """Switch to wizard mode (left=inputs, right=code+3D)."""
        self._mode = "wizard"
        self.left_stack.setCurrentIndex(0)
        self.right_stack.setCurrentIndex(0)
        self.statusbar.showMessage("Wizard mode", 3000)

    def _switch_to_results(self):
        """Switch to results mode (left=controls, right=result tabs)."""
        self._mode = "results"
        self.left_stack.setCurrentIndex(1)
        self.right_stack.setCurrentIndex(1)
        self.statusbar.showMessage("Results viewer mode", 3000)

    # ------------------------------------------------------------------
    # Results file loading
    # ------------------------------------------------------------------
    def _open_results_file(self):
        """Load a NetCDF results file and switch to results mode."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open Results File",
            "",
            "NetCDF Files (*.nc);;All Files (*)",
        )
        if not file_name:
            return

        try:
            import xarray as xr
            import ospgrillage as og

            ds = xr.open_dataset(file_name)
            proxy = og.model_proxy_from_results(ds)
        except KeyError as e:
            QMessageBox.warning(
                self,
                "Incompatible File",
                f"This file is missing geometry data:\n{e}\n\n"
                "Re-save results with ospgrillage >= 0.5.4 to include "
                "node coordinates and member connectivity.",
            )
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load results file:\n{e}")
            return

        self._model_proxy = proxy
        self._results = ds

        # Populate controls
        loadcase_names = []
        if "Loadcase" in ds.coords:
            loadcase_names = [str(lc) for lc in ds.coords["Loadcase"].values]
        self.results_panel.populate_loadcases(loadcase_names)
        self.results_panel.update_available_members(proxy)

        n_vars = len(ds.data_vars)
        n_lc = len(loadcase_names)
        self.results_panel.set_file_info(
            os.path.basename(file_name),
            f"{n_vars} variables, {n_lc} load cases",
        )

        # Shell contour visibility
        is_shell = proxy.model_type == "shell_beam"
        self.results_panel.set_shell_contour_visible(is_shell)

        # Enable/disable the Shell Contour tab
        for i in range(self.results_tabs.count()):
            if self.results_tabs.tabText(i) == "Shell Contour":
                self.results_tabs.setTabEnabled(i, is_shell)
                break

        # Mark all result tabs stale and switch mode
        self._stale_tabs = {"BMD", "SFD", "TMD", "Deflection"}
        if is_shell:
            self._stale_tabs.add("Shell Contour")
        self._switch_to_results()

        # Grey out contour controls unless Shell Contour tab is active
        current_label = self.results_tabs.tabText(self.results_tabs.currentIndex())
        self.results_panel.set_shell_contour_enabled(current_label == "Shell Contour")

        self._refresh_current_result_tab()

    # ------------------------------------------------------------------
    # Lazy result tab rendering
    # ------------------------------------------------------------------
    def _on_results_control_changed(self, _=None):
        """Slot: loadcase or member filter changed — debounced refresh."""
        self._stale_tabs = {"BMD", "SFD", "TMD", "Deflection", "Shell Contour"}
        # Debounce: multiple checkbox changes in quick succession are
        # collapsed into a single render via a short single-shot timer.
        if not hasattr(self, "_debounce_timer"):
            from PyQt6.QtCore import QTimer

            self._debounce_timer = QTimer(self)
            self._debounce_timer.setSingleShot(True)
            self._debounce_timer.setInterval(200)  # ms
            self._debounce_timer.timeout.connect(self._refresh_current_result_tab)
        self._debounce_timer.start()

    def _on_result_tab_changed(self, index):
        """Slot: user switched result tab — render if stale."""
        label = self.results_tabs.tabText(index)
        self.results_panel.set_shell_contour_enabled(label == "Shell Contour")
        self._refresh_current_result_tab()

    def _refresh_current_result_tab(self):
        """Render only the currently visible result tab if it is stale."""
        if self._model_proxy is None or self._results is None:
            return
        if not _WEBENGINE_AVAILABLE:
            return

        current_idx = self.results_tabs.currentIndex()
        label = self.results_tabs.tabText(current_idx)
        if label not in self._stale_tabs:
            return

        import ospgrillage as og

        loadcase = self.results_panel.selected_loadcase()
        members = self.results_panel.selected_members()

        widget = self._result_tab_widgets.get(label)
        if widget is None:
            return

        try:
            if label == "Shell Contour":
                # Shell contour — reads directly from Dataset
                comp = self.results_panel.contour_component_combo.currentText()
                cs = self.results_panel.contour_colorscale_combo.currentText()
                fig = og.plot_srf(
                    self._results,
                    component=comp,
                    loadcase=loadcase,
                    backend="plotly",
                    show=False,
                    colorscale=cs,
                )
                overlay = self.results_panel.contour_overlay_combo.currentText()
                _OVERLAY_FN = {
                    "BMD": og.plot_bmd,
                    "SFD": og.plot_sfd,
                    "TMD": og.plot_tmd,
                    "Deflection": og.plot_def,
                }
                overlay_fn = _OVERLAY_FN.get(overlay)
                if overlay_fn is not None:
                    fig = overlay_fn(
                        self._model_proxy,
                        self._results,
                        members=members,
                        loadcase=loadcase,
                        backend="plotly",
                        show=False,
                        show_supports=False,
                        ax=fig,
                    )
            else:
                _PLOT_FN = {
                    "BMD": og.plot_bmd,
                    "SFD": og.plot_sfd,
                    "TMD": og.plot_tmd,
                    "Deflection": og.plot_def,
                }
                plot_fn = _PLOT_FN.get(label)
                if plot_fn is None:
                    return
                fig = plot_fn(
                    self._model_proxy,
                    self._results,
                    members=members,
                    loadcase=loadcase,
                    backend="plotly",
                    show=False,
                    show_supports=False,
                )

            fig.update_layout(
                legend=dict(x=1.02, y=1, xanchor="left", yanchor="top"),
                margin=dict(r=200),
            )
            # Write to temp file and load via URL to avoid
            # QWebEngineView's 2 MB setHtml() size limit.
            import tempfile
            from PyQt6.QtCore import QUrl

            tmp = tempfile.NamedTemporaryFile(
                suffix=".html",
                delete=False,
                mode="w",
                encoding="utf-8",
            )
            tmp.write(fig.to_html(include_plotlyjs=True))
            tmp.close()
            widget.setUrl(QUrl.fromLocalFile(tmp.name))
            widget.update()
            self._stale_tabs.discard(label)
            self.statusbar.showMessage(f"{label} updated", 3000)
        except Exception as e:
            widget.setHtml(
                f"<html><body style='padding:20px;font-family:sans-serif'>"
                f"<h3>Could not render {label}</h3><pre>{e}</pre>"
                f"</body></html>"
            )
            self._stale_tabs.discard(label)
            logger.warning("Result plot %s failed: %s", label, e)

    def run_analysis(self):
        """Handle Run Analysis button click"""
        # Ensure we're in wizard mode
        if self._mode != "wizard":
            self._switch_to_wizard()
        try:
            # First apply any changes
            self.apply_changes()

            # Update status bar
            self.statusbar.showMessage("Running analysis...")

            # Get the current code (either generated or manually edited)
            current_code = self.code_tab.toPlainText()

            # Create a dictionary to capture the output
            output = {}

            # Execute the code in a separate namespace
            namespace = {
                "og": None,
                "print": lambda x: output.setdefault("print", []).append(x),
            }

            # Try to import ospgrillage
            try:
                import ospgrillage as og

                namespace["og"] = og
            except ImportError:
                QMessageBox.critical(
                    self,
                    "Error",
                    "ospgrillage package not found. Please install it first.",
                )
                return

            # Execute the generated ospgrillage code shown in the code view panel.
            # current_code is always the output of the GUI's own code-generation
            # methods (generate_code / apply_changes), never raw user text input.
            #
            # Suppress matplotlib plt.show() during exec so the generated code
            # doesn't pop up a separate window.  The generated code still
            # contains og.plot_model(...) so it works when saved and run
            # standalone.
            import matplotlib.pyplot as _plt

            _orig_show = _plt.show
            _plt.show = lambda *a, **kw: None
            try:
                exec(current_code, namespace)  # noqa: S102
            finally:
                _plt.show = _orig_show

            try:
                # Render interactive 3D model
                if "model" in namespace and namespace["model"] is not None:
                    try:
                        fig = og.plot_model(
                            namespace["model"], backend="plotly", show=False
                        )
                        # Move legends outside the plot area
                        fig.update_layout(
                            legend=dict(
                                x=1.02,
                                y=1,
                                xanchor="left",
                                yanchor="top",
                            ),
                            margin=dict(r=200),
                        )
                        if _WEBENGINE_AVAILABLE:
                            # Write to temp file and load via URL to avoid
                            # QWebEngineView's 2 MB setHtml() size limit.
                            import tempfile
                            from PyQt6.QtCore import QUrl

                            tmp = tempfile.NamedTemporaryFile(
                                suffix=".html",
                                delete=False,
                                mode="w",
                                encoding="utf-8",
                            )
                            tmp.write(fig.to_html(include_plotlyjs=True))
                            tmp.close()
                            self.viz_tab.setUrl(QUrl.fromLocalFile(tmp.name))
                            self.right_panel.setCurrentWidget(self.viz_tab)
                        else:
                            # Open interactive 3D view in system browser
                            fig.show()
                    except Exception as viz_err:
                        logger.warning("Plotly visualization failed: %s", viz_err)

                self.statusbar.showMessage("Geometry created successfully", 5000)

            except Exception as e:
                error_msg = f"Error during analysis:\n{str(e)}"
                self.statusbar.showMessage("Analysis failed", 5000)
                QMessageBox.critical(self, "Analysis Error", error_msg)

        except Exception as e:
            self.statusbar.showMessage(f"Analysis failed: {str(e)}", 5000)
            QMessageBox.critical(self, "Error", f"Failed to create geometry: {str(e)}")


def main():
    """Launch the *ospgui* graphical interface.

    Entry point for the ``ospgui`` console script.  Checks that PyQt6 is
    available and exits with a helpful message if not, otherwise starts the
    Qt application and opens :class:`BridgeAnalysisGUI`.

    Raises
    ------
    SystemExit
        With code 1 if PyQt6 is not installed; with the Qt application's
        return code on normal exit.
    """
    if not _PYQT6_AVAILABLE:
        print(
            "ospgui requires PyQt6, which is not installed in this environment.\n"
            "Install it with:\n\n"
            "    pip install ospgrillage[gui]\n\n"
            "or:\n\n"
            "    pip install PyQt6",
            file=sys.stderr,
        )
        sys.exit(1)
    app = QApplication(sys.argv)
    window = BridgeAnalysisGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
