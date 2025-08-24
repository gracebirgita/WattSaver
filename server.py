from flask import Flask, render_template, request, url_for, session, redirect, flash
# from waitress import serve
# import libsql_client
# from libsql_client import create_client
import libsql
import sqlite3
import time
import joblib
import numpy as np
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus
from dotenv import load_dotenv
import os
import time
import random

load_dotenv("enviro.env")
# load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

database_domain = os.getenv('database')
API_KEY = os.getenv('auth_token')

app = Flask(__name__)
app.secret_key = 'secret-key'

# Debug print saat modul di-import (akan jalan meskipun via gunicorn)
print(">>> Railway PORT (saat import):", os.environ.get("PORT"))

def get_db():
    # koneksi turso
    conn = libsql.connect(
        database=database_domain,
        auth_token=API_KEY
    )
    # conn = sqlite3.connect('WattSaverDB-newest.db')
    return conn

# generate rumah_id
def generate_rumahID(conn):
    cur = conn.cursor()
    cur.execute('SELECT rumah_id FROM Rumah ORDER BY rumah_id DESC LIMIT 1')
    last_id = cur.fetchone()

    if last_id:
        last_num = int(last_id[0][1:]) # R
        new_row = last_num+1
    else:
        new_row=1
    return f"R{new_row:03d}" # karakter ke 3 setelah r


def check_user_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM User")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    conn.close()

def check_rumah_table():
    conn= get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Rumah")
    rows = cur.fetchall()
    for row in rows:
        print(row)

def check_rumahid_intime(user_id):
    # cek data rumah_id milik user sudah ada/blm
    bulan = time.localtime().tm_mon
    tahun = time.localtime().tm_year

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT rumah_id FROM Rumah WHERE user_id=? AND bulan=? AND tahun=?", (user_id,bulan, tahun))
    data_rumah = cur.fetchone() # row data

    if data_rumah:
        print(f'rumah_id for {user_id} : {data_rumah} at {bulan}/{tahun}')
    else:
        print(f'rumah_id for {user_id} not found..')
        # Cari rumah terakhir milik user
        cur.execute("SELECT * FROM Rumah WHERE user_id=? ORDER BY tahun DESC, bulan DESC LIMIT 1", (user_id,))
        last_rumah = cur.fetchone()
        print(f'last rumah_id for {user_id} : {last_rumah}')
        rumah_id_baru = generate_rumahID(conn)
        if last_rumah:
            # Copy data dari rumah lama ke rumah baru, update bulan & tahun
            cur.execute("""
                INSERT INTO Rumah (
                    rumah_id, user_id, daya_va, 
                    kWh_tinggi, total_tinggi, 
                    kWh_sedang, total_sedang, 
                    kWh_rendah, total_rendah, 
                    pemakaian_kWh, biaya_tagihan, 
                    bulan, tahun, label, target_pemakaian
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rumah_id_baru, user_id,
                last_rumah[2], last_rumah[3], last_rumah[4], last_rumah[5],
                last_rumah[6], last_rumah[7], last_rumah[8], last_rumah[9],
                last_rumah[10],
                bulan, tahun, last_rumah[13], last_rumah[14]
            ))
            # Copy semua alat dari rumah lama ke rumah baru
            for table_name in ["Alat_tinggi", "Alat_sedang", "Alat_rendah"]:
                cur.execute(f"SELECT * FROM {table_name} WHERE rumah_id=?", (last_rumah[0],))
                alat_rows = cur.fetchall()
                print(alat_rows[0])
                for alat in alat_rows:
                    # Buat alat_id baru
                    alat_id_baru = generate_alatID(conn, alat[3])
                    # Asumsi kolom: alat_id, nama_alat, rumah_id, watt, jumlah_alat, waktu_penggunaan, total_biaya, tingkat_kepentingan
                    cur.execute(f"""
                        INSERT INTO {table_name} (
                            alat_id, rumah_id, watt, jumlah_alat, waktu_penggunaan, total_biaya, nama_alat, tingkat_kepentingan
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        alat_id_baru, rumah_id_baru, alat[2], alat[3], alat[4], alat[5], alat[6], alat[7]
                    ))
        else:
            # User belum pernah punya rumah, buat baru kosong
            cur.execute("""INSERT INTO Rumah
                        (rumah_id, user_id, 
                        target_pemakaian, daya_va, 
                        kWh_tinggi, total_tinggi,
                        kWh_sedang,total_sedang,
                        kWh_rendah, total_rendah,
                        pemakaian_kWh, biaya_tagihan,
                        bulan, tahun,
                        label
                        ) VALUES (?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ?, ?, 0)""", 
                        (generate_rumahID(conn), user_id, bulan, tahun))
    conn.commit()
    conn.close()
    check_rumah_table()


def generate_alatID(conn, watt):
    if watt in range(700,2000):
        prefix = "AT"
        table_name= "Alat_tinggi"
        # return f"AR{new_row:03d}"
    elif watt in range(150,700):
        # return f"AS{new_row:03d}"
        prefix = "AS"
        table_name= "Alat_sedang"
    elif watt <150:
        prefix = "AR"
        table_name= "Alat_rendah"
        # return f"AR{new_row:03d}"
    else:
        print("tingkat kepentingan out-of-range")
        return None
    
    # Gunakan waktu dan random agar unik
    unique_part = f"{int(time.time()*1000)}{random.randint(100,999)}"
    alat_id_baru = f"{prefix}{unique_part}"

    return alat_id_baru


