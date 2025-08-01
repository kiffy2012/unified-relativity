import sys
from PyQt5.QtWidgets import (QApplication, QOpenGLWidget, QMainWindow, QWidget,
                             QHBoxLayout, QVBoxLayout, QLabel, QSlider, QComboBox,
                             QPushButton, QGroupBox, QListWidget, QMenuBar, QMenu,
                             QAction, QStackedWidget, QLineEdit)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QVector3D
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from space_object import SpaceObject
from PyQt5.QtGui import QVector3D
import math
from PyQt5.QtCore import pyqtSignal

class GridVisualizer(QOpenGLWidget):
    object_selected = pyqtSignal(int)

    def __init__(self, space_time_grid):
        super().__init__()
        self.space_time_grid = space_time_grid
        self.rotation = QVector3D(30, 30, 0)
        self.lastPos = None
        self.grid_density = 10
        self.grid_opacity = 1.0
        self.zoom = -1.5
        self.offset = QVector3D(-0.5, -0.5, -0.5)
        self.dimension = 3
        self.objects = []
        # Default formulas for the four fundamental forces. "r" represents the
        # distance from an object.
        self.force_formulas = {
            "gravity": "1/(r*r)",
            "electromagnetic": "0",
            "strong": "0",
            "weak": "0",
        }

    def initializeGL(self):
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"OpenGL error in initializeGL: {error}")

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = w / h
        gluPerspective(45, aspect, 0.01, 1000.0)

    def paintGL(self):
        print("Starting paintGL")
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslatef(0, 0, self.zoom)
            glRotatef(self.rotation.x(), 1, 0, 0)
            glRotatef(self.rotation.y(), 0, 1, 0)
            glTranslatef(self.offset.x(), self.offset.y(), self.offset.z())

            # Draw grid
            glBegin(GL_LINES)
            # ... (rest of the grid drawing code)
            glEnd()

            # Draw objects
            print(f"Number of objects to draw: {len(self.objects)}")
            for i, obj in enumerate(self.objects):
                print(f"Drawing object {i}: position={obj.position}, radius={obj.radius}, color={obj.color}")
                self.draw_sphere(obj.position, obj.radius, obj.color)
            
            print("paintGL completed successfully")
        except Exception as e:
            print(f"Error in paintGL: {str(e)}")
            import traceback
            traceback.print_exc()


        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glTranslatef(0, 0, self.zoom)
            glRotatef(self.rotation.x(), 1, 0, 0)
            glRotatef(self.rotation.y(), 0, 1, 0)
            glTranslatef(self.offset.x(), self.offset.y(), self.offset.z())

            # Draw grid
            glBegin(GL_LINES)
            # ... (rest of the grid drawing code)
            glEnd()

        # Draw objects
            for obj in self.objects:
                self.draw_sphere(obj.position, obj.radius, obj.color)
        
            print("paintGL completed successfully")
        except Exception as e:
            print(f"Error in paintGL: {str(e)}")
            import traceback
            traceback.print_exc()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, self.zoom)
        glRotatef(self.rotation.x(), 1, 0, 0)
        glRotatef(self.rotation.y(), 0, 1, 0)
        glTranslatef(self.offset.x(), self.offset.y(), self.offset.z())

        glBegin(GL_LINES)
        step = 1.0 / (self.grid_density - 1)
        glColor4f(1, 1, 1, self.grid_opacity)

        mid_point = self.grid_density // 2

        if self.dimension == 1:  # 1D: single line
            p1 = self._apply_displacement(QVector3D(0, 0.5, 0.5))
            p2 = self._apply_displacement(QVector3D(1, 0.5, 0.5))
            glVertex3f(p1.x(), p1.y(), p1.z())
            glVertex3f(p2.x(), p2.y(), p2.z())
            for i in range(self.grid_density):
                p1 = self._apply_displacement(QVector3D(i * step, 0.49, 0.5))
                p2 = self._apply_displacement(QVector3D(i * step, 0.51, 0.5))
                glVertex3f(p1.x(), p1.y(), p1.z())
                glVertex3f(p2.x(), p2.y(), p2.z())

        elif self.dimension == 2:  # 2D: grid on XY plane
            for i in range(self.grid_density):
                # Vertical lines
                p1 = self._apply_displacement(QVector3D(i * step, 0, 0.5))
                p2 = self._apply_displacement(QVector3D(i * step, 1, 0.5))
                glVertex3f(p1.x(), p1.y(), p1.z())
                glVertex3f(p2.x(), p2.y(), p2.z())
                # Horizontal lines
                p3 = self._apply_displacement(QVector3D(0, i * step, 0.5))
                p4 = self._apply_displacement(QVector3D(1, i * step, 0.5))
                glVertex3f(p3.x(), p3.y(), p3.z())
                glVertex3f(p4.x(), p4.y(), p4.z())

        else:  # 3D: cube
            for i in range(self.grid_density):
                for j in range(self.grid_density):
                    # X-axis aligned lines
                    p1 = self._apply_displacement(QVector3D(0, i * step, j * step))
                    p2 = self._apply_displacement(QVector3D(1, i * step, j * step))
                    glVertex3f(p1.x(), p1.y(), p1.z())
                    glVertex3f(p2.x(), p2.y(), p2.z())
                    # Y-axis aligned lines
                    p3 = self._apply_displacement(QVector3D(i * step, 0, j * step))
                    p4 = self._apply_displacement(QVector3D(i * step, 1, j * step))
                    glVertex3f(p3.x(), p3.y(), p3.z())
                    glVertex3f(p4.x(), p4.y(), p4.z())
                    # Z-axis aligned lines
                    p5 = self._apply_displacement(QVector3D(i * step, j * step, 0))
                    p6 = self._apply_displacement(QVector3D(i * step, j * step, 1))
                    glVertex3f(p5.x(), p5.y(), p5.z())
                    glVertex3f(p6.x(), p6.y(), p6.z())

        glEnd()

        # Draw objects
        for obj in self.objects:
            self.draw_sphere(obj.position, obj.radius, obj.color)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            selected_index = self.select_object(event.x(), event.y())
            if selected_index is not None:
                self.object_selected.emit(selected_index)
            self.lastPos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.rotation.setX(self.rotation.x() + dy)
            self.rotation.setY(self.rotation.y() + dx)
            self.update()

        self.lastPos = event.pos()

    def wheelEvent(self, event):
        self.zoom += event.angleDelta().y() / 120
        self.update()

    def set_grid_opacity(self, opacity):
        self.grid_opacity = opacity
        self.update()

    def set_grid_density(self, density):
        self.grid_density = max(2, min(50, density))  # Clamp between 2 and 50
        self.update()

    def set_dimension(self, dim):
        self.dimension = dim
        if dim == 1:
            self.rotation = QVector3D(0, 0, 0)
            self.offset = QVector3D(-0.5, -0.5, -0.5)
        elif dim == 2:
            self.rotation = QVector3D(0, 0, 0)
            self.offset = QVector3D(-0.5, -0.5, -0.5)
        else:  # 3D
            self.rotation = QVector3D(30, 30, 0)
            self.offset = QVector3D(-0.5, -0.5, -0.5)
        self.update()

    def update_force_formulas(self, formulas):
        """Update force formulas from the settings panel."""
        self.force_formulas.update(formulas)
        self.update()

    def _evaluate_formula(self, formula, r):
        try:
            return eval(formula, {"r": r, "math": math, "np": np})
        except Exception:
            return 0

    def _apply_displacement(self, position):
        displacement = QVector3D(0, 0, 0)
        for obj in self.objects:
            r_vec = QVector3D(position.x() - obj.position.x(),
                              position.y() - obj.position.y(),
                              position.z() - obj.position.z())
            r = math.sqrt(r_vec.x() ** 2 + r_vec.y() ** 2 + r_vec.z() ** 2)
            if r == 0:
                continue
            r_unit = QVector3D(r_vec.x() / r, r_vec.y() / r, r_vec.z() / r)
            for formula in self.force_formulas.values():
                value = self._evaluate_formula(formula, r)
                if value != 0:
                    displacement -= r_unit * value
        return QVector3D(position.x() + displacement.x(),
                         position.y() + displacement.y(),
                         position.z() + displacement.z())

    def draw_sphere(self, position, radius, color):
        glPushMatrix()
        glTranslatef(position.x(), position.y(), position.z())
        glColor4f(*color)
        
        slices = 16
        stacks = 16
        
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            z0 = math.sin(lat0)
            zr0 = math.cos(lat0)
            
            lat1 = math.pi * (-0.5 + float(i+1) / stacks)
            z1 = math.sin(lat1)
            zr1 = math.cos(lat1)
            
            glBegin(GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j) / slices
                x = math.cos(lng)
                y = math.sin(lng)
                
                glNormal3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr0 * radius, y * zr0 * radius, z0 * radius)
                glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(x * zr1 * radius, y * zr1 * radius, z1 * radius)
            glEnd()
        
        glPopMatrix()

    def add_object(self, position, radius, color):
        print(f"GridVisualizer: Adding object with position={position}, radius={radius}, color={color}")
        try:
            new_object = SpaceObject(position, radius, color)
            print("SpaceObject created successfully")
            self.objects.append(new_object)
            print(f"Object appended to self.objects. Total objects: {len(self.objects)}")
            self.update()
            print("GridVisualizer: update() called")
        except Exception as e:
            print(f"Error in add_object: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def select_object(self, x, y):
        self.makeCurrent()
        viewport = glGetIntegerv(GL_VIEWPORT)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        
        winX = float(x)
        winY = float(viewport[3] - y)
        
        for i, obj in enumerate(self.objects):
            objX, objY, objZ = gluProject(obj.position.x(), obj.position.y(), obj.position.z(), modelview, projection, viewport)
            distance = math.sqrt((winX - objX)**2 + (winY - objY)**2)
            if distance < 10:  # 10 pixels tolerance
                return i
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            selected_index = self.select_object(event.x(), event.y())
            if selected_index is not None:
                self.object_selected.emit(selected_index)
            self.lastPos = event.pos()
        super().mousePressEvent(event)
    def remove_object(self, index):
        if 0 <= index < len(self.objects):
            del self.objects[index]
            self.update()


def remove_object(self, index):
    if 0 <= index < len(self.objects):
        del self.objects[index]
        self.update()

class SettingsPanel(QWidget):
    def __init__(self, visualizer):
        super().__init__()
        self.visualizer = visualizer
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Dimension control
        dimension_group = QGroupBox("Dimension")
        dimension_layout = QHBoxLayout()
        self.dim_1d_button = QPushButton("1D")
        self.dim_2d_button = QPushButton("2D")
        self.dim_3d_button = QPushButton("3D")
        self.dim_1d_button.clicked.connect(lambda: self.set_dimension(1))
        self.dim_2d_button.clicked.connect(lambda: self.set_dimension(2))
        self.dim_3d_button.clicked.connect(lambda: self.set_dimension(3))
        dimension_layout.addWidget(self.dim_1d_button)
        dimension_layout.addWidget(self.dim_2d_button)
        dimension_layout.addWidget(self.dim_3d_button)
        dimension_group.setLayout(dimension_layout)
        layout.addWidget(dimension_group)

        # Grid density control
        density_group = QGroupBox("Grid Density")
        density_layout = QHBoxLayout()
        self.decrease_density_button = QPushButton("Decrease Density")
        self.increase_density_button = QPushButton("Increase Density")
        self.decrease_density_button.clicked.connect(self.decrease_density)
        self.increase_density_button.clicked.connect(self.increase_density)
        density_layout.addWidget(self.decrease_density_button)
        density_layout.addWidget(self.increase_density_button)
        density_group.setLayout(density_layout)
        layout.addWidget(density_group)

        # Grid opacity control
        opacity_group = QGroupBox("Grid Opacity")
        opacity_layout = QVBoxLayout()
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)  # Start with full opacity
        self.opacity_slider.valueChanged.connect(self.update_grid_opacity)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_group.setLayout(opacity_layout)
        layout.addWidget(opacity_group)

        # Force formulas control
        force_group = QGroupBox("Force Formulas")
        force_layout = QVBoxLayout()
        self.force_inputs = {}
        defaults = [
            ("Gravity", "1/(r*r)"),
            ("Electromagnetic", "0"),
            ("Strong", "0"),
            ("Weak", "0"),
        ]
        for name, default in defaults:
            hlayout = QHBoxLayout()
            hlayout.addWidget(QLabel(f"{name}:"))
            line = QLineEdit(default)
            hlayout.addWidget(line)
            force_layout.addLayout(hlayout)
            self.force_inputs[name.lower()] = line
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_force_formulas)
        force_layout.addWidget(apply_btn)
        force_group.setLayout(force_layout)
        layout.addWidget(force_group)

        self.setLayout(layout)

    def set_dimension(self, dim):
        self.visualizer.set_dimension(dim)

    def increase_density(self):
        current_density = self.visualizer.grid_density
        self.visualizer.set_grid_density(current_density + 1)

    def decrease_density(self):
        current_density = self.visualizer.grid_density
        self.visualizer.set_grid_density(current_density - 1)

    def update_grid_opacity(self, value):
        opacity = value / 100.0
        self.visualizer.set_grid_opacity(opacity)

    def apply_force_formulas(self):
        formulas = {name: edit.text() for name, edit in self.force_inputs.items()}
        self.visualizer.update_force_formulas(formulas)

