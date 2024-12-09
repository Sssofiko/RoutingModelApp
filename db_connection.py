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
def add_computer(ip_address, mac_address, router_id, network_name):
    query = "INSERT INTO computer (ip_address, mac_address, router_id, network_name) VALUES (%s, %s, %s, %s)"
    params = (ip_address, mac_address, router_id, network_name)
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
def add_router(ip_address, mac_address, public_ip_address, network_name):
    query = "INSERT INTO router (ip_address, mac_address, public_ip_address, network_name) VALUES (%s, %s, %s, %s)"
    params = (ip_address, mac_address, public_ip_address, network_name)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()  # Подтверждаем изменения
    cursor.close()
    conn.close()

# Функция для получения списка компьютеров
def list_computers():
    query = "SELECT id, ip_address, mac_address FROM computer"
    return execute_query(query)

def list_computers_with_router():
    query = "SELECT id, ip_address, mac_address, router_id FROM computer"
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
    query = "SELECT id, ip_address, mac_address FROM router"
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
        SELECT ip_address, mac_address, router_id, network_name
        FROM computer
        WHERE id = %s
    """
    result = execute_query(query, (computer_id,))
    return result[0] if result else None

def update_computer(computer_id, ip_address, mac_address, router_id, network_name):
    query = """
        UPDATE computer
        SET ip_address = %s, mac_address = %s, router_id = %s, network_name = %s
        WHERE id = %s
    """
    params = (ip_address, mac_address, router_id, network_name, computer_id)
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
