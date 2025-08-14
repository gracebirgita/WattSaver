import sqlite3
import joblib
import numpy as np


def predict_hemat(data_input, model_path='mlp_model.pkl', scaler_path='scaler.pkl'):
    """
    Function untuk prediksi label hemat menggunakan model MLP yang sudah di-train
    
    Parameters:
    - data_input: List atau array dengan 9 nilai fitur [daya_va, kWh_tinggi, total_tinggi, 
                  kWh_sedang, total_sedang, kWh_rendah, total_rendah, pemakaian_kWh, biaya_tagihan]
    
    Returns:
    - prediction: Label prediksi (0, 1, atau 2)
    - probability: Probabilitas untuk setiap kelas
    """
    
    # Load model dan scaler
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    
    # Prepare data - pastikan bentuk array 2D
    if isinstance(data_input, list):
        input_data = np.array([data_input])
    else:
        input_data = np.array(data_input).reshape(1, -1)
    
    # Scale data
    input_scaled = scaler.transform(input_data)
    
    # Prediksi
    prediction = model.predict(input_scaled)[0]
    probability = model.predict_proba(input_scaled)[0]
    
    return prediction, probability

def get_collumnData(rumah_id):
    data = []
    conn = sqlite3.connect('WattSaverDB.db')
    selectQuery = "SELECT * FROM rumah WHERE rumah_id = ?"
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(selectQuery, (rumah_id,))

    rows = cursor.fetchall()

    #Akses berdasarkan index
    print("=== Akses berdasarkan Index ===")
    for row in rows:
        print(f"Kolom daya_va: {row[1]}")  # Kolom pertama
        print(f"Kolom kWh_tinggi: {row[3]}")  # Kolom kedua
        print(f"Kolom total_tinggi: {row[4]}")  # Kolom ketiga
        print(f"Kolom kWh_sedang: {row[5]}")  # Kolom ketiga
        print(f"Kolom total_sedang: {row[6]}")  # Kolom ketiga
        print(f"Kolom kWh_rendah: {row[7]}")  # Kolom ketiga
        print(f"Kolom total_rendah: {row[8]}")  # Kolom ketiga
        print(f"Kolom pemakaian_kWh: {row[9]}")  # Kolom ketiga
        print(f"Kolom biaya_tagiah: {row[10]}")  # Kolom ketiga
        print("---")
        data.append(row[1])
        data.append(row[3])
        data.append(row[4])
        data.append(row[5])
        data.append(row[6])
        data.append(row[7])
        data.append(row[8])
        data.append(row[9])
        data.append(row[10])
    conn.close()
    return data

def get_houseLabel(rumah_id):
    # Cek apakah rumah_id ada terlebih dahulu
    if not check_rumah_exists(rumah_id):
        print(f"Error: Rumah ID {rumah_id} tidak ditemukan dalam database")
        return None
    
    data = get_collumnData(rumah_id=rumah_id)
    print(f"Data yang diambil: {data}")
    print(f"Jumlah fitur: {len(data)}")

    # Validasi data sebelum prediksi
    if len(data) == 9:
        prediction, prob = predict_hemat(data)
        print(f"Prediksi: {prediction}")
        print(f"Probabilitas kelas 0: {prob[0]:.4f}")
        print(f"Probabilitas kelas 1: {prob[1]:.4f}")
        print(f"Probabilitas kelas 2: {prob[2]:.4f}")
        label_map = {0: "hemat", 1: "wajar", 2: "boros"}
        print(f"Hasil: {label_map[prediction]}")
        return prediction
    else:
        print(f"Error: Data harus memiliki 9 fitur, tapi ditemukan {len(data)} fitur")
        print("Fitur yang diharapkan: [daya_va, kWh_tinggi, total_tinggi, kWh_sedang, total_sedang, kWh_rendah, total_rendah, pemakaian_kWh, biaya_tagihan]")
        return None


def check_rumah_exists(rumah_id):
    """
    Function untuk mengecek apakah rumah_id ada dalam database
    
    Parameters:
    - rumah_id: ID rumah yang akan dicek
    
    Returns:
    - True jika rumah_id ada, False jika tidak ada
    """
    conn = sqlite3.connect("WattSaverDB.db")
    cursor = conn.cursor()
    
    checkQuery = "SELECT COUNT(*) FROM rumah WHERE rumah_id = ?"
    cursor.execute(checkQuery, (rumah_id,))
    result = cursor.fetchone()
    
    conn.close()
    
    # Jika COUNT(*) > 0, berarti rumah_id ada
    return result[0] > 0

def update_rumah(rumah_id):
    """
    Function untuk mengupdate tabel rumah
    jika rumah_id belum ada (user baru) maka akan di input id nya ke database dengan default value semua 0 kecuali golongan kWh, diset 900

    """
    conn = sqlite3.connect("WattSaverDB.db")
    cursor = conn.cursor()
    
    # Cek apakah rumah_id ada
    checkQuery = "SELECT * FROM rumah WHERE rumah_id = ?"
    cursor.execute(checkQuery, (rumah_id,))
    result = cursor.fetchall()
    
    if result:
        print(f"Rumah ID {rumah_id} ditemukan!")
        print(f"Data: {result}")
        # Lakukan update di sini untuk table yang sudah ada (nanti isinya count data yang ada di table alat-alat)
    else:
        print(f"Rumah ID {rumah_id} tidak ditemukan dalam database")
        insertQuery = """
        INSERT INTO rumah (
            rumah_id, daya_va, jumlah_penghuni,
            kWh_tinggi, total_tinggi, kWh_sedang, total_sedang,
            kWh_rendah, total_rendah, pemakaian_kWh, biaya_tagihan, label_hemat
        ) VALUES (?, 900, 0, 0.0, 0, 0.0, 0, 0, 0, 0, 0, 0);
        """
        cursor.execute(insertQuery, (rumah_id,))
        conn.commit()
        print("insert data baru berhasil")
    
    conn.close()
    return len(result) > 0

def update_alat(rumah_id, watt, jumlah, waktu_penggunaan):
    conn = sqlite3.connect("WattSaverDB.db")
    cursor = conn.cursor()
    pass

def delete_alat(rumah_id, alat_id):
    pass

def delete_user(rumah_id):
    pass


rumah_id = "R001"

# Cara 1: Menggunakan function khusus untuk pengecekan
print("=== Pengecekan Keberadaan Rumah ID ===")
if check_rumah_exists(rumah_id):
    print(f"Rumah ID {rumah_id} ada dalam database")
    get_houseLabel(rumah_id=rumah_id)
else:
    print(f"Rumah ID {rumah_id} tidak ada dalam database")

print("\n=== Update Rumah ===")
update_rumah(rumah_id=rumah_id)

# Test dengan rumah_id yang berbeda
print("\n=== Test dengan rumah_id lain ===")
test_ids = ["R001", "R002", "R999"]
for test_id in test_ids:
    exists = check_rumah_exists(test_id)
    status = "Ada" if exists else "Tidak ada"
    print(f"Rumah ID {test_id}: {status}")