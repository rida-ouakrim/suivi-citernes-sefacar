@echo off
title SEFACAR - Suivi de Production des Citernes
echo =================================================================
echo        SEFACAR - Demarrage du Serveur de Suivi Citernes
echo =================================================================
echo.
echo L'application va s'ouvrir dans votre navigateur.
echo Pour y acceder depuis votre smartphone / tablette sur le meme Wi-Fi,
echo utilisez l'adresse IP de ce PC avec le port 8501.
echo.
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
pause
