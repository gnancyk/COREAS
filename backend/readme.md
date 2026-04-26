CAHIER DES CHARGES
&
PROPOSITION FONCTIONNELLE & TECHNIQUE
SaphirV3 — Plateforme d'Audit et de Vérification
des Environnements Microsoft Dynamics CRM
Version 2.0  |  Avril 2026
Confidentiel — Usage interne

PARTIE I — CAHIER DES CHARGES

1. Contexte et Enjeux
Les environnements Microsoft Dynamics CRM SaphirV3 sont au cœur des processus métier de l'organisation : gestion des relations clients, facturation, gestion des campagnes, reporting et intégration avec les systèmes tiers. La création ou la reconfiguration d'un nouvel environnement implique un nombre élevé de vérifications manuelles dispersées, longues à effectuer et sources d'erreurs.
L'objectif du projet est de développer une plateforme web permettant d'automatiser, centraliser et tracer l'ensemble des contrôles de conformité d'un environnement SaphirV3, depuis la validation du service CentralParam jusqu'à la vérification des services Windows, de la base SQL Server et des rapports SSRS.

Point d'entrée obligatoire : CentralParam est le service SOAP (.svc) contenant toutes les valeurs de configuration de l'environnement. Aucun autre contrôle ne peut être lancé avant que CentralParam soit validé et ses paramètres récupérés.

2. Acteurs du Système
Acteur	Type	Rôle et responsabilités
Technicien d'intégration	Utilisateur principal	Lance les vérifications, consulte les résultats, exporte les rapports
Administrateur plateforme	Utilisateur admin	Gère les environnements enregistrés, les utilisateurs, les configurations
CentralParam	Système externe	Service SOAP fournissant toutes les valeurs de configuration à tester
Active Directory	Système externe	Authentification des utilisateurs, vérification des groupes (PrivUserGroup)
SQL Server	Système externe	Instance hébergeant la base CRM, source des vérifications DB
SSRS	Système externe	Serveur de rapports dont la disponibilité et la config sont vérifiées
Serveurs Windows (WMI/WinRM)	Système externe	Cibles des vérifications infrastructure via PowerShell distant

3. Fonctionnalités
3.1 Point d'entrée — CentralParam (obligatoire en premier)
•	Valider la syntaxe de l'URL CentralParam (http/https + domaine).
•	Vérifier que l'URL est un service SVC/WCF valide (réponse HTTP 200 + contenu WCF).
•	Récupérer l'ensemble des paramètres de configuration via le WSDL SOAP.
•	Récupérer un paramètre spécifique par son nom (avec parsing des chaînes clé=valeur).
•	Tester CentralParam et CentralParamConfig (liens, disponibilité).
•	Enregistrer le snapshot des paramètres récupérés pour traçabilité (VerificationConfigurations).

3.2 Module CRM Dynamics
•	Vérifier la disponibilité et l'accessibilité de l'application CRM (HTTP NTLM).
•	Authentifier un compte utilisateur sur le CRM et récupérer la version.
•	Vérifier la ressource web gs2e_FonctionsGenerales :
◦	nomBaseDeDonnees : doit correspondre au catalogue CRM
◦	strIpserveur : doit contenir le lien CRM
◦	strUrl_webservic_ps_extern_database : lien vers le service ExecutionPS du serveur Batch
•	Vérifier la ressource js_edition (absence d'erreur d'encodage base64).
•	Récupérer et tester les valeurs des Fonctions Générales encodées.
•	Vérifier que les utilisateurs peuvent interagir sans erreur avec l'interface CRM.

3.3 Module Backend (Services Dynamics CRM)
•	Vérifier que les services Windows CRM sont démarrés :
◦	Service de traitement asynchrone Microsoft Dynamics CRM (MSCRMAsyncService)
◦	Service de traitement Bac à sable Microsoft Dynamics CRM (MSCRMSandboxService)
•	Vérifier que les comptes de démarrage des services appartiennent au groupe PrivUserGroup dans Active Directory.

