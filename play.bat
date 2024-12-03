:: Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
)

:: Activate the virtual environment
call venv\Scripts\activate

:: Install required packages
pip install -r requirements.txt

:: Run the application
python main.py
pause