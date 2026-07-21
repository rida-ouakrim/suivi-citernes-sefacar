# 🚛 SEFACAR — Application de Suivi de Production des Citernes

Application web de suivi en temps réel de la fabrication des citernes (Carburant et Eau) pour **SEFACAR**, remplaçant la gestion sous fichier Excel par un système digitalisé réactif sur **Mobile** et **PC**.

---

## 📁 Structure du Projet

```
Suivi/
├── app.py                     # Application principale Streamlit (Mode Tournée & Administration)
├── db.py                      # Gestionnaire de la base de données SQLite
├── init_db.py                 # Script d'initialisation depuis l'Excel d'origine
├── SUIVI CITERNE 2107.xlsx    # Fichier Excel source des données
├── suivi_citernes.db          # Base de données SQLite locale (générée automatiquement)
├── requirements.txt           # Dépendances Python nécessaires
├── run.bat                    # Script de lancement 1-clic pour Windows (Serveur Local/Wi-Fi)
├── run.sh                     # Script de lancement pour Linux / Mac
├── Dockerfile                 # Fichier de conteneurisation Docker
└── Procfile                   # Fichier de déploiement Cloud (Render/Railway/Heroku)
```

---

## 🚀 Options de Déploiement

### Option 1 : Déploiement sur le Réseau Local / Wi-Fi d'Entreprise (Recommandé)

Pour déployer l'application au sein de l'entreprise **SEFACAR** afin que le responsable de suivi puisse l'utiliser sur son smartphone/tablette pendant la tournée et l'administration sur ses PC :

1. **Sur le PC Serveur / PC fixe de l'entreprise** :
   - Assurez-vous que Python est installé.
   - Double-cliquez simplement sur le fichier **`run.bat`**.

2. **Accès depuis les téléphones et tablettes en tournée** :
   - Connectez les smartphones/tablettes au réseau Wi-Fi de l'entreprise.
   - Ouvrez le navigateur du téléphone et tapez l'adresse IP du PC serveur :
     ```text
     http://<IP_DE_VOTRE_PC>:8501
     ```
     *(Exemple : http://192.168.1.50:8501)*

---

### Option 2 : Déploiement Cloud Gratuit (Accessible partout via Internet)

Pour rendre l'application accessible depuis n'importe où hors de l'entreprise via Internet :

#### A. Via Streamlit Community Cloud (Gratuit & Rapide)
1. Publiez ce dossier sur votre compte **GitHub**.
2. Allez sur **[share.streamlit.io](https://share.streamlit.io/)** et connectez votre compte GitHub.
3. Cliquez sur **"New app"**, sélectionnez le dépôt `Suivi` et le fichier principal `app.py`.
4. Cliquez sur **Deploy**. Votre application sera en ligne avec une URL HTTPS sécurisée !

#### B. Via Render / Railway
1. Créez un compte sur **[Render.com](https://render.com/)** ou **[Railway.app](https://railway.app/)**.
2. Connectez votre dépôt GitHub. Le fichier `Procfile` et `requirements.txt` seront automatiquement détectés pour déployer l'application.

---

### Option 3 : Déploiement avec Docker (Conteneur)

Si vous disposez d'un serveur Linux/Windows avec Docker :

1. **Construire l'image Docker** :
   ```bash
   docker build -t sefacar-suivi .
   ```

2. **Lancer le conteneur** :
   ```bash
   docker run -d -p 8501:8501 --name sefacar_container --restart always sefacar-suivi
   ```

---

## 🛠️ Maintenance & Mise à jour des données

- **Sauvegardes** : Les données saisies lors des tournées sont stockées dans le fichier `suivi_citernes.db`. Vous pouvez copier ce fichier pour effectuer des sauvegardes régulières.
- **Réinitialisation depuis l'Excel** : Depuis l'onglet `⚙️ Configuration & Synchro` de l'application, vous pouvez ré-importer les données initiales du fichier Excel à tout moment.

---

*Développé pour l'entreprise **SEFACAR**.*