3.4 Module Batch
•	Tester CentralParam et CentralParamConfig (disponibilité, liens).
•	Tester les liens déclarés dans CentralParamConfig.
•	Récupérer les services depuis le pool et les valeurs depuis CentralParam.
•	Vérifier que les services Windows critiques sont démarrés : ASP.NET State Service, World Wide Web Publishing Service.
•	Vérifier les réponses HTTP des services web (code 200 attendu).
•	Tester la disponibilité de l'instance SQL depuis le serveur Batch.
•	Lister les services contenant 'SAPHIRV3' dans leur nom et vérifier leur état (démarré / arrêté).
•	Vérifier le paramètre CentralisationParamEndPoint dans les fichiers .config de chaque service SAPHIRV3 et du service facturation .
•	Vérifier l'existence du fichier des critères (paramètre PARAMCRIT0001).

3.5 Module SQL Server
•	Vérifier les valeurs dans le facturier encaissable (lien CentralParam).
•	Vérifier la cohérence des champs OrganizationID dans toutes les tables CRM.
•	Vérifier les taux de fragmentation des index (rebuild / reorganize si nécessaire).
•	Identifier les index manquants (sys.dm_db_missing_index_details).
•	Vérifier l'existence et l'activation des triggers :
◦	gs2e_Trg_UniciteCampagneFacturation (table gs2e_campagne_facturationBase)
◦	trg_UpdateRequeteSQL (table rmdb_valeurdecritreBase)
•	Vérifier les catalogues référencés dans les procédures stockées et fonctions.
•	Vérifier les catalogues dans la colonne gs2e_requete_sql de rmdb_valeurdecritreBase.
•	Vérifier la migration du paramétrage comptable.

3.6 Module Reporting (SSRS)
•	Vérifier que le service SQL Server Reporting Services est démarré et accessible.
•	Vérifier la source de données configurée pour chaque rapport.
•	Vérifier que la clé de chiffrement SSRS est renseignée et active.(CRM)
•	Vérifier que les chaînes de connexion partagées sont correctes (login/mot de passe).
•	Vérifier  la source de donnee de tout les rapport du portail que la chaîne de connexion partagée est configurée pour tous les rapports du portail.

3.7 Module Infrastructure
•	Vérifier que la fonctionnalité IIS est installée sur les serveurs cibles.
•	Vérifier que le package Web Deploy est installé.
•	Vérifier l'ouverture du port 5986 (WinRM HTTPS).
•	Vérifier la configuration des fichiers .config (CentralParam, service de facturation).
•	Ping de disponibilité et récupération des informations OS (via PowerShell distant / WMI).
Connaitre l’espace du c 
3.8 Module Administration & Préparation
•	Enregistrer et gérer les environnements CRM à tester (nom, URL CentralParam, serveurs associés).
•	Lister les utilisateurs administrateurs de chaque environnement.
•	Permettre une présélection des contrôles à exécuter avant le lancement.
•	Tracer et stocker chaque session de vérification avec horodatage, résultats OK/KO, messages d'erreur.
•	Exporter un rapport de vérification (PDF).

4. Cas d'Usage Principaux
ID	Cas d'usage	Acteur	Précondition	Résultat attendu
UC-01	Lancer une vérification complète d'un environnement	Technicien	Environnement enregistré, CentralParam accessible	Rapport complet OK/KO par module
UC-02	Valider CentralParam avant tout autre test	Technicien	URL CentralParam fournie	Paramètres récupérés, snapshot enregistré
UC-03	Vérifier la ressource JS gs2e_FonctionsGenerales	Technicien	Instance SQL + catalogue CRM fournis	Statut des 3 paramètres (catalogue, lien CRM, ExecutionPS)
UC-04	Contrôler les services Windows SAPHIRV3	Technicien	Serveur Batch accessible via WinRM	Liste des services avec état + anomalies config
UC-05	Vérifier les triggers et index SQL	Technicien	Credentials SQL fournis	Statut des triggers, taux de fragmentation, index manquants
UC-06	Consulter l'historique des vérifications	Technicien / Admin	Vérifications existantes en base	Liste triée par date/environnement avec statuts agrégés
UC-07	Gérer les environnements enregistrés	Administrateur	Compte admin	CRUD sur les environnements et leurs configurations
UC-08	Exporter le rapport d'audit	Technicien	Vérification terminée	Fichier PDF ou Excel téléchargeable

