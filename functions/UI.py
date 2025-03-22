# pip install pyqt5 matplotlib
import Config.config as config  # Correct way to import the config module with an alias

import sys
from PyQt5.QtWidgets import QApplication,QGridLayout,QLineEdit,QCheckBox, QMainWindow, QVBoxLayout, QWidget, QTabWidget ,QWidget, QScrollArea, QPushButton, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# ----- From Files
from functions.functions import *
from functions.Data_Fetching_Cleaning import *

class MatplotlibTab(QWidget):
    def __init__(self, title=None, fig=None, plots_data=None, grid_size=(1, 1)):
        super().__init__()

        layout = QGridLayout(self)
        self.setLayout(layout)

        if plots_data:
            # Handle multiple plots in the grid
            for i, entry in enumerate(plots_data):
                if isinstance(entry, tuple):  # For individual plot and position
                    plot, position = entry
                    row, col = position  # Destructure (row, col)
                    self.add_plot_to_grid(plot, row, col)
                elif isinstance(entry, dict):  # For subplots in grid
                    title = entry.get("title")
                    plots_in_grid = entry.get("plots_data")
                    grid_size = entry.get("grid_size", (1, 1))

                    # Handle the subplots as a grid
                    for plot, position in plots_in_grid:
                        row, col = position  # Destructure (row, col)
                        self.add_plot_to_grid(plot, row, col, grid_size)

        elif fig:
            # If a single figure is provided, render it at (1,1) or other position in the grid
            self.add_plot_to_grid(fig, 1, 1)

    def add_plot_to_grid(self, plot, row, col, grid_size=(1, 1)):
        """
        Helper function to add a plot (figure) to the grid.
        This can handle both individual figures and lists of figures.
        """
        if isinstance(plot, list):
            # If plot is a list, create a container for all figures in that grid cell
            container_layout = QVBoxLayout()  # Or QHBoxLayout, depending on how you want to arrange them
            container_widget = QWidget()

            # Create a scroll area for the list of figures
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)  # Makes sure the area resizes when the widget size changes
            scroll_area.setFixedHeight(600)  # Set a fixed height to ensure the scroll area works
            scroll_area.setWidget(container_widget)  # Add the container to the scroll area

            # Create a widget to hold the layout of canvases (the figures)
            canvas_container_widget = QWidget()
            canvas_container_widget.setLayout(container_layout)

            # Add all figures to the container layout
            for individual_plot in plot:
                canvas = FigureCanvas(individual_plot)  # Create a canvas for each figure
                canvas.setFixedSize(800, 600)  # Set the fixed size for each canvas (adjust this)
                container_layout.addWidget(canvas)  # Add each canvas to the container layout

            # Add the canvas container widget to the scroll area
            scroll_area.setWidget(canvas_container_widget)

            # Add the scroll area to the grid
            self.layout().addWidget(scroll_area, row - 1, col - 1)
        else:
            # If plot is a single figure, render it directly
            self.render_plot_in_grid(plot, row, col, grid_size)

    def render_plot_in_grid(self, plot, row, col, grid_size=(1, 1)):
        """
        Renders an individual plot in the specified grid position.
        """
        canvas = FigureCanvas(plot)  # Create a FigureCanvas for the plot (figure)
        #canvas.setFixedSize(800, 600)  # Set the fixed size for each canvas (adjust this)
        self.layout().addWidget(canvas, row - 1, col - 1)  # Add the canvas to the grid at the specified position
