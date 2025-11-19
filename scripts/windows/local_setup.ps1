Set-Location -Path "src"
pyenv local 3.11.6
python -m venv venv
.\venv\Scripts\activate.ps1
pip install -r requirements.txt
npm install
npm run build-css
python manage.py migrate