5. Contraintes Techniques et Métiers
5.1 Contraintes techniques
•	Le backend doit fonctionner sur Windows Server (WMI, PowerShell requis pour les appels distants).
•	Les serveurs cibles doivent avoir WinRM activé (port 5986) et un compte avec droits d'administration distante.
•	SQL Server : ODBC Driver 17 for SQL Server requis sur le serveur hébergeant le backend.
•	CentralParam est un service WCF/SOAP : la bibliothèque Zeep est utilisée pour la consommation WSDL.
•	Le frontend doit fonctionner sur les navigateurs modernes (Chrome, Edge) sans plugin.
•	Python 3.10+ et Node.js 20+ requis pour le backend et le build frontend.

5.2 Contraintes métiers
•	CentralParam est le point d'entrée obligatoire : aucun autre module ne peut être exécuté sans avoir préalablement récupéré les paramètres.
•	Les credentials (login/mot de passe) ne doivent jamais être stockés en base de données. Ils sont fournis à chaque session de vérification.
•	Un snapshot de la configuration au moment de la vérification doit être enregistré pour traçabilité (table VerificationConfigurations).
•	Les résultats doivent être consultables par un utilisateur n'ayant pas lancé la vérification.

PARTIE II — PROPOSITION FONCTIONNELLE & TECHNIQUE

6. Architecture Globale
6.1 Vue d'ensemble
L'architecture proposée est une architecture en trois tiers découplés communiquant via une API REST :
•	Frontend Vue.js 3 (Vite) : interface utilisateur consommant l'API.
•	Backend FastAPI (Python) : logique métier, orchestration des vérifications, exposition des endpoints.
•	Base de données PostgreSQL : persistance des environnements, des sessions de vérification et des résultats.

Hypothèse architecturale : le passage de Flask à FastAPI est recommandé pour bénéficier de la validation automatique des schémas (Pydantic), de la documentation OpenAPI native (/docs), de la gestion asynchrone (async/await) et des meilleures performances. Flask reste une option viable si la migration est jugée trop coûteuse à court terme.

6.2 Stack technique recommandée
Couche	Technologie	Version	Justification
Backend API	FastAPI + Pydantic	0.115+	Validation auto, OpenAPI natif, async, typage fort
Backend (alternatif)	Flask + Flask-RESTX	3.x	Migration minimale depuis l'existant
Frontend	Vue.js 3 + Vite	3.x / 5.x	SPA légère, réactive, compatible Composition API
Base de données	PostgreSQL	16+	Relations complexes, JSON natif, robustesse production
Base (alternatif dev)	SQLite	—	Simple pour développement local uniquement
ORM	SQLAlchemy 2 + Alembic	2.x	Migrations versionnées, support async
Auth	python-jose + passlib	—	JWT HS256, hachage bcrypt
AD Integration	ldap3	2.9+	LDAP/NTLM sur Active Directory
SOAP/WCF	Zeep	4.x	Consommation WSDL CentralParam
SQL Server	pyodbc + ODBC Driver 17	—	Connexion aux instances SQL cibles
WMI / PowerShell	wmi + pythoncom + subprocess	—	Collecte distante sur serveurs Windows
HTTP Client	httpx (async) ou requests	—	Appels CRM, SSRS, services web
Config	python-dotenv + pydantic-settings	—	Variables d'environnement typées
Tests	pytest + httpx (TestClient)	—	Tests unitaires et d'intégration
Documentation	OpenAPI / Swagger UI	natif FastAPI	Exposition automatique sur /docs

6.3 Organisation des dossiers (Backend)
Structure modulaire recommandée pour le backend FastAPI :

