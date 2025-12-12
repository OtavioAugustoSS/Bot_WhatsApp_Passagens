CREATE TABLE IF NOT EXISTS ofertas_enviadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    voo_id VARCHAR(255) NOT NULL,
    origem VARCHAR(3) NOT NULL,
    destino VARCHAR(3) NOT NULL,
    data_ida DATE NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_offer (voo_id, data_envio)
);
