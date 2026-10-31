
# Permet de définir les modèles de données reçues par l'API.
from pydantic import BaseModel, Field, ConfigDict

# Fournit les outils FastAPI pour créer les routes,
# récupérer les dépendances et renvoyer des erreurs HTTP.
from fastapi import APIRouter, Depends, HTTPException

# Permet de reconnaître les erreurs provenant de SQLAlchemy,
# notre outil de communication avec la base de données.
from sqlalchemy.exc import SQLAlchemyError

# Fournit les informations de l'utilisateur authentifié
# ainsi que la dépendance qui vérifie son authentification.
from app.core.dependencies import CurrentAuth, get_current_auth

# Contient la logique métier de gestion des objectifs :
# création, lecture, modification et suppression.
from app.services.goal_service import GoalService


# ============================================================
# 1. MODÈLES DE DONNÉES : validation des requêtes
# ============================================================

class GoalCreateRequest(BaseModel):
    """
    Décrit les données que le client doit ou peut envoyer
    pour créer un nouvel objectif.
    """

    # Le titre est obligatoire et doit contenir entre 1 et 100
    # caractères. Le service vérifiera aussi les espaces seuls.
    title: str = Field(min_length=1, max_length=100)

    # La description est facultative. None signifie qu'elle
    # peut être absente ou explicitement envoyée comme null.
    description: str | None = None

    # Si character_id est renseigné, l'objectif sera associé
    # à ce personnage. Sinon, il s'agira d'un objectif de warband.
    character_id: int | None = None

    # Par défaut, un nouvel objectif est en cours.
    status: str = "IN_PROGRESS"


class GoalUpdateRequest(BaseModel):
    """
    Décrit les champs acceptés pour modifier un objectif existant.

    Comme il s'agit d'une modification partielle (PATCH),
    le client peut envoyer uniquement les champs à modifier.
    """

    # Refuse les champs inconnus pour éviter d'accepter
    # accidentellement des données qui ne sont pas prévues.
    model_config = ConfigDict(extra="forbid")

    # None par défaut signifie que le titre peut être omis.
    # La route refusera explicitement un titre envoyé à null.
    title: str | None = Field(default=None, max_length=100)

    # Une description envoyée à null permet de l'effacer.
    description: str | None = None

    # Un character_id envoyé à null permet de détacher
    # l'objectif de son personnage.
    character_id: int | None = None

    # Le statut peut être omis, mais pas envoyé explicitement
    # à null. Les valeurs autorisées sont vérifiées par le service.
    status: str | None = None


# ============================================================
# 2. INITIALISATION DU ROUTEUR ET DU SERVICE
# ============================================================

# Regroupe les routes sous le préfixe /api/goals.
# Par exemple, @router.get("") correspond à GET /api/goals.
# Le tag "goals" regroupe ces endpoints dans la documentation
# interactive de FastAPI, accessible via /docs.
router = APIRouter(prefix="/api/goals", tags=["goals"])

# Crée l'objet chargé d'exécuter les opérations métier.
# Les routes lui délèguent le travail plutôt que de contenir
# directement toute la logique d'accès à la base de données.
goal_service = GoalService()


# ============================================================
# 3. CRÉER UN OBJECTIF
# ============================================================

@router.post("")
def create_goal(
    payload: GoalCreateRequest,
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """
    Crée un objectif pour l'utilisateur actuellement connecté.

    payload contient les données envoyées par le client.
    current_auth est fourni par FastAPI après vérification
    de l'authentification.
    """

    try:
        goal = goal_service.create_goal(
            # Important : l'identité vient de l'authentification,
            # jamais d'un user_id choisi par le client.
            user_id=current_auth.user_id,
            title=payload.title,
            description=payload.description,
            character_id=payload.character_id,
            status=payload.status,
        )

        # Renvoie l'objectif créé dans une réponse JSON.
        return {"goal": goal}

    except ValueError as exc:
        # Une ValueError représente ici une règle métier invalide,
        # par exemple un titre vide ou un statut non autorisé.
        raise HTTPException(
            status_code=400,
            detail={"message": str(exc)},
        ) from exc

    except SQLAlchemyError as exc:
        # Une erreur SQL indique un problème lors d'une opération
        # avec la base de données. On ne révèle pas les détails
        # techniques internes au client.
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to create goal"},
        ) from exc


# ============================================================
# 4. RÉCUPÉRER LES OBJECTIFS DE L'UTILISATEUR
# ============================================================

@router.get("")
def get_goals(
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """
    Renvoie les objectifs appartenant à l'utilisateur connecté.
    """

    try:
        # Le service doit filtrer les objectifs par user_id.
        goals = goal_service.get_goals(user_id=current_auth.user_id)

        return {"goals": goals}

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to retrieve goals"},
        ) from exc


# ============================================================
# 5. MODIFIER UN OBJECTIF
# ============================================================

@router.patch("/{goal_id}")
def update_goal(
    goal_id: int,
    payload: GoalUpdateRequest,
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """
    Modifie uniquement les champs envoyés par le client.

    Exemple : PATCH /api/goals/12 avec {"status": "COMPLETED"}
    modifie le statut de l'objectif 12 sans toucher à son titre.
    """

    # model_fields_set contient les champs réellement envoyés
    # dans la requête, même si leur valeur est null.
    # Cela permet de distinguer un champ omis d'un champ à effacer.
    fields_set = payload.model_fields_set

    # Le titre et le statut ne doivent pas être explicitement null.
    if "title" in fields_set and payload.title is None:
        raise HTTPException(
            status_code=422,
            detail={"message": "Le titre ne peut pas être null."},
        )

    if "status" in fields_set and payload.status is None:
        raise HTTPException(
            status_code=422,
            detail={"message": "Le statut ne peut pas être null."},
        )

    # Construit un dictionnaire contenant uniquement les champs
    # fournis par le client. Les champs absents ne seront pas
    # transmis au service et ne seront donc pas modifiés.
    update_data = {
        field: getattr(payload, field)
        for field in fields_set
    }

    try:
        goal = goal_service.update_goal(
            # Le service doit vérifier que l'objectif appartient
            # bien à l'utilisateur connecté.
            goal_id=goal_id,
            user_id=current_auth.user_id,
            **update_data,
        )

        return {"goal": goal}

    except ValueError as exc:
        message = str(exc)

        # Un objectif inaccessible ou un personnage qui
        # n'appartient pas à l'utilisateur renvoie 404.
        # Les autres erreurs métier renvoient 400.
        status_code = (
            404
            if message in {
                "Objectif introuvable ou inaccessible.",
                "Ce personnage n'existe pas ou ne vous appartient pas.",
            }
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail={"message": message},
        ) from exc

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to update goal"},
        ) from exc


# ============================================================
# 6. SUPPRIMER UN OBJECTIF
# ============================================================

@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    current_auth: CurrentAuth = Depends(get_current_auth),
):
    """
    Supprime un objectif appartenant à l'utilisateur connecté.

    La confirmation avant suppression sera gérée par le frontend.
    """

    try:
        # Le service vérifie que l'objectif existe et appartient
        # à l'utilisateur avant de le supprimer.
        return goal_service.delete_goal(
            goal_id=goal_id,
            user_id=current_auth.user_id,
        )

    except ValueError as exc:
        # On ne révèle pas si l'objectif d'un autre utilisateur
        # existe : on renvoie également une erreur 404.
        raise HTTPException(
            status_code=404,
            detail={"message": str(exc)},
        ) from exc

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unable to delete goal"},
        ) from exc