Dossier / Fichier	Rôle
app/main.py	Point d'entrée FastAPI, inclusion des routers, middleware CORS
app/config.py	Settings Pydantic (BaseSettings), lecture du .env
app/database.py	Session SQLAlchemy async, init Base
app/models/	Modèles SQLAlchemy (ORM) — un fichier par entité
app/schemas/	Schémas Pydantic — Request/Response par module
app/routers/	Un router par module (central_param, crm, batch, sql, ssrs, infra)
app/services/	Logique métier — un service par domaine fonctionnel
app/utils/	Utilitaires transverses (powershell, sql_runner, bd_tools, time_utils)
app/dependencies.py	Injection de dépendances FastAPI (db session, current_user)
alembic/	Migrations de base de données versionnées
.env / .env.example	Configuration d'environnement
requirements.txt	Dépendances Python

7. Base de Données
7.1 Analyse du schéma existant
Le schéma fourni (image) est une base solide. Il couvre les entités clés : Environments, Servers, Users, Verifications, Modules, Controls, ControlResults, ServerResults, EnvConfigurations et VerificationConfigurations. Les améliorations proposées portent sur la normalisation, la traçabilité et la sécurité.

7.2 Schéma amélioré — Tables et champs
Table : environments
Colonne	Type	Contrainte	Description
environment_id	UUID	PK, default gen_random_uuid()	Identifiant unique
name	VARCHAR(150)	NOT NULL, UNIQUE	Nom de l'environnement
central_param_url	VARCHAR(500)	NOT NULL	URL du service CentralParam
description	TEXT	—	Notes libres
created_at	TIMESTAMP	NOT NULL, default now()	Date de création
updated_at	TIMESTAMP	—	Dernière mise à jour
is_active	BOOLEAN	default true	Actif / archivé

Table : servers
Colonne	Type	Contrainte	Description
server_id	UUID	PK	Identifiant unique
environment_id	UUID	FK → environments	Environnement parent
server_name	VARCHAR(200)	NOT NULL	Nom DNS / NetBIOS du serveur
ip_address	INET	—	Adresse IP (type PostgreSQL natif)
role	VARCHAR(50)	NOT NULL	frontend | backend | batch | sql | report
sql_instance	VARCHAR(200)	—	Nom de l'instance SQL (ex: SERVEUR\SQL2016)
port_winrm	INTEGER	default 5986	Port WinRM

Table : users
Colonne	Type	Contrainte	Description
user_id	UUID	PK	Identifiant unique
username	VARCHAR(100)	NOT NULL, UNIQUE	Login applicatif
email	VARCHAR(200)	UNIQUE	Adresse email
hashed_password	VARCHAR(200)	—	Null si auth AD uniquement
ad_username	VARCHAR(150)	—	Login Active Directory associé
role	VARCHAR(20)	default 'technicien'	technicien | admin
is_active	BOOLEAN	default true	Compte actif
created_at	TIMESTAMP	NOT NULL	Date de création

Table : verifications
Colonne	Type	Contrainte	Description
verification_id	UUID	PK	Identifiant unique de la session
environment_id	UUID	FK → environments	Environnement audité
user_id	UUID	FK → users	Utilisateur ayant lancé la vérif
start_time	TIMESTAMP	NOT NULL	Début de la session
end_time	TIMESTAMP	—	Fin (null si en cours)
total_tests	INTEGER	default 0	Nombre total de contrôles
total_ok	INTEGER	default 0	Contrôles passés
total_ko	INTEGER	default 0	Contrôles en erreur
overall_status	VARCHAR(20)	—	pending | running | success | failed

Tables : modules, controls, verification_modules, control_results
Ces tables reprennent le schéma existant avec les améliorations suivantes :
•	modules : ajouter un champ execution_order (INTEGER) pour garantir que CentralParam est toujours exécuté en premier, et un champ is_required (BOOLEAN).
•	controls : ajouter control_key (VARCHAR, unique par module) pour référencer les contrôles par code dans le code, description (TEXT) et expected_value (TEXT) pour documenter la valeur attendue.
•	control_results : ajouter actual_value (TEXT) pour stocker la valeur observée (ex: version CRM détectée), et duration_ms (INTEGER) pour la durée d'exécution du contrôle.
•	verification_configurations : snapshot JSON des paramètres CentralParam au moment de la vérification. Ajouter un champ params_json (JSONB) pour stocker l'intégralité du snapshot de façon interrogeable.

