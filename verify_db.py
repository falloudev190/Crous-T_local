#!/usr/bin/env python3
"""
Script de vérification et de requêtes de démonstration de la BD CROUS-T / VCN
Auteurs: Mame Awa Kare & Fallou Wade
"""

import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "crous_t.db")

def print_table(title, columns, rows):
    print(f"\n{'='*80}\n {title}\n{'='*80}")
    if not rows:
        print("  Aucun enregistrement trouvé.")
        return
    
    col_widths = [max(len(str(col)), max(len(str(row[i] if row[i] is not None else '')) for row in rows)) for i, col in enumerate(columns)]
    col_widths = [min(w, 40) for w in col_widths]  # Troncature d'affichage si trop large

    header = " | ".join(f"{col:<{col_widths[i]}}" for i, col in enumerate(columns))
    print(header)
    print("-" * len(header))
    
    for row in rows:
        formatted_row = []
        for i, val in enumerate(row):
            str_val = str(val) if val is not None else "NULL"
            if len(str_val) > col_widths[i]:
                str_val = str_val[:col_widths[i]-3] + "..."
            formatted_row.append(f"{str_val:<{col_widths[i]}}")
        print(" | ".join(formatted_row))

def run_verifications():
    if not os.path.exists(DB_FILE):
        print(f"[!] Erreur: La base de données {DB_FILE} n'existe pas.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Vérification du décompte des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"[+] Nombre total de tables créées: {len(tables)}")
    for t in sorted(tables):
        cursor.execute(f"SELECT COUNT(*) FROM {t};")
        count = cursor.fetchone()[0]
        print(f"    - {t:<22} : {count} enregistrements")

    # 2. Requete 1 : Vue des Demandes complètes (DCUVE)
    cursor.execute("SELECT codeDemande, nomDemandeur, typeDemande, natureActivite, statutDemande, avisDCUVE FROM v_demandes_completes;")
    cols = ["Code Demande", "Demandeur", "Type", "Activité Projetée", "Statut", "Avis DCUVE"]
    print_table("1. SUIVI DES DEMANDES D'ATTRIBUTION & AVIS DCUVE", cols, cursor.fetchall())

    # 3. Requete 2 : Contrats et Synthèse Financière / Quittances
    cursor.execute("SELECT numContrat, codeLocal, locataire, montant, modePaiement, datePaiement, numQuittance FROM v_synthese_recouvrement;")
    cols = ["Num Contrat", "Local", "Locataire", "Montant Versé", "Mode Paiement", "Date Paiement", "Quittance PDF"]
    print_table("2. ENREGISTREMENT ET SUIVI DES PAIEMENTS & QUITTANCES", cols, cursor.fetchall())

    # 4. Requete 3 : Incidents Techniques & Alerte de Dépassement > 3 jours
    cursor.execute("SELECT codeLocal, typeProbleme, description, dateSignalement, statut, nomTechnicien, alerteRetard3Jours FROM v_incidents_alertes;")
    cols = ["Local", "Type Pannes", "Description", "Signalé Le", "Statut", "Technicien", "Alerte >3 Jours"]
    print_table("3. INCIDENTS TECHNIQUES & CONTRÔLE DU DÉLAI DE 3 JOURS", cols, cursor.fetchall())

    # 5. Requete 4 : Contrôles QHSE (Hygiène & Sécurité)
    cursor.execute("""
        SELECT l.codeLocal, u.nom || ' ' || u.prenom AS agentQHSE, f.dateControle, 
               f.estConforme, f.estRecidive, f.observations
        FROM FicheQHSE f
        JOIN LocalCommercial l ON f.idLocal = l.idLocal
        JOIN AgentAdministration a ON f.idAgent = a.idUtilisateur
        JOIN Utilisateur u ON a.idUtilisateur = u.idUtilisateur;
    """)
    cols = ["Local", "Agent QHSE", "Date Contrôle", "Conforme", "Récidive", "Observations"]
    print_table("4. FICHIERS DE CONTRÔLE ET D'INSPECTION QHSE", cols, cursor.fetchall())

    # 6. Requete 5 : Produits et Avis des Étudiants
    cursor.execute("""
        SELECT l.codeLocal, l.typeActivite, a.note || '/5' AS note, a.commentaire, a.dateAvis
        FROM AvisEtudiant a
        JOIN LocalCommercial l ON a.idLocal = l.idLocal;
    """)
    cols = ["Local", "Activité", "Note", "Avis Étudiant", "Date Avis"]
    print_table("5. CONSULTATION & RETOURS DES ÉTUDIANTS / USAGERS", cols, cursor.fetchall())

    conn.close()

if __name__ == "__main__":
    run_verifications()
