import sys


from PyQt5.QtWidgets import (
    QApplication,
    QOpenGLWidget,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QSlider,
    QComboBox,
    QPushButton,
    QGroupBox,
    QListWidget,
    QMenuBar,
    QMenu,
    QAction,
    QStackedWidget,
    QLineEdit,
    QDialog,
    QFormLayout,
    QDoubleSpinBox,
    QCheckBox,
)

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QVector3D
from OpenGL.GL import *
from OpenGL.GLU import *
from space_object import SpaceObject
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
        # Translation applied to grid to simulate object velocity
        self.grid_translation = QVector3D(0.0, 0.0, 0.0)
        # Default formulas for the four fundamental forces. "r" represents the
        # distance from an object.
        self.force_formulas = {
            "gravity": "G * m / (r*r)",
            "electromagnetic": "0",
            "strong": "0",
            "weak": "0",
        }
        # Scaling factors for each force so the grid does not collapse
        self.force_scaling = {"gravity": 0.05}
        # Constants accessible from formulas
        self.constants = {"G": 1.0}

        self.show_forces = {
            "gravity": True,
            "electromagnetic": False,
            "strong": False,
            "weak": False,
        }
        self.force_colors = {
            "gravity": (1.0, 1.0, 1.0),
            "electromagnetic": (0.0, 0.0, 1.0),
            "strong": (1.0, 0.0, 0.0),
            "weak": (0.0, 1.0, 0.0),
        }

        # Number of segments used to draw each grid line so they can bend
        self.line_segments = 20


    def initializeGL(self):
        glClearColor(0, 0, 0, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        error = glGetError()
        if error != GL_NO_ERROR:
            # Log the error instead of printing to stdout
            sys.stderr.write(f"OpenGL error in initializeGL: {error}\n")

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = w / h
        gluPerspective(45, aspect, 0.01, 1000.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, self.zoom)
        glRotatef(self.rotation.x(), 1, 0, 0)
        glRotatef(self.rotation.y(), 0, 1, 0)
        glTranslatef(self.offset.x(), self.offset.y(), self.offset.z())

        if self.grid_density >= 2:

            for name, visible in self.show_forces.items():
                if visible:
                    self._draw_grid_for_force(name)

            step = 1.0 / (self.grid_density - 1)
            glColor4f(1, 1, 1, self.grid_opacity)
            ox = self.grid_translation.x()
            oy = self.grid_translation.y()
            oz = self.grid_translation.z()

            if self.dimension == 1:  # 1D: single line
                self._draw_displaced_line(
                    QVector3D(0, 0.5, 0.5), QVector3D(1, 0.5, 0.5)
                )
                for i in range(self.grid_density):
                    x = (i * step + ox) % 1.0
                    if i in (0, self.grid_density - 1):
                        continue
                    self._draw_displaced_line(
                        QVector3D(x, 0.49, 0.5),
                        QVector3D(x, 0.51, 0.5),
                    )

            elif self.dimension == 2:  # 2D: grid on XY plane
                self._draw_bounding_square()
                for i in range(self.grid_density):
                    x = (i * step + ox) % 1.0
                    if i not in (0, self.grid_density - 1):
                        self._draw_displaced_line(
                            QVector3D(x, 0, 0.5),
                            QVector3D(x, 1, 0.5),
                        )
                    y = (i * step + oy) % 1.0
                    if i not in (0, self.grid_density - 1):
                        self._draw_displaced_line(
                            QVector3D(0, y, 0.5),
                            QVector3D(1, y, 0.5),
                        )

            else:  # 3D: cube
                self._draw_bounding_box()
                for iy in range(self.grid_density):
                    y = (iy * step + oy) % 1.0
                    for iz in range(self.grid_density):
                        z = (iz * step + oz) % 1.0
                        if iy in (0, self.grid_density - 1) and iz in (
                            0,
                            self.grid_density - 1,
                        ):
                            continue
                        self._draw_displaced_line(
                            QVector3D(0, y, z), QVector3D(1, y, z)
                        )
                for ix in range(self.grid_density):
                    x = (ix * step + ox) % 1.0
                    for iz in range(self.grid_density):
                        z = (iz * step + oz) % 1.0
                        if ix in (0, self.grid_density - 1) and iz in (
                            0,
                            self.grid_density - 1,
                        ):
                            continue
                        self._draw_displaced_line(
                            QVector3D(x, 0, z), QVector3D(x, 1, z)
                        )
                for ix in range(self.grid_density):
                    x = (ix * step + ox) % 1.0
                    for iy in range(self.grid_density):
                        y = (iy * step + oy) % 1.0
                        if ix in (0, self.grid_density - 1) and iy in (
                            0,
                            self.grid_density - 1,
                        ):
                            continue
                        self._draw_displaced_line(
                            QVector3D(x, y, 0), QVector3D(x, y, 1)
                        )



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

        # Use the original zoom step for a snappier feel
        self.zoom += event.angleDelta().y() / 120

        self.zoom += event.angleDelta().y() / 60.0

        self.update()

    def set_grid_opacity(self, opacity):
        self.grid_opacity = opacity
        self.update()

    def set_grid_density(self, density):
        self.grid_density = max(0, min(50, density))  # Allow 0 to hide grid
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

    def _evaluate_formula(self, formula, r, m):
        """Safely evaluate a force formula."""
        try:
            return eval(
                formula,
                {
                    "r": r,
                    "m": m,
                    "math": math,
                    **self.constants,
                },
            )
        except Exception:
            return 0


    def _apply_force(self, position, force_name):
        displacement = QVector3D(0, 0, 0)
        formula = self.force_formulas.get(force_name, "0")
        scaling = self.force_scaling.get(force_name, 0.0)
        for obj in self.objects:
            r_vec = QVector3D(
                position.x() - obj.position.x(),
                position.y() - obj.position.y(),
                position.z() - obj.position.z(),
            )

            r = math.sqrt(r_vec.x() ** 2 + r_vec.y() ** 2 + r_vec.z() ** 2)
            if r == 0:
                continue
            r_unit = QVector3D(r_vec.x() / r, r_vec.y() / r, r_vec.z() / r)

            value = self._evaluate_formula(formula, r, obj.mass)
            if value != 0 and scaling:
                displacement -= r_unit * value * scaling
        return QVector3D(
            position.x() + displacement.x(),
            position.y() + displacement.y(),
            position.z() + displacement.z(),
        )

    def _draw_bounding_square(self):
        glBegin(GL_LINES)
        edges = [
            (0, 0, 0.5, 1, 0, 0.5),
            (1, 0, 0.5, 1, 1, 0.5),
            (1, 1, 0.5, 0, 1, 0.5),
            (0, 1, 0.5, 0, 0, 0.5),
        ]
        for e in edges:
            glVertex3f(e[0], e[1], e[2])
            glVertex3f(e[3], e[4], e[5])
        glEnd()

    def _draw_bounding_box(self):
        glBegin(GL_LINES)
        edges = [
            (0, 0, 0, 1, 0, 0),
            (1, 0, 0, 1, 1, 0),
            (1, 1, 0, 0, 1, 0),
            (0, 1, 0, 0, 0, 0),
            (0, 0, 1, 1, 0, 1),
            (1, 0, 1, 1, 1, 1),
            (1, 1, 1, 0, 1, 1),
            (0, 1, 1, 0, 0, 1),
            (0, 0, 0, 0, 0, 1),
            (1, 0, 0, 1, 0, 1),
            (1, 1, 0, 1, 1, 1),
            (0, 1, 0, 0, 1, 1),
        ]
        for e in edges:
            glVertex3f(e[0], e[1], e[2])
            glVertex3f(e[3], e[4], e[5])
        glEnd()

    def advance_simulation(self, dt):
        for obj in self.objects:
            self.grid_translation.setX(
                (self.grid_translation.x() - obj.velocity.x() * dt) % 1.0
            )
            self.grid_translation.setY(
                (self.grid_translation.y() - obj.velocity.y() * dt) % 1.0
            )
            self.grid_translation.setZ(
                (self.grid_translation.z() - obj.velocity.z() * dt) % 1.0
            )

    def _apply_displacement(self, position):
        displacement = QVector3D(0, 0, 0)
        for obj in self.objects:
            r_vec = QVector3D(
                position.x() - obj.position.x(),
                position.y() - obj.position.y(),
                position.z() - obj.position.z(),
            )


            r = math.sqrt(r_vec.x() ** 2 + r_vec.y() ** 2 + r_vec.z() ** 2)
            if r == 0:
                continue
            r_unit = QVector3D(r_vec.x() / r, r_vec.y() / r, r_vec.z() / r)

            for name, formula in self.force_formulas.items():
                scaling = self.force_scaling.get(name, 0.0)
                value = self._evaluate_formula(formula, r, obj.mass)
                if value != 0 and scaling:
                    displacement -= r_unit * value * scaling
        return QVector3D(
            position.x() + displacement.x(),
            position.y() + displacement.y(),
            position.z() + displacement.z(),
        )

    def _draw_displaced_line(self, start, end):
        glBegin(GL_LINE_STRIP)
        for k in range(self.line_segments + 1):
            t = k / self.line_segments
            pos = QVector3D(
                start.x() + (end.x() - start.x()) * t,
                start.y() + (end.y() - start.y()) * t,
                start.z() + (end.z() - start.z()) * t,
            )
            pos = self._apply_displacement(pos)
            glVertex3f(pos.x(), pos.y(), pos.z())
        glEnd()

    def _draw_force_line(self, start, end, force_name):
        glBegin(GL_LINE_STRIP)
        for k in range(self.line_segments + 1):
            t = k / self.line_segments
            pos = QVector3D(
                start.x() + (end.x() - start.x()) * t,
                start.y() + (end.y() - start.y()) * t,
                start.z() + (end.z() - start.z()) * t,
            )
            pos = self._apply_force(pos, force_name)
            glVertex3f(pos.x(), pos.y(), pos.z())
        glEnd()

    def _draw_grid_for_force(self, force_name):
        glColor4f(*self.force_colors[force_name], self.grid_opacity)
        step = 1.0 / (self.grid_density - 1)
        ox = self.grid_translation.x()
        oy = self.grid_translation.y()
        oz = self.grid_translation.z()
        if self.dimension == 1:
            self._draw_force_line(
                QVector3D(0, 0.5, 0.5), QVector3D(1, 0.5, 0.5), force_name
            )
            for i in range(self.grid_density):
                x = (i * step + ox) % 1.0
                if i in (0, self.grid_density - 1):
                    continue
                self._draw_force_line(
                    QVector3D(x, 0.49, 0.5),
                    QVector3D(x, 0.51, 0.5),
                    force_name,
                )
        elif self.dimension == 2:
            for i in range(self.grid_density):
                x = (i * step + ox) % 1.0
                if i not in (0, self.grid_density - 1):
                    self._draw_force_line(
                        QVector3D(x, 0, 0.5),
                        QVector3D(x, 1, 0.5),
                        force_name,
                    )
                y = (i * step + oy) % 1.0
                if i not in (0, self.grid_density - 1):
                    self._draw_force_line(
                        QVector3D(0, y, 0.5),
                        QVector3D(1, y, 0.5),
                        force_name,
                    )
        else:
            for iy in range(self.grid_density):
                y = (iy * step + oy) % 1.0
                for iz in range(self.grid_density):
                    z = (iz * step + oz) % 1.0
                    if iy in (0, self.grid_density - 1) and iz in (
                        0,
                        self.grid_density - 1,
                    ):
                        continue
                    self._draw_force_line(
                        QVector3D(0, y, z), QVector3D(1, y, z), force_name
                    )
            for ix in range(self.grid_density):
                x = (ix * step + ox) % 1.0
                for iz in range(self.grid_density):
                    z = (iz * step + oz) % 1.0
                    if ix in (0, self.grid_density - 1) and iz in (
                        0,
                        self.grid_density - 1,
                    ):
                        continue
                    self._draw_force_line(
                        QVector3D(x, 0, z), QVector3D(x, 1, z), force_name
                    )
            for ix in range(self.grid_density):
                x = (ix * step + ox) % 1.0
                for iy in range(self.grid_density):
                    y = (iy * step + oy) % 1.0
                    if ix in (0, self.grid_density - 1) and iy in (
                        0,
                        self.grid_density - 1,
                    ):
                        continue
                    self._draw_force_line(
                        QVector3D(x, y, 0), QVector3D(x, y, 1), force_name
                    )



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

    def add_object(self, position, radius, color, mass, velocity=None):
        print(
            f"GridVisualizer: Adding object with position={position}, radius={radius}, "
            f"color={color}, mass={mass}, velocity={velocity}"
        )
        try:
            if velocity is None:
                velocity = QVector3D(0.0, 0.0, 0.0)
            new_object = SpaceObject(position, radius, color, mass, velocity)
            print("SpaceObject created successfully")
            self.objects.append(new_object)
            self.update()
        except Exception as e:
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

    def remove_object(self, index):
        if 0 <= index < len(self.objects):
            del self.objects[index]
            self.update()


class ForceFormulasDialog(QDialog):
    def __init__(self, formulas, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Force Formulas")
        self.inputs = {}
        layout = QVBoxLayout()
        for name in ["gravity", "electromagnetic", "strong", "weak"]:
            hlayout = QHBoxLayout()
            hlayout.addWidget(QLabel(f"{name.capitalize()}:"))
            line = QLineEdit(formulas.get(name, ""))
            hlayout.addWidget(line)
            self.inputs[name] = line
            layout.addLayout(hlayout)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.accept)
        layout.addWidget(apply_btn)
        self.setLayout(layout)


class ObjectSettingsDialog(QDialog):
    def __init__(self, obj, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Object Settings")
        form = QFormLayout()
        self.mass_spin = QDoubleSpinBox()
        self.mass_spin.setRange(0, 1e20)
        self.mass_spin.setValue(obj.mass)
        form.addRow("Mass", self.mass_spin)
        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setRange(0.001, 1.0)
        self.radius_spin.setValue(obj.radius)
        form.addRow("Radius", self.radius_spin)
        # Velocity components
        self.vx_spin = QDoubleSpinBox()
        self.vx_spin.setRange(-1e6, 1e6)
        self.vx_spin.setValue(obj.velocity.x())
        form.addRow("Velocity X", self.vx_spin)
        self.vy_spin = QDoubleSpinBox()
        self.vy_spin.setRange(-1e6, 1e6)
        self.vy_spin.setValue(obj.velocity.y())
        form.addRow("Velocity Y", self.vy_spin)
        self.vz_spin = QDoubleSpinBox()
        self.vz_spin.setRange(-1e6, 1e6)
        self.vz_spin.setValue(obj.velocity.z())
        form.addRow("Velocity Z", self.vz_spin)
        apply = QPushButton("Apply")
        apply.clicked.connect(self.accept)
        form.addRow(apply)
        self.setLayout(form)

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

        # Force grid toggles
        force_group = QGroupBox("Force Grids")
        force_layout = QVBoxLayout()
        self.force_checks = {}
        for name in ["gravity", "electromagnetic", "strong", "weak"]:
            check = QCheckBox(name.capitalize())
            check.setChecked(self.visualizer.show_forces[name])
            check.stateChanged.connect(lambda state, n=name: self.toggle_force(n, state))
            self.force_checks[name] = check
            force_layout.addWidget(check)
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

    def toggle_force(self, name, state):
        self.visualizer.show_forces[name] = state == Qt.Checked
        self.visualizer.update()

class MainWindow(QMainWindow):
    def __init__(self, space_time_grid):
        super().__init__()
        self.space_time_grid = space_time_grid
        self.initUI()
        
        # Add a timer to trigger updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(16)  # Update roughly 60 times per second

    def update_simulation(self):
        self.visualizer.advance_simulation(0.016)
        self.visualizer.update()

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
        try:
            current_list = self.object_stack.currentWidget()
            if current_list.currentItem():
                selected_object = current_list.currentItem().text()
                scale = self.scale_combo.currentText()
                position = QVector3D(0.5, 0.5, 0.5)  # Center of the grid
                radius = self.get_object_radius(scale)
                color = self.get_object_color(selected_object)
                mass = self.get_object_mass(scale)
                velocity = QVector3D(0.0, 0.0, 0.0)

                print(
                    f"Object properties: position={position}, radius={radius}, "
                    f"color={color}, mass={mass}, velocity={velocity}"
                )
                self.visualizer.add_object(position, radius, color, mass, velocity)
                print(f"Added {selected_object} at {scale} scale")
            print("Finished add_selected_object method")


        except Exception as e:
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

    def get_object_mass(self, scale):
        scale_masses = {
            "Quantum": 1e-6,
            "Subatomic": 1e-4,
            "Atomic": 1e-3,
            "Molecular": 1e-2,
            "Macroscopic": 1.0,
            "Astronomical": 1e10,
            "Cosmological": 1e20,
        }
        return scale_masses.get(scale, 1.0)

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
        settings_menu = menubar.addMenu('Settings')
        formula_action = QAction('Force Formulas', self)
        formula_action.triggered.connect(self.open_force_formula_dialog)
        settings_menu.addAction(formula_action)

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

        edit_object_button = QPushButton("Edit Selected Object")
        edit_object_button.clicked.connect(self.edit_selected_object)
        right_layout.addWidget(edit_object_button)

        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel, 1)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Connect the object_selected signal
        self.visualizer.object_selected.connect(self.on_object_selected)

    def on_object_selected(self, index):
        self.selected_objects_list.clear()
        obj = self.visualizer.objects[index]
        self.selected_objects_list.addItem(
            f"Object {index}: pos={obj.position}, vel={obj.velocity}, mass={obj.mass}, radius={obj.radius}")

    def remove_selected_object(self):
        if self.selected_objects_list.count() > 0:
            index = int(self.selected_objects_list.item(0).text().split(':')[0].split(' ')[1])
            self.visualizer.remove_object(index)
            self.selected_objects_list.clear()

    def edit_selected_object(self):
        if self.selected_objects_list.count() > 0:
            index = int(self.selected_objects_list.item(0).text().split(':')[0].split(' ')[1])
            obj = self.visualizer.objects[index]
            dlg = ObjectSettingsDialog(obj, self)
            if dlg.exec_():
                obj.mass = dlg.mass_spin.value()
                obj.radius = dlg.radius_spin.value()
                obj.velocity = QVector3D(dlg.vx_spin.value(), dlg.vy_spin.value(), dlg.vz_spin.value())
                self.visualizer.update()
                self.on_object_selected(index)

    def open_force_formula_dialog(self):
        dlg = ForceFormulasDialog(self.visualizer.force_formulas, self)
        if dlg.exec_():
            formulas = {name: edit.text() for name, edit in dlg.inputs.items()}
            self.visualizer.update_force_formulas(formulas)


def visualize_grid(space_time_grid):
    app = QApplication(sys.argv)
    window = MainWindow(space_time_grid)
    window.show()
    sys.exit(app.exec_())
