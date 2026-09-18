# Importe BaseSettings, qui permet de créer une classe
# destinée à récupérer et valider des variables de configuration.
from pydantic_settings import BaseSettings


# Crée une classe représentant la configuration
# générale de notre application Warband HQ.
class Settings(BaseSettings):

    # Définit le nom de notre application.
    # Cette valeur pourra être utilisée ailleurs dans le projet.
    app_name: str = "Warband HQ"

    # Définit l'environnement dans lequel l'application fonctionne.
    # "development" sera notre valeur par défaut pour le moment.
    environment: str = "development"


# Crée une instance unique de notre configuration.
# Les autres parties du backend pourront utiliser cet objet
# pour accéder aux paramètres de l'application.
settings = Settings()