7.3 Justifications des choix
•	UUID comme clé primaire : évite les collisions lors de synchronisation ou d'import entre environnements, plus sûr que les INTEGER auto-incrémentés exposés en API.
•	PostgreSQL : support natif JSONB (params_json), INET (ip_address), UUID (gen_random_uuid()), performances en lecture sur grands volumes de résultats.
•	Pas de stockage de credentials : les mots de passe SQL/Windows ne sont jamais persistés. Ils transitent uniquement en mémoire pendant l'exécution des contrôles.
•	JSONB pour params_json : permet d'interroger le snapshot CentralParam avec des opérateurs JSON natifs PostgreSQL sans désérialisation applicative.
•	Champ execution_order sur modules : garantit contractuellement que le module CentralParam (order=1) est toujours exécuté avant les autres.

8. Implémentation des Fonctionnalités
8.1 Flux d'exécution global d'une vérification
1.	Le frontend soumet l'URL CentralParam + credentials via POST /verifications/start.
2.	Le backend crée un enregistrement Verification (status=running) et retourne le verification_id.
3.	Le module CentralParam est exécuté en premier (execution_order=1) : récupération et validation de tous les paramètres, snapshot enregistré dans VerificationConfigurations.
4.	Les autres modules sont ensuite exécutés en parallèle (asyncio.gather) ou séquentiellement selon la configuration, en utilisant les valeurs issues du snapshot CentralParam.
5.	Chaque contrôle écrit son résultat dans ControlResults (status, message, actual_value, duration_ms).
6.	À la fin, la Verification est mise à jour (end_time, total_ok, total_ko, overall_status).
7.	Le frontend peut interroger GET /verifications/{id} pour afficher les résultats en temps réel (polling ou WebSocket).

8.2 Endpoints API principaux
Méthode	Endpoint	Description	Body / Params
POST	/auth/login	Authentification (local ou AD)	username, password
GET	/environments	Liste des environnements	—
POST	/environments	Créer un environnement	name, central_param_url, servers[]
GET	/environments/{id}	Détail d'un environnement	—
POST	/verifications/start	Lancer une vérification	environment_id, username, password, modules[]
GET	/verifications/{id}	Résultats d'une vérification	—
GET	/verifications	Historique des vérifications	?environment_id, ?limit
GET	/verifications/{id}/export	Exporter le rapport (PDF/Excel)	?format=pdf|excel
POST	/central-param/validate	Valider une URL CentralParam	url
POST	/central-param/parameters	Récupérer tous les paramètres	url, username, password
POST	/crm/check	Vérifier la disponibilité du CRM	crm_url, username, password
POST	/crm/resource	Analyser gs2e_FonctionsGenerales	instance_sql, database, username, password, lien_crm, serveur_batch
POST	/batch/services	Lister les services SAPHIRV3	server, username, password
POST	/batch/services/config	Vérifier config CentralParam des services	server, username, password, central_param_url
POST	/sql/organization-id	Vérifier OrganizationID	instance_sql, database, username, password
POST	/sql/triggers	Vérifier les triggers	instance_sql, database, username, password
POST	/sql/fragmentation	Vérifier fragmentation des index	instance_sql, database, username, password
POST	/sql/missing-indexes	Index manquants	instance_sql, database, username, password
POST	/ssrs/check	Disponibilité SSRS	ssrs_url, username, password
POST	/infra/availability	Ping et port 5986	servers[]
POST	/infra/os-info	Informations OS via WMI	servers[], username, password
POST	/auth/ad/verify	Vérifier compte AD	username, password
POST	/auth/ad/privusergroup	Vérifier appartenance PrivUserGroup	username, password, domain

