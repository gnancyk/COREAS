-- Schéma de base de données COREAS pour SQL Server (Version Française)

-- 1. Categorie
CREATE TABLE Categorie (
    categorie_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    nom NVARCHAR(255) NOT NULL UNIQUE
);

-- 2. Role
CREATE TABLE Role (
    role_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    nom NVARCHAR(255) NOT NULL UNIQUE
);

-- 3. Utilisateur
CREATE TABLE Utilisateur (
    utilisateur_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    nom_utilisateur NVARCHAR(255) NOT NULL UNIQUE,
    nom_complet NVARCHAR(255),
    email NVARCHAR(255) NOT NULL UNIQUE
);

-- 4. Module
CREATE TABLE Module (
    module_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    code NVARCHAR(50) NOT NULL UNIQUE,
    nom NVARCHAR(255),
    est_requis BIT DEFAULT 1
);

-- 5. Environnement
CREATE TABLE Environnement (
    environnement_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    nom NVARCHAR(255) NOT NULL UNIQUE,
    url_central_param NVARCHAR(MAX),
    categorie_id UNIQUEIDENTIFIER NOT NULL,
    est_actif BIT DEFAULT 1,
    CONSTRAINT FK_Environnement_Categorie FOREIGN KEY (categorie_id) REFERENCES Categorie(categorie_id)
);

-- 6. Serveur
CREATE TABLE Serveur (
    serveur_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    nom_serveur NVARCHAR(255) NOT NULL,
    nom_hote NVARCHAR(255),
    adresse_ip NVARCHAR(50),
    role_id UNIQUEIDENTIFIER NOT NULL,
    environnement_id UNIQUEIDENTIFIER NOT NULL,
    port_winrm INT DEFAULT 5985,
    port INT,
    identifiant NVARCHAR(255),
    mot_de_passe NVARCHAR(MAX),
    CONSTRAINT FK_Serveur_Role FOREIGN KEY (role_id) REFERENCES Role(role_id),
    CONSTRAINT FK_Serveur_Environnement FOREIGN KEY (environnement_id) REFERENCES Environnement(environnement_id)
);

-- 7. Controle
CREATE TABLE Controle (
    controle_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    point_controle NVARCHAR(50) NOT NULL UNIQUE,
    description NVARCHAR(MAX),
    valeur_attendue NVARCHAR(MAX),
    chemin_endpoint NVARCHAR(MAX),
    delai_secondes INT DEFAULT 30,
    module_id UNIQUEIDENTIFIER NOT NULL,
    CONSTRAINT FK_Controle_Module FOREIGN KEY (module_id) REFERENCES Module(module_id)
);

-- 8. Verification
CREATE TABLE Verification (
    verification_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    environnement_id UNIQUEIDENTIFIER NOT NULL,
    utilisateur_id UNIQUEIDENTIFIER NOT NULL,
    date_debut DATETIME2 DEFAULT GETUTCDATE(),
    date_fin DATETIME2,
    statut_global NVARCHAR(50),
    total_tests INT DEFAULT 0,
    total_ok INT DEFAULT 0,
    total_ko INT DEFAULT 0,
    total_avertissements INT DEFAULT 0,
    CONSTRAINT FK_Verification_Environnement FOREIGN KEY (environnement_id) REFERENCES Environnement(environnement_id),
    CONSTRAINT FK_Verification_Utilisateur FOREIGN KEY (utilisateur_id) REFERENCES Utilisateur(utilisateur_id)
);

-- 9. CaptureConfig
CREATE TABLE CaptureConfig (
    capture_config_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    verification_id UNIQUEIDENTIFIER NOT NULL UNIQUE,
    params_json NVARCHAR(MAX),
    capture_le DATETIME2 DEFAULT GETUTCDATE(),
    CONSTRAINT FK_CaptureConfig_Verification FOREIGN KEY (verification_id) REFERENCES Verification(verification_id)
);

-- 10. VerificationModule
CREATE TABLE VerificationModule (
    verification_module_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    verification_id UNIQUEIDENTIFIER NOT NULL,
    module_id UNIQUEIDENTIFIER NOT NULL,
    statut NVARCHAR(50),
    total_tests INT DEFAULT 0,
    total_ok INT DEFAULT 0,
    total_ko INT DEFAULT 0,
    CONSTRAINT FK_VerificationModule_Verification FOREIGN KEY (verification_id) REFERENCES Verification(verification_id),
    CONSTRAINT FK_VerificationModule_Module FOREIGN KEY (module_id) REFERENCES Module(module_id)
);

-- 11. ResultatControle
CREATE TABLE ResultatControle (
    resultat_controle_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    verification_module_id UNIQUEIDENTIFIER NOT NULL,
    controle_id UNIQUEIDENTIFIER NOT NULL,
    serveur_id UNIQUEIDENTIFIER NOT NULL,
    statut NVARCHAR(50),
    valeur_observee NVARCHAR(MAX),
    valeur_attendue NVARCHAR(MAX),
    message_erreur NVARCHAR(MAX),
    details NVARCHAR(MAX),
    duree_ms INT,
    CONSTRAINT FK_ResultatControle_VerificationModule FOREIGN KEY (verification_module_id) REFERENCES VerificationModule(verification_module_id),
    CONSTRAINT FK_ResultatControle_Controle FOREIGN KEY (controle_id) REFERENCES Controle(controle_id),
    CONSTRAINT FK_ResultatControle_Serveur FOREIGN KEY (serveur_id) REFERENCES Serveur(serveur_id)
);

-- 12. ResultatServeur
CREATE TABLE ResultatServeur (
    resultat_serveur_id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    verification_id UNIQUEIDENTIFIER NOT NULL,
    serveur_id UNIQUEIDENTIFIER NOT NULL,
    statut NVARCHAR(50),
    details NVARCHAR(MAX),
    temps_reponse_ms INT,
    CONSTRAINT FK_ResultatServeur_Verification FOREIGN KEY (verification_id) REFERENCES Verification(verification_id),
    CONSTRAINT FK_ResultatServeur_Serveur FOREIGN KEY (serveur_id) REFERENCES Serveur(serveur_id)
);
