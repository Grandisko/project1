import sqlite3

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
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
        self.cursor.execute("SELECT * FROM Transactions")
        rows = self.cursor.fetchall()
        column_names = [desc[0] for desc in self.cursor.description]
        return rows, column_names

    def get_warehouses(self):
        self.cursor.execute("SELECT * FROM Warehouse")
        rows = self.cursor.fetchall()
        column_names = [desc[0] for desc in self.cursor.description]
        return rows, column_names

    def get_warehouse_goods(self, warehouse_id):
        self.cursor.execute("""
            SELECT g.id, g.articul, g.name, g.price, g.ex_time, g.img, gw.count, gw.expire_date
            FROM Goods g
            JOIN GoodsWarehouse gw ON g.id = gw.good_id
            WHERE gw.warehouse_id =?
        """, (warehouse_id,))
        rows = self.cursor.fetchall()
        column_names = [desc[0] for desc in self.cursor.description]
        return rows, column_names

    def get_all_goods(self):
        self.cursor.execute("SELECT * FROM Goods")
        rows = self.cursor.fetchall()
        column_names = [desc[0] for desc in self.cursor.description]
        return rows, column_names

    def add_good(self, good):
        self.cursor.execute("""
            INSERT INTO Goods (articul, name, price, ex_time, img)
            VALUES (?,?,?,?,?)
        """, good)
        self.conn.commit()

    def add_warehouse(self, warehouse):
        self.cursor.execute("""
            INSERT INTO Warehouse (name, coordinates_a, coordinates_b, adress)
            VALUES (?,?,?,?)
        """, warehouse)
        self.conn.commit()

    def delete_good(self, good_id):
        self.cursor.execute("DELETE FROM Goods WHERE id =?", (good_id,))
        self.cursor.execute("DELETE FROM GoodsWarehouse WHERE good_id =?", (good_id,))
        self.conn.commit()

    def delete_warehouse_good(self, good_id, warehouse_id):
        self.cursor.execute("DELETE FROM GoodsWarehouse WHERE good_id =? AND warehouse_id =?", (good_id, warehouse_id))
        self.conn.commit()

    def delete_warehouse(self, warehouse_id):
        self.cursor.execute("DELETE FROM Warehouse WHERE id =?", (warehouse_id,))
        self.cursor.execute("DELETE FROM GoodsWarehouse WHERE warehouse_id =?", (warehouse_id,))
        self.conn.commit()

    def get_admin_params(self, login, password):
        self.cursor.execute("SELECT inner, sell, client, redact, super FROM Admin WHERE login =? AND password =?", (login, password))
        row = self.cursor.fetchone()
        if row:
            return {'inner': row[0], 'ell': row[1], 'client': row[2], 'edact': row[3], 'uper': row[4]}
        else:
            return None

    def close(self):
        self.conn.close()

# Пример использования:
db = Database("database.db")
db.create_tables()

# добавление данных
db.add_good(("articul1", "name1", 100, "2022-01-01", "img1"))
db.add_warehouse(("warehouse1", 1.0, 2.0, "adress1"))

# получение данных
rows, column_names = db.get_transactions()
print(rows, column_names)

rows, column_names = db.get_warehouses()
print(rows, column_names)

rows, column_names = db.get_warehouse_goods(1)
print(rows, column_names)

rows, column_names = db.get_all_goods()
print(rows, column_names)

# закрытие соединения
db.close()

tables = {
    "Goods": ["id", "articul", "name", "price", "ex_time", "img"],
    "GoodsWarehouse": ["id", "good_id", "warehouse_id", "count", "expire_date", "accept_date", "accept_id"],
    "Warehouse": ["id", "name", "coordinates_a", "coordinates_b", "adress"],
    "Client": ["id", "Fio", "telephone", "type"],
    "Admin": ["id", "login", "password", "inner", "sell", "client", "redact", "super"],
    "Sell": ["id", "transaction_id", "client_id", "from_wh"],
    "Transactions": ["id", "type", "who", "time", "PS"],
    "Transportation": ["id", "transaction_id", "from_wh", "to_wh"],
    "TransportationData": ["id", "good_id", "transportation_id", "count", "expire_date"],
    "AcceptanceData": ["id", "good_id", "acceptance_id", "count", "expire_date"],
    "Acceptance": ["id", "transaction_id", "to_wh"],
    "SellData": ["id", "good_id", "sell_id", "count", "expire_date"],
    "WriteOff": ["id", "transaction_id", "from_wh"],
    "WriteOffData": ["id", "good_id", "write_of_id", "count", "expire_date"],
}

functions = {
    "create_tables": "Создает таблицы в базе данных, если они еще не существуют.",
    "get_transactions": "Извлекает все транзакции из таблицы Transactions.",
    "get_warehouses": "Извлекает все склады из таблицы Warehouse.",
    "get_warehouse_goods": "Извлекает все товары с определенного склада.",
    "get_all_goods": "Извлекает все товары из таблицы «Goods».",
    "add_good": "Добавляет новый товар в таблицы Goods и GoodsWarehouse.",
    "add_warehouse": "Добавляет новый склад в таблицы Warehouse и GoodsWarehouse.",
    "delete_good": "Удаляет товар и связанные с ним данные из таблиц «Goods» и «GoodsWarehouse».",
    "delete_warehouse_good": "Удаляет конкретный товар с определенного склада.",
    "delete_warehouse": "Удаляет склад и связанные с ним данные из таблиц «Warehouse» и «GoodsWarehouse».",
    "get_admin_params": "Получает параметры администратора для данного логина и пароля.",
}
print('Hello. Dima')