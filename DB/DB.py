import sqlite3
from PyQt5 import QtWidgets, QtCore
import datetime
from Constants import Constants

class Database:
    db_file = Constants.DATABASE_PATH
    def __init__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
    # ex_time только дни и к ним прибавляем время транзакции
    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Goods (
                id INTEGER PRIMARY KEY,
                articul VARCHAR UNIQUE,  
                name VARCHAR,
                price INTEGER,
                ex_time DATETIME, 
                img VARCHAR
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS GoodsWarehouse (
                id INTEGER PRIMARY KEY,
                good_id INTEGER,
                warehouse_id INTEGER,
                count INTEGER,
                expire_date INTEGER,
                accept_date INTEGER,
                accept_id INTEGER,
                UNIQUE (good_id, warehouse_id),  
                FOREIGN KEY (good_id) REFERENCES Goods(id) ON DELETE CASCADE,
                FOREIGN KEY (warehouse_id) REFERENCES Warehouse(id) ON DELETE CASCADE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Warehouse (
                id INTEGER PRIMARY KEY,
                name VARCHAR UNIQUE,
                coordinates_a REAL,
                coordinates_b REAL,
                adress VARCHAR
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Client (
                id INTEGER PRIMARY KEY,
                Fio VARCHAR,
                telephone VARCHAR UNIQUE,
                type BOOLEAN
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Admin (
                id INTEGER PRIMARY KEY,
                login VARCHAR UNIQUE,  
                password VARCHAR,
                inner BOOLEAN,
                sell BOOLEAN,
                client BOOLEAN,
                redact BOOLEAN,
                super BOOLEAN
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Sell (
                id INTEGER PRIMARY KEY,
                transaction_id INTEGER,
                client_id INTEGER,
                from_wh_id INTEGER,
                UNIQUE (transaction_id, client_id, from_wh_id), 
                FOREIGN KEY (transaction_id) REFERENCES Transactions(id) ON DELETE CASCADE,
                FOREIGN KEY (client_id) REFERENCES Client(id) ON DELETE CASCADE,
                FOREIGN KEY (from_wh_id) REFERENCES Warehouse(id) ON DELETE CASCADE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Transactions (
                id INTEGER PRIMARY KEY,
                type VARCHAR,
                who INTEGER,
                time DATETIME,
                PS TEXT,
                who_login TEXT GENERATED ALWAYS AS (
                    SELECT a.login FROM Admin a WHERE a.id = Transactions.who
                ) VIRTUAL,
                FOREIGN KEY (who) REFERENCES Admin(id) ON DELETE CASCADE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Transportation (
                id INTEGER PRIMARY KEY,
                transaction_id INTEGER,
                from_wh_id INTEGER,
                to_wh_id INTEGER,
                UNIQUE (transaction_id, from_wh_id, to_wh_id), 
                FOREIGN KEY (transaction_id) REFERENCES Transactions(id) ON DELETE CASCADE,
                FOREIGN KEY (from_wh_id) REFERENCES Warehouse(id) ON DELETE CASCADE,
                FOREIGN KEY (to_wh_id) REFERENCES Warehouse(id) ON DELETE CASCADE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS TransportationData (
                id INTEGER PRIMARY KEY,
                good_id INTEGER,
                transportation_id INTEGER,
                count INTEGER,
                expire_date INTEGER,
                UNIQUE (good_id, transportation_id),  
                FOREIGN KEY (good_id) REFERENCES Goods(id) ON DELETE CASCADE,
                FOREIGN KEY (transportation_id) REFERENCES Transportation(id) ON DELETE CASCADE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS AcceptanceData (
                id INTEGER PRIMARY KEY,
                good_id INTEGER,
                acceptance_id INTEGER,
                count INTEGER,
                expire_date INTEGER,
                UNIQUE (good_id, acceptance_id),  
                FOREIGN KEY (good_id) REFERENCES Goods(id) ON DELETE CASCADE,
                FOREIGN KEY (acceptance_id) REFERENCES Acceptance(id) ON DELETE CASCADE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Acceptance (
                id INTEGER PRIMARY KEY,
                transaction_id INTEGER,
                to_wh INTEGER,
                UNIQUE (transaction_id, to_wh), 
                FOREIGN KEY (transaction_id) REFERENCES Transactions(id) ON DELETE CASCADE,
                FOREIGN KEY (to_wh) REFERENCES Warehouse(id) ON DELETE CASCADE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SellData (
                id INTEGER PRIMARY KEY,
                good_id INTEGER,
                sell_id INTEGER,
                count INTEGER,
                expire_date INTEGER,
                UNIQUE (good_id, sell_id),  
                FOREIGN KEY (good_id) REFERENCES Goods(id) ON DELETE CASCADE,
                FOREIGN KEY (sell_id) REFERENCES Sell(id) ON DELETE CASCADE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS WriteOff (
                id INTEGER PRIMARY KEY,
                transaction_id INTEGER,
                from_wh_id INTEGER,
                UNIQUE (transaction_id, from_wh_id),  
                FOREIGN KEY (transaction_id) REFERENCES Transactions(id) ON DELETE CASCADE,
                FOREIGN KEY (from_wh_id) REFERENCES Warehouse(id) ON DELETE CASCADE
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS WriteOffData (
                id INTEGER PRIMARY KEY,
                good_id INTEGER,
                write_of_id INTEGER,
                count INTEGER,
                expire_date INTEGER,
                UNIQUE (good_id, write_of_id),  
                FOREIGN KEY (good_id) REFERENCES Goods(id) ON DELETE CASCADE,
                FOREIGN KEY (write_of_id) REFERENCES WriteOff(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def delete(self, table_name, id_or_ids):
        """
        функция удаления
        """
        if isinstance(id_or_ids, list):
            self.cursor.execute(f"DELETE FROM {table_name} WHERE id IN ({', '.join('?' for _ in id_or_ids)})",
                                id_or_ids)
        else:
            self.cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (id_or_ids,))
        self.conn.commit()

    def update(self, table_name, id_or_ids, changes):
        """
        функция изменения
        """
        if isinstance(id_or_ids, list):
            if isinstance(changes, list):
                for i, id in enumerate(id_or_ids):
                    self.cursor.execute(
                        f"UPDATE {table_name} SET {', '.join(f'{key} = ?' for key in changes[i].keys())} WHERE id = ?",
                        (*changes[i].values(), id))
            elif isinstance(changes, dict):
                self.cursor.execute(
                    f"UPDATE {table_name} SET {', '.join(f'{key} = ?' for key in changes.keys())} WHERE id IN ({', '.join('?' for _ in id_or_ids)})",
                    (*changes.values(), *id_or_ids))
        else:
            self.cursor.execute(
                f"UPDATE {table_name} SET {', '.join(f'{key} = ?' for key in changes.keys())} WHERE id = ?",
                (*changes.values(), id_or_ids))
        self.conn.commit()

    def insert(self, table_name, data):
        """
        функция добавления
        """
        if isinstance(data, list):
            for item in data:
                self.cursor.execute(
                    f"INSERT INTO {table_name} ({', '.join(item.keys())}) VALUES ({', '.join('?' for _ in item.values())})",
                    (*item.values(),))
        else:
            self.cursor.execute(
                f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({', '.join('?' for _ in data.values())})",
                (*data.values(),))
        self.conn.commit()
    def get_transactions(self):
        """
        Извлекает все транзакции из таблицы Transactions.
        """
        self.cursor.execute("SELECT * FROM Transactions")
        return self.cursor.fetchall()
    def get_clients(self):
        """
        Извлекает всех клиентов из таблицы Client.
        """
        self.cursor.execute("SELECT * FROM Client")
        return self.cursor.fetchall()

    def get_warehouses(self):
        """
        Извлекает все склады из таблицы Warehouse.
        """
        self.cursor.execute("""
                SELECT id, name, adress
                FROM Warehouse
            """)
        return self.cursor.fetchall()

    def get_warehouse_goods(self, warehouse_id):
        """
        Извлекает все товары с определенного склада.
        """
        self.cursor.execute("""
            SELECT g.id, g.articul, g.name, g.price, g.ex_time, g.img, gw.count, gw.expire_date
            FROM Goods g
            JOIN GoodsWarehouse gw ON g.id = gw.good_id
            WHERE gw.warehouse_id =?
        """, (warehouse_id,))
        return self.cursor.fetchall()

    def get_all_goods(self):
        """
        Извлекает все товары из таблицы «Goods».
        """
        self.cursor.execute("SELECT * FROM Goods")
        return self.cursor.fetchall()

    def add_good(self, good):
        """
        Добавляет новый товар в таблицы Goods и GoodsWarehouse.
        """
        self.cursor.execute("""
            INSERT OR IGNORE INTO Goods (articul, name, price, ex_time, img)
            VALUES (?,?,?,?,?)
        """, good)
        self.conn.commit()

    def add_warehouse(self, warehouse):
        """
        Добавляет новый склад в таблицы Warehouse и GoodsWarehouse.
        """
        self.cursor.execute("""
            INSERT OR IGNORE INTO Warehouse (name, coordinates_a, coordinates_b, adress)
            VALUES (?,?,?,?)
        """, warehouse)
        self.conn.commit()

    def delete_good(self, good_id):
        """
        Удаляет товар и связанные с ним данные из таблиц «Goods» и «GoodsWarehouse».
        """
        self.cursor.execute("DELETE FROM Goods WHERE id =?", (good_id,))
        self.cursor.execute("DELETE FROM GoodsWarehouse WHERE good_id =?", (good_id,))
        self.conn.commit()

    def delete_warehouse_good(self, good_id, warehouse_id):
        """
        Удаляет конкретный товар с определенного склада.
        """
        self.cursor.execute("DELETE FROM GoodsWarehouse WHERE good_id =? AND warehouse_id =?", (good_id, warehouse_id))
        self.conn.commit()

    def delete_warehouse(self, warehouse_id):
        """
        Удаляет склад и связанные с ним данные из таблиц «Warehouse» и «GoodsWarehouse».
        """
        self.cursor.execute("DELETE FROM Warehouse WHERE id =?", (warehouse_id,))
        self.cursor.execute("DELETE FROM GoodsWarehouse WHERE warehouse_id =?", (warehouse_id,))
        self.conn.commit()

    def get_admin_params(self, login, password):
        """
        Получает параметры администратора для данного логина и пароля.
        """
        self.cursor.execute("SELECT id, inner, sell, client, redact, super FROM Admin WHERE login =? AND password =?",
                            (login, password))
        row = self.cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'inner': row[1],
                'sell': row[2],
                'clients': row[3],
                'redact': row[4],
                'super': row[5]
            }
        else:
            return None

    def get_good_characteristics(self, good_id):
        """
        функция, которая вернет характеристики товара из таблицы Goods
        """
        self.cursor.execute("SELECT * FROM Goods WHERE id=?", (good_id,))
        good_info = self.cursor.fetchone()
        if good_info is None:
            return None
        good_info = list(good_info)
        self.cursor.execute("SELECT SUM(count) FROM GoodsWarehouse WHERE good_id=?", (good_id,))
        total_count = self.cursor.fetchone()[0]
        if total_count is None:
            total_count = 0
        good_info.append(total_count)
        return good_info
    def table_check(self):
        """
        проверки на наличие информации в курсоре
        """
        if self.cursor.rowcount == 0:
            print("Table Goods already exists")
        self.conn.commit()

    def merge_duplicates(self, table_name, columns_to_merge):
        """
        Merge duplicate records in a table, excluding `id` and `count` columns.
        :param table_name: Name of the table to merge duplicates in
        :param columns_to_merge: List of column names to merge duplicates on
        """
        self.cursor.execute(
            f"SELECT {', '.join(columns_to_merge)} FROM {table_name} GROUP BY {', '.join(columns_to_merge)}")
        unique_rows = self.cursor.fetchall()

        for row in unique_rows:
            self.cursor.execute(
                f"SELECT id, count FROM {table_name} WHERE {', '.join([f'{col} = ?' for col in columns_to_merge])}",
                row)
            duplicate_rows = self.cursor.fetchall()

            if len(duplicate_rows) > 1:
                # Merge duplicate rows
                merged_id = duplicate_rows[0][0]
                merged_count = sum([r[1] for r in duplicate_rows])

                self.cursor.execute(f"UPDATE {table_name} SET count = ? WHERE id = ?", (merged_count, merged_id))

                # Delete duplicate rows
                for row in duplicate_rows[1:]:
                    self.cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (row[0],))

        self.conn.commit()

    def check_transaction_type(self, transaction_data):
        """
        Check the type of a transaction.
        :param transaction_data: Dictionary with transaction data
        :return: Type of the transaction (one of 'sell', 'transportation', 'acceptance', 'write_off')
        """
        transaction_type = transaction_data['type']
        if transaction_type == 0:
            return 'OPERATION_RELOCATE'
        elif transaction_type == 1:
            return 'OPERATION_WRITE_OFF'
        elif transaction_type == 2:
            return 'OPERATION_ACCEPT'
        elif transaction_type == 3:
            return 'OPERATION_SELL'
        else:
            raise ValueError(f"Unknown transaction type: {transaction_type}")

    def save_transaction(self, transaction_params):
        """
        Save a transaction to the Transactions table.

        :param transaction_params: dict (transaction parameters)
        """
        transaction_types = {
            0: 'Relocate',
            1: 'WriteOff',
            2: 'Accept',
            3: 'Sell'
        }
        type_str = transaction_types[transaction_params['type']]

        ps = self._format_context(transaction_params['context'])

        if 'warehouse' in transaction_params:
            warehouse_id = transaction_params['warehouse']
            self.cursor.execute("SELECT name FROM Warehouses WHERE id = ?", (warehouse_id,))
            warehouse_name = self.cursor.fetchone()[0]
            self.cursor.execute("""
                INSERT INTO Transactions (type, who, time, PS, warehouse)
                VALUES (?, ?, ?, ?, ?)
            """, (type_str, transaction_params['who'], datetime.datetime.now(), ps, warehouse_name))
        elif 'client' in transaction_params:
            client_id = transaction_params['client']
            self.cursor.execute("SELECT name FROM Clients WHERE id = ?", (client_id,))
            client_name = self.cursor.fetchone()[0]
            self.cursor.execute("""
                INSERT INTO Transactions (type, who, time, PS, client)
                VALUES (?, ?, ?, ?, ?)
            """, (type_str, transaction_params['who'], datetime.datetime.now(), ps, client_name))
        else:
            self.cursor.execute("""
                INSERT INTO Transactions (type, who, time, PS)
                VALUES (?, ?, ?, ?)
            """, (type_str, transaction_params['who'], datetime.datetime.now(), ps))

        self.conn.commit()

    def _format_context(self, context):
        """
        Format the transaction context as a string.

        :param context: dict (transaction-specific context)
        :return: str
        """
        if isinstance(context, dict):
            result = []
            for k, v in context.items():
                if isinstance(k, int):  # assume k is an ID
                    self.cursor.execute("SELECT name FROM Items WHERE id = ?", (k,))
                    item_name = self.cursor.fetchone()[0]
                    result.append(f"{item_name}: {v}")
                else:
                    result.append(f"{k}: {v}")
            return ', '.join(result)
        elif isinstance(context, list):
            return ', '.join(self._format_context(item) for item in context)
        else:
            raise ValueError("Invalid context format")
    def close(self):
        self.conn.close()

TABLES = {
    "Goods": {
        "id": Constants.PRIMARY_KEY,
        "articul": Constants.TEXT,
        "name": Constants.TEXT,
        "price": Constants.NUMERIC,
        "ex_time": Constants.DATETIME,
        "img": Constants.TEXT
    },
    "GoodsWarehouse": {
        "id": Constants.PRIMARY_KEY,
        "good_id": Constants.FOREIGN_KEY,
        "warehouse_id": Constants.FOREIGN_KEY,
        "count": Constants.NUMERIC,
        "expire_date": Constants.DATETIME,
        "accept_date": Constants.DATETIME,
        "accept_id": Constants.FOREIGN_KEY
    },
    "Warehouse": {
        "id": Constants.PRIMARY_KEY,
        "name": Constants.TEXT,
        "coordinates_a": Constants.NUMERIC,
        "coordinates_b": Constants.NUMERIC,
        "adress": Constants.TEXT
    },
    "Client": {
        "id": Constants.PRIMARY_KEY,
        "Fio": Constants.TEXT,
        "telephone": Constants.TEXT,
        "type": Constants.TEXT
    },
    "Admin": {
        "id": Constants.PRIMARY_KEY,
        "login": Constants.TEXT,
        "password": Constants.TEXT,
        "inner": Constants.BOOL,
        "sell": Constants.BOOL,
        "client": Constants.BOOL,
        "redact": Constants.BOOL,
        "super": Constants.BOOL
    },
    "Sell": {
        "id": Constants.PRIMARY_KEY,
        "transaction_id": Constants.FOREIGN_KEY,
        "client_id": Constants.FOREIGN_KEY,
        "from_wh": Constants.FOREIGN_KEY
    },
    "Transactions": {
        "id": Constants.PRIMARY_KEY,
        "type": Constants.TEXT,
        "who": Constants.FOREIGN_KEY,
        "time": Constants.DATETIME,
        "PS": Constants.TEXT
    },
    "Transportation": {
        "id": Constants.PRIMARY_KEY,
        "transaction_id": Constants.FOREIGN_KEY,
        "from_wh": Constants.FOREIGN_KEY,
        "to_wh": Constants.FOREIGN_KEY
    },
    "TransportationData": {
        "id": Constants.PRIMARY_KEY,
        "good_id": Constants.FOREIGN_KEY,
        "transportation_id": Constants.FOREIGN_KEY,
        "count": Constants.NUMERIC,
        "expire_date": Constants.DATETIME
    },
    "AcceptanceData": {
        "id": Constants.PRIMARY_KEY,
        "good_id": Constants.FOREIGN_KEY,
        "acceptance_id": Constants.FOREIGN_KEY,
        "count": Constants.NUMERIC,
        "expire_date": Constants.DATETIME
    },
    "Acceptance": {
        "id": Constants.PRIMARY_KEY,
        "transaction_id": Constants.FOREIGN_KEY,
        "to_wh": Constants.FOREIGN_KEY
    },
    "SellData": {
        "id": Constants.PRIMARY_KEY,
        "good_id": Constants.FOREIGN_KEY,
        "sell_id": Constants.FOREIGN_KEY,
        "count": Constants.NUMERIC,
        "expire_date": Constants.DATETIME
    },
    "WriteOff": {
        "id": Constants.PRIMARY_KEY,
        "transaction_id": Constants.FOREIGN_KEY,
        "from_wh": Constants.FOREIGN_KEY
    },
    "WriteOffData": {
        "id": Constants.PRIMARY_KEY,
        "good_id": Constants.FOREIGN_KEY,
        "write_of_id": Constants.FOREIGN_KEY,
        "count": Constants.NUMERIC,
        "expire_date": Constants.DATETIME
    }
}