# Main window class
class MainWindow(QMainWindow):
    def __init__(self, plots,pdf_filepath,date_folder,df):
        super().__init__()

        self.setWindowTitle("Degiro Analysis")
        self.setGeometry(100, 100, 800, 600)

        # Create a QTabWidget for the tabs
        self.tabs = QTabWidget()

        # Create tabs dynamically by calling a method
        self.create_tabs(plots)
        # Create the ButtonTab and add it as a tab
        button_tab = ButtonTab(plots,pdf_filepath,date_folder,df)
        self.tabs.addTab(button_tab, "Exports")

        # Create the ConfigEditTab and add it as a tab
        #config_tab = ConfigEditTab()
        #self.tabs.addTab(config_tab, "Configuration")

        # Set the QTabWidget as the central widget
        self.setCentralWidget(self.tabs)

        # Adjust the tab size using stylesheets
        self.adjust_tabs_size()

        # Show the window
        self.show()
    def adjust_tabs_size(self):
        try:
            self.tabs.setStyleSheet("""
                QTabWidget::pane {
                border: 1px solid lightgray;
                top:-1px; 
                background: rgb(245, 245, 245);; 
                } 

                QTabBar::tab {
                background: rgb(230, 230, 230); 
                border: 1px solid lightgray; 
                padding: 15px;
                } 

                QTabBar::tab:selected { 
                background: rgb(245, 245, 245); 
                margin-bottom: -1px; 
                }
            """)
        except Exception as e:
            print(f"Error applying stylesheet: {e}")

    def create_tabs(self, plots):
        # List of all the figures and plots
        figs_data = [
            # Title
            {"title": "About", "fig": plots["ReadMe"], "grid_size": (1, 1)},
            # KPI
            {"title": "KPI", "fig": plots["KPI Plot"], "grid_size": (1, 1)},
            # pivot
            {"title": "Pivot Table", "fig": plots["Pivot Table"], "grid_size": (1, 1)},
            # Tab with 4 subplots (2x2 grid)
            {"title": "Overview", 
            "plots_data": [
                (plots["Total Pct by Date"], (1, 1)),  # Use plot from the 'plots' dictionary
                (plots["Total by Date"], (1, 2)),     # Similarly use 'Sine Wave'
                (plots["Portfolio Product Percentage"], (2, 1)), # Use 'Cosine Wave'
                (plots["Pie Portfolio by ISIN"], (2, 2))  # Use 'Exponential Curve'
            ], "grid_size": (2, 2)},
                        # Tab with 4 subplots (2x2 grid)
            {"title": "Appendixes", 
            "plots_data": [
                (plots["ISIN Percentage by Date"], (1, 1)),  # Use plot from the 'plots' dictionary
                (plots["ISIN by Date"], (1, 2)),     # Similarly use 'Sine Wave'
                (plots["Portfolio by ISIN by Date"], (2, 1)) # Use 'Cosine Wave'
            ], "grid_size": (2, 2)},
        ]

        # Dynamically create tabs from figs_data
        for tab_data in figs_data:
            if "plots_data" in tab_data:
                # Handle multiple plots in one tab
                tab = MatplotlibTab(plots_data=tab_data["plots_data"], grid_size=tab_data["grid_size"])
            else:
                # Handle a single plot
                tab = MatplotlibTab(fig=tab_data["fig"], grid_size=tab_data["grid_size"])
            self.tabs.addTab(tab, tab_data["title"])

            


