# Qt6 Python App Setup

## Add in .env:
```yml
# Application Configuration
APP_NAME=QtApp
APP_VERSION=0.0.1
UI_FILE=main_window.ui

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lab4_db
DB_USER=postgres
DB_PASSWORD=secret
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
