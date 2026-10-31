# Importe la classe FastAPI pour créer l'application et HTTPException pour gérer les erreurs HTTP.
from fastapi import FastAPI, HTTPException

# Importe le middleware CORS, qui contrôle les origines autorisées à appeler l'API depuis un navigateur.
from fastapi.middleware.cors import CORSMiddleware

# Importe l'exception utilisée lorsque les données d'une requête ne respectent pas la validation attendue.
from fastapi.exceptions import RequestValidationError

# Importe le middleware qui gère les sessions à l'aide d'un cookie signé.
from starlette.middleware.sessions import SessionMiddleware

# Importe la configuration centralisée du projet, notamment la clé secrète des sessions.
from app.core.config import settings

# Importe le routeur responsable de la gestion des tags.
from app.api.tags import router as tags_router

# Importe le routeur utilisé pour vérifier que l'API fonctionne.
from app.api.health import router as health_router

# Importe le routeur qui gère l'authentification et les opérations liées au compte.
from app.api.auth import router as auth_router

# Importe le routeur qui gère les personnages.
from app.api.characters import router as characters_router

# IMporte le routeur qui gère les objectifs.
from app.api.goals import router as goals_router

# Importe les fonctions personnalisées qui formateront les différentes réponses d'erreur.
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    unexpected_exception_handler,
)


# Crée l'application FastAPI principale.
# Les métadonnées suivantes sont notamment utilisées dans la documentation automatique de l'API.
app = FastAPI(
    title="Warband HQ API",  # Nom de l'API.
    description="Backend API for Warband HQ",  # Description de l'API.
    version="0.1.0",  # Version actuelle déclarée du projet.
)

# Configure le middleware CORS pour autoriser le frontend à communiquer avec le backend.
app.add_middleware(
    CORSMiddleware,
    # Liste des origines autorisées : protocole, domaine et port.
    allow_origins=[
        "http://127.0.0.1:5173",
    ],
    # Autorise l'envoi des cookies et autres informations d'authentification compatibles avec CORS.
    allow_credentials=True,
    # Autorise toutes les méthodes HTTP, par exemple GET, POST, PUT ou DELETE.
    allow_methods=["*"],
    # Autorise tous les en-têtes HTTP dans les requêtes CORS.
    allow_headers=["*"],
)

# Ajoute le middleware qui gère les sessions à l'aide d'un cookie signé.
app.add_middleware(
    SessionMiddleware,
    # Utilise la clé secrète définie dans la configuration du projet pour signer le cookie.
    secret_key=settings.session_secret_key,
    # Autorise notamment le fonctionnement des cookies dans les navigations de premier niveau.
    same_site="lax",
    # Désactive l'attribut Secure du cookie, ce qui convient au développement local en HTTP.
    # En production, HTTPS et un paramétrage adapté sont nécessaires.
    https_only=False,
)

# Associe les erreurs HTTP aux réponses préparées par notre gestionnaire personnalisé.
app.add_exception_handler(
    HTTPException,
    http_exception_handler,
)

# Associe les erreurs de validation des données reçues à leur gestionnaire personnalisé.
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

# Associe les autres exceptions non traitées à un gestionnaire générique.
app.add_exception_handler(
    Exception,
    unexpected_exception_handler,
)

# Enregistre les routes de vérification de l'état de l'API.
app.include_router(health_router)

# Enregistre les routes d'authentification.
app.include_router(auth_router)

# Enregistre les routes relatives aux personnages.
app.include_router(characters_router)

# Enregistre les routes relatives aux tags.
app.include_router(tags_router)

# Enregistre les routes relatives aux objectifs.
app.include_router(goals_router)
