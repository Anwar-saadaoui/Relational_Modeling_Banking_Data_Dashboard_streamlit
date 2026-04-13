CREATE INDEX IF NOT EXISTS idx_transactions_client_id     ON transactions(client_id);
CREATE INDEX IF NOT EXISTS idx_transactions_agence        ON transactions(agence);
CREATE INDEX IF NOT EXISTS idx_transactions_date          ON transactions(date_transaction);
CREATE INDEX IF NOT EXISTS idx_transactions_produit       ON transactions(produit);
CREATE INDEX IF NOT EXISTS idx_transactions_statut        ON transactions(statut);