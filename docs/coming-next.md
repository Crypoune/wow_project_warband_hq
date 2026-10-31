# Warband HQ - Améliorations futures

**Projet :** Warband HQ - Suivi des personnages de World of Warcraft
**Version :** 1.1
**Statut :** Pistes d'amélioration

## 1. Objectif du document

Ce document rassemble les fonctionnalités qui pourraient enrichir Warband HQ après la réalisation du MVP.

Il reprend les User Stories classées _Could Have_ et _Won't Have_ dans le Product Backlog, ainsi que de nouvelles idées identifiées au cours du développement et des échanges avec d'autres élèves.

L'objectif est de conserver une vision des évolutions possibles sans élargir le périmètre du MVP ni s'engager sur une date de réalisation.

Chaque fonctionnalité devra être évaluée en fonction de son utilité, de sa faisabilité technique, des données disponibles et du temps nécessaire à son développement.

## 2. Organisation et analyse des personnages

### 2.1 US-16 - Collections personnalisées

**Objectif :** permettre aux joueurs de regrouper leurs personnages ou leurs objectifs selon différents critères.

Cette fonctionnalité apporterait davantage de flexibilité dans l'organisation d'une Warband, notamment pour les joueurs possédant de nombreux personnages.

Fonctionnalités possibles :

- Créer et gérer des collections.
- Associer plusieurs personnages à une collection.
- Organiser les personnages selon ses préférences ou ses objectifs en jeu.

**Dépendance :** US-03 - Vue d'ensemble des personnages.

**Priorité actuelle :** Could Have.

### 2.2 US-18 - Comparaison des personnages

**Objectif :** permettre de comparer plusieurs personnages afin d'identifier rapidement leurs différences en matière d'équipement et de progression.

Fonctionnalités possibles :

- Sélectionner plusieurs personnages à comparer.
- Afficher leurs principales informations côte à côte.
- Comparer leur équipement, leur niveau d'objet et les données de progression disponibles.

Les critères de comparaison dépendront des informations accessibles via l'API Blizzard et des données gérées par Warband HQ.

**Dépendance :** US-06 - Détails d'un personnage.

**Priorité actuelle :** Could Have.

### 2.3 Informations complémentaires - Temps de jeu

**Objectif :** afficher le temps total passé à jouer sur chaque personnage.

Cette information permettrait aux joueurs de mieux connaître le temps investi dans leurs personnages et d'obtenir une statistique personnelle supplémentaire.

Fonctionnalités envisagées :

- Afficher le temps de jeu total en jours et en heures.
- Présenter cette information sur la fiche détaillée du personnage.
- Éventuellement, comparer le temps de jeu entre plusieurs personnages.

**Point à vérifier :** déterminer si le temps de jeu est accessible via l'API Blizzard. Si cette donnée n'est pas disponible, étudier la possibilité de la récupérer par un autre mécanisme autorisé, notamment un addon WoW.

La faisabilité et la fiabilité de cette récupération devront être vérifiées avant toute implémentation.

## 3. Métiers et progression des professions

### 3.1 Affichage des métiers d'un personnage

**Objectif :** permettre aux joueurs de consulter les métiers de leurs personnages et leur niveau de progression.

Fonctionnalités envisagées :

- Afficher les métiers connus pour chaque personnage.
- Présenter leur niveau de compétence et leur progression en expérience lorsque ces informations sont disponibles.
- Distinguer les spécialisations de métier si les données nécessaires sont accessibles.

### 3.2 Progression des métiers des extensions précédentes

Il serait également intéressant de consulter la progression des métiers associés aux extensions précédentes de World of Warcraft.

Fonctionnalités envisagées :

- Afficher les niveaux de métier propres aux différentes extensions.
- Distinguer la progression actuelle de celle des anciennes extensions.
- Faciliter le suivi des métiers pour les joueurs souhaitant compléter leur progression historique.

**Points à vérifier :**

- Les informations réellement exposées par l'API Blizzard.
- La disponibilité des niveaux de compétence et de progression détaillés.
- La manière de représenter les systèmes de métiers propres aux différentes extensions.

Cette fonctionnalité pourrait enrichir les fiches de personnages et donner une vision plus complète de leur progression artisanale.

## 4. Suivi de la progression hebdomadaire

### 4.1 Suivi du coffre hebdomadaire - Grande chambre

**Objectif :** permettre aux joueurs de visualiser leur progression vers les récompenses du coffre hebdomadaire, appelé Grande chambre dans World of Warcraft.

Le suivi pourrait centraliser les informations relatives aux activités qui contribuent à débloquer les récompenses.

Fonctionnalités envisagées :

- Afficher la progression des activités Mythique+, raid et PvP, selon les données disponibles.
- Présenter les paliers atteints et ceux restant à débloquer.
- Indiquer les activités ou objectifs encore nécessaires pour atteindre le prochain palier.
- Afficher les récompenses potentielles associées aux paliers.

### 4.2 Estimation du niveau d'objet des récompenses

**Objectif :** aider les joueurs à comprendre quelles récompenses ils pourraient obtenir en fonction de leur progression hebdomadaire.

Fonctionnalités envisagées :

