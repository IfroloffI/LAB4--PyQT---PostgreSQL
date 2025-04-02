# Qt6 Python App Setup

## Add in .env:
```yml
APP_NAME=MyQtApp
APP_VERSION=1.0.0
UI_FILE=design.ui
DB_ENDPOINT=
```

## Initial Setup and RUN
RUN docker-compose.yml
```bash
python -m venv venv           # Create virtual environment
venv\Scripts\activate         # Activate on Windows
source venv/bin/activate      # Activate on Linux/Mac

python -m pip install --upgrade pip
pip install PyQt6 python-dotenv psycopg2-binary # OR requirements.txt TODO: Add requirements
python -m app.core.utils.convert_ui
python -m app.main
```

# For Developers (FOR EDIT PROJECT)
## Download QT Designer on Folder 'designer': https://build-system.fman.io/qt-designer-download

## Run 'designer/designer.exe'

## Save UI files in 'design/ui' folder, update .env

## For transform UI to PY and RUN:
```bash
python -m app.core.utils.convert_ui
python -m app.main
```
