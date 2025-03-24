# pip install pyqt5 matplotlib
import Config.config as config  # Correct way to import the config module with an alias

import sys
from PyQt5.QtWidgets import QApplication,QGridLayout,QLineEdit,QCheckBox, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QScrollArea, QPushButton, QLabel,QDateEdit,QVBoxLayout 
from PyQt5.QtCore import QDate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import ScalarFormatter

# ----- From Files
from functions.functions import *
from functions.Data_Fetching_Cleaning import *

class CustomNavigationToolbar(NavigationToolbar):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)

        # 0. Pan/Zoom (Hand tool): Allows user to pan and zoom the plot interactively
        self.actions()[0].setVisible(True)  # Make the Pan/Zoom (Hand tool) visible
        self.actions()[0].setEnabled(True)  # Ensure Pan/Zoom (Hand tool) is enabled
        self.actions()[0].setText('Pan/Zoom (Hand tool)')

        # 1. Zoom to Rectangle (Zoom-in tool): Allows user to select a region on the plot to zoom in
        self.actions()[1].setVisible(True)  # Make the Zoom to Rectangle (Zoom-in tool) visible
        self.actions()[1].setEnabled(True)  # Ensure Zoom to Rectangle (Zoom-in tool) is enabled
        self.actions()[1].setText('Zoom to Rectangle (Zoom-in)')

        # 2. Save Figure: Saves the current plot to a file
        self.actions()[2].setVisible(True)  # Make the Save Figure button visible
        self.actions()[2].setEnabled(True)  # Ensure Save Figure is enabled
        self.actions()[2].setText('Save Figure')

        # 3. Home (Reset Zoom): Resets the plot zoom to the original state
        self.actions()[3].setVisible(True)  # Make the Home (Reset Zoom) button visible
        self.actions()[3].setEnabled(True)  # Ensure Home (Reset Zoom) is enabled
        self.actions()[3].setText('Home (Reset Zoom)')

        # 4. Back (Undo Zoom): Goes back to the previous zoom level
        self.actions()[4].setVisible(True)  # Make the Back (Undo Zoom) button visible
        self.actions()[4].setEnabled(True)  # Ensure Back (Undo Zoom) is enabled
        self.actions()[4].setText('Back (Undo Zoom)')

        # 5. Forward (Redo Zoom): Redoes the zoom (if a back action was performed)
        self.actions()[5].setVisible(True)  # Make the Forward (Redo Zoom) button visible
        self.actions()[5].setEnabled(True)  # Ensure Forward (Redo Zoom) is enabled
        self.actions()[5].setText('Forward (Redo Zoom)')

        # 6. Settings (Customize): Opens a settings or customization dialog for the canvas
        self.actions()[6].setVisible(False)  # Make the Settings (Customize) button visible
        self.actions()[6].setEnabled(False)  # Ensure Settings is enabled
        self.actions()[6].setText('Settings')

        # 7. 
        self.actions()[7].setVisible(False)  # Make the Toggle Grid button visible
        self.actions()[7].setEnabled(False)  # Ensure Toggle Grid is enabled
        self.actions()[7].setText('Toggle Grid')

class MatplotlibTab(QWidget):
    def __init__(self,title=None, fig=None, plots_data=None, grid_size=(1, 1),show_toolbar=None):
        super().__init__()

        # Initialize the layout here
        self.layout = QGridLayout()  # Use QGridLayout for grid-based widget placement
        self.setLayout(self.layout)  # Set the layout for the current widget

        if plots_data:
            # Handle multiple plots in the grid
            for i, entry in enumerate(plots_data):
                if isinstance(entry, tuple):  # For individual plot and position
                    plot, position,show_toolbar = entry
                    row, col = position  # Destructure (row, col)
                    show_toolbar = show_toolbar
                    self.add_plot_to_grid(plot, row, col,show_toolbar)
                elif isinstance(entry, dict):  # For subplots in grid
                    title = entry.get("title")
                    plots_in_grid = entry.get("plots_data")
                    grid_size = entry.get("grid_size", (1, 1))
                    show_toolbar = entry.get("show_toolbar")
                    # Handle the subplots as a grid
                    for plot, position,show_toolbar in plots_in_grid:
                        row, col = position  # Destructure (row, col)
                        self.add_plot_to_grid(plot, row, col,show_toolbar, grid_size)

        elif fig:
            # If a single figure is provided, render it at (1,1) or other position in the grid
            self.add_plot_to_grid(fig, 1, 1,show_toolbar)

    def add_plot_to_grid(self, plot, row, col,show_toolbar, grid_size=(1, 1)):
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

                individual_plot.tight_layout()

                # Trigger a redraw of the canvas to ensure layout changes are reflected
                canvas.updateGeometry()  # Efficiently trigger a redraw after layout changes

                # Draw the canvas to ensure layout changes are reflected properly
                canvas.draw()

            # Add the canvas container widget to the scroll area
            scroll_area.setWidget(canvas_container_widget)

            # Add the scroll area to the grid
            self.layout.addWidget(scroll_area, row - 1, col - 1)
        else:
            # If plot is a single figure, render it directly
            self.render_plot_in_grid(plot, row, col,show_toolbar)
                # Apply tight_layout after adding the plot to the canvas (to ensure proper spacing)


    def render_plot_in_grid(self, plot, row, col, show_toolbar=True):
        """
        Renders an individual plot in the specified grid position.
        This includes adding the NavigationToolbar for interactivity.
        """
        # Apply tight_layout after adding the plot to the canvas (to ensure proper spacing)
        plot.tight_layout()

        canvas = FigureCanvas(plot)

        # Access each axis in the figure and set the ScalarFormatter
        for ax in plot.get_axes():  # Iterate over all axes in the figure
            ax.yaxis.set_major_formatter(ScalarFormatter())
            # Disable scientific notation
            ax.ticklabel_format(style='plain', axis='y')
        # Optionally add the toolbar if the flag is set to True
        if show_toolbar:
            self.add_toolbar_to_grid(canvas, plot, row, col)

        # Layout to place the canvas in the grid
        self.layout.addWidget(canvas, row * 2, col * 2)  # Adjust position (canvas below the toolbar)

        # Apply tight_layout after adding the plot to the canvas (to ensure proper spacing)
        plot.tight_layout(pad=3.0)

        # Trigger a redraw of the canvas to ensure layout changes are reflected properly
        canvas.draw()

        # Ensure the layout is refreshed
        self.layout.update()

    def add_toolbar_to_grid(self, canvas, plot, row, col):
        """
        Helper function to add the NavigationToolbar above the plot.
        """
        toolbar = CustomNavigationToolbar(canvas, self)

        # Add toolbar to grid layout (position above the plot)
        self.layout.addWidget(toolbar, row * 2 - 1, col * 2)