class ButtonTab(QWidget):
    def __init__(self, plots, pdf_filepath, date_folder,df):
        super().__init__()

        # Save the passed parameters for later use
        self.plots = plots
        self.pdf_filepath = pdf_filepath
        self.date_folder = date_folder
        self.df=df
        # Create a label for feedback
        #self.label = QLabel("Click a button to perform an action.", self)

        # Create buttons and connect them to their respective functions
        self.button1 = QPushButton("Export full report as PDF", self)
        self.button2 = QPushButton("Export Each Plot as PNG", self)
        self.button3 = QPushButton("Export dataset as CSV", self)
        self.button4 = QPushButton("Export stock data as SQL DB & CSV", self)

        # Automatically add buttons to the instance, then apply size and style
        self.set_button_size_and_style()

        # Connect buttons to functions with the required parameters using lambda
        self.button1.clicked.connect(lambda: self.Export_PDF())
        self.button2.clicked.connect(lambda: self.Export_PNG())
        self.button3.clicked.connect(lambda: self.Export_CSV())
        self.button4.clicked.connect(lambda: self.Export_DB())

        # Set up the grid layout
        layout = QGridLayout()
        
        # Add widgets to the layout at specific positions
        #layout.addWidget(self.label, 0, 0, 1, 2)  # Label spans across two columns
        layout.addWidget(self.button1, 1, 0)
        layout.addWidget(self.button2, 1, 1)
        layout.addWidget(self.button3, 2, 0)
        layout.addWidget(self.button4, 2, 1)

        self.setLayout(layout)
    def set_button_size_and_style(self):
        # Iterate through each attribute in the instance that is a QPushButton
        for name, button in vars(self).items():
            if isinstance(button, QPushButton):
                button.setFixedSize(500, 150)
                button.setStyleSheet("font-size: 25px; padding: 15px;")

    def Export_PDF(self):
        create_output_folder(self.date_folder)
        plots_saveAs_OnePDF(self.pdf_filepath, self.plots)
        open_system(self.pdf_filepath)

    def Export_PNG(self):
        create_output_folder(self.date_folder)
        plots_saveAs_PNG(self.date_folder, self.plots)

    def Export_CSV(self):
        create_output_folder(self.date_folder)
        export_df_csv(self.date_folder,self.df)
    def Export_DB(self):
        create_output_folder(self.date_folder)
        store_tickers_data_sqlite3_DB(self.df, self.date_folder)
        export_sqlite_to_csv(f'{self.date_folder}/tickers_data.db', 'tickers_data', f'{self.date_folder}/dboutput.csv')
     



# New ConfigEditTab to edit the config file variables
class ConfigEditTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        
        self.config_variables = {}  # Dictionary to hold references to the input widgets

        # List all variables from the config module dynamically
        config_vars = {name: value for name, value in vars(config).items() if not name.startswith("__")}
        print(config_vars)
        # Create UI elements for each variable dynamically
        for var_name, var_value in config_vars.items():
            if isinstance(var_value, bool):  # For boolean variables, use a checkbox
                label = QLabel(f"{var_name}:")
                input_widget = QCheckBox()
                input_widget.setChecked(var_value)
            else:  # For other types (strings, ints, floats), use a QLineEdit
                label = QLabel(f"{var_name}:")
                input_widget = QLineEdit(str(var_value))

            layout.addWidget(label)
            layout.addWidget(input_widget)

            # Store the input widgets in the dictionary for later access
            self.config_variables[var_name] = input_widget

        # Save button to apply changes
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_changes(self):
        """
        Save the changes made to the config variables back to the config file.
        """
        # Loop through all the input widgets and update the config variables
        for var_name, input_widget in self.config_variables.items():
            if isinstance(input_widget, QCheckBox):  # For checkboxes (boolean values)
                globals()[var_name] = input_widget.isChecked()
            else:  # For text input (strings, integers, floats)
                globals()[var_name] = input_widget.text()
        print(var_name)
        # Save the updated values back to the config file
        #self.save_to_config_file()

    def save_to_config_file(self):
        """
        Save the updated configuration variables back to the config.py file.
        """
        config_path = "Config/config.py"  # Path to your config file

        # Read the current content of the config file
        with open(config_path, "r") as config_file:
            lines = config_file.readlines()

        # Prepare the updated content for the config file
        updated_lines = []
        for line in lines:
            for var_name, var_value in self.config_variables.items():
                if line.startswith(var_name):  # Find the line with the variable
                    if isinstance(var_value, bool):
                        updated_lines.append(f"{var_name} = {var_value}\n")  # Boolean value
                    else:
                        updated_lines.append(f"{var_name} = '{var_value}'\n")  # String, int, float
                    break
            else:
                updated_lines.append(line)  # Keep the original line if no match

        # Write the updated content back to the config file
        with open(config_path, "w") as config_file:
            config_file.writelines(updated_lines)
        print('saved')

def createUI(plots,pdf_filepath,date_folder,df):
    app = QApplication(sys.argv)
    window = MainWindow(plots,pdf_filepath,date_folder,df)
    # Show the window and run the event loop
    window.showMaximized()
    sys.exit(app.exec_())

#main()