def get_rumah_id():
    user_id = session.get('user_id')

    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT rumah_id FROM Rumah WHERE user_id=?', (user_id,))
    rumah_id = cur.fetchone() # row data
    conn.close()
    if rumah_id:
        return rumah_id[0]
    return None


# GET jumlah_alat based on kepentingan
def get_jumlah_alat(watt, nama_alat):
    conn = get_db()
    cur = conn.cursor()

    if watt in range(700,2000): #tinggi
        cur.execute("SELECT jumlah_alat FROM Alat_tinggi WHERE nama_alat=?", (nama_alat))
        result = cur.fetchone()
    elif watt in range(150,700): #sedang
        cur.execute("SELECT jumlah_alat FROM Alat_sedang WHERE nama_alat=?", (nama_alat))
        result = cur.fetchone()
    elif watt < 150: #rendah
        cur.execute("SELECT jumlah_alat FROM Alat_rendah WHERE nama_alat=?", (nama_alat))
        result = cur.fetchone()
    else:
        result=None

    if result:
        jumlah = result[0]

    conn.close()
    return jumlah

def get_status_count():
    rumah_id = get_latest_rumah_id(session.get('user_id'))
    conn=get_db()
    cur = conn.cursor()
    total_count={}

    for key in[
        ["total_tinggi"],
        ["total_sedang"],
        ["total_rendah"]
    ]:

        cur.execute("SELECT total_tinggi, total_sedang, total_rendah FROM Rumah WHERE rumah_id=?",
                    (rumah_id,))
        count = cur.fetchone()
        conn.close()

        if count:
            total_count={
                "total_tinggi": count[0] or 0,
                "total_sedang": count[1] or 0,
                "total_rendah": count[2] or 0
            }
        else:
            total_count={
                "total_tinggi": 0,
                "total_sedang": 0,
                "total_rendah": 0
            }
        return total_count


def check_target_filled():
    user_id = session.get('user_id')
    conn=get_db()
    cur = conn.cursor()
    cur.execute('SELECT target_pemakaian, daya_va FROM Rumah WHERE user_id=?', (user_id,))
    target = cur.fetchone()
    conn.close()

    if not target or not target[0] or not target[1]:
        print(f"Target pemakaian atau daya_va belum diatur untuk user_id: {user_id}")
        return False

    return True

def recommend_device_usage_by_rumah(rumah_id):
    # Ambil data perangkat untuk rumah_id tertentu
    conn = get_db()
    cur = conn.cursor()
    devices_list = []
    kepentingan_dict = {1: "Rendah", 2: "Sedang", 3: "Tinggi"}
    min_usage_pct = {'Rendah': 0.1, 'Sedang': 0.2, 'Tinggi': 0.5}

    for table_name, status in [
        ("Alat_rendah", "Rendah"),
        ("Alat_sedang", "Sedang"),
        ("Alat_tinggi", "Tinggi")
    ]:
        cur.execute(f"""
            SELECT nama_alat, jumlah_alat, total_biaya, tingkat_kepentingan, watt, waktu_penggunaan, alat_id
            FROM {table_name}
            WHERE rumah_id=?
        """, (rumah_id,))
        rows = cur.fetchall()
        for row in rows:
            nama_alat = row[0]
            jml_alat = row[1]
            biaya_tagihan = int(float(row[2]))
            kepentingan = row[3]
            watt = float(row[4])
            waktu_penggunaan = float(row[5])
            total_kWh = float(jml_alat) * float(watt/1000) * float(waktu_penggunaan)
            kepentingan_str = kepentingan_dict[kepentingan]
            min_usage = min_usage_pct[kepentingan_str]
            alat_id = row[6]
            devices_list.append({
                'nama': nama_alat,
                'jumlah': jml_alat,
                'total_kWh': round(total_kWh,2),
                'total_biaya': biaya_tagihan,
                'kepentingan': kepentingan_str,
                'status' : status,
                'watt':watt,
                'jml_alat': jml_alat,
                'min_usage': min_usage,
                'waktu_penggunaan': waktu_penggunaan,
                'alat_id' : alat_id,
            })
    # Ambil data rumah
    cur.execute("SELECT daya_va, target_pemakaian, biaya_tagihan FROM Rumah WHERE rumah_id=?", (rumah_id,))
    rumah_row = cur.fetchone()
    conn.close()
    if not rumah_row:
        return []
    daya_va, target_pemakaian, biaya_tagihan_now = rumah_row
    print('tagihan by rumah: ', biaya_tagihan)
    print('target by rumah: ', target_pemakaian)

    tarif_listrik = {
        900: 1352,
        1300: 1444.7,
        2200: 1444.7,
        3500: 1699.53
    }
    biaya_per_kwh = tarif_listrik.get(daya_va, 1352)

    if float(biaya_tagihan_now) < float(target_pemakaian):
        print(biaya_tagihan, ' < ', target_pemakaian)
        return "not"

    # Optimasi
    model_opt = LpProblem("optimasi_penggunaan_listrik", LpMinimize)
    jam_vars = {}
    for device in devices_list:
        device_id = device['alat_id']
        min_jam = device['waktu_penggunaan'] * device['min_usage']
        max_jam = device['waktu_penggunaan']
        jam_vars[device_id] = LpVariable(f"Jam_{device_id}", lowBound=min_jam, upBound=max_jam)
    if not jam_vars:
        return []
    model_opt += lpSum([
        ((device['watt'] * device['jml_alat'] * jam_vars[device['alat_id']]) / 1000) * 30 * biaya_per_kwh
        for device in devices_list if device['alat_id'] in jam_vars
    ]), "total_cost_monthly"
    model_opt += lpSum([
        ((device['watt'] * device['jml_alat'] * jam_vars[device['alat_id']]) / 1000) * 30 * biaya_per_kwh
        for device in devices_list if device['alat_id'] in jam_vars
    ]) <= target_pemakaian, "budget_constraint"
    model_opt.solve()
    hasil_optimasi = []
    if model_opt.status == 1:
        for device in devices_list:
            device_id = device['alat_id']
            if device_id not in jam_vars:
                continue
            jam_optimal = jam_vars[device_id].value()
            jam_awal = device['waktu_penggunaan']
            pengurangan_jam = jam_awal - jam_optimal
            penghematan_kwh = ((device['watt'] * device['jml_alat'] * pengurangan_jam) / 1000) * 30
            penghematan_biaya = penghematan_kwh * biaya_per_kwh
            hasil_optimasi.append({
                'nama': device['nama'],
                'pengurangan_jam': pengurangan_jam,
                'jumlah_alat': device['jml_alat'],
                'biaya_hemat': rupiah_format(penghematan_biaya),
            })
    return hasil_optimasi


