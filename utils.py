def konversi_suhu(nilai, dari, ke):
    # Daftar satuan suhu
    satuan_valid = ["c", "f", "k"]
    dari = dari.lower()
    ke = ke.lower()
    
    # Cek satuan input
    if dari not in satuan_valid:
        return f"Error: Satuan asal '{dari}' tidak dikenal. Gunakan C, F, atau K"
    if ke not in satuan_valid:
        return f"Error: Satuan tujuan '{ke}' tidak dikenal. Gunakan C, F, atau K"

    # Validasi nilai minimal untuk masing-masing suhu
    batas_minimum = {
        "c": -273.15,
        "f": -459.67,
        "k": 0
    }
    
    if nilai < batas_minimum[dari]:
        return f"Error: Nilai {dari.upper()} tidak boleh kurang dari {batas_minimum[dari]}"

    # Jika satuan sama, langsung kembalikan nilai
    if dari == ke:
        return nilai

    # Konversi melalui Celsius sebagai perantara
    try:
        # Konversi ke celsius
        if dari == "c":
            celsius = nilai
        elif dari == "f":
            celsius = (nilai - 32) * 5/9
        elif dari == "k":
            celsius = nilai - 273.15

        # Dari Celsius ke satuan tujuan
        if ke == "c":
            hasil = celsius
        elif ke == "f":
            hasil = (celsius * 9/5) + 32
        elif ke == "k":
            hasil = celsius + 273.15

        return hasil

    except Exception as e:
        return f"Terjadi kesalahan saat konversi: {str(e)}"