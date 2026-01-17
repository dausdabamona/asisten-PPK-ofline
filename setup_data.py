#!/usr/bin/env python3
"""
PPK DOCUMENT FACTORY v3.0 - Setup Sample Data
==============================================
Script untuk membuat data contoh (pegawai, penyedia)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db_manager

def setup_sample_data():
    """Create sample data for testing"""
    
    print("=" * 60)
    print("SETUP SAMPLE DATA - PPK DOCUMENT FACTORY v3.0")
    print("=" * 60)
    
    db = get_db_manager()
    
    # Sample Pegawai
    pegawai_data = [
        {
            'nip': '197001011995031001',
            'nama': 'Ahmad Hidayat',
            'gelar_depan': '',
            'gelar_belakang': 'S.Pi., M.M.',
            'pangkat': 'Pembina',
            'golongan': 'IV/a',
            'jabatan': 'Kepala Bagian Umum',
            'unit_kerja': 'Bagian Umum',
            'npwp': '01.234.567.8-951.000',
            'is_ppk': 1,
            'is_ppspm': 0,
            'is_bendahara': 0,
            'is_pemeriksa': 1,
        },
        {
            'nip': '198005152005011001',
            'nama': 'Budi Santoso',
            'gelar_depan': '',
            'gelar_belakang': 'S.E., M.M.',
            'pangkat': 'Penata Tingkat I',
            'golongan': 'III/d',
            'jabatan': 'Kepala Sub Bagian Keuangan',
            'unit_kerja': 'Sub Bagian Keuangan',
            'npwp': '02.345.678.9-951.000',
            'is_ppk': 0,
            'is_ppspm': 1,
            'is_bendahara': 0,
            'is_pemeriksa': 0,
        },
        {
            'nip': '199001012015012001',
            'nama': 'Siti Rahayu',
            'gelar_depan': '',
            'gelar_belakang': 'S.E.',
            'pangkat': 'Penata',
            'golongan': 'III/c',
            'jabatan': 'Bendahara Pengeluaran',
            'unit_kerja': 'Sub Bagian Keuangan',
            'npwp': '03.456.789.0-951.000',
            'is_ppk': 0,
            'is_ppspm': 0,
            'is_bendahara': 1,
            'is_pemeriksa': 0,
        },
        {
            'nip': '198512122010011001',
            'nama': 'Andi Wijaya',
            'gelar_depan': '',
            'gelar_belakang': 'S.Kom.',
            'pangkat': 'Penata Muda Tingkat I',
            'golongan': 'III/b',
            'jabatan': 'Pranata Komputer',
            'unit_kerja': 'Sub Bagian Umum',
            'is_ppk': 0,
            'is_ppspm': 0,
            'is_bendahara': 0,
            'is_pemeriksa': 1,
        },
        {
            'nip': '199203152018011001',
            'nama': 'Dedi Kurniawan',
            'gelar_depan': '',
            'gelar_belakang': 'S.St.Pi.',
            'pangkat': 'Penata Muda',
            'golongan': 'III/a',
            'jabatan': 'Pengadministrasi',
            'unit_kerja': 'Sub Bagian Umum',
            'is_ppk': 0,
            'is_ppspm': 0,
            'is_bendahara': 0,
            'is_pemeriksa': 1,
        },
    ]
    
    print("\n📌 Menambahkan data Pegawai...")
    for peg in pegawai_data:
        try:
            db.save_pegawai(peg)
            print(f"   ✅ {peg['nama']}")
        except Exception as e:
            print(f"   ⚠️  {peg['nama']}: {e}")
    
    # Sample Penyedia
    penyedia_data = [
        {
            'nama': 'CV. Mitra Jaya Abadi',
            'nama_direktur': 'Hendra Kusuma',
            'jabatan_direktur': 'Direktur',
            'alamat': 'Jl. Ahmad Yani No. 45, Sorong',
            'kota': 'Sorong',
            'npwp': '01.123.456.7-951.000',
            'no_rekening': '1234567890',
            'nama_bank': 'Bank Papua',
            'nama_rekening': 'CV. Mitra Jaya Abadi',
            'telepon': '0951-321456',
            'is_pkp': 1,
        },
        {
            'nama': 'PT. Karya Mandiri Sejahtera',
            'nama_direktur': 'Ir. Bambang Sutrisno',
            'jabatan_direktur': 'Direktur Utama',
            'alamat': 'Jl. Basuki Rahmat No. 88, Sorong',
            'kota': 'Sorong',
            'npwp': '02.234.567.8-951.000',
            'no_rekening': '2345678901',
            'nama_bank': 'Bank BRI',
            'nama_rekening': 'PT. Karya Mandiri Sejahtera',
            'telepon': '0951-322567',
            'is_pkp': 1,
        },
        {
            'nama': 'CV. Harapan Baru Papua',
            'nama_direktur': 'Yohanes Wambrauw',
            'jabatan_direktur': 'Direktur',
            'alamat': 'Jl. Sudirman No. 12, Sorong',
            'kota': 'Sorong',
            'npwp': '03.345.678.9-951.000',
            'no_rekening': '3456789012',
            'nama_bank': 'Bank Mandiri',
            'nama_rekening': 'CV. Harapan Baru Papua',
            'telepon': '0951-323678',
            'is_pkp': 1,
        },
        {
            'nama': 'UD. Sinar Laut',
            'nama_direktur': 'Agus Salim',
            'jabatan_direktur': 'Pemilik',
            'alamat': 'Jl. Pelabuhan No. 5, Sorong',
            'kota': 'Sorong',
            'npwp': '04.456.789.0-951.000',
            'no_rekening': '4567890123',
            'nama_bank': 'Bank BNI',
            'nama_rekening': 'Agus Salim',
            'telepon': '0951-324789',
            'is_pkp': 0,
        },
        {
            'nama': 'PT. Teknologi Cerdas Indonesia',
            'nama_direktur': 'Dr. Ir. Surya Pratama, M.T.',
            'jabatan_direktur': 'Direktur',
            'alamat': 'Jl. Diponegoro No. 100, Sorong',
            'kota': 'Sorong',
            'npwp': '05.567.890.1-951.000',
            'no_rekening': '5678901234',
            'nama_bank': 'Bank Mandiri',
            'nama_rekening': 'PT. Teknologi Cerdas Indonesia',
            'telepon': '0951-325890',
            'email': 'info@teknologicerdas.co.id',
            'is_pkp': 1,
        },
    ]
    
    print("\n📌 Menambahkan data Penyedia...")
    for pen in penyedia_data:
        try:
            db.save_penyedia(pen)
            print(f"   ✅ {pen['nama']}")
        except Exception as e:
            print(f"   ⚠️  {pen['nama']}: {e}")
    
    # Sample Paket
    from datetime import date, timedelta
    
    paket_data = [
        {
            'nama': 'Pengadaan Laptop untuk Laboratorium Komputer',
            'jenis_pengadaan': 'Barang',
            'metode_pengadaan': 'Pengadaan Langsung',
            'lokasi': 'Politeknik KP Sorong',
            'sumber_dana': 'DIPA',
            'kode_akun': '5211.001',
            'nilai_pagu': 150000000,
            'nilai_hps': 145000000,
            'nilai_kontrak': 140000000,
            'jenis_pph': 'PPh 22',
            'tarif_pph': 0.015,
            'jangka_waktu': 30,
        },
        {
            'nama': 'Pengadaan Alat Praktik Penangkapan Ikan',
            'jenis_pengadaan': 'Barang',
            'metode_pengadaan': 'Pengadaan Langsung',
            'lokasi': 'Politeknik KP Sorong',
            'sumber_dana': 'DIPA',
            'kode_akun': '5211.002',
            'nilai_pagu': 200000000,
            'nilai_hps': 195000000,
            'nilai_kontrak': 190000000,
            'jenis_pph': 'PPh 22',
            'tarif_pph': 0.015,
            'jangka_waktu': 45,
        },
        {
            'nama': 'Jasa Pemeliharaan AC Ruang Kelas',
            'jenis_pengadaan': 'Jasa Lainnya',
            'metode_pengadaan': 'Pengadaan Langsung',
            'lokasi': 'Politeknik KP Sorong',
            'sumber_dana': 'DIPA',
            'kode_akun': '5231.001',
            'nilai_pagu': 50000000,
            'nilai_hps': 48000000,
            'nilai_kontrak': 45000000,
            'jenis_pph': 'PPh 23',
            'tarif_pph': 0.02,
            'jangka_waktu': 14,
        },
    ]
    
    # Get first PPK and Penyedia IDs
    ppk_list = db.get_pegawai_list('ppk')
    ppspm_list = db.get_pegawai_list('ppspm')
    bend_list = db.get_pegawai_list('bendahara')
    peny_list = db.get_penyedia_list()
    
    print("\n📌 Menambahkan data Paket Contoh...")
    for i, paket in enumerate(paket_data):
        paket['ppk_id'] = ppk_list[0]['id'] if ppk_list else None
        paket['ppspm_id'] = ppspm_list[0]['id'] if ppspm_list else None
        paket['bendahara_id'] = bend_list[0]['id'] if bend_list else None
        paket['penyedia_id'] = peny_list[i % len(peny_list)]['id'] if peny_list else None
        paket['tanggal_mulai'] = date.today()
        paket['tanggal_selesai'] = date.today() + timedelta(days=paket['jangka_waktu'])
        paket['nilai_ppn'] = round(paket['nilai_kontrak'] * 0.11)
        paket['nilai_pph'] = round(paket['nilai_kontrak'] * paket['tarif_pph'])
        
        try:
            paket_id = db.create_paket(paket)
            print(f"   ✅ {paket['nama'][:50]}...")
        except Exception as e:
            print(f"   ⚠️  {paket['nama'][:30]}...: {e}")
    
    print("\n" + "=" * 60)
    print("SETUP SELESAI!")
    print("=" * 60)
    print("\nJalankan START.bat untuk membuka aplikasi.")
    print()


if __name__ == "__main__":
    setup_sample_data()
    input("Tekan Enter untuk menutup...")
