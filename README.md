# Battleship Game

Welcome to the Battleship Game project, a graphical implementation of the classic board game using PyQt6. This application features a dynamic graphical user interface for interactive gameplay against either another player or an AI opponent.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Known Issues](#known-issues)
- [Future Plans](#future-plans)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Graphical User Interface**: Utilizes PyQt6 for rich, interactive graphics and user inputs.
- **Interactive Ship Placement**: Drag-and-drop interface to position ships on the board.
- **Cross-Platform**: Designed to work on Linux, with future support for Windows and macOS.
- **Modular Design**: Clear separation of game logic, graphics, and event handling.

## Installation

To set up the Battleship Game on your local machine, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/sigmareaver/BattleshipGame.git
   cd BattleshipGame
   ```

2. **Install the necessary packages:**

   Ensure that [Python 3](https://www.python.org/downloads/) and [PyQt6](https://pypi.org/project/PyQt6/) are installed. You can install PyQt6 using pip:

   ```bash
   pip install PyQt6
   ```

3. **Run the game:**

   Execute the main script to launch the game:

   ```bash
   python main.py
   ```

**OR**

4. **Just use the included shell/bat script for a venv:**

   Execute the script to setup dependencies and run the game with:

   ```bash
   chmod +x play.sh
   ./play.sh
   ```

## Usage

- **Start a Game**: Follow the on-screen instructions to begin setting up your board.
- **Play**: Take turns to attack your opponent's grid and try to sink all their ships.
- **Quit**: Close the game window to exit.

## Known Issues

- **Native Event Handler on Windows**: The `NativeEventHandler` for Windows has not been implemented yet due to lack of access to a Windows machine.

## Future Plans

- **Implement Windows Native Event Handler**: Extend the event handler support for Windows platforms.
- **Advanced AI Development**: Integrate a more challenging AI opponent, potentially using Monte Carlo Tree Search (MCTS) for decision-making.

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request for review. For major changes, please open an issue first to discuss your ideas.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any inquiries, feel free to reach out:

- **Author**: sigmareaver
- **Website**: [GitHub Profile](https://www.github.com/sigmareaver)

Thank you for visiting the Battleship Game project repository! Enjoy playing and feel free to contribute to its development.