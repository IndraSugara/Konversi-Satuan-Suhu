from utils import konversi_suhu

def tampilkan_hasil(nilai, dari, ke, hasil):
    simbol = {
        "c": "°C",
        "f": "°F",
        "k": "K"
    }
    print(f"\n🔄 Hasil Konversi:")
    print(f"{nilai:.1f}{simbol[dari]} = {hasil:.1f}{simbol[ke]}")
    print("━━━━━━━━━━━━━━━━━━━━")

def main():
    print("🌡️  Program Konversi Suhu")
    print("=" * 30)
    
    try:
        # Input dari pengguna
        nilai_input = float(input("Masukkan nilai suhu: "))
        satuan_awal = input("Satuan asal (C/F/K): ").strip().lower()
        satuan_tujuan = input("Satuan tujuan (C/F/K): ").strip().lower()

        # Proses konversi
        result = konversi_suhu(nilai_input, satuan_awal, satuan_tujuan)

        # Tampilkan hasil atau error
        if isinstance(result, float):
            tampilkan_hasil(nilai_input, satuan_awal, satuan_tujuan, result)
        else:
            print(f"\n❌ {result}")

    except ValueError:
        print("\n❌ Input tidak valid! Harap masukkan angka untuk nilai suhu")
    except KeyboardInterrupt:
        print("\n\nOperasi dibatalkan oleh pengguna")
    except Exception as e:
        print(f"\n💥 Terjadi kesalahan tak terduga: {str(e)}")

if __name__ == "__main__":
    main()