-- Создание таблицы для хранения информации о компьютерах в сети
CREATE TABLE computer (
                          id SERIAL PRIMARY KEY,
                          ip_address VARCHAR,
                          mac_address VARCHAR UNIQUE,
                          router_id INTEGER,
                          CONSTRAINT unique_network_ip UNIQUE (ip_address, router_id)
);

-- Создание таблицы для хранения информации о маршрутизаторах
CREATE TABLE router (
                        id SERIAL PRIMARY KEY,
                        ip_address VARCHAR,
                        mac_address VARCHAR UNIQUE,
                        public_ip_address VARCHAR UNIQUE,
                        network_name VARCHAR UNIQUE
);

-- Создание таблицы ARP, хранящей соответствие между IP и MAC-адресами
CREATE TABLE arp_table (
                           id SERIAL PRIMARY KEY,
                           ip_address VARCHAR,
                           mac_address VARCHAR,
                           device_id INTEGER,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы NAT, хранящей соответствие между внутренними и публичными IP-адресами
CREATE TABLE nat_table (
                           id SERIAL PRIMARY KEY,
                           router_id INTEGER,
                           internal_ip_address VARCHAR,
                           public_ip_address VARCHAR,
                           internal_port INTEGER,
                           public_port INTEGER,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы DNS, хранящей соответствие между доменными именами и IP-адресами
CREATE TABLE dns_table (
                           id SERIAL PRIMARY KEY,
                           domain_name VARCHAR,
                           ip_address VARCHAR,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Связи между таблицами
ALTER TABLE computer ADD CONSTRAINT fk_computer_router FOREIGN KEY (router_id) REFERENCES router(id) ON DELETE SET NULL;
ALTER TABLE arp_table ADD CONSTRAINT fk_arp_computer FOREIGN KEY (device_id) REFERENCES computer(id) ON DELETE CASCADE;
ALTER TABLE arp_table ADD CONSTRAINT fk_arp_router FOREIGN KEY (device_id) REFERENCES router(id) ON DELETE CASCADE;
ALTER TABLE nat_table ADD CONSTRAINT fk_nat_router FOREIGN KEY (router_id) REFERENCES router(id) ON DELETE CASCADE;
