CREATE TABLE IF NOT EXISTS customers (
    client_id VARCHAR(20) PRIMARY KEY,
    segment_client VARCHAR(50),
    score_credit_client NUMERIC(5,2)
);

CREATE TABLE IF NOT EXISTS agencies (
    agence VARCHAR(100) PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS products (
    produit VARCHAR(100) PRIMARY KEY,
    categorie VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    client_id VARCHAR(20) NOT NULL REFERENCES customers(client_id),
    agence VARCHAR(100) NOT NULL REFERENCES agencies(agence),
    produit VARCHAR(100) NOT NULL REFERENCES products(produit),
    date_transaction DATE NOT NULL,
    montant NUMERIC(15,2) NOT NULL,
    devise VARCHAR(10),
    taux_change_eur NUMERIC(10,6),
    montant_eur NUMERIC(15,2),
    type_operation VARCHAR(50),
    statut VARCHAR(30),
    solde_avant NUMERIC(15,2),
    taux_interet NUMERIC(6,4)
);