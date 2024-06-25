import random
from DB import Database
db = Database("database.db")
db.create_tables()

# Populate Goods table
goods = []
for i in range(10):
    articul = f"articul{i}"
    name = f"good{i}"
    price = random.randint(10, 100)
    ex_time = "2022-01-01"
    img = f"img{i}"
    goods.append((articul, name, price, ex_time, img))
db.cursor.executemany("INSERT INTO Goods (articul, name, price, ex_time, img) VALUES (?,?,?,?,?)", goods)
db.conn.commit()

# Populate Warehouse table
warehouses = []
for i in range(5):
    name = f"warehouse{i}"
    coordinates_a = random.random()
    coordinates_b = random.random()
    adress = f"adress{i}"
    warehouses.append((name, coordinates_a, coordinates_b, adress))
db.cursor.executemany("INSERT INTO Warehouse (name, coordinates_a, coordinates_b, adress) VALUES (?,?,?,?)", warehouses)
db.conn.commit()

# Populate GoodsWarehouse table
goods_warehouse = []
for i in range(20):
    good_id = random.randint(1, 10)
    warehouse_id = random.randint(1, 5)
    count = random.randint(1, 10)
    expire_date = "2022-01-01"
    goods_warehouse.append((good_id, warehouse_id, count, expire_date))
db.cursor.executemany("INSERT INTO GoodsWarehouse (good_id, warehouse_id, count, expire_date) VALUES (?,?,?,?)", goods_warehouse)
db.conn.commit()

# Populate Client table
clients = []
for i in range(10):
    Fio = f"client{i}"
    telephone = f"phone{i}"
    type = random.choice([True, False])
    clients.append((Fio, telephone, type))
db.cursor.executemany("INSERT INTO Client (Fio, telephone, type) VALUES (?,?,?)", clients)
db.conn.commit()

# Populate Admin table
admins = []
for i in range(5):
    login = f"admin{i}"
    password = f"password{i}"
    inner = random.choice([True, False])
    sell = random.choice([True, False])
    client = random.choice([True, False])
    redact = random.choice([True, False])
    super = random.choice([True, False])
    admins.append((login, password, inner, sell, client, redact, super))
db.cursor.executemany("INSERT INTO Admin (login, password, inner, sell, client, redact, super) VALUES (?,?,?,?,?,?,?)", admins)
db.conn.commit()

# Populate Sell table
sells = []
for i in range(10):
    transaction_id = random.randint(1, 10)
    client_id = random.randint(1, 10)
    from_wh = random.randint(1, 5)
    sells.append((transaction_id, client_id, from_wh))
db.cursor.executemany("INSERT INTO Sell (transaction_id, client_id, from_wh) VALUES (?,?,?)", sells)
db.conn.commit()

# Populate Transactions table
transactions = []
for i in range(10):
    type = random.choice(["sell", "buy"])
    who = random.randint(1, 10)
    time = "2022-01-01"
    PS = f"PS{i}"
    transactions.append((type, who, time, PS))
db.cursor.executemany("INSERT INTO Transactions (type, who, time, PS) VALUES (?,?,?,?)", transactions)
db.conn.commit()

# Populate Transportation table
transportations = []
for i in range(10):
    transaction_id = random.randint(1, 10)
    from_wh = random.randint(1, 5)
    to_wh = random.randint(1, 5)
    transportations.append((transaction_id, from_wh, to_wh))
db.cursor.executemany("INSERT INTO Transportation (transaction_id, from_wh, to_wh) VALUES (?,?,?)", transportations)
db.conn.commit()

# Populate TransportationData table
transportation_data = []
for i in range(20):
    good_id = random.randint(1, 10)
    transportation_id = random.randint(1, 10)
    count = random.randint(1, 10)
    expire_date = "2022-01-01"
    transportation_data.append((good_id, transportation_id, count, expire_date))
db.cursor.executemany("INSERT INTO TransportationData (good_id, transportation_id, count, expire_date) VALUES (?,?,?,?)", transportation_data)
db.conn.commit()

acceptance_data = []
for i in range(20):
    good_id = random.randint(1, 10)
    acceptance_id = random.randint(1, 10)
    count = random.randint(1, 10)
    expire_date = "2022-01-01"
    acceptance_data.append((good_id, acceptance_id, count, expire_date))
db.cursor.executemany("INSERT INTO AcceptanceData (good_id, acceptance_id, count, expire_date) VALUES (?,?,?,?)", acceptance_data)
db.conn.commit()

# Populate Acceptance table
acceptances = []
for i in range(10):
    transaction_id = random.randint(1, 10)
    to_wh = random.randint(1, 5)
    acceptances.append((transaction_id, to_wh))
db.cursor.executemany("INSERT INTO Acceptance (transaction_id, to_wh) VALUES (?,?)", acceptances)
db.conn.commit()

# Populate SellData table
sell_data = []
for i in range(20):
    good_id = random.randint(1, 10)
    sell_id = random.randint(1, 10)
    count = random.randint(1, 10)
    expire_date = "2022-01-01"
    sell_data.append((good_id, sell_id, count, expire_date))
db.cursor.executemany("INSERT INTO SellData (good_id, sell_id, count, expire_date) VALUES (?,?,?,?)", sell_data)
db.conn.commit()

# Populate WriteOff table
write_offs = []
for i in range(10):
    transaction_id = random.randint(1, 10)
    from_wh = random.randint(1, 5)
    write_offs.append((transaction_id, from_wh))
db.cursor.executemany("INSERT INTO WriteOff (transaction_id, from_wh) VALUES (?,?)", write_offs)
db.conn.commit()

# Populate WriteOffData table
write_off_data = []
for i in range(20):
    good_id = random.randint(1, 10)
    write_of_id = random.randint(1, 10)
    count = random.randint(1, 10)
    expire_date = "2022-01-01"
    write_off_data.append((good_id, write_of_id, count, expire_date))
db.cursor.executemany("INSERT INTO WriteOffData (good_id, write_of_id, count, expire_date) VALUES (?,?,?,?)", write_off_data)
db.conn.commit()

db.close()
