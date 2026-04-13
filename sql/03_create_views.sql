-- Full detail view
CREATE OR REPLACE VIEW vw_transaction_details AS
SELECT
    t.transaction_id,
    t.date_transaction,
    t.montant,
    t.montant_eur,
    t.devise,
    t.type_operation,
    t.statut,
    t.solde_avant,
    t.taux_interet,
    c.client_id,
    c.segment_client,
    c.score_credit_client,
    a.agence,
    p.produit,
    p.categorie
FROM transactions t
JOIN customers c ON t.client_id = c.client_id
JOIN agencies a ON t.agence = a.agence
JOIN products p ON t.produit = p.produit;


-- KPI: total & avg per agency per month
CREATE OR REPLACE VIEW vw_agency_monthly_kpi AS
SELECT
    agence,
    DATE_TRUNC('month', date_transaction) AS mois,
    COUNT(*)                              AS nb_transactions,
    SUM(montant_eur)                      AS total_eur,
    ROUND(AVG(montant_eur), 2)            AS moyenne_eur
FROM transactions
GROUP BY agence, DATE_TRUNC('month', date_transaction);




CREATE OR REPLACE VIEW vw_client_solde_vs_moyenne AS
SELECT
    c.client_id,          
    c.segment_client,
    c.score_credit_client,
    ROUND(AVG(t.solde_avant), 2)                        AS solde_moyen,
    ROUND(AVG(AVG(t.solde_avant)) OVER (), 2)           AS moyenne_nationale,
    CASE
        WHEN AVG(t.solde_avant) < AVG(AVG(t.solde_avant)) OVER ()
        THEN 'En dessous de la moyenne'
        ELSE 'Au dessus de la moyenne'
    END AS statut_solde
FROM transactions t
JOIN customers c ON t.client_id = c.client_id
GROUP BY c.client_id, c.segment_client, c.score_credit_client;


-- KPI: default rate by segment
CREATE OR REPLACE VIEW vw_taux_defaut_segment AS
SELECT
    c.segment_client,
    COUNT(DISTINCT t.client_id) AS total_clients,
    SUM(CASE WHEN t.statut = 'defaut' THEN 1 ELSE 0 END) AS en_defaut,
    ROUND(
        SUM(CASE WHEN t.statut = 'defaut' THEN 1 ELSE 0 END)::NUMERIC
        / NULLIF(COUNT(DISTINCT t.client_id), 0) * 100, 
    2) AS taux_defaut_pct
FROM transactions t
JOIN customers c 
    ON t.client_id = c.client_id
GROUP BY c.segment_client;
