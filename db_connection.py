import psycopg2

def get_db_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="postgres",
        host="localhost",  # или другой хост
        port="5433"        # стандартный порт PostgreSQL
    )

# Функция для добавления нового компьютера
def add_computer(ip_address, mac_address, router_id):
    query = "INSERT INTO computer (ip_address, mac_address, router_id) VALUES (%s, %s, %s)"
    params = (ip_address, mac_address, router_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()  # Подтверждаем изменения
    cursor.close()
    conn.close()

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

# Функция для добавления нового маршрутизатора
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
            cursor.execute(query_dns, (domain_name, ip_address))

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
