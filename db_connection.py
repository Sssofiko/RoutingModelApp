import psycopg2

def get_db_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",  # или другой хост
        port="5433"        # стандартный порт PostgreSQL
    )

def execute_query_without_return(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()

# Функция для добавления нового компьютера
def add_computer(ip_address, mac_address, router_id):
    query = "INSERT INTO computer (ip_address, mac_address, router_id) VALUES (%s, %s, %s)"
    params = (ip_address, mac_address, router_id)
    execute_query_without_return(query, params)

def delete_computer_by_id(computer_id):
    query = "DELETE FROM computer WHERE id = %s"
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, (computer_id,))
        conn.commit()  # Подтверждаем удаление
    except Exception as e:
        conn.rollback()
        print(f"Database Error in delete_computer_by_id: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def add_router(ip_address, mac_address, public_ip_address, network_name, domain_name=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Добавляем маршрутизатор
        query_router = """
            INSERT INTO router (ip_address, mac_address, public_ip_address, network_name)
            VALUES (%s, %s, %s, %s) RETURNING id
        """
        cursor.execute(query_router, (ip_address, mac_address, public_ip_address, network_name))

        # Если доменное имя указано, добавляем его в таблицу DNS
        if domain_name:
            query_dns = """
                INSERT INTO dns_table (domain_name, ip_address)
                VALUES (%s, %s)
            """
            # Используем public_ip_address вместо ip_address
            cursor.execute(query_dns, (domain_name, public_ip_address))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# Функция для получения списка компьютеров
def list_computers():
    """
    Возвращает список компьютеров с их данными и публичным IP маршрутизатора.
    """
    query = """
        SELECT c.id, c.ip_address, c.mac_address, r.network_name
        FROM computer c
        LEFT JOIN router r ON c.router_id = r.id
    """
    return execute_query(query)

# Функция для выполнения запросов
def execute_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result

# Функция для разрешения DNS
def resolve_dns(domain_name):
    query = "SELECT ip_address FROM dns_table WHERE domain_name = %s"
    result = execute_query(query, (domain_name,))
    return result[0][0] if result else None

def list_routers():
    query = "SELECT id, ip_address, mac_address, public_ip_address, network_name FROM router"
    return execute_query(query)

def delete_router_by_id(router_id):
    query = "DELETE FROM router WHERE id = %s"
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, (router_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_computer_by_id(computer_id):
    """Получает данные компьютера по ID."""
    query = """
        SELECT ip_address, mac_address, router_id
        FROM computer
        WHERE id = %s
    """
    result = execute_query(query, (computer_id,))
    return result[0] if result else None

def get_router_id_by_public_ip(public_ip):
    """Получает ID маршрутизатора по его публичному IP."""
    query = "SELECT id FROM router WHERE public_ip_address = %s"
    result = execute_query(query, (public_ip,))
    return result[0][0] if result else None

def get_router_public_ip_by_id(router_id):
    """Получает публичный IP маршрутизатора по его ID."""
    query = "SELECT public_ip_address FROM router WHERE id = %s"
    result = execute_query(query, (router_id,))
    return result[0][0] if result else None

def update_computer(computer_id, ip_address, mac_address, router_id):
    query = """
        UPDATE computer
        SET ip_address = %s, mac_address = %s, router_id = %s
        WHERE id = %s
    """
    params = (ip_address, mac_address, router_id, computer_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def find_computer_id(network_name, computer_ip):
    query = '''SELECT c.id 
                FROM computer c join router r on c.router_id = r.id 
                WHERE c.ip_address = %s 
                AND network_name = %s'''
    params = (computer_ip, network_name)
    res = execute_query(query, params)
    return res[0] if res else None

def find_router_mac_by_network(network_name):
    query = "SELECT mac_address FROM router WHERE network_name = %s"
    params = (network_name,)
    res = execute_query(query, params)
    return res[0][0] if res else None

def find_router_ip_by_network(network_name):
    query = "SELECT ip_address FROM router WHERE network_name = %s"
    params = (network_name,)
    res = execute_query(query, params)
    return res[0][0] if res else None

def find_router_id_by_network(network_name):
    query = "SELECT id FROM router WHERE network_name = %s"
    params = (network_name,)
    res = execute_query(query, params)
    return res[0] if res else None

def find_record_in_arp_table(device_id, ip_to_find):
    query = '''SELECT mac_address 
                FROM arp_table 
                WHERE device_id = %s 
                AND ip_address = %s
                ORDER BY created_at DESC
                LIMIT 1'''
    params = (device_id, ip_to_find)
    res = execute_query(query, params)
    return res[0][0] if res else None

def add_record_to_arp_table(device_id, ip_address, mac_address):
    query = "INSERT INTO arp_table (ip_address, mac_address, device_id) VALUES (%s, %s, %s)"
    params = (ip_address, mac_address, device_id)
    return execute_query_without_return(query, params)

def generate_port_number(router_id, computer_ip):
    query = '''SELECT MAX(public_port) + 1
                FROM nat_table
                WHERE router_id = %s
                AND internal_ip_address = %s'''
    params = (router_id, computer_ip)
    port = execute_query(query, params)
    return port[0][0] if port[0][0] else 1

def add_record_to_nat_table(network_name, computer_ip, computer_port):
    router_id = find_router_id_by_network(network_name)
    router_public_ip = get_router_public_ip_by_id(router_id)
    public_port = generate_port_number(router_id, computer_ip)
    query = '''INSERT INTO nat_table (router_id, 
                                      internal_ip_address, 
                                      internal_port,
                                      public_ip_address,
                                      public_port)
               VALUES (%s, %s, %s, %s, %s)'''
    params = (router_id, computer_ip, computer_port, router_public_ip, public_port)
    execute_query_without_return(query, params)
    return router_public_ip, public_port

def find_record_in_nat_table(public_ip, public_port):
    query = '''SELECT internal_ip_address, internal_port
    FROM nat_table
    WHERE public_ip_address = %s
    AND public_port = %s'''
    params = (public_ip, public_port)
    res = execute_query(query, params)
    return res[0] if res else None

def route_file_to_server(computer_ip, computer_network, domain_name, port = 80):
    log = 'File transmission started\n'
    computer_id = find_computer_id(computer_network, computer_ip)
    if not computer_id:
        log += 'No computer found'
        return log

    log += f'Source: {computer_ip} in {computer_network}. Destination: {domain_name}\n\n'

    log += f'[UDP] DNS request: who has domain name {domain_name}?\n'
    destination_ip = resolve_dns(domain_name)
    if not destination_ip:
        log += 'No domain name found\n'
        return log

    log += f'[UDP] DNS response: {destination_ip}\n\n'

    router_ip = find_router_ip_by_network(computer_network)
    if not router_ip:
        log += 'Computer is not connected to a router'
        return log

    log += f'[ARP] Trying to find router ip {router_ip} in ARP table\n'
    arp_table_res = find_record_in_arp_table(computer_id, router_ip)

    if arp_table_res:
        router_mac = arp_table_res[-1]
        log += f'[ARP] Record found. Router mac: {router_mac}\n\n'
    else:
        log += f'[ARP] No record found. Starting broadcast\n'
        log += f'[ARP] Who has ip {router_ip}? Tell {computer_ip}\n'
        router_mac = find_router_mac_by_network(computer_network)
        log += f'[ARP] Mac received. Router mac: {router_mac}\n'
        add_record_to_arp_table(computer_id, router_ip, router_mac)
        log += f'[ARP] Record added to arp table\n\n'

    log += f'[TCP] Initiating 3-way handshake\n'
    log += f'[NAT] SYN packet sent to router. Starting address translation. Local ip: {computer_ip}. Local port: {port}\n'
    public_ip, public_port = add_record_to_nat_table(computer_network, computer_ip, port)
    log += f'[NAT] Record added to nat table. Public IP: {public_ip}. Public port: {public_port}\n\n'

    log += f'[TCP] SYN packet received by {destination_ip} on port {port} successfully. Sending SYN-ACK to {public_ip}:{public_port}\n'
    log += f'[TCP] SYN-ACK received by {public_ip} on port {public_port} successfully\n'
    log += f'[NAT] Translating into local computer IP and port\n'
    private_ip, private_port = find_record_in_nat_table(public_ip, public_port)
    log += f'[NAT] Record in table found. Local ip: {private_ip}. Local port: {private_port}\n'
    log += f'[TCP] SYN-ACK received. Sending ACK to {destination_ip}:{port}\n'
    log += '[TCP] Connection established successfully\n'
    log += f'[HTTP] Sending file from {private_ip} to {destination_ip} on port {port}\n'
    log += f'[HTTP] File received by {destination_ip} on port {port} successfully\n'
    log += f'[TCP] Connection closed via a 4-way handshake successfully\n'

    return log
