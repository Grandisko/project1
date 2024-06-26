import sqlite3
from PyQt5 import QtWidgets, QtCore
from forcrut.Constants import Constants

class Database:
    db_file = "database.db"
    def __init__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Goods (
                id INTEGER PRIMARY KEY,
                articul VARCHAR,
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
                FOREIGN KEY (good_id) REFERENCES Goods(id),
                FOREIGN KEY (warehouse_id) REFERENCES Warehouse(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Warehouse (
                id INTEGER PRIMARY KEY,
                name VARCHAR,
                coordinates_a REAL,
                coordinates_b REAL,
                adress VARCHAR
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Client (
                id INTEGER PRIMARY KEY,
                Fio VARCHAR,
                telephone VARCHAR,
                type BOOLEAN
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Admin (
                id INTEGER PRIMARY KEY,
                login VARCHAR,
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
                from_wh INTEGER,
                FOREIGN KEY (transaction_id) REFERENCES Transactions(id),
                FOREIGN KEY (client_id) REFERENCES Client(id),
                FOREIGN KEY (from_wh) REFERENCES Warehouse(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Transactions (
                id INTEGER PRIMARY KEY,
                type VARCHAR,
                who INTEGER,
                time DATETIME,
                PS TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Transportation (
                id INTEGER PRIMARY KEY,
                transaction_id INTEGER,
                from_wh INTEGER,
                to_wh INTEGER,
                FOREIGN KEY (transaction_id) REFERENCES Transactions(id),
                FOREIGN KEY (from_wh) REFERENCES Warehouse(id),
                FOREIGN KEY (to_wh) REFERENCES Warehouse(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS TransportationData (
                id INTEGER PRIMARY KEY,
                good_id INTEGER,
                transportation_id INTEGER,
                count INTEGER,
                expire_date INTEGER,
                FOREIGN KEY (good_id) REFERENCES Goods(id),
                FOREIGN KEY (transportation_id) REFERENCES Transportation(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS AcceptanceData (
                id INTEGER PRIMARY KEY,
                good_id INTEGER,
                acceptance_id INTEGER,
                count INTEGER,
                expire_date INTEGER,
                FOREIGN KEY (good_id) REFERENCES Goods(id),
                FOREIGN KEY (acceptance_id) REFERENCES Acceptance(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Acceptance (
                id INTEGER PRIMARY KEY,
                transaction_id INTEGER,
                to_wh INTEGER,
                FOREIGN KEY (transaction_id) REFERENCES Transactions(id),
                FOREIGN KEY (to_wh) REFERENCES Warehouse(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SellData (
                id INTEGER PRIMARY KEY,
                good_id INTEGER,
                sell_id INTEGER,
                count INTEGER,
                expire_date INTEGER,
                FOREIGN KEY (good_id) REFERENCES Goods(id),
                FOREIGN KEY (sell_id) REFERENCES Sell(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS WriteOff (
                id INTEGER PRIMARY KEY,
                transaction_id INTEGER,
                from_wh INTEGER,
                FOREIGN KEY (transaction_id) REFERENCES Transactions(id),
                FOREIGN KEY (from_wh) REFERENCES Warehouse(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS WriteOffData (
                id INTEGER PRIMARY KEY,
                good_id INTEGER,
                write_of_id INTEGER,
                count INTEGER,
                expire_date INTEGER,
                FOREIGN KEY (good_id) REFERENCES Goods(id),
                FOREIGN KEY (write_of_id) REFERENCES WriteOff(id)
            )
        """)
        self.conn.commit()

    def get_transactions(self):
        """
        Извлекает все транзакции из таблицы Transactions.
        """
        self.cursor.execute("SELECT * FROM Transactions")
        return self.cursor.fetchall()
    def get_Clients(self):
        """
        Извлекает всех клиентов из таблицы Client.
        """
        self.cursor.execute("SELECT * FROM Client")
        return self.cursor.fetchall()

    def get_warehouses(self):
        """
        Извлекает все склады из таблицы Warehouse.
        """
        self.cursor.execute("SELECT * FROM Warehouse")
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
        self.cursor.execute("SELECT inner, sell, client, redact, super FROM Admin WHERE login =? AND password =?",
                            (login, password))
        row = self.cursor.fetchone()
        if row:
            return {'inner': row[0], 'sell': row[1], 'client': row[2], 'redact': row[3], 'super': row[4]}
        else:
            return None

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