- Afficher le niveau d'objet (ilvl) associé aux récompenses potentielles.
- Distinguer les récompenses correspondant aux différents paliers.
- Présenter, lorsque les données le permettent, le niveau d'objet de la récompense et les éventuelles améliorations disponibles.

Cette fonctionnalité permettrait de mieux visualiser les objectifs de progression et les récompenses à atteindre.

**Points à vérifier :**

- L'accès aux données individuelles du coffre hebdomadaire via l'API Blizzard.
- La possibilité de récupérer les activités réalisées et les paliers effectivement débloqués.
- La disponibilité des règles de récompenses et des niveaux d'objet associés à la saison en cours.

Si l'API ne fournit pas directement toutes les informations nécessaires, il faudra étudier la possibilité de calculer certains éléments à partir de données disponibles ou d'utiliser un mécanisme complémentaire.

## 5. Partage et disponibilité des données

### 5.1 US-17 - Partage public

**Objectif :** permettre aux joueurs de partager publiquement certaines informations de Warband HQ.

Fonctionnalités possibles :

- Choisir les informations à partager.
- Générer une page publique présentant une sélection de personnages ou de données de progression.
- Contrôler les informations qui restent privées.

Une attention particulière devra être portée à la confidentialité et à la protection des informations liées au compte.

**Dépendance :** US-03 - Vue d'ensemble des personnages.

**Priorité actuelle :** Could Have.

### 5.2 US-19 - Accès aux dernières données en cas d'indisponibilité de l'API Blizzard

**Objectif :** permettre aux joueurs de consulter les dernières informations synchronisées lorsque l'API Blizzard est indisponible.

Cette fonctionnalité a été exclue du MVP afin de limiter la complexité de la première version.

Une future implémentation pourrait permettre :

- De conserver les dernières données récupérées avec succès.
- D'afficher ces données lorsqu'une nouvelle récupération échoue.
- D'indiquer la date de dernière synchronisation.
- De distinguer les informations conservées en base des données actualisées.

**Priorité actuelle :** Won't Have pour le MVP.

**Statut :** Hors périmètre du MVP, mais réévaluable pour une version future.

## 6. Étude d'un addon World of Warcraft

### 6.1 Objectif

Étudier la possibilité de développer un addon WoW capable de récupérer certaines informations accessibles depuis l'interface du jeu, mais qui ne seraient pas disponibles via l'API Blizzard.

L'objectif serait de compléter les données de Warband HQ sans remplacer l'API officielle, qui resterait la source principale des informations.

Cette idée a notamment été proposée lors d'un échange avec un autre élève et pourrait constituer une piste technique intéressante pour enrichir les fonctionnalités de l'application.

### 6.2 Fonctionnalités potentielles

Selon les données réellement accessibles aux addons, plusieurs informations pourraient être étudiées :

- Le temps de jeu d'un personnage.
- Certaines informations détaillées sur les métiers et leur progression.
- Des données complémentaires sur les activités et la progression en jeu.
- D'éventuelles informations utiles au suivi hebdomadaire.

La liste définitive dépendra des possibilités réelles de l'interface WoW et des restrictions applicables aux addons.

### 6.3 Échange de données avec Warband HQ

Si la faisabilité est confirmée, un mécanisme d'échange entre l'addon et l'application pourrait être étudié.

Pistes possibles :

- Exporter les données de l'addon dans un fichier structuré.
- Permettre leur importation dans Warband HQ.
- Étudier un format d'échange commun, par exemple JSON.
- Prévoir une validation des données côté backend avant leur utilisation.

La possibilité d'une communication directe entre l'addon et le backend devra être vérifiée séparément. Un export et un import manuels pourraient constituer une première solution plus simple.

### 6.4 Contraintes et faisabilité

Avant d'entreprendre ce développement, plusieurs éléments devront être étudiés :

- Les informations réellement accessibles aux addons Lua.
- Les restrictions concernant la collecte et l'export des données.
- Les possibilités de transfert vers une application externe.
- La fiabilité et la fraîcheur des données récupérées.
- La compatibilité avec les versions du jeu.
- Le temps nécessaire au développement et à la maintenance de l'addon.

Cette piste reste expérimentale. Elle ne fait pas partie du périmètre du MVP et ne sera envisagée qu'après une étude de faisabilité.

## 7. Priorisation des futures évolutions

Les fonctionnalités présentées dans ce document ne sont pas toutes prioritaires et ne seront pas nécessairement développées.

Leur sélection devra tenir compte :

- De leur utilité réelle pour les joueurs.
- De leur complexité et du temps de développement nécessaire.
- De leurs dépendances avec les fonctionnalités existantes.
- De la disponibilité des données via l'API Blizzard.
- Des éventuelles solutions complémentaires nécessaires.
- De leur impact sur l'architecture, la confidentialité et la maintenabilité.

Les fonctionnalités retenues pourront être ajoutées à une future version du Product Backlog et priorisées avec la méthode MoSCoW.

## 8. Mise à jour du document

Ce document constitue une liste évolutive de pistes d'amélioration, et non un engagement de développement.

Le périmètre du MVP reste défini par le Product Backlog actuel.

Le document pourra être mis à jour après la réalisation du MVP, à la suite de nouveaux besoins ou lorsque les contraintes techniques et le temps disponible évolueront.

Toute fonctionnalité retenue devra être précisée, priorisée et planifiée avant le début de son développement.