# Main window class
class MainWindow(QMainWindow):
    def __init__(self, plots, pdf_filepath, date_folder, df):
        super().__init__()

        self.setWindowTitle("Degiro Analysis")
        self.setGeometry(100, 100, 800, 600)

        # Create a QTabWidget for the tabs
        self.tabs = QTabWidget()

        # Create the date range widget (start and stop date pickers)
        self.create_date_range_widget()

        # Create tabs dynamically
        self.create_tabs(plots)

        # Create the ButtonTab and add it as a tab
        button_tab = ButtonTab(plots, pdf_filepath, date_folder, df)
        self.tabs.addTab(button_tab, "Exports")

        # Set the QTabWidget as the central widget
        self.setCentralWidget(self.tabs)

        # Adjust the tab size using stylesheets
        self.adjust_tabs_size()

        # Show the window
        self.show()

    def create_date_range_widget(self):
        # Create the QWidget to contain the date range selection
        date_range_widget = QWidget()
        date_layout = QVBoxLayout()

        # Create start date picker
        self.start_date_picker = QDateEdit(self)
        self.start_date_picker.setDisplayFormat("yyyy-MM-dd")
        self.start_date_picker.setDate(QDate.currentDate())

        # Create stop date picker
        self.stop_date_picker = QDateEdit(self)
        self.stop_date_picker.setDisplayFormat("yyyy-MM-dd")
        self.stop_date_picker.setDate(QDate.currentDate())

        # Add date pickers to layout
        date_layout.addWidget(self.start_date_picker)
        date_layout.addWidget(self.stop_date_picker)

        # Optionally, add a button to confirm the date range selection
        self.confirm_button = QPushButton("Select Date Range", self)
        self.confirm_button.clicked.connect(self.on_date_range_selected)
        date_layout.addWidget(self.confirm_button)

        # Set layout for the date range widget
        date_range_widget.setLayout(date_layout)

    def on_date_range_selected(self):
        # Get the selected start and stop dates
        start_date = self.start_date_picker.date().toString("yyyy-MM-dd")
        stop_date = self.stop_date_picker.date().toString("yyyy-MM-dd")

        print(f"Selected date range: {start_date} to {stop_date}")

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
            {"title": "About", "fig": plots["ReadMe"], "grid_size": (1, 1), "show_toolbar": False},
            {"title": "KPI", "fig": plots["KPI Plot"], "grid_size": (1, 1), "show_toolbar": False},
            {"title": "Pivot Table", "fig": plots["Pivot Table"], "grid_size": (1, 1), "show_toolbar": False},
            # Tab with 4 subplots (2x2 grid)
            {"title": "Overview", 
            "plots_data": [
                (plots["Total Pct by Date"], (1, 1),True),  # Use plot from the 'plots' dictionary
                (plots["Total by Date"], (1, 2),True),     # Similarly use 'Sine Wave'
                (plots["Portfolio Product Percentage"], (2, 1),True), # Use 'Cosine Wave'
                (plots["Pie Portfolio by ISIN"], (2, 2),True)  # Use 'Exponential Curve'
            ], "grid_size": (2, 2)},
                        # Tab with 4 subplots (2x2 grid)
            {"title": "Appendixes", 
            "plots_data": [
                (plots["ISIN Percentage by Date"], (1, 1),True),  # Use plot from the 'plots' dictionary
                (plots["ISIN by Date"], (1, 2),True),     # Similarly use 'Sine Wave'
                (plots["Portfolio by ISIN by Date"], (2, 1),True) # Use 'Cosine Wave'
            ], "grid_size": (2, 2)},
        ]

        # Dynamically create tabs from figs_data
        for tab_data in figs_data:
            if "plots_data" in tab_data:
                # Handle a group of subplots
                tab = MatplotlibTab(
                    plots_data=tab_data["plots_data"],  # directly pass plots_data
                    grid_size=tab_data["grid_size"]
                )
            else:
                # Handle a single figure (wrap it in a list as figs_data)
                tab = MatplotlibTab(fig=tab_data["fig"], grid_size=tab_data["grid_size"], show_toolbar=tab_data["show_toolbar"])

            
            # Add the tab to the UI
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
