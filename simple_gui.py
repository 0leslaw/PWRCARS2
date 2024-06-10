import os
import sys
import config_loaded
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QApplication, QTabWidget)
from PySide6.QtGui import QPixmap, Qt
import game


class PlayerChoosingWidget(QWidget):
    """
    Widget for choosing a player and selecting car textures.

    Attributes:
        player_name (str): The name of the player.
        car_textures (list): List of paths to car texture images.
        current_texture_index (int): Index of the currently selected car texture.
        name_label (QLabel): Label for displaying the player's name.
        texture_label (QLabel): Label for displaying the selected car texture.
        previous_texture_button (QPushButton): Button for selecting the previous car texture.
        next_texture_button (QPushButton): Button for selecting the next car texture.
    """
    def __init__(self, player_name):
        """
        Initialize the PlayerChoosingWidget.

        Args:
            player_name (str): The name of the player.
        """
        super().__init__()

        self.player_name = player_name
        self.car_textures = [os.path.join(config_loaded.ConfigData.get_attr('car_textures_dir'), name)
                             for name in os.listdir(config_loaded.ConfigData.get_attr('car_textures_dir')) if name != 'cars.jpg']
        self.current_texture_index = 0

        layout = QVBoxLayout()

        self.name_label = QLabel(player_name)
        layout.addWidget(self.name_label)

        self.texture_label = QLabel()
        self.texture_label.setFixedSize(100, 100)  # Set fixed dimensions for the label
        self.texture_label.setScaledContents(True)  # Enable scaling of pixmap to fit label
        layout.addWidget(self.texture_label)

        self.update_texture_display()

        toggler_layout = QHBoxLayout()

        self.previous_texture_button = QPushButton("Previous")
        self.previous_texture_button.clicked.connect(self.show_previous_texture)
        toggler_layout.addWidget(self.previous_texture_button)

        self.next_texture_button = QPushButton("Next")
        self.next_texture_button.clicked.connect(self.show_next_texture)
        toggler_layout.addWidget(self.next_texture_button)

        layout.addLayout(toggler_layout)

        self.setLayout(layout)

    @property
    def current_texture(self):
        """
        str: The path to the currently selected car texture image.
        """
        return self.car_textures[self.current_texture_index]

    def update_texture_display(self):
        """
        Update the texture label to display the currently selected car texture.
        """
        pixmap = QPixmap(self.car_textures[self.current_texture_index])
        pixmap = pixmap.scaled(self.texture_label.size(), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)  # Scale pixmap to fit label
        self.texture_label.setPixmap(pixmap)

    def show_previous_texture(self):
        """Select the previous car texture."""
        self.current_texture_index = (self.current_texture_index - 1) % len(self.car_textures)
        self.update_texture_display()

    def show_next_texture(self):
        """Select the next car texture."""
        self.current_texture_index = (self.current_texture_index + 1) % len(self.car_textures)
        self.update_texture_display()


class PlayerSelectionWindow(QWidget):
    """
    Window for selecting players and game settings before starting the game.

    Attributes:
        lap_count (int): The number of laps for the game.
        lap_label (QLabel): Label for displaying the lap count.
        decrement_lap_button (QPushButton): Button for decrementing the lap count.
        increment_lap_button (QPushButton): Button for incrementing the lap count.
        start_button (QPushButton): Button for starting the game.
        tab_widget (QTabWidget): Widget for displaying tabs for single and two player modes.
        single_player_panel (QWidget): Panel for selecting settings in single player mode.
        two_player_panel (QWidget): Panel for selecting settings in two player mode.
    """
    def __init__(self):
        """Initialize the PlayerSelectionWindow."""
        super().__init__()

        self.setWindowTitle("PWR CARS 2")
        self.setGeometry(100, 100, 400, 300)

        self.lap_count = 1

        layout = QVBoxLayout()

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.single_player_panel = self.create_single_player_panel()
        self.two_player_panel = self.create_two_player_panel()

        self.tab_widget.addTab(self.single_player_panel, "Single Player")
        self.tab_widget.addTab(self.two_player_panel, "Two Player")

        # Adding the Lap Toggler
        lap_toggler_layout = QHBoxLayout()
        self.lap_label = QLabel(f"Laps: {self.lap_count}")
        lap_toggler_layout.addWidget(self.lap_label)

        self.decrement_lap_button = QPushButton("-")
        self.decrement_lap_button.clicked.connect(self.decrement_lap_count)
        lap_toggler_layout.addWidget(self.decrement_lap_button)

        self.increment_lap_button = QPushButton("+")
        self.increment_lap_button.clicked.connect(self.increment_lap_count)
        lap_toggler_layout.addWidget(self.increment_lap_button)

        layout.addLayout(lap_toggler_layout)

        # Adding the Start button
        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("background-color: red; color: white;")
        self.start_button.clicked.connect(self.start_game)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def create_single_player_panel(self):
        """
        Create the panel for selecting settings in single player mode.

        Returns:
            QWidget: The single player panel.
        """
        panel = QWidget()
        layout = QHBoxLayout()

        player_widget = PlayerChoosingWidget("player_1")
        layout.addWidget(player_widget)

        panel.setLayout(layout)
        return panel

    def create_two_player_panel(self):
        """
        Create the panel for selecting settings in two player mode.

        Returns:
            QWidget: The two player panel.
        """
        panel = QWidget()
        layout = QHBoxLayout()

        player1_widget = PlayerChoosingWidget("player_1")
        layout.addWidget(player1_widget)

        player2_widget = PlayerChoosingWidget("player_2")
        layout.addWidget(player2_widget)

        panel.setLayout(layout)

        return panel

    def increment_lap_count(self):
        """Increment the lap count."""
        self.lap_count += 1
        self.lap_label.setText(f"Laps: {self.lap_count}")

    def decrement_lap_count(self):
        """Decrement the lap count."""
        if self.lap_count > 1:
            self.lap_count -= 1
            self.lap_label.setText(f"Laps: {self.lap_count}")

    def start_game(self):
        """Start the game with selected settings."""
        settings_dict = {}

        current_index = self.tab_widget.currentIndex()
        current_tab_name = self.tab_widget.tabText(current_index)
        settings_dict['game_mode'] = current_tab_name
        settings_dict['laps'] = str(self.lap_count)

        # this is the panel
        current = self.tab_widget.currentWidget()
        layout = current.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                item = item.widget()
                settings_dict[item.player_name] = item.current_texture

        config_loaded.set_config_for_game(settings_dict)
        game.start_game()


def main():
    app = QApplication(sys.argv)
    window = PlayerSelectionWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