### main function in page ###

# set target_expense & tarif_group -> analisis target-form
@app.route('/get_month_target', methods=['POST'])
def get_month_target():
    user_id = session.get('user_id')
    rumah_id_terbaru = get_latest_rumah_id(user_id)
    print("USER ID -month target= ", user_id)
    if request.method=='POST':
        target_expense = request.form.get('target-expense')
        tarif_group = request.form.get('tarif-group')

        try:
            target_expense = int(target_expense)
        except ValueError:
            flash('Masukan nominal target(Rupiah) berupa angka', 'target-form')
            return redirect(url_for('analisis'))
        if not tarif_group:
            flash('Input golongan tarif', 'target-form')
            return redirect(url_for('analisis'))

        conn= get_db()
        cur= conn.cursor()
        cur.execute("UPDATE Rumah SET target_pemakaian=?, daya_va=? WHERE rumah_id=?", (target_expense, tarif_group, rumah_id_terbaru))
        conn.commit()
        conn.close()

        # check data update
        check_rumah_table()
        flash('Target disimpan', 'target-form')

        return redirect(url_for('analisis'))
    return render_template('analisis.html')

# check status device based on watt input
def get_device_status(watt):
    # pass
    # range_watt = {
    # "tinggi": (700, 2000),
    # "sedang": (150, 450),
    # "rendah": (10, 150)
    # }
    if watt in range(700,2000):
        return "Alat_tinggi"
    elif watt in range(150,700):
        return "Alat_sedang"
    elif watt <150:
        return "Alat_rendah"
    else:
        print("tingkat kepentingan out-of-range")


# check alat table
def check_alat_table(status):
    table_name = get_device_status(status)
    conn= get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()
    conn.close()
    for row in rows:
        print(row)

# get daya_va
def get_daya_group():
    conn = get_db()
    cur = conn.cursor()
    rumah_id = get_latest_rumah_id(session.get('user_id'))

    cur.execute("SELECT daya_va FROM Rumah WHERE rumah_id=?", (rumah_id,))
    daya_va = cur.fetchone()
    conn.close()
    if daya_va:
        print(f"Daya VA : {daya_va}")
        return daya_va[0]
    else:
        print("daya not found..")
        return 900

# update pemakaian_kwh Rumah
def update_pemakaian_kwh():
    rumah_id = get_latest_rumah_id(session.get('user_id'))
    conn = get_db()
    cur = conn.cursor()

    tarif_listrik = {
        900: 1352,
        1300: 1444.7,
        2200: 1444.7,
        3500: 1699.53
    }

    # get 3 status kwh
    cur.execute("SELECT kWh_tinggi, kWh_sedang, kWh_rendah,daya_va FROM Rumah WHERE rumah_id=?",
                (rumah_id,))
    row=cur.fetchone()
    
    if row:
        kwh_tinggi = row[0] or 0
        kwh_sedang = row[1] or 0
        kwh_rendah = row[2] or 0
        daya= row[3] or 0
    else:
        kwh_tinggi=kwh_sedang=kwh_rendah=daya=0

    # update pemakaian_kwh
    pemakaian_kwh = kwh_rendah+kwh_tinggi+kwh_sedang
    biaya_tagihan = pemakaian_kwh*tarif_listrik[daya]
    cur.execute("UPDATE Rumah SET pemakaian_kWh=?, biaya_tagihan=? WHERE rumah_id=?", 
                (pemakaian_kwh, biaya_tagihan, rumah_id))

    conn.commit()
    conn.close()


