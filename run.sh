#!/bin/bash
echo "================================================================="
echo "       SEFACAR - Démarrage du Serveur de Suivi Citernes"
echo "================================================================="
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
