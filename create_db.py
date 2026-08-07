#!/usr/bin/env python3
"""
Script d'initialisation et de remplissage de la base de données SQLite CROUS-T (Site VCN)
Auteurs: Mame Awa Kare & Fallou Wade
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "crous_t.db")
SCHEMA_FILE = os.path.join(BASE_DIR, "schema.sql")

def init_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"[-] Ancienne base de données {DB_FILE} supprimée.")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Application du schéma DDL
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)
    print(f"[+] Schéma appliqué depuis {SCHEMA_FILE}.")

    # =========================================================================
    # INSERTION DES DONNÉES DE DEMONSTRATION
    # =========================================================================

    # 1. Insertion Utilisateurs & Rôles
    utilisateurs = [
        # Locataires (1-4)
        ("Diop", "Mame Diarra", "mame.diop@ugb.edu.sn", "+221771234567", "DEMANDEUR_LOCATAIRE"),
        ("Ndiaye", "Ousmane", "ousmane.ndiaye@gmail.com", "+221772345678", "DEMANDEUR_LOCATAIRE"),
        ("Sow", "Awa", "awa.sow@ugb.edu.sn", "+221773456789", "DEMANDEUR_LOCATAIRE"),
        ("Fall", "Moustapha", "moustapha.fall@gmail.com", "+221774567890", "DEMANDEUR_LOCATAIRE"),
        
        # Agents Administration (5-7)
        ("Kare", "Mame Awa", "mameawa.kare@crous-t.sn", "+221775678901", "AGENT_ADMINISTRATION"),
        ("Tall", "Maniang", "maniang.tall@crous-t.sn", "+221776789012", "AGENT_ADMINISTRATION"),
        ("Ba", "Ibrahima", "ibrahima.ba@crous-t.sn", "+221777890123", "AGENT_ADMINISTRATION"),
        
        # Techniciens (8-10)
        ("Sarr", "Modou", "modou.sarr@crous-t.sn", "+221778901234", "TECHNICIEN"),
        ("Faye", "Cheikh", "cheikh.faye@crous-t.sn", "+221779012345", "TECHNICIEN"),
        ("Gaye", "Babacar", "babacar.gaye@crous-t.sn", "+221770123456", "TECHNICIEN"),
    ]
    cursor.executemany("""
        INSERT INTO Utilisateur (nom, prenom, email, telephone, role) 
        VALUES (?, ?, ?, ?, ?)
    """, utilisateurs)

    # Tables filles d'Utilisateur
    demandeurs = [
        (1, "1758199500123", 1, "P1812345"),
        (2, "1758198800456", 0, None),
        (3, "2758200100789", 1, "P2019876"),
        (4, "1758199000321", 0, None)
    ]
    cursor.executemany("INSERT INTO DemandeurLocataire (idUtilisateur, cni, estEtudiant, numEtudiant) VALUES (?, ?, ?, ?)", demandeurs)

    agents = [
        (5, "DCUVE", "ADM-2024-001"),
        (6, "RECOUVREMENT", "ADM-2024-002"),
        (7, "QHSE", "ADM-2024-003")
    ]
    cursor.executemany("INSERT INTO AgentAdministration (idUtilisateur, service, matricule) VALUES (?, ?, ?)", agents)

    techniciens = [
        (8, "PLOMBERIE", 1),
        (9, "ELECTRICITE", 1),
        (10, "SECURITE", 0)
    ]
    cursor.executemany("INSERT INTO Technicien (idUtilisateur, specialite, disponibilite) VALUES (?, ?, ?)", techniciens)

    # 2. Locaux Commerciaux (VCN)
    locaux = [
        ("LOC-VCN-001", "PAPETERIE", 25.5, "OCCUPE"),
        ("LOC-VCN-002", "ELECTRONIQUE", 30.0, "OCCUPE"),
        ("LOC-VCN-003", "ALIMENTAIRE", 45.0, "OCCUPE"),
        ("LOC-VCN-004", "COSMETIQUE", 20.0, "DISPONIBLE"),
        ("LOC-VCN-005", "ALIMENTAIRE", 50.0, "EN_MAINTENANCE")
    ]
    cursor.executemany("INSERT INTO LocalCommercial (codeLocal, typeActivite, surfaceM2, statut) VALUES (?, ?, ?, ?)", locaux)

    # 3. Demandes & Pièces Justificatives
    demandes = [
        ("DEM-2026-001", 1, "OBTENTION", "Papeterie et Photocopie Universitaire", "2026-01-10 10:00:00", "FAVORABLE"),
        ("DEM-2026-002", 2, "OBTENTION", "Vente Matériel Électronique & Accessoires", "2026-01-15 11:30:00", "FAVORABLE"),
        ("DEM-2026-003", 3, "CONSTRUCTION", "Restauration Rapide & Cantine Alimentaire", "2026-02-01 09:15:00", "FAVORABLE"),
        ("DEM-2026-004", 4, "OBTENTION", "Boutique Produits Cosmétiques & Soins", "2026-02-10 14:00:00", "MITIGE")
    ]
    cursor.executemany("""
        INSERT INTO DemandeLocal (codeDemande, idDemandeur, typeDemande, natureActivite, dateDepot, statut)
        VALUES (?, ?, ?, ?, ?, ?)
    """, demandes)

    pieces = [
        (1, "CV", "/docs/dem_001/cv.pdf"),
        (1, "CNI", "/docs/dem_001/cni.pdf"),
        (1, "BUSINESS_PLAN", "/docs/dem_001/business_plan.pdf"),
        (2, "CV", "/docs/dem_002/cv.pdf"),
        (2, "BUSINESS_PLAN", "/docs/dem_002/business_plan.pdf"),
        (3, "CV", "/docs/dem_003/cv.pdf"),
        (3, "DEVIS", "/docs/dem_003/devis_plomberie.pdf"),
        (3, "MAQUETTE_3D", "/docs/dem_003/maquette3d.pdf"),
        (4, "CV", "/docs/dem_004/cv.pdf")
    ]
    cursor.executemany("INSERT INTO PieceJustificative (idDemande, typePiece, urlFichier) VALUES (?, ?, ?)", pieces)

    fiches_analyse = [
        (1, 5, "FAVORABLE", "Dossier complet, excellente viabilité du projet pour la rentrée universitaire.", None),
        (2, 5, "FAVORABLE", "Projet conforme aux besoins des étudiants du site VCN.", None),
        (3, 5, "FAVORABLE", "Projet validé sous réserve du respect des normes d'hygiène et de cuisine.", None),
        (4, 5, "MITIGE", "Pièces justificatives manquantes : devis d'aménagement à fournir.", "Fournir un devis estimatif complet sous 15 jours.")
    ]
    cursor.executemany("""
        INSERT INTO FicheAnalyse (idDemande, idAgent, avis, commentaires, justificatifsDemandes)
        VALUES (?, ?, ?, ?, ?)
    """, fiches_analyse)

    # 4. Contrats
    contrats = [
        ("CTR-2026-001", 1, 1, 1, 45000.0, "2026-01-20 10:00:00", 1, 1, "ACTIF"),
        ("CTR-2026-002", 2, 2, 2, 60000.0, "2026-01-25 15:30:00", 1, 1, "ACTIF"),
        ("CTR-2026-003", 3, 3, 3, 75000.0, "2026-02-05 12:00:00", 1, 1, "ACTIF")
    ]
    cursor.executemany("""
        INSERT INTO Contrat (numContrat, idDemande, idDemandeur, idLocal, montantLoyerMensuel, dateSignature, valideParDirecteur, valideParDemandeur, statut)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, contrats)

    # 5. Paiements & Quittances
    paiements = [
        (1, 45000.0, "2026-02-04 10:00:00", "ESPECES", "VALIDE"),
        (1, 45000.0, "2026-03-03 11:00:00", "ESPECES", "VALIDE"),
        (2, 60000.0, "2026-02-05 14:00:00", "ESPECES", "VALIDE"),
        (2, 60000.0, "2026-03-04 16:00:00", "MOBILE_MONEY", "VALIDE"),
        (3, 75000.0, "2026-02-08 09:30:00", "ESPECES", "VALIDE")  # Retard au-delà du 5 !
    ]
    cursor.executemany("""
        INSERT INTO Paiement (idContrat, montant, datePaiement, modePaiement, statutPaiement)
        VALUES (?, ?, ?, ?, ?)
    """, paiements)

    quittances = [
        (1, "QUIT-2026-001", "2026-02-04 10:05:00", "/quittances/quit_001.pdf"),
        (2, "QUIT-2026-002", "2026-03-03 11:05:00", "/quittances/quit_002.pdf"),
        (3, "QUIT-2026-003", "2026-02-05 14:10:00", "/quittances/quit_003.pdf"),
        (4, "QUIT-2026-004", "2026-03-04 16:05:00", "/quittances/quit_004.pdf"),
        (5, "QUIT-2026-005", "2026-02-08 09:35:00", "/quittances/quit_005.pdf")
    ]
    cursor.executemany("""
        INSERT INTO Quittance (idPaiement, numQuittance, dateEmission, urlPdf)
        VALUES (?, ?, ?, ?)
    """, quittances)

    # 6. Incidents Techniques (avec simulation d'un retard > 3 jours)
    incidents = [
        (3, "PLOMBERIE", "Fuite d'eau importante au niveau de l'évier principal de la cantine.", "2026-08-01 08:00:00", 8, 5, "EN_COURS"), # >3 jours!
        (2, "ELECTRICITE", "Disjoncteur général saute régulièrement, câbles des caméras endommagés.", "2026-08-06 14:00:00", 9, 1, "TRANSMIS"),
        (1, "SECURITE", "Serrure de la porte principale bloquée.", "2026-08-05 10:00:00", 10, 1, "RESOLU")
    ]
    cursor.executemany("""
        INSERT INTO IncidentTechnique (idLocal, typeProbleme, description, dateSignalement, idTechnicien, delaiInterventionJours, statut)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, incidents)

    # 7. Fiches QHSE
    fiches_qhse = [
        (1, 7, "2026-08-01 09:00:00", 1, 0, "Local très propre et ordonné."),
        (3, 7, "2026-08-01 10:00:00", 0, 0, "Taches noires sur les murs, absence de gants en cuisine."),
        (3, 7, "2026-08-07 10:00:00", 0, 1, "Récidive : les gants ne sont toujours pas portés et fuite non réparée.")
    ]
    cursor.executemany("""
        INSERT INTO FicheQHSE (idLocal, idAgent, dateControle, estConforme, estRecidive, observations)
        VALUES (?, ?, ?, ?, ?, ?)
    """, fiches_qhse)

    # 8. Produits & Catalogues
    produits = [
        (1, "Rames de Papier A4 (500 feuilles)", 2500.0, 1),
        (1, "Stylos à bille (Carton)", 1500.0, 1),
        (1, "Cahiers 200 pages", 600.0, 1),
        (2, "Clé USB 64Go SanDisk", 4500.0, 1),
        (2, "Souris sans fil Logitech", 6000.0, 1),
        (2, "Chargeur Universel PC", 12000.0, 1),
        (3, "Plat du jour (Riz au Poisson - Thiéboudienne)", 1000.0, 1),
        (3, "Sandwich Viande Hachée", 800.0, 1),
        (3, "Jus Naturel Bissap / Bouye", 300.0, 1)
    ]
    cursor.executemany("INSERT INTO Produit (idLocal, nom, prix, disponible) VALUES (?, ?, ?, ?)", produits)

    # 9. Avis Étudiants
    avis = [
        (1, 1, 5, "Très bonne papeterie, toujours bien approvisionnée pour la rentrée !", "2026-02-15 10:00:00"),
        (2, 3, 4, "Service de matériel électronique pratique sur place.", "2026-02-18 16:30:00"),
        (3, 1, 3, "Le repas est bon mais l'hygiène de la cuisine doit être améliorée.", "2026-08-02 12:00:00")
    ]
    cursor.executemany("INSERT INTO AvisEtudiant (idLocal, idUtilisateur, note, commentaire, dateAvis) VALUES (?, ?, ?, ?, ?)", avis)

    conn.commit()
    conn.close()
    print("[+] Données de démonstration insérées avec succès dans crous_t.db !")

if __name__ == "__main__":
    init_database()