# 2. add new device
@app.route('/add_new_device', methods=['POST'])
def add_new_device():
    rumah_id = get_latest_rumah_id(session.get('user_id'))
    name = request.form.get('device-name')
    amount = request.form.get('device-jml')
    important = request.form.get('device-kepentingan')
    important = int(important)
    watt = request.form.get('device-watt')
    print("watt device : ", watt)

    table_name = get_device_status(float(watt))
    usage_hours = request.form.get('device-jam') # jam/hari
    # total_biaya = round(kwh * biaya_per_kwh/1000, 2)
    daya_va = get_daya_group()
    tarif_listrik = {
        900: 1352,
        1300: 1444.7,
        2200: 1444.7,
        3500: 1699.53
    }

    biaya_per_kwh = tarif_listrik[daya_va]
    biaya_tagihan = ((float(watt)/1000) *float(usage_hours)) *biaya_per_kwh

    # query
    conn = get_db()
    cur = conn.cursor()

    # jika device dgn watt & jam belum ada -> add
    alat_id=generate_alatID(conn, float(watt))
    cur.execute(f"""
    INSERT INTO {table_name}
                (alat_id,
                nama_alat,
                rumah_id,
                watt,
                jumlah_alat,
                waktu_penggunaan,
                total_biaya,
                tingkat_kepentingan)
                VALUES (?,?,?,?,?,?, ?,?)
    """, (alat_id, name, rumah_id, watt, amount, usage_hours, biaya_tagihan, important))
    conn.commit()
    conn.close()
    check_alat_table(important)
    update_pemakaian_kwh()

    flash('perangkat berhasil ditambahkan', 'add-device-form')
    return redirect(url_for('analisis'))


#### page route ###
@app.route("/")
# beranda
@app.route('/index')
def index():
    username = session.get('username')
    user_id = session.get('user_id')
    if username:
        print(f"Username = {username} & ID = {user_id}")
    return render_template("index.html", username=username)

# logged in status
@app.context_processor
def inject_logged_in():
    return dict(logged_in =('email' in session))

# register
@app.route('/register', methods=['POST', 'GET']) # get user data, post to db
def register():
    if request.method=='POST':
        username = request.form['username'] # name atribut
        password = request.form['password']
        email = request.form['email']

        if len(password) < 5:
            flash("Password minimal 5 karakter")
            return render_template('register.html')
        
        # connect db
        conn = get_db()
        cur = conn.cursor()
        
        # check duplicate account 
        cur.execute('SELECT * FROM User WHERE email=?', (email,))
        account_exist = cur.fetchone() # row from database
        if account_exist:
            conn.close()
            flash('Akun sudah ada, silahkan login')
            return render_template('register.html')

        cur.execute('INSERT INTO User(user_name, email, password) VALUES (?,?,?)', (username, email,password))
        conn.commit()
        conn.close()

        # cek data update
        check_user_db()
        flash('Registrasi berhasil! silahkan login')
        return redirect(url_for('login'))

    return render_template('register.html')

# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method =='POST':
        # username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # connect db
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM User WHERE email=? AND password=?', (email, password))
        user = cur.fetchone()
        conn.close()

        if user:
            # session['username']= username
            session['email'] = email
            session['user_id'] = user[0] # index kolom ke 0
            print("set session userid : ", session['user_id'])

            # cek apakah sudah punya rumah_id pada bln/thn tertentu
            user_id = session.get('user_id')
            check_rumahid_intime(user_id)
            
            return redirect(url_for('index'))
        else:
            flash('nama pengguna  atau password tidak sesuai')
    return render_template('login.html')

@app.route('/logout')
def logout():
    # session.pop('username', None)
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('index'))


# GET data for table
# def get_data_table():
#     conn = get_db()
#     cur = conn.cursor()

#     # get devices user
#     cur.execute("""
#     SELECT ar.jumlah_alat, as.jumlah_alat, at.jumlah_alat
#     FROM  Alat_rendah ar, Alat_sedang as, Alat_tinggi at 
#     """)
    
#     cur.execute('SELECT * FROM Rumah WHERE user_id=?', (session['user_id']))
#     rows = cur.fetchall()
#     conn.close()

#     devices =[]
#     for row in rows:
#         # raw row from db
#         nama, jumlah, pemakaian_kwh, biaya, kepentingan, status = row
        
#         jumlah = get_jumlah_alat(kepentingan, nama)
        
#         devices.append({
#             'nama' : nama,
#             'jumlah': jumlah,
#             'total_kwh': pemakaian_kwh,
#             'biaya': biaya,
#             'kepentingan': kepentingan,
#             'status' : status
#         })
#         return devices

    # modif column
    # <th scope="col">Nama</th>
    #                 <th scope="col">Jumlah</th>
    #                 <th scope="col">Total (kWh)</th>
    #                 <th scope="col">Total Biaya (Rp)</th>
    #                 <th scope="col">Kepentingan</th>
    #                 <th scope="col">Status</th>

# update_rumah_from_alat
# def update_rumah_from_alat(rumah_id):
#     conn = get_db()
#     cur = conn.cursor()

#     status_category = [
#         ("Alat_tinggi", "kWh_tinggi", "total_tinggi"),
#         ("Alat_sedang", "kWh_sedang", "total_sedang"),
#         ("Alat_rendah", "kWh_rendah", "total_rendah")
#     ]

#     kwh_dict={}
#     alat_dict={}

#     for table_name, kwh_col, alat_col in status_category:
#         cur.execute(f"""
#             SELECT SUM(jumlah_alat), SUM(jumlah_alat*watt*waktu_penggunaan/1000.0)
#                 FROM {table_name}
#                 WHERE rumah_id=?
#         """, (rumah_id,))

#         jumlah, total_kwh = cur.fetchone()
#         kwh_dict[kwh_col] = total_kwh or 0
#         alat_dict[alat_col] = jumlah or 0


