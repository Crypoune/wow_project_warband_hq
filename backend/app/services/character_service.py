import httpx

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.character import Character
from app.services.auth_service import (
    AuthService,
    InvalidBlizzardProfileError,
)


class CharacterService:
    """
    Centralise la logique métier liée aux personnages WoW.

    Ce service fait le lien entre :
    - La base de données Warband HQ, qui mémorise les personnages importés.
    - L'API Blizzard, qui fournit les informations actualisées des personnages.
    - Les routes de l'API Warband HQ, qui utilisent ce service pour répondre
      aux requêtes du frontend.

    Les données propres à Blizzard restent la source de vérité pour les
    informations du personnage. La base Warband HQ conserve notamment
    l'identifiant interne, le statut favori et les dates de suivi.
    """

    def __init__(self):
        """
        Initialise le service d'accès à l'API Blizzard.

        AuthService gère les appels à Blizzard. On lui transmet la
        configuration de l'application, notamment la région Blizzard
        et les paramètres nécessaires aux requêtes.
        """
        self.auth_service = AuthService(settings)

    def get_available_characters(self, access_token: str) -> list[dict]:
        """
        Récupère les personnages disponibles sur le compte Blizzard.

        Le jeton OAuth représente l'autorisation obtenue par l'utilisateur
        lors de la connexion à son compte Blizzard.

        Cette méthode délègue la récupération des personnages à AuthService,
        qui s'occupe de communiquer avec l'API Blizzard.
        """
        return self.auth_service.get_account_characters(access_token)

    def import_characters(
        self,
        user_id: int,
        access_token: str,
        character_ids: list[int],
    ) -> list[dict]:
        """
        Importe dans Warband HQ les personnages sélectionnés par l'utilisateur.

        Le processus se déroule en plusieurs étapes :
        1. Récupérer les personnages accessibles sur le compte Blizzard.
        2. Vérifier que chaque identifiant demandé appartient bien à ce compte.
        3. Identifier les personnages déjà importés dans Warband HQ.
        4. Insérer uniquement les nouveaux personnages en base de données.
        5. Retourner les données Blizzard des personnages nouvellement importés.

        Cette vérification évite qu'un utilisateur puisse importer un personnage
        qui n'appartient pas au compte Blizzard auquel il est connecté.
        """

        # Récupère la liste des personnages réellement accessibles via Blizzard.
        available_characters = self.get_available_characters(access_token)

        # Crée un dictionnaire indexé par identifiant Blizzard.
        # Cela permet de retrouver rapidement les données d'un personnage.
        available_by_id = {
            character["id"]: character
            for character in available_characters
        }

        # Un utilisateur ne peut importer que les personnages de son compte.
        # On recherche les identifiants demandés qui ne figurent pas dans
        # la liste renvoyée par Blizzard.
        invalid_ids = set(character_ids) - set(available_by_id)

        if invalid_ids:
            raise ValueError(
                "One or more characters do not belong to the Blizzard account"
            )

        imported = []

        # SessionLocal ouvre une session SQLAlchemy pour interagir avec MySQL.
        # Le bloc with garantit que la session est fermée à la fin du bloc.
        with SessionLocal() as db:
            # Recherche les personnages demandés qui sont déjà importés
            # par cet utilisateur dans Warband HQ.
            existing_characters = db.scalars(
                select(Character).where(
                    Character.user_id == user_id,
                    Character.blizzard_character_id.in_(character_ids),
                )
            ).all()

            # Conserve uniquement les identifiants Blizzard déjà présents.
            existing_ids = {
                character.blizzard_character_id
                for character in existing_characters
            }

            # dict.fromkeys conserve l'ordre tout en éliminant les doublons
            # éventuels présents dans la liste fournie par le frontend.
            for character_id in dict.fromkeys(character_ids):
                # Aucun nouvel enregistrement n'est nécessaire si
                # le personnage est déjà importé.
                if character_id in existing_ids:
                    continue

                # Crée un enregistrement local associé à l'utilisateur.
                # Les informations détaillées restent récupérées auprès
                # de Blizzard au moment où elles sont nécessaires.
                character = Character(
                    user_id=user_id,
                    blizzard_character_id=character_id,
                )

                db.add(character)
                imported.append(character_id)

            # Enregistre les nouveaux personnages dans la base de données.
            db.commit()

        # Retourne les données Blizzard correspondant aux nouveaux imports.
        # Les personnages déjà importés ne sont pas renvoyés une seconde fois.
        return [
            available_by_id[character_id]
            for character_id in imported
        ]

    def update_favorite(
        self,
        user_id: int,
        character_id: int,
        is_favorite: bool,
    ) -> dict | None:
        """
        Modifie le statut favori d'un personnage.

        Les identifiants utilisés ici sont ceux de Warband HQ :
        - user_id identifie l'utilisateur connecté.
        - character_id identifie l'enregistrement local du personnage.

        Retourne le nouvel état du favori, ou None si le personnage n'existe
        pas ou n'appartient pas à l'utilisateur.
        """

        with SessionLocal() as db:
            # Recherche le personnage en vérifiant simultanément son identifiant
            # local et l'identifiant de son propriétaire.
            character = db.scalar(
                select(Character).where(
                    Character.id == character_id,
                    Character.user_id == user_id,
                )
            )

            if character is None:
                return None

            # Met à jour le champ favori de l'enregistrement SQLAlchemy.
            character.is_favorite = is_favorite

            # Enregistre la modification en base de données.
            db.commit()

            # Recharge les valeurs persistées dans l'objet.
            db.refresh(character)

            # Ne retourne que les informations nécessaires au frontend.
            return {
                "id": character.id,
                "is_favorite": character.is_favorite,
            }

    def get_imported_characters(
        self,
        user_id: int,
        access_token: str,
    ) -> list[dict]:
        """
        Retourne les personnages importés par l'utilisateur.

        Cette méthode prépare les données nécessaires à la liste des
        personnages de My Warband.

        Les métadonnées locales proviennent de MySQL, tandis que les
        informations du personnage, ses médias et ses niveaux d'objet
        sont récupérés depuis Blizzard.

        Les médias sont facultatifs : un personnage doit pouvoir rester
        affichable même si son portrait ou son rendu principal est absent.
        """

        with SessionLocal() as db:
            # Récupère uniquement les personnages appartenant à l'utilisateur.
            imported_characters = db.scalars(
                select(Character).where(Character.user_id == user_id)
            ).all()

            # Copie les données utiles dans des dictionnaires simples.
            # Cette copie est effectuée avant la fermeture de la session :
            # le reste de la méthode ne dépend donc plus des objets SQLAlchemy.
            imported_data = [
                {
                    "id": character.id,
                    "blizzard_character_id": character.blizzard_character_id,
                    "is_favorite": character.is_favorite,
                    "imported_at": character.imported_at,
                    "last_synced_at": character.last_synced_at,
                }
                for character in imported_characters
            ]

        # Si aucun personnage n'est importé, aucune requête Blizzard
        # supplémentaire n'est nécessaire.
        if not imported_data:
            return []

        # Blizzard reste la source de vérité pour les données du personnage.
        # On récupère la liste disponible sur le compte connecté.
        available_characters = self.get_available_characters(access_token)

        # Indexe les personnages par leur identifiant Blizzard afin de
        # retrouver facilement les données associées à chaque import local.
        available_by_id = {
            character["id"]: character
            for character in available_characters
        }

        result = []

        for imported in imported_data:
            # Récupère les données Blizzard correspondant à cet import.
            # Si le personnage n'est plus présent dans la liste accessible,
            # on utilise un dictionnaire vide pour éviter une KeyError.
            blizzard_data = available_by_id.get(
                imported["blizzard_character_id"], {}
            )

            # Fusionne les deux sources.
            # Les métadonnées locales sont placées en dernier pour préserver
            # les valeurs de Warband HQ, comme l'identifiant interne et le favori.
            character_data = {**blizzard_data, **imported}

            realm_slug = character_data.get("realm_slug")
            character_name = character_data.get("name")

            # Initialise les données facultatives.
            # Le frontend reçoit toujours ces clés, même lorsque Blizzard
            # ne fournit pas les informations correspondantes.
            character_data["portrait_url"] = None
            character_data["main_art_url"] = None
            character_data["average_item_level"] = None
            character_data["equipped_item_level"] = None
            character_data["equipment"] = []

            # Les appels de profil nécessitent le royaume et le nom du personnage.
            if realm_slug and character_name:

                # ---------------------------------------------------------
                # 1. Récupération des médias du personnage
                # ---------------------------------------------------------
                try:
                    # AuthService effectue un appel à l'endpoint Blizzard
                    # character-media et renvoie un dictionnaire contenant :
                    #
                    # portrait_url : l'URL du portrait, généralement basée
                    # sur l'asset inset, avec avatar comme solution de repli.
                    #
                    # main_art_url : l'URL de l'asset main, utilisé pour
                    # afficher le rendu complet au centre de l'armurerie.
                    #
                    # La réponse peut être mise en cache par AuthService afin
                    # d'éviter de répéter inutilement le même appel.
                    media = self.auth_service.get_character_media(
                        access_token,
                        realm_slug,
                        character_name,
                    )

                    # Sépare les deux médias pour les exposer clairement
                    # dans la réponse de l'API Warband HQ.
                    character_data["portrait_url"] = media["portrait_url"]
                    character_data["main_art_url"] = media["main_art_url"]

                except httpx.HTTPError:
                    # Une erreur HTTP ne doit pas empêcher l'affichage
                    # de la carte du personnage.
                    # Les deux URL restent à None.
                    pass

                # ---------------------------------------------------------
                # 2. Récupération du profil et des niveaux d'objet
                # ---------------------------------------------------------
                try:
                    # Cet appel récupère le profil détaillé du personnage.
                    # On utilise ici les valeurs Blizzard pour les niveaux
                    # d'objet moyen et équipé.
                    profile = self.auth_service.get_character_profile(
                        access_token,
                        realm_slug,
                        character_name,
                    )

                    character_data["average_item_level"] = profile.get(
                        "average_item_level"
                    )

                    character_data["equipped_item_level"] = profile.get(
                        "equipped_item_level"
                    )

                except (httpx.HTTPError, InvalidBlizzardProfileError):
                    # Si le profil est inaccessible ou mal formé,
                    # les niveaux d'objet restent à None.
                    # Le reste des informations du personnage est conservé.
                    pass

            # Ajoute le personnage enrichi à la liste finale.
            result.append(character_data)

        return result

    def get_character_details(
        self,
        user_id: int,
        character_id: int,
        access_token: str,
    ) -> dict | None:
        """
        Retourne les informations détaillées d'un personnage importé.

        Cette méthode alimente la page de détails d'un personnage, qui évoluera
        vers la page d'armurerie de Warband HQ.

        Elle rassemble :
        - Les métadonnées locales de l'import.
        - Les informations générales fournies par Blizzard.
        - Le portrait et le rendu principal du personnage.
        - Les niveaux d'objet moyen et équipé.

        Retourne None si le personnage n'existe pas dans Warband HQ
        ou s'il n'appartient pas à l'utilisateur connecté.
        """

        # -------------------------------------------------------------
        # 1. Vérification de l'appartenance du personnage
        # -------------------------------------------------------------
        with SessionLocal() as db:
            # On recherche l'enregistrement local en vérifiant son propriétaire.
            # Cela évite de permettre à un utilisateur d'accéder aux détails
            # d'un personnage importé par un autre utilisateur.
            character = db.scalar(
                select(Character).where(
                    Character.id == character_id,
                    Character.user_id == user_id,
                )
            )

            if character is None:
                return None

            # Copie les métadonnées avant de fermer la session SQLAlchemy.
            imported_data = {
                "id": character.id,
                "blizzard_character_id": character.blizzard_character_id,
                "is_favorite": character.is_favorite,
                "imported_at": character.imported_at,
                "last_synced_at": character.last_synced_at,
            }

        # -------------------------------------------------------------
        # 2. Récupération des informations générales depuis Blizzard
        # -------------------------------------------------------------

        # Récupère les personnages accessibles sur le compte Blizzard.
        available_characters = self.get_available_characters(access_token)

        # Recherche le personnage correspondant à l'identifiant Blizzard
        # conservé lors de l'import dans Warband HQ.
        blizzard_data = next(
            (
                item
                for item in available_characters
                if item["id"] == imported_data["blizzard_character_id"]
            ),
            {},
        )

        # Fusionne les informations Blizzard et les métadonnées locales.
        # Les valeurs locales gardent la priorité pour les champs communs.
        character_data = {**blizzard_data, **imported_data}

        # Initialise les données détaillées.
        # Ces valeurs par défaut garantissent une structure de réponse stable,
        # même si certaines informations ne sont pas disponibles.
        character_data["portrait_url"] = None
        character_data["main_art_url"] = None
        character_data["average_item_level"] = None
        character_data["equipped_item_level"] = None
        character_data["equipment"] = []

        realm_slug = character_data.get("realm_slug")
        character_name = character_data.get("name")

        if realm_slug and character_name:

            # ---------------------------------------------------------
            # 3. Récupération du portrait et du rendu principal
            # ---------------------------------------------------------
            try:
                # Une seule méthode récupère les deux médias.
                # Le portrait sert notamment aux petites cartes de personnages.
                # Le rendu main servira à la représentation centrale de
                # l'armurerie, lorsque le frontend sera prêt à l'afficher.
                media = self.auth_service.get_character_media(
                    access_token,
                    realm_slug,
                    character_name,
                )

                character_data["portrait_url"] = media["portrait_url"]
                character_data["main_art_url"] = media["main_art_url"]

            except httpx.HTTPError:
                # L'absence de médias n'empêche pas de consulter les détails.
                # Les champs restent à None et le frontend pourra afficher
                # une image de remplacement.
                pass

            # ---------------------------------------------------------
            # 4. Récupération du profil détaillé
            # ---------------------------------------------------------

            # Le profil fournit notamment les niveaux d'objet.
            # On conserve ici le comportement de la méthode existante :
            # les erreurs de récupération du profil peuvent remonter à la route.
            profile = self.auth_service.get_character_profile(
                access_token,
                realm_slug,
                character_name,
            )

            character_data["average_item_level"] = profile.get(
                "average_item_level"
            )

            character_data["equipped_item_level"] = profile.get(
                "equipped_item_level"
            )

            # ---------------------------------------------------------
            # 5. Récupération de l'équipement du personnage
            # ---------------------------------------------------------

            try:
                # Récupère la liste des objets actuellement équipés.
                equipment_data = self.auth_service.get_character_equipment(
                    access_token,
                    realm_slug,
                    character_name,
                )

                # Transmet les objets équipés au frontend.
                character_data["equipment"] = equipment_data["equipped_items"]

            except (httpx.HTTPError, InvalidBlizzardProfileError):
                # Un échec de cet appel ne doit pas empêcher
                # l'affichage du reste de la fiche du personnage.
                pass

        # Retourne un dictionnaire directement exploitable par la route API.
        return character_data
