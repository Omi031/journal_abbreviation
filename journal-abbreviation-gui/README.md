# Journal Abbreviation GUI

This project is a graphical user interface (GUI) application designed to format bibliographic references based on user input. It leverages existing functionality from a command-line application and provides a more user-friendly experience.

## Project Structure

- **src/**: Contains the source code for the application.
  - **main.py**: The entry point of the application that initializes the GUI and displays the main window.
  - **gui/**: Contains the GUI components.
    - **main_window.py**: Defines the main window class that constructs the main interface of the application.
    - **widgets/**: Contains custom widgets for user interaction.
      - **input_widget.py**: Defines the widget for user input of references.
      - **output_widget.py**: Defines the widget for displaying formatted references.
  - **core/**: Contains the core logic of the application.
    - **app.py**: Maintains the functionality of the existing command-line application and provides methods to be called from the GUI.
    - **formatter.py**: Contains logic related to formatting references.
  - **utils/**: Contains utility functions.
    - **file_loader.py**: Defines utility functions for loading CSV and YAML files.

- **data/**: Contains data files used by the application.
  - **jo_abb.csv**: CSV file containing journal abbreviations.
  - **jo_del.csv**: CSV file containing journal names to be deleted.
  - **mo_abb.csv**: CSV file containing other abbreviations.
  - **settings.yml**: YAML file containing application settings.

- **requirements.txt**: Lists the Python packages required for the project.

- **setup.py**: Contains information for setting up the project.

- **README.md**: Documentation for the project.

## Installation

To install the required packages, run:

```
pip install -r requirements.txt
```

## Usage

Run the application using:

```
python src/main.py
```

This will launch the GUI where you can input references and receive formatted outputs.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.