#     # update Rumah (main table)
#     cur.execute(f"""
#         UPDATE Rumah SET
#             kWh_tinggi=?,
#             kWh_sedang=?,
#             kWh_rendah=?,
#             total_tinggi=?,
#             total_sedang=?,
#             total_rendah=?,
#             WHERE rumah_id=?
#         """, (
#             kwh_dict['kWh_tinggi'],
#             kwh_dict['kWh_sedang'],
#             kwh_dict['kWh_rendah'],
#             alat_dict['total_tinggi'],
#             alat_dict['total_sedang'],
#             alat_dict['total_rendah'],
#             rumah_id
#         ))
#     row = cur.fetchone()

#     pemakaian_kwh =

#     cur.execute(f"""
#         UPDATE Rumah SET
#             pemakaian_kWh=?
#             WHERE rumah_id=?
#         """, (
#             pemakaian_kwh,
#             rumah_id
#         ))
    
#     conn.commit()
#     conn.close()
def get_latest_rumah_id(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT rumah_id FROM Rumah
        WHERE user_id=?
        ORDER BY tahun DESC, bulan DESC
        LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

# 3. GET data tabel live
def get_table_devices(user_id):
    conn = get_db()
    cur = conn.cursor()
    devices=[]

    rumah_id = get_latest_rumah_id(user_id)

    # kepentingan
    kepentingan_dict={
        1:"Rendah",
        2:"Sedang",
        3:"Tinggi"
    }

    min_usage_pct = {'Rendah': 0.1, 'Sedang': 0.2, 'Tinggi': 0.5}
    # status
    for table_name, status in [
        ("Alat_rendah", "Rendah"),
        ("Alat_sedang", "Sedang"),
        ("Alat_tinggi", "Tinggi")
    ]:
        cur.execute(f"""
            SELECT nama_alat, jumlah_alat, total_biaya, tingkat_kepentingan, watt, waktu_penggunaan, alat_id
            FROM {table_name}
            WHERE rumah_id=?
        """, (rumah_id,))
        
        rows = cur.fetchall()

        if not rows:
            print(f"tidak ada perangkat di tabel {table_name}")
            continue

        print(f"Rows fetch from {table_name}: {rows}")
        for row in rows:
            nama_alat = row[0]
            jml_alat = row[1]
            biaya_tagihan = int(float(row[2]))
            kepentingan = row[3]
            watt = float(row[4])
            waktu_penggunaan = float(row[5])
            total_kWh = float(jml_alat) * float(watt/1000) * float(waktu_penggunaan)

            kepentingan_str = kepentingan_dict[kepentingan]
            min_usage = min_usage_pct[kepentingan_str]
            alat_id = row[6]

            devices.append({
                'nama': nama_alat,
                'jumlah': jml_alat,
                'total_kWh': round(total_kWh,2),
                'total_biaya': rupiah_format(biaya_tagihan),
                'kepentingan': kepentingan_str,
                'status' : status,
                
                # lp value
                'watt':watt,
                'jml_alat': jml_alat,
                'min_usage': min_usage, # max persentase pengurangan
                'waktu_penggunaan': waktu_penggunaan, #jam awal
                'alat_id' : alat_id,
            })
            # print(f"Added device: {devices[-1]}")

    conn.close()
    print(f"Final devices list: {devices}")
    # update -> table Rumah (kwh & total alat)
    # update -> Rumah (pemakaian_kWh = kwh tinggi+ sedang+rendah)
    return devices

def check_total_kwh():
    rumah_id = get_latest_rumah_id(session.get('user_id'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT pemakaian_kWh FROM Rumah WHERE rumah_id=?", (rumah_id,))
    kwh_row = cur.fetchone()
    print(kwh_row)
    conn.close()
    tot_konsumsi = kwh_row[0] if kwh_row else 0

    return tot_konsumsi

def check_biaya_tagihan():
    rumah_id = get_latest_rumah_id(session.get('user_id'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT biaya_tagihan FROM Rumah WHERE rumah_id=?", (rumah_id,))
    biaya_row = cur.fetchone()
    print(biaya_row)
    conn.close()
    tot_konsumsi = biaya_row[0] if biaya_row else 0

    return tot_konsumsi

# select target biaya listrik
def check_target_pemakaian():
    rumah_id = get_latest_rumah_id(session.get('user_id'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT target_pemakaian FROM Rumah WHERE rumah_id=?", (rumah_id,))
    target_row = cur.fetchone()
    print(target_row)
    conn.close()
    target_biaya = target_row[0] if target_row else 0
    return target_biaya

def rupiah_format(amount):
    try:
        return f"{amount:,.0f}".replace(",", ".")
    except:
        print('rupiah format eror')
        return str(amount)

# 1. get feature input for model
def get_feature_data():
    rumah_id=get_latest_rumah_id(session.get('user_id'))
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT daya_va, 
            kWh_tinggi, total_tinggi, 
            kWh_sedang, total_sedang, 
            kWh_rendah, total_rendah, 
            pemakaian_kWh, biaya_tagihan 
        FROM Rumah WHERE rumah_id=?    
    """, (rumah_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        feature_data = list(row)
        return feature_data
    else:
        print("feature data not found - rumah_id: ", rumah_id)
        return []
        

# 2. get model, scaler, get parameter untuk klasifikasi
def predict_hemat(model_path='model/random_forest.pkl', scaler_path='model/minmax_scaler.pkl'):
    """
    Function untuk prediksi label hemat menggunakan model MLP yang sudah di-train
    
    Parameters:
    - data_input: List atau array dengan 9 nilai fitur 
    [daya_va, kWh_tinggi, total_tinggi, 
            kWh_sedang, total_sedang, 
            kWh_rendah, total_rendah, 
            pemakaian_kWh, biaya_tagihan]
    
    Returns:
    - prediction: Label prediksi (0, 1, atau 2)
    - probability: Probabilitas untuk setiap kelas
    """
    # Load model dan scaler
    try : 
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        print("model load SUCESS ...")
    except:
        print("model+scaler not found")
    finally:
        print("get model+scalar done")

    # cek feature input
    feature_input = get_feature_data()
    if feature_input:
        print("feature input data : ", feature_input)
    else:
        print("feature input not fount..")    

    # Prepare data - pastikan bentuk array 2D
    if isinstance(feature_input, list):
        feature_input = np.array([feature_input])
    else:
        feature_input = np.array(feature_input).reshape(1, -1)
    
    # Scale data
    input_scaled = scaler.transform(feature_input)
    
    # Prediksi
    prediction = model.predict(input_scaled)[0]
    probability = model.predict_proba(input_scaled)[0]
    
    return prediction, probability

def update_predict_label(prediction, rumah_id):
    conn = get_db()
    cur = conn.cursor()
    print(f"update prediction : {int(prediction)}, rumah_id = {rumah_id}")
    cur.execute("UPDATE Rumah SET label=? WHERE rumah_id=?",
                (int(prediction), rumah_id,))
    conn.commit()
    conn.close()

def get_label_prediction():
    rumah_id = get_latest_rumah_id(session.get('user_id'))
    
    data_feature = get_feature_data()
    if not data_feature or len(data_feature) !=9:
        print("fitur input data tidak valid untuk predict")
        return None
    
    print(f"Data feature : {data_feature}")
    print(f"amount feature : {len(data_feature)}")

    # validation before predict
    if len(data_feature)==9:
        # predict
        prediction, prob = predict_hemat()
        print(f"Prediction: {prediction}")
        print(f"Probability class: {prob}")

        # mapping predict label
        label_map= {0:"Hemat", 1:"Normal", 2:"Boros"}
        label = label_map[prediction]
        print(f"Predict label : {label}")

        # update to db
        update_predict_label(prediction, rumah_id)

        return label
    else:
        print("Error: feature data not valid..")
        return None

def recommend_device_usage():
    user_id = session.get('user_id')
    # label_map= {"Hemat":0, "Normal":1, "Boros":2}
    # label_str = get_label_prediction()
    # label = label_map[label_str]

    # make optimation model -> minimalize electric usage
    model_opt = LpProblem("optimasi_penggunaan_listrik", LpMinimize)
    # variabel : waktu_penggunaan -> 3 tabel
    devices_list = get_table_devices(user_id)
    jam_vars={} # var keputusan tiap alat
    daya_va = get_daya_group()
    if not daya_va:
        print("Daya VA tidak ditemukan")
        return []
    
    # target biaya user
    target_pemakaian = float(check_target_pemakaian())
    print("target rekomend",target_pemakaian)
    # biaya bulan sblmnya(real)
    biaya_tagihan_now = float(check_biaya_tagihan())*30
    print("tagihan now rekomend",biaya_tagihan_now)

    if biaya_tagihan_now < target_pemakaian:
        print('tagihan < target (hemat) -> not')
        return "not"

    tarif_listrik = {
        900: 1352,
        1300: 1444.7,
        2200: 1444.7,
        3500: 1699.53
    }
    biaya_per_kwh = tarif_listrik[daya_va]
    if not biaya_per_kwh:
        print("tarif listrik daya not found in recommendation")
        return []
    
    print("\n\nDEVICE LIST")
    for device in devices_list:
        device_id = device['alat_id']  # Gunakan ID alat dari database
        print(f"ID perangkat: {device_id}")

        min_jam = device['waktu_penggunaan'] * device['min_usage']
        max_jam = device['waktu_penggunaan']

        # Buat variabel keputusan berdasarkan ID alat
        jam_vars[device_id] = LpVariable(f"Jam_{device_id}", lowBound=min_jam, upBound=max_jam)

    if not jam_vars:
        print("Tidak ada perangkat valid untuk optimasi.")
        return []

    # Fungsi tujuan: Meminimalkan biaya bulanan
    model_opt += lpSum([
        ((device['watt'] * device['jml_alat'] * jam_vars[device['alat_id']]) / 1000) * 30 * biaya_per_kwh
        for device in devices_list if device['alat_id'] in jam_vars
    ]), "total_cost_monthly"

    model_opt += lpSum([
        ((device['watt'] * device['jml_alat'] * jam_vars[device['alat_id']]) / 1000) * 30 * biaya_per_kwh
        for device in devices_list if device['alat_id'] in jam_vars
    ]) <= target_pemakaian, "budget_constraint"

    # biaya_aktual = sum(
    #     ((device['watt'] * device['jml_alat'] * device['waktu_penggunaan']) / 1000) * 30 * biaya_per_kwh
    #     for device in devices_list
    # )
    # print("Biaya aktual (tagihan rekomendasi):", biaya_aktual)
    
    # total_biaya_min = sum(
    # ((device['watt'] * device['jml_alat'] * device['waktu_penggunaan'] * device['min_usage']) / 1000) * 30 * biaya_per_kwh
    # for device in devices_list
    # )
    # print("Total biaya minimum yang bisa dicapai:", total_biaya_min)
    # print("Target pemakaian:", target_pemakaian)

    # Solve optimization
    model_opt.solve()

    hasil_optimasi = []
    if model_opt.status == 1:  # Optimal/feasible
        for device in devices_list:
            device_id = device['alat_id']
            if device_id not in jam_vars:
                continue

            jam_optimal = jam_vars[device_id].value()
            jam_awal = device['waktu_penggunaan']
            pengurangan_jam = jam_awal - jam_optimal

            penghematan_kwh = ((device['watt'] * device['jml_alat'] * pengurangan_jam) / 1000) * 30
            penghematan_biaya = penghematan_kwh * biaya_per_kwh

            hasil_optimasi.append({
                'nama': device['nama'],
                'pengurangan_jam': pengurangan_jam,
                'jumlah_alat': device['jml_alat'],
                'biaya_hemat': rupiah_format(penghematan_biaya),
            })
            print(f"Device: {device['nama']}, Optimal Usage: {jam_optimal} hours/day")
    else:
        print(f"Optimasi gagal. Status: {LpStatus[model_opt.status]}")
    print("Hasil optimasi:", hasil_optimasi)
    return hasil_optimasi


@app.route('/analisis.html', methods=['GET'])
def analisis():
    devices = get_table_devices(session.get('user_id')) # get table-device
    rumah_id = get_rumah_id()
    target_set = check_target_filled() # set target
    listrik_perbulan = check_total_kwh()
    biaya_tagihan = check_biaya_tagihan()
    target_pemakaian = check_target_pemakaian()
    print(devices) # devices

    # chart js status count
    status_count = get_status_count()
    print(status_count)

    # label_prediction
    label_target = get_label_prediction()
    # rekomendasi_optimasi = recommend_device_usage()
    rekomendasi_optimasi = recommend_device_usage_by_rumah(rumah_id)
    total_penghematan = sum(
        float(hasil['biaya_hemat'].replace('Rp', '').replace(',', '').replace('.', '').strip())
        for hasil in rekomendasi_optimasi if 'biaya_hemat' in hasil
    )

    from_page = request.args.get('from_page', '')
    print(f'nav dari {from_page}')
    return render_template("analisis.html", 
                           devices=devices, 
                           target_set=target_set,
                           listrik_perbulan=round(listrik_perbulan,2),
                           biaya_tagihan=rupiah_format(biaya_tagihan),
                           target_pemakaian = rupiah_format(target_pemakaian),
                           label_target = label_target,
                           rekomendasi_optimasi=rekomendasi_optimasi,
                           total_penghematan= rupiah_format(total_penghematan),
                           status_count=status_count)
                        

@app.route('/edit.html', methods=['GET'])
def edit():
    from_page = request.args.get('from_page', '')
    print(f'nav dari {from_page}')

    user_id = session.get('user_id')
    devices = get_table_devices(user_id)
    return render_template('edit.html', devices=devices)

@app.route('/update_device', methods=['POST'])
def update_device():
    print("masuk update_device")
    print(request.method)
    print(request.form)
    total_str = request.form.get('total')
    if total_str is None:
        # Tidak ada field total, kemungkinan request dari form lain (misal: delete)
        return redirect(url_for('edit'))
    conn = get_db()
    try:
        cursor = conn.cursor()
        total = int(total_str)
        for i in range(1, total+1):
            alat_id = request.form.get(f'alat_id_{i}')
            nama = request.form.get(f'nama_{i}')
            jumlah = request.form.get(f'jumlah_{i}')
            kepentingan = request.form.get(f'kepentingan_{i}')
            watt = request.form.get(f'watt_{i}')
            jam = request.form.get(f'jam_{i}')

            daya_va = get_daya_group()
            tarif_listrik = {
                900: 1352,
                1300: 1444.7,
                2200: 1444.7,
                3500: 1699.53
            }

            biaya_per_kwh = tarif_listrik[daya_va]
            total_biaya = ((float(watt)/1000) *float(jam)) *float(biaya_per_kwh) *float(jumlah)
            print("jumlah diupdate device : ", jumlah, "nama: ", nama, "watt: ", watt)

            if "AT" in alat_id:
                cursor.execute("""
                    UPDATE Alat_tinggi
                    SET nama_alat=?, jumlah_alat=?, tingkat_kepentingan=?, watt=?, waktu_penggunaan=?, total_biaya=?
                    WHERE alat_id=?
                """, (nama, jumlah, kepentingan, watt, jam, total_biaya,alat_id))

            elif "AS" in alat_id:
                cursor.execute("""
                    UPDATE Alat_sedang
                    SET nama_alat=?, jumlah_alat=?, tingkat_kepentingan=?, watt=?, waktu_penggunaan=?, total_biaya=?
                    WHERE alat_id=?
                """, (nama, jumlah, kepentingan, watt, jam, total_biaya, alat_id))

            elif "AR" in alat_id:
                cursor.execute("""
                    UPDATE Alat_rendah
                    SET nama_alat=?, jumlah_alat=?, tingkat_kepentingan=?, watt=?, waktu_penggunaan=?, total_biaya=?
                    WHERE alat_id=?
                """, (nama, jumlah, kepentingan, watt, jam,total_biaya,alat_id))

            print("nama: ",nama,"jumlah diupdate device : ", jumlah, "kepentingan: ", kepentingan, "watt: ", watt, "jam: ", jam, "alat_id: ", alat_id, "total biaya: ", total_biaya)
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for('analisis'))

@app.route('/delete_device', methods=['POST'])
def delete_device():
    print("alat_id yang bakal dipake:", request.form.get('alat_id'))
    alat_id = request.form.get('alat_id')
    conn = get_db()
    try:
        cursor = conn.cursor()
        if "AT" in alat_id:
            cursor.execute("""
                DELETE FROM Alat_tinggi
                WHERE alat_id=?
            """, (alat_id,))
        elif "AS" in alat_id:
            cursor.execute("""
                DELETE FROM Alat_sedang
                WHERE alat_id=?
            """, (alat_id,))
        elif "AR" in alat_id:
            cursor.execute("""
                DELETE FROM Alat_rendah
                WHERE alat_id=?
            """, (alat_id,))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for('edit'))

@app.route('/history.html')
def history():
    user_id = session.get('user_id')

    label_map = {0: "Hemat", 1: "Normal", 2: "Boros"}
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
                    SELECT rumah_id, bulan, tahun, target_pemakaian, biaya_tagihan, label
                    FROM Rumah
                    WHERE user_id=?
                    ORDER BY tahun DESC, bulan DESC
                """, (user_id,))
    rumah_list = cur.fetchall()
    conn.close()
    nama_bulan = [
        '', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
        'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ]
    total_target = sum(rumah[3] for rumah in rumah_list)
    total_pengeluaran = sum(rumah[4] for rumah in rumah_list)
    total_penghematan = total_target - total_pengeluaran
    paling_hemat_rumah = None
    paling_hemat_nilai = None
    for rumah in rumah_list:
        selisih = rumah[3] - rumah[4]
        if (paling_hemat_nilai is None) or (selisih > paling_hemat_nilai):
            paling_hemat_nilai = selisih
            paling_hemat_rumah = rumah

    return render_template('history.html', rumah_list=rumah_list, nama_bulan=nama_bulan, total_penghematan=total_penghematan, paling_hemat_rumah=paling_hemat_rumah)


@app.route('/detail', methods=['GET'])
def detail():
    rumah_id = request.args.get('rumah_id')
    print('rumah_id detail: ', rumah_id)
    from_page = request.args.get('from_page', '')
    print(f"nav dari : {from_page}")

    #ambil data rumah dari DB
    conn = get_db()
    curr = conn.cursor()
    curr.execute("""
        SELECT rumah_id, user_id, target_pemakaian, daya_va, 
               kWh_tinggi, total_tinggi, 
               kWh_sedang, total_sedang, 
               kWh_rendah, total_rendah, 
               pemakaian_kWh, biaya_tagihan, 
               bulan, tahun, label
        FROM Rumah WHERE rumah_id=?
    """, (rumah_id,))
    rumah = curr.fetchone()

    # Ambil data perangkat untuk rumah ini
    devices = []
    kepentingan_dict = {1: "Rendah", 2: "Sedang", 3: "Tinggi"}
    for table_name, status in [
        ("Alat_rendah", "Rendah"),
        ("Alat_sedang", "Sedang"),
        ("Alat_tinggi", "Tinggi")
    ]:
        curr.execute(f"""
            SELECT nama_alat, jumlah_alat, total_biaya, tingkat_kepentingan, watt, waktu_penggunaan
            FROM {table_name}
            WHERE rumah_id=?
        """, (rumah_id,))
        rows = curr.fetchall()
        for row in rows:
            nama_alat = row[0]
            jml_alat = row[1]
            biaya_tagihan = int(float(row[2]))
            kepentingan = kepentingan_dict[row[3]]
            watt = float(row[4])
            waktu_penggunaan = float(row[5])
            total_kWh = float(jml_alat) * float(watt/1000) * float(waktu_penggunaan)
            devices.append({
                'nama': nama_alat,
                'jumlah': jml_alat,
                'total_kWh': round(total_kWh,2),
                'total_biaya': biaya_tagihan,
                'kepentingan': kepentingan,
                'status' : status,
                'watt':watt,
                'waktu_penggunaan': waktu_penggunaan,
            })
    conn.close()
    # Ambil data analisis dari rumah
    listrik_perbulan = rumah[10]  # pemakaian_kWh
    biaya_tagihan = rumah[11]     # biaya_tagihan
    target_pemakaian = rumah[2]   # target_pemakaian


    label_map = {0: "Hemat", 1: "Normal", 2: "Boros"}
    label_target = label_map.get(rumah[14], "Tidak diketahui")
    status_count = {"Rendah": 0, "Sedang": 0, "Tinggi": 0}
    for device in devices:
        status_count[device['status']] += 1
    # rekomendasi_optimasi = recommend_device_usage()
    rekomendasi_optimasi = recommend_device_usage_by_rumah(rumah_id)
    # Kirim data ke template detail.html
    return render_template(
        'detail.html',
        rumah=rumah,
        devices=devices,
        listrik_perbulan=round(listrik_perbulan,2),
        biaya_tagihan=rupiah_format(int(biaya_tagihan)),
        target_pemakaian=rupiah_format(int(target_pemakaian)),
        label_target=label_target,
        status_count=status_count,
        rekomendasi_optimasi=rekomendasi_optimasi
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ambil port dari Railway
    app.run(host="0.0.0.0", port=port)
    # serve(app, host= "0.0.0.0", port=8000)
    # app.run(debug=True)
