-- ============================================================================
-- BASE DE DONNÉES CROUS-T / SITE VCN - SCHÉMA SQLITE
-- Conception : Mame Awa Kare & Fallou Wade
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. TABLE MÈRE : Utilisateur (Abstract Base Class)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Utilisateur (
    idUtilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    telephone TEXT,
    role TEXT NOT NULL CHECK(role IN ('DEMANDEUR_LOCATAIRE', 'AGENT_ADMINISTRATION', 'TECHNICIEN')),
    dateCreation DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 2. TABLES FILLES (Héritage Class Table Inheritance)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DemandeurLocataire (
    idUtilisateur INTEGER PRIMARY KEY REFERENCES Utilisateur(idUtilisateur) ON DELETE CASCADE,
    cni TEXT NOT NULL,
    estEtudiant BOOLEAN NOT NULL DEFAULT 0 CHECK(estEtudiant IN (0, 1)),
    numEtudiant TEXT
);

CREATE TABLE IF NOT EXISTS AgentAdministration (
    idUtilisateur INTEGER PRIMARY KEY REFERENCES Utilisateur(idUtilisateur) ON DELETE CASCADE,
    service TEXT NOT NULL CHECK(service IN ('DCUVE', 'RECOUVREMENT', 'JURIDIQUE', 'QHSE', 'COURRIER', 'CABINET_DIRECTEUR')),
    matricule TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Technicien (
    idUtilisateur INTEGER PRIMARY KEY REFERENCES Utilisateur(idUtilisateur) ON DELETE CASCADE,
    specialite TEXT NOT NULL CHECK(specialite IN ('PLOMBERIE', 'ELECTRICITE', 'SECURITE', 'AUTRE')),
    disponibilite BOOLEAN NOT NULL DEFAULT 1 CHECK(disponibilite IN (0, 1))
);

-- ----------------------------------------------------------------------------
-- 3. GESTION DES LOCAUX COMMERCIAUX
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS LocalCommercial (
    idLocal INTEGER PRIMARY KEY AUTOINCREMENT,
    codeLocal TEXT UNIQUE NOT NULL,
    typeActivite TEXT NOT NULL CHECK(typeActivite IN ('ALIMENTAIRE', 'PAPETERIE', 'ELECTRONIQUE', 'COSMETIQUE', 'AUTRE')),
    surfaceM2 REAL NOT NULL CHECK(surfaceM2 > 0),
    statut TEXT NOT NULL DEFAULT 'DISPONIBLE' CHECK(statut IN ('DISPONIBLE', 'OCCUPE', 'EN_MAINTENANCE'))
);

-- ----------------------------------------------------------------------------
-- 4. DEMANDES & PIÈCES JUSTIFICATIVES
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS DemandeLocal (
    idDemande INTEGER PRIMARY KEY AUTOINCREMENT,
    codeDemande TEXT UNIQUE NOT NULL,
    idDemandeur INTEGER NOT NULL REFERENCES DemandeurLocataire(idUtilisateur) ON DELETE RESTRICT,
    typeDemande TEXT NOT NULL CHECK(typeDemande IN ('OBTENTION', 'CONSTRUCTION')),
    natureActivite TEXT NOT NULL,
    dateDepot DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    statut TEXT NOT NULL DEFAULT 'EN_ATTENTE' CHECK(statut IN ('EN_ATTENTE', 'FAVORABLE', 'MITIGE', 'DEFAVORABLE'))
);

CREATE TABLE IF NOT EXISTS PieceJustificative (
    idPiece INTEGER PRIMARY KEY AUTOINCREMENT,
    idDemande INTEGER NOT NULL REFERENCES DemandeLocal(idDemande) ON DELETE CASCADE,
    typePiece TEXT NOT NULL CHECK(typePiece IN ('CV', 'CNI', 'BUSINESS_PLAN', 'DEVIS', 'MAQUETTE_3D', 'CERTIFICAT_APTITUDE', 'CERTIFICAT_MEDICAL', 'FICHIER_PRIX', 'AUTRE')),
    urlFichier TEXT NOT NULL,
    dateDepot DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS FicheAnalyse (
    idFiche INTEGER PRIMARY KEY AUTOINCREMENT,
    idDemande INTEGER UNIQUE NOT NULL REFERENCES DemandeLocal(idDemande) ON DELETE CASCADE,
    idAgent INTEGER NOT NULL REFERENCES AgentAdministration(idUtilisateur) ON DELETE RESTRICT,
    avis TEXT NOT NULL CHECK(avis IN ('FAVORABLE', 'MITIGE', 'DEFAVORABLE')),
    commentaires TEXT,
    justificatifsDemandes TEXT,
    dateAnalyse DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- 5. CONTRATS & FINANCES
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Contrat (
    idContrat INTEGER PRIMARY KEY AUTOINCREMENT,
    numContrat TEXT UNIQUE NOT NULL,
    idDemande INTEGER UNIQUE REFERENCES DemandeLocal(idDemande) ON DELETE SET NULL,
    idDemandeur INTEGER NOT NULL REFERENCES DemandeurLocataire(idUtilisateur) ON DELETE RESTRICT,
    idLocal INTEGER NOT NULL REFERENCES LocalCommercial(idLocal) ON DELETE RESTRICT,
    montantLoyerMensuel REAL NOT NULL CHECK(montantLoyerMensuel >= 0),
    dateSignature DATETIME,
    valideParDirecteur BOOLEAN NOT NULL DEFAULT 0 CHECK(valideParDirecteur IN (0, 1)),
    valideParDemandeur BOOLEAN NOT NULL DEFAULT 0 CHECK(valideParDemandeur IN (0, 1)),
    statut TEXT NOT NULL DEFAULT 'ACTIF' CHECK(statut IN ('ACTIF', 'RESILIE', 'SUSPENDU'))
);

CREATE TABLE IF NOT EXISTS Paiement (
    idPaiement INTEGER PRIMARY KEY AUTOINCREMENT,
    idContrat INTEGER NOT NULL REFERENCES Contrat(idContrat) ON DELETE RESTRICT,
    montant REAL NOT NULL CHECK(montant > 0),
    datePaiement DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modePaiement TEXT NOT NULL CHECK(modePaiement IN ('ESPECES', 'MOBILE_MONEY', 'EN_LIGNE')),
    statutPaiement TEXT NOT NULL DEFAULT 'VALIDE' CHECK(statutPaiement IN ('EN_ATTENTE', 'VALIDE', 'REJETE'))
);

CREATE TABLE IF NOT EXISTS Quittance (
    idQuittance INTEGER PRIMARY KEY AUTOINCREMENT,
    idPaiement INTEGER UNIQUE NOT NULL REFERENCES Paiement(idPaiement) ON DELETE CASCADE,
    numQuittance TEXT UNIQUE NOT NULL,
    dateEmission DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    urlPdf TEXT
);

-- ----------------------------------------------------------------------------
-- 6. INCIDENTS TECHNIQUES & SUIVI DE MAINTENANCE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS IncidentTechnique (
    idIncident INTEGER PRIMARY KEY AUTOINCREMENT,
    idLocal INTEGER NOT NULL REFERENCES LocalCommercial(idLocal) ON DELETE CASCADE,
    typeProbleme TEXT NOT NULL CHECK(typeProbleme IN ('PLOMBERIE', 'ELECTRICITE', 'SECURITE', 'AUTRE')),
    description TEXT NOT NULL,
    dateSignalement DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    idTechnicien INTEGER REFERENCES Technicien(idUtilisateur) ON DELETE SET NULL,
    delaiInterventionJours INTEGER DEFAULT 0,
    statut TEXT NOT NULL DEFAULT 'SIGNALE' CHECK(statut IN ('SIGNALE', 'TRANSMIS', 'EN_COURS', 'RESOLU'))
);

-- ----------------------------------------------------------------------------
-- 7. CONTRÔLE QHSE (HYGIÈNE & SÉCURITÉ)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS FicheQHSE (
    idFicheQHSE INTEGER PRIMARY KEY AUTOINCREMENT,
    idLocal INTEGER NOT NULL REFERENCES LocalCommercial(idLocal) ON DELETE CASCADE,
    idAgent INTEGER NOT NULL REFERENCES AgentAdministration(idUtilisateur) ON DELETE RESTRICT,
    dateControle DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estConforme BOOLEAN NOT NULL DEFAULT 1 CHECK(estConforme IN (0, 1)),
    estRecidive BOOLEAN NOT NULL DEFAULT 0 CHECK(estRecidive IN (0, 1)),
    observations TEXT
);

-- ----------------------------------------------------------------------------
-- 8. PRODUITS & AVIS ÉTUDIANTS
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Produit (
    idProduit INTEGER PRIMARY KEY AUTOINCREMENT,
    idLocal INTEGER NOT NULL REFERENCES LocalCommercial(idLocal) ON DELETE CASCADE,
    nom TEXT NOT NULL,
    prix REAL NOT NULL CHECK(prix >= 0),
    disponible BOOLEAN NOT NULL DEFAULT 1 CHECK(disponible IN (0, 1))
);

CREATE TABLE IF NOT EXISTS AvisEtudiant (
    idAvis INTEGER PRIMARY KEY AUTOINCREMENT,
    idLocal INTEGER NOT NULL REFERENCES LocalCommercial(idLocal) ON DELETE CASCADE,
    idUtilisateur INTEGER REFERENCES Utilisateur(idUtilisateur) ON DELETE SET NULL,
    note INTEGER NOT NULL CHECK(note BETWEEN 1 AND 5),
    commentaire TEXT,
    dateAvis DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------------------------
-- INDEX D'OPTIMISATION DE PERFORMANCE
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_demande_demandeur ON DemandeLocal(idDemandeur);
CREATE INDEX IF NOT EXISTS idx_demande_statut ON DemandeLocal(statut);
CREATE INDEX IF NOT EXISTS idx_contrat_local ON Contrat(idLocal);
CREATE INDEX IF NOT EXISTS idx_contrat_demandeur ON Contrat(idDemandeur);
CREATE INDEX IF NOT EXISTS idx_paiement_contrat ON Paiement(idContrat);
CREATE INDEX IF NOT EXISTS idx_incident_local ON IncidentTechnique(idLocal);
CREATE INDEX IF NOT EXISTS idx_incident_statut ON IncidentTechnique(statut);
CREATE INDEX IF NOT EXISTS idx_qhse_local ON FicheQHSE(idLocal);
CREATE INDEX IF NOT EXISTS idx_produit_local ON Produit(idLocal);

-- ----------------------------------------------------------------------------
-- VUES MÉTIERS RÉCAPITULATIVES
-- ----------------------------------------------------------------------------

-- Vue des demandes complètes avec infos demandeur et avis d'analyse
CREATE VIEW IF NOT EXISTS v_demandes_completes AS
SELECT 
    d.idDemande,
    d.codeDemande,
    u.nom || ' ' || u.prenom AS nomDemandeur,
    u.email,
    dl.cni,
    dl.estEtudiant,
    d.typeDemande,
    d.natureActivite,
    d.dateDepot,
    d.statut AS statutDemande,
    fa.avis AS avisDCUVE,
    fa.commentaires AS commentairesDCUVE
FROM DemandeLocal d
JOIN DemandeurLocataire dl ON d.idDemandeur = dl.idUtilisateur
JOIN Utilisateur u ON dl.idUtilisateur = u.idUtilisateur
LEFT JOIN FicheAnalyse fa ON d.idDemande = fa.idDemande;

-- Vue des incidents techniques avec suivi d'alerte > 3 jours
CREATE VIEW IF NOT EXISTS v_incidents_alertes AS
SELECT 
    i.idIncident,
    l.codeLocal,
    l.typeActivite,
    i.typeProbleme,
    i.description,
    i.dateSignalement,
    i.statut,
    u.nom || ' ' || u.prenom AS nomTechnicien,
    t.specialite,
    CAST((julianday('now') - julianday(i.dateSignalement)) AS INTEGER) AS joursEcoules,
    CASE 
        WHEN i.statut != 'RESOLU' AND (julianday('now') - julianday(i.dateSignalement)) > 3 THEN 1
        WHEN i.delaiInterventionJours > 3 THEN 1
        ELSE 0
    END AS alerteRetard3Jours
FROM IncidentTechnique i
JOIN LocalCommercial l ON i.idLocal = l.idLocal
LEFT JOIN Technicien t ON i.idTechnicien = t.idUtilisateur
LEFT JOIN Utilisateur u ON t.idUtilisateur = u.idUtilisateur;

-- Vue de synthèse financière et quittances
CREATE VIEW IF NOT EXISTS v_synthese_recouvrement AS
SELECT 
    p.idPaiement,
    q.numQuittance,
    c.numContrat,
    l.codeLocal,
    u.nom || ' ' || u.prenom AS locataire,
    p.montant,
    p.modePaiement,
    p.datePaiement,
    c.montantLoyerMensuel
FROM Paiement p
JOIN Contrat c ON p.idContrat = c.idContrat
JOIN LocalCommercial l ON c.idLocal = l.idLocal
JOIN DemandeurLocataire dl ON c.idDemandeur = dl.idUtilisateur
JOIN Utilisateur u ON dl.idUtilisateur = u.idUtilisateur
LEFT JOIN Quittance q ON p.idPaiement = q.idPaiement;