8.3 Gestion asynchrone des vérifications
Certains contrôles impliquent des appels réseau longs (WMI, PowerShell, SQL). La stratégie recommandée est la suivante :
•	Utiliser FastAPI avec async/await pour les endpoints déclencheurs.
•	Exécuter les contrôles bloquants (WMI, subprocess PowerShell) dans un ThreadPoolExecutor via asyncio.run_in_executor pour ne pas bloquer la boucle d'événements.
•	Pour les vérifications longues, retourner immédiatement le verification_id et utiliser un endpoint de polling GET /verifications/{id} ou un WebSocket /ws/verifications/{id} pour le suivi en temps réel.
•	Limiter la concurrence sur les appels WMI avec un asyncio.Semaphore pour éviter la saturation des ressources Windows.

9. Sécurité et Intégration Active Directory
9.1 Authentification
•	Option 1 — Authentification locale (JWT) : l'utilisateur s'authentifie avec un login/mot de passe stocké en base (haché bcrypt). Le backend retourne un token JWT (HS256, expiration 8h). Recommandé pour les environnements sans AD accessible depuis le serveur backend.
•	Option 2 — Authentification AD via LDAP/NTLM (recommandé) : l'utilisateur fournit ses credentials Windows. Le backend vérifie via ldap3 + NTLM que le compte existe et appartient au groupe autorisé (ex: GRP_SaphirV3_Admins). Aucun mot de passe n'est stocké en base.
•	Option 3 — Hybride : tentative AD en premier, fallback sur compte local si AD inaccessible.

Hypothèse : le groupe AD GRP_SaphirV3_Admins n'existe peut-être pas encore. Deux options : créer ce groupe et l'utiliser comme filtre, ou simplement vérifier que le compte peut s'authentifier sur le domaine (bind LDAP réussi).

9.2 Autorisation
Rôle	Droits
technicien	Lancer des vérifications, consulter les résultats, exporter les rapports
admin	Tout ce que le technicien peut faire + gérer les environnements, les utilisateurs, consulter tous les historiques

