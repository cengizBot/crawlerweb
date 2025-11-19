@echo off
echo ============================================
echo  Lancement du Web Crawler + Tkinter
echo ============================================

REM ----- 1. Démarrage MySQL dans Docker -----
echo [1/4] Démarrage de la base MySQL...
docker compose up -d

REM ----- 2. Création du virtualenv -----
if not exist venv (
    echo [2/4] Création de l'environnement virtuel...
    python -m venv venv
)

REM ----- 3. Activation du virtualenv -----
echo [3/4] Activation de l'environnement...
call venv\Scripts\activate

REM ----- 4. Installation des dépendances -----
echo [4/4] Installation des dépendances Python...
pip install -r requirements.txt

REM ----- 5. Lancement du programme -----
echo Lancement du programme Tkinter...
python main.py

pause