class MainWindow(QMainWindow):
    def __init__(self, space_time_grid):
        super().__init__()
        self.space_time_grid = space_time_grid
        self.initUI()
        
        # Add a timer to trigger updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.visualizer.update)
        self.timer.start(16)  # Update roughly 60 times per second

    def initUI(self):
        self.setWindowTitle('Unified Theory Simulation')
        self.setGeometry(100, 100, 1400, 800)

        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        file_menu.addAction('New Simulation')
        file_menu.addAction('Open Simulation')
        file_menu.addAction('Save Simulation')
        file_menu.addAction('Export Results')
        file_menu.addSeparator()
        file_menu.addAction('Exit')

        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        edit_menu.addAction('Undo')
        edit_menu.addAction('Redo')
        edit_menu.addSeparator()
        edit_menu.addAction('Preferences')

        # View menu
        view_menu = menubar.addMenu('View')
        view_menu.addAction('Reset View')
        view_menu.addAction('Toggle 3D/4D View')
        view_menu.addAction('Show/Hide Grid')

        # Simulation menu
        sim_menu = menubar.addMenu('Simulation')
        sim_menu.addAction('Start')
        sim_menu.addAction('Pause')
        sim_menu.addAction('Stop')
        sim_menu.addAction('Step Forward')
        sim_menu.addSeparator()
        sim_menu.addAction('Configure Parameters')

        # Analysis menu
        analysis_menu = menubar.addMenu('Analysis')
        analysis_menu.addAction('Generate Report')
        analysis_menu.addAction('Plot Results')
        analysis_menu.addAction('Export Data')

        # Help menu
        help_menu = menubar.addMenu('Help')
        help_menu.addAction('Documentation')
        help_menu.addAction('About')

        # Central widget
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left panel (visualization)
        self.visualizer = GridVisualizer(self.space_time_grid)
        main_layout.addWidget(self.visualizer, 3)

        # Right panel (controls and object adding)
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        # Scale selection
        scale_layout = QHBoxLayout()
        scale_label = QLabel("Scale:")
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["Quantum", "Subatomic", "Atomic", "Molecular", "Macroscopic", "Astronomical", "Cosmological"])
        self.scale_combo.currentTextChanged.connect(self.on_scale_changed)
        scale_layout.addWidget(scale_label)
        scale_layout.addWidget(self.scale_combo)
        right_layout.addLayout(scale_layout)

        # Settings panel
        self.settings_panel = SettingsPanel(self.visualizer)
        right_layout.addWidget(self.settings_panel)

        # Object adding
        self.object_stack = QStackedWidget()
        self.setup_object_lists()
        right_layout.addWidget(QLabel("Add Objects:"))
        right_layout.addWidget(self.object_stack)

        add_object_button = QPushButton("Add Selected Object")
        add_object_button.clicked.connect(self.add_selected_object)
        right_layout.addWidget(add_object_button)

        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel, 1)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def setup_object_lists(self):
        scales = ["Quantum", "Subatomic", "Atomic", "Molecular", "Macroscopic", "Astronomical", "Cosmological"]
        for scale in scales:
            list_widget = QListWidget()
            if scale == "Quantum":
                list_widget.addItems(["Quark", "Electron", "Neutrino", "Photon"])
            elif scale == "Subatomic":
                list_widget.addItems(["Proton", "Neutron", "Atom Nucleus"])
            elif scale == "Atomic":
                list_widget.addItems(["Hydrogen", "Helium", "Carbon", "Iron"])
            elif scale == "Molecular":
                list_widget.addItems(["Water", "Glucose", "DNA", "Protein"])
            elif scale == "Macroscopic":
                list_widget.addItems(["Rock", "Tree", "Building", "Mountain"])
            elif scale == "Astronomical":
                list_widget.addItems(["Planet", "Star", "Nebula", "Black Hole"])
            elif scale == "Cosmological":
                list_widget.addItems(["Galaxy", "Galaxy Cluster", "Cosmic Web", "Dark Matter Halo"])
            self.object_stack.addWidget(list_widget)

    def on_scale_changed(self, scale):
        self.object_stack.setCurrentIndex(self.scale_combo.currentIndex())

    def add_selected_object(self):
        print("Starting add_selected_object method")
        try:
            current_list = self.object_stack.currentWidget()
            if current_list.currentItem():
                selected_object = current_list.currentItem().text()
                scale = self.scale_combo.currentText()
                print(f"Selected object: {selected_object}, Scale: {scale}")
                
                position = QVector3D(0.5, 0.5, 0.5)  # Center of the grid
                radius = self.get_object_radius(scale)
                color = self.get_object_color(selected_object)
                print(f"Object properties: position={position}, radius={radius}, color={color}")
                
                print("Calling visualizer.add_object")
                self.visualizer.add_object(position, radius, color)
                print(f"Added {selected_object} at {scale} scale")
            print("Finished add_selected_object method")
        except Exception as e:
            print(f"Error in add_selected_object: {str(e)}")
            import traceback
            traceback.print_exc()

    def get_object_radius(self, scale):
    # Define radii for different scales (you can adjust these values)
        scale_radii = {
            "Quantum": 0.01,
            "Subatomic": 0.02,
            "Atomic": 0.03,
            "Molecular": 0.04,
            "Macroscopic": 0.05,
            "Astronomical": 0.06,
            "Cosmological": 0.07
    }
        return scale_radii.get(scale, 0.05)

    def get_object_color(self, object_type):
        # Define colors for different object types (you can adjust these values)
        object_colors = {
            "Quark": (1, 0, 0, 1),  # Red
            "Electron": (0, 1, 0, 1),  # Green
            "Proton": (0, 0, 1, 1),  # Blue
            "Neutron": (1, 1, 0, 1),  # Yellow
            "Atom": (0, 1, 1, 1),  # Cyan
            "Molecule": (1, 0, 1, 1),  # Magenta
            "Planet": (0.5, 0.5, 0.5, 1),  # Gray
            "Star": (1, 1, 0.5, 1),  # Light Yellow
            "Galaxy": (0.5, 0, 1, 1),  # Purple
        }
        return object_colors.get(object_type, (1, 1, 1, 1))  # Default to white
    
    def initUI(self):
        self.setWindowTitle('Unified Theory Simulation')
        self.setGeometry(100, 100, 1400, 800)

        # Create menu bar
        menubar = self.menuBar()
        
        # ... (rest of the menu creation code)

        # Central widget
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left panel (visualization)
        self.visualizer = GridVisualizer(self.space_time_grid)
        main_layout.addWidget(self.visualizer, 3)

        # Right panel (controls and object adding)
        right_panel = QWidget()
        right_layout = QVBoxLayout()

        # Scale selection
        scale_layout = QHBoxLayout()
        scale_label = QLabel("Scale:")
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["Quantum", "Subatomic", "Atomic", "Molecular", "Macroscopic", "Astronomical", "Cosmological"])
        self.scale_combo.currentTextChanged.connect(self.on_scale_changed)
        scale_layout.addWidget(scale_label)
        scale_layout.addWidget(self.scale_combo)
        right_layout.addLayout(scale_layout)

        # Settings panel
        self.settings_panel = SettingsPanel(self.visualizer)
        right_layout.addWidget(self.settings_panel)

        # Object adding
        self.object_stack = QStackedWidget()
        self.setup_object_lists()
        right_layout.addWidget(QLabel("Add Objects:"))
        right_layout.addWidget(self.object_stack)

        add_object_button = QPushButton("Add Selected Object")
        add_object_button.clicked.connect(self.add_selected_object)
        right_layout.addWidget(add_object_button)

        # Add selected objects list
        self.selected_objects_list = QListWidget()
        right_layout.addWidget(QLabel("Selected Objects:"))
        right_layout.addWidget(self.selected_objects_list)

        # Add remove button
        remove_object_button = QPushButton("Remove Selected Object")
        remove_object_button.clicked.connect(self.remove_selected_object)
        right_layout.addWidget(remove_object_button)

        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel, 1)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Connect the object_selected signal
        self.visualizer.object_selected.connect(self.on_object_selected)

    def on_object_selected(self, index):
        self.selected_objects_list.clear()
        obj = self.visualizer.objects[index]
        self.selected_objects_list.addItem(f"Object {index}: {obj.position}")

    def remove_selected_object(self):
        if self.selected_objects_list.count() > 0:
            index = int(self.selected_objects_list.item(0).text().split(':')[0].split(' ')[1])
            self.visualizer.remove_object(index)
            self.selected_objects_list.clear()


def visualize_grid(space_time_grid):
    app = QApplication(sys.argv)
    window = MainWindow(space_time_grid)
    window.show()
    sys.exit(app.exec_())