9.3 Bonnes pratiques de sécurité
•	Ne jamais stocker les credentials SQL/Windows : ils transitent uniquement en mémoire pendant la vérification.
•	Utiliser HTTPS en production (certificat TLS sur le serveur d'hébergement).
•	Valider toutes les entrées avec les schémas Pydantic (types, longueurs, formats URL).
•	Ajouter une liste blanche d'adresses IP autorisées si le backend est exposé sur le réseau.
•	Logger les actions sensibles (lancement de vérification, export, modification d'environnement) avec user_id et timestamp.
•	Utiliser des variables d'environnement (.env) pour toutes les valeurs sensibles (SECRET_KEY, DATABASE_URL) — jamais dans le code source.
•	Ajouter un rate limiting sur les endpoints d'authentification (ex: slowapi pour FastAPI).

10. Bonnes Pratiques et Standards de Développement
10.1 Backend
•	Utiliser Pydantic BaseModel pour tous les schémas d'entrée/sortie API — validation automatique + documentation OpenAPI.
•	Séparer strictement routers (HTTP), services (logique métier) et repositories (accès DB) : un changement d'ORM ne doit pas impacter les services.
•	Toujours gérer les exceptions métier avec des HTTPException FastAPI typées (status_code, detail structuré en JSON).
•	Centraliser les timeouts (PS_TIMEOUT, SQL_TIMEOUT) dans la configuration Pydantic — jamais hardcodés dans les services.
•	Écrire des tests unitaires pour chaque service avec pytest + unittest.mock pour mocker WMI, pyodbc et subprocess.
•	Utiliser Alembic pour toutes les migrations de schéma — ne jamais modifier la base manuellement.

10.2 Frontend
•	Utiliser l'API Composition de Vue.js 3 (setup(), ref, computed, watch) pour toutes les nouvelles pages.
•	Centraliser les appels API dans un dossier services/ (ex: verificationService.js, environmentService.js) — ne jamais appeler axios directement depuis les composants.
•	Stocker VITE_API_BASE_URL dans .env.development et .env.production — jamais en dur dans le code.
•	Gérer les états de chargement, d'erreur et de succès de façon systématique dans chaque composant.
•	Utiliser Vue Router pour la navigation et Pinia (ou Vuex 4) pour l'état global (utilisateur connecté, environnement sélectionné).

10.3 Gestion de la configuration
Variable .env	Type	Description
DATABASE_URL	str	URL PostgreSQL (postgresql+asyncpg://user:pass@host/db)
SECRET_KEY	str	Clé JWT — générer avec secrets.token_hex(32)
FLASK_ENV / ENV	str	development | production
AD_SERVER	str	ldap://serveur-ad:389
AD_DOMAIN	str	Domaine Windows (ex: univers)
AD_AUTH_GROUP	str	Groupe AD requis pour se connecter (optionnel)
CRM_SSL_VERIFY	bool	False en dev (certif auto-signé), True en prod
SQL_EXCLUDED_CATALOGS	str	Catalogues à exclure (dbo,master,model,msdb,tempdb)
PS_TIMEOUT	int	Timeout PowerShell distant en secondes (défaut: 30)
SQL_TIMEOUT	int	Timeout connexion SQL en secondes (défaut: 10)
CORS_ORIGINS	str	URL(s) autorisées par CORS (ex: http://localhost:5173)

11. Améliorations par Rapport à l'Existant
Problème identifié	Impact	Solution proposée
Flask monolithique (Old/run.py) — tout dans un seul fichier	Maintenabilité nulle, impossible à tester	Migration vers architecture modulaire FastAPI : routers / services / schemas
Pas de configuration externalisée (.env absent)	Valeurs hardcodées (domaine AD, catalogues, clé secrète)	python-dotenv + pydantic-settings — toutes les valeurs sensibles dans .env
Bug boucle batch_controller.py — résultats écrasés	Résultats de vérification incorrects	Correction de la logique d'itération + tests unitaires
Credentials SQL/Windows hardcodés dans Old/run.py	Faille de sécurité critique	Suppression, passage en paramètre de requête uniquement, jamais persistés
Pas de gestion d'erreurs globale	Exceptions Python non catchées retournées en HTML	Gestionnaire d'erreurs FastAPI + middleware exception handler
Pas de timeout sur PowerShell / SQL	Appels bloquants indéfinis	PS_TIMEOUT et SQL_TIMEOUT configurables via .env
Signature incohérente de executer_sql_instance	Bugs silencieux (mauvais ordre paramètres)	Signature normalisée : (instance, username, password, query, database)
Pas d'historique des vérifications	Pas de traçabilité	Tables Verifications + ControlResults + VerificationConfigurations
Pas de documentation API	Intégration frontend difficile	OpenAPI / Swagger natif FastAPI sur /docs
Frontend sans URL d'API définie	Dépendance à l'URL localhost hardcodée	VITE_API_BASE_URL dans .env.development / .env.production

12. Livrables et Plan de Développement Suggéré
Phase	Durée estimée	Livrables
Phase 1 — Fondations	2 semaines	Migration config .env, correction bug batch, endpoint port WinRM, structure FastAPI, modèles DB + migrations Alembic, authentification JWT/AD
Phase 2 — CRM & Auth	2 semaines	Module CRM complet (disponibilité, version, gs2e_FonctionsGenerales), module Auth AD (PrivUserGroup), endpoints REST documentés
Phase 3 — SQL & Batch	2 semaines	Triggers, fragmentation, index manquants, OrganizationID, services SAPHIRV3 corrigés, fichier critères, CentralParamConfig
Phase 4 — Infra & SSRS	1-2 semaines	IIS, Web Deploy, SSRS (disponibilité, sources de données, clé de chiffrement, chaînes de connexion)
Phase 5 — Historique & Export	1 semaine	Stockage des résultats en base, consultation de l'historique, export PDF/Excel
Phase 6 — Frontend & Tests	2 semaines	Composants Vue.js pour tous les nouveaux modules, tests pytest, documentation Swagger complète


— Fin du document —
