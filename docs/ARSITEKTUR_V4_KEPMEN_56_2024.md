# ARSITEKTUR ASISTEN PPK v4.0
## Selaras dengan Kepmen KP Nomor 56 Tahun 2024
### Tata Cara Pembayaran Dalam Rangka Pelaksanaan APBN

---

## DAFTAR ISI

1. [Ringkasan Perubahan](#1-ringkasan-perubahan)
2. [Arsitektur Modul](#2-arsitektur-modul)
3. [Workflow Engine](#3-workflow-engine)
4. [Skema Database (ERD)](#4-skema-database-erd)
5. [Flow UI PPK-Operator](#5-flow-ui-ppk-operator)
6. [Daftar Template Dokumen](#6-daftar-template-dokumen)
7. [Checklist Kepatuhan](#7-checklist-kepatuhan)
8. [Implementasi Teknis](#8-implementasi-teknis)

---

## 1. RINGKASAN PERUBAHAN

### 1.1 Filosofi Sistem (Dipertahankan)

| Prinsip | Penjelasan |
|---------|------------|
| **Helper, not Auditor** | Membantu PPK, bukan mengaudit |
| **Suggest, not Force** | Menyarankan, bukan memaksa |
| **Warn, not Reject** | Peringatan, bukan penolakan |
| **Fokus PPK** | Mempermudah pekerjaan PPK |

### 1.2 Perubahan Utama v4.0

| Aspek | v3.0 (Sebelum) | v4.0 (Kepmen 56/2024) |
|-------|----------------|------------------------|
| Workflow | 11 tahap generik | 4 fase, 28 tahap spesifik |
| Database | Tabel terpisah | Relasi terstruktur |
| Role | Single user | PPK + Operator |
| Pembayaran | Sederhana | SPBy→DRPP→SSP→SPP→SPM→SP2D |
| Validasi | Hard block | Warning only |

---

## 2. ARSITEKTUR MODUL

### 2.1 Diagram Arsitektur

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        ASISTEN PPK v4.0                                 │
│                  (Kepmen KP 56/2024 Compliant)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      PRESENTATION LAYER                          │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │   │
│  │  │  Dashboard  │ │   Paket     │ │  Dokumen    │ │ Checklist │  │   │
│  │  │   Utama     │ │  Manager    │ │  Generator  │ │    SPJ    │  │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘  │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │   │
│  │  │   Foto      │ │ Pembayaran  │ │   Pajak     │ │  Laporan  │  │   │
│  │  │   BAHP      │ │   Manager   │ │   Manager   │ │  Manager  │  │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      BUSINESS LOGIC LAYER                        │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │   │
│  │  │  Workflow   │ │  Validasi   │ │  Kalkulasi  │ │  Approval │  │   │
│  │  │   Engine    │ │   Engine    │ │   Engine    │ │   Engine  │  │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘  │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │   │
│  │  │  Template   │ │  Numbering  │ │  Timeline   │ │   Role    │  │   │
│  │  │   Engine    │ │   Engine    │ │   Engine    │ │  Manager  │  │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                        DATA LAYER                                │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐  │   │
│  │  │   SQLite    │ │   Config    │ │  Templates  │ │   Output  │  │   │
│  │  │  Database   │ │    JSON     │ │  Word/Excel │ │   Files   │  │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Struktur Modul

```
app/
├── core/
│   ├── config.py              # Konfigurasi aplikasi
│   ├── database.py            # Database manager
│   ├── constants.py           # Konstanta (NEW)
│   └── roles.py               # Role manager (NEW)
│
├── workflow/
│   ├── engine.py              # Workflow engine utama
│   ├── stages.py              # Definisi tahapan (NEW)
│   ├── validation.py          # Validasi engine (NEW)
│   └── approval.py            # Approval engine (NEW)
│
├── pembayaran/                # (NEW MODULE)
│   ├── __init__.py
│   ├── spby_manager.py        # SPBy (Surat Permintaan Bayar)
│   ├── drpp_manager.py        # DRPP
│   ├── ssp_manager.py         # SSP PPN & PPh
│   ├── spp_manager.py         # SPP-LS/GUP/TUP/PTUP
│   ├── spm_manager.py         # SPM
│   ├── sp2d_manager.py        # SP2D
│   └── calculator.py          # Kalkulasi pembayaran
│
├── templates/
│   ├── engine.py              # Template engine
│   ├── placeholders.py        # Placeholder dictionary (NEW)
│   └── numbering.py           # Auto numbering (NEW)
│
├── ui/
│   ├── dashboard.py           # Dashboard utama
│   ├── paket_manager.py       # Manajemen paket
│   ├── checklist_spj_manager.py
│   ├── foto_dokumentasi_manager.py
│   ├── pembayaran_dashboard.py  # (NEW)
│   ├── approval_panel.py        # (NEW)
│   └── status_pertanggungjawaban.py  # (NEW)
│
└── reports/                   # (NEW MODULE)
    ├── rekap_pajak.py
    ├── rekap_pembayaran.py
    └── status_spj.py
```

---

## 3. WORKFLOW ENGINE

### 3.1 Empat Fase Utama (Kepmen 56/2024)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW KEPMEN KP 56/2024                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  FASE A: PERENCANAAN                                                    │
│  ════════════════════                                                   │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐           │
│  │  DIPA  │→│  KAK   │→│ SPEK   │→│ SURVEY │→│BA SURV │           │
│  │(refer) │  │        │  │ TEKNIS │  │ HARGA  │  │        │           │
│  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘           │
│       │                                               │                 │
│       └───────────────────┬───────────────────────────┘                 │
│                           ▼                                             │
│                    ┌────────┐  ┌────────┐  ┌────────┐                  │
│                    │  HPS   │→│  RAB   │→│ NOTA   │                  │
│                    │        │  │        │  │ DINAS  │                  │
│                    └────────┘  └────────┘  └────────┘                  │
│                                               │                         │
│  ══════════════════════════════════════════════════════════════════    │
│                                               ▼                         │
│  FASE B: PENGADAAN & KONTRAK                                           │
│  ════════════════════════════                                           │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐           │
│  │PERMINT │→│BA EVAL │→│BA EVAL │→│BA EVAL │→│PENETAP │           │
│  │PENAWAR │  │ ADMIN  │  │ TEKNIS │  │ HARGA  │  │PENYEDIA│           │
│  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘           │
│                                                       │                 │
│       ┌───────────────────────────────────────────────┘                 │
│       ▼                                                                 │
│  ┌────────┐  ┌────────┐  ┌────────┐                                    │
│  │  SPK/  │→│JAMINAN │→│ SPMK   │                                    │
│  │ PERJ.  │  │(opt)   │  │        │                                    │
│  └────────┘  └────────┘  └────────┘                                    │
│                               │                                         │
│  ══════════════════════════════════════════════════════════════════    │
│                               ▼                                         │
│  FASE C: PELAKSANAAN                                                   │
│  ═══════════════════                                                    │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐                        │
│  │LAPORAN │→│SK TIM  │→│ BAHP   │→│ BAST/  │                        │
│  │PENYEDIA│  │PERIKSA │  │        │  │PHO/FHO │                        │
│  └────────┘  └────────┘  └────────┘  └────────┘                        │
│                                           │                             │
│  ══════════════════════════════════════════════════════════════════    │
│                                           ▼                             │
│  FASE D: PEMBAYARAN (INTI KEPMEN 56/2024)                              │
│  ════════════════════════════════════════                               │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐           │
│  │INVOICE │→│KUITANSI│→│ SPBy   │→│ DRPP   │→│SSP PPN │           │
│  │        │  │        │  │        │  │        │  │SSP PPh │           │
│  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘           │
│                                                       │                 │
│       ┌───────────────────────────────────────────────┘                 │
│       ▼                                                                 │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐                        │
│  │SPP-LS/ │→│  SPM   │→│ SP2D   │→│ BUKTI  │                        │
│  │GUP/TUP │  │        │  │        │  │TRANSFER│                        │
│  └────────┘  └────────┘  └────────┘  └────────┘                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Kode Workflow Stages

```python
# app/workflow/stages.py

from enum import IntEnum
from dataclasses import dataclass
from typing import List, Optional

class WorkflowPhase(IntEnum):
    """Fase workflow sesuai Kepmen 56/2024"""
    PERENCANAAN = 1
    PENGADAAN_KONTRAK = 2
    PELAKSANAAN = 3
    PEMBAYARAN = 4

class WorkflowStage(IntEnum):
    """Tahapan detail dalam workflow"""
    # FASE A: PERENCANAAN (100-199)
    DIPA = 101
    KAK = 102
    SPESIFIKASI_TEKNIS = 103
    SURVEY_HARGA = 104
    BA_SURVEY = 105
    HPS = 106
    RAB = 107
    NOTA_DINAS_KPA = 108

    # FASE B: PENGADAAN & KONTRAK (200-299)
    PERMINTAAN_PENAWARAN = 201
    BA_EVALUASI_ADMIN = 202
    BA_EVALUASI_TEKNIS = 203
    BA_EVALUASI_HARGA = 204
    PENETAPAN_PENYEDIA = 205
    SPK_KONTRAK = 206
    JAMINAN = 207
    SPMK = 208

    # FASE C: PELAKSANAAN (300-399)
    LAPORAN_PENYEDIA = 301
    SK_TIM_PEMERIKSA = 302
    BAHP = 303
    BAST = 304

    # FASE D: PEMBAYARAN (400-499)
    INVOICE = 401
    KUITANSI = 402
    SPBY = 403
    DRPP = 404
    SSP_PPN = 405
    SSP_PPH = 406
    SPP = 407
    SPM = 408
    SP2D = 409
    BUKTI_TRANSFER = 410

@dataclass
class StageConfig:
    """Konfigurasi per tahap"""
    code: WorkflowStage
    name: str
    phase: WorkflowPhase
    description: str
    required: bool = True
    operator_can_input: bool = True
    ppk_approval_required: bool = False
    template_type: str = 'word'
    template_file: str = None
    prerequisites: List[WorkflowStage] = None
    outputs: List[str] = None

# Konfigurasi lengkap semua tahap
WORKFLOW_STAGES_CONFIG = {
    # FASE A: PERENCANAAN
    WorkflowStage.DIPA: StageConfig(
        code=WorkflowStage.DIPA,
        name='DIPA',
        phase=WorkflowPhase.PERENCANAAN,
        description='Daftar Isian Pelaksanaan Anggaran (referensi)',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        prerequisites=None,
    ),
    WorkflowStage.KAK: StageConfig(
        code=WorkflowStage.KAK,
        name='Kerangka Acuan Kerja',
        phase=WorkflowPhase.PERENCANAAN,
        description='KAK / Terms of Reference',
        required=True,
        operator_can_input=True,
        ppk_approval_required=True,  # PPK harus approve
        template_type='word',
        template_file='kak.docx',
        prerequisites=[WorkflowStage.DIPA],
        outputs=['KAK'],
    ),
    WorkflowStage.SPESIFIKASI_TEKNIS: StageConfig(
        code=WorkflowStage.SPESIFIKASI_TEKNIS,
        name='Spesifikasi Teknis',
        phase=WorkflowPhase.PERENCANAAN,
        description='Spesifikasi teknis barang/jasa',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        template_type='word',
        template_file='spesifikasi_teknis.docx',
        prerequisites=[WorkflowStage.KAK],
        outputs=['SPESIFIKASI'],
    ),
    WorkflowStage.SURVEY_HARGA: StageConfig(
        code=WorkflowStage.SURVEY_HARGA,
        name='Survey Harga',
        phase=WorkflowPhase.PERENCANAAN,
        description='Survey harga dari minimal 3 sumber',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        template_type='excel',
        template_file='survey_harga.xlsx',
        prerequisites=[WorkflowStage.SPESIFIKASI_TEKNIS],
        outputs=['SURVEY_HARGA'],
    ),
    WorkflowStage.BA_SURVEY: StageConfig(
        code=WorkflowStage.BA_SURVEY,
        name='Berita Acara Survey',
        phase=WorkflowPhase.PERENCANAAN,
        description='BA hasil survey harga',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        template_type='word',
        template_file='ba_survey.docx',
        prerequisites=[WorkflowStage.SURVEY_HARGA],
        outputs=['BA_SURVEY'],
    ),
    WorkflowStage.HPS: StageConfig(
        code=WorkflowStage.HPS,
        name='Harga Perkiraan Sendiri',
        phase=WorkflowPhase.PERENCANAAN,
        description='HPS berdasarkan survey harga',
        required=True,
        operator_can_input=True,
        ppk_approval_required=True,  # PPK harus approve HPS
        template_type='excel',
        template_file='hps.xlsx',
        prerequisites=[WorkflowStage.BA_SURVEY],
        outputs=['HPS'],
    ),
    WorkflowStage.RAB: StageConfig(
        code=WorkflowStage.RAB,
        name='Rencana Anggaran Biaya',
        phase=WorkflowPhase.PERENCANAAN,
        description='RAB detail',
        required=False,  # Opsional
        operator_can_input=True,
        ppk_approval_required=False,
        template_type='excel',
        template_file='rab.xlsx',
        prerequisites=[WorkflowStage.HPS],
        outputs=['RAB'],
    ),
    WorkflowStage.NOTA_DINAS_KPA: StageConfig(
        code=WorkflowStage.NOTA_DINAS_KPA,
        name='Nota Dinas ke KPA',
        phase=WorkflowPhase.PERENCANAAN,
        description='Permintaan persetujuan pengadaan',
        required=True,
        operator_can_input=True,
        ppk_approval_required=True,
        template_type='word',
        template_file='nota_dinas_kpa.docx',
        prerequisites=[WorkflowStage.HPS],
        outputs=['NOTA_DINAS_KPA'],
    ),

    # FASE B: PENGADAAN & KONTRAK
    WorkflowStage.PERMINTAAN_PENAWARAN: StageConfig(
        code=WorkflowStage.PERMINTAAN_PENAWARAN,
        name='Permintaan Penawaran',
        phase=WorkflowPhase.PENGADAAN_KONTRAK,
        description='Surat permintaan penawaran ke penyedia',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        template_type='word',
        template_file='permintaan_penawaran.docx',
        prerequisites=[WorkflowStage.NOTA_DINAS_KPA],
        outputs=['PERMINTAAN_PENAWARAN'],
    ),
    WorkflowStage.BA_EVALUASI_ADMIN: StageConfig(
        code=WorkflowStage.BA_EVALUASI_ADMIN,
        name='BA Evaluasi Administrasi',
        phase=WorkflowPhase.PENGADAAN_KONTRAK,
        description='Evaluasi kelengkapan administrasi',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        template_type='word',
        template_file='ba_eval_admin.docx',
        prerequisites=[WorkflowStage.PERMINTAAN_PENAWARAN],
        outputs=['BA_EVALUASI_ADMIN'],
    ),
    WorkflowStage.BA_EVALUASI_TEKNIS: StageConfig(
        code=WorkflowStage.BA_EVALUASI_TEKNIS,
        name='BA Evaluasi Teknis',
        phase=WorkflowPhase.PENGADAAN_KONTRAK,
        description='Evaluasi kesesuaian teknis',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        template_type='word',
        template_file='ba_eval_teknis.docx',
        prerequisites=[WorkflowStage.BA_EVALUASI_ADMIN],
        outputs=['BA_EVALUASI_TEKNIS'],
    ),
    WorkflowStage.BA_EVALUASI_HARGA: StageConfig(
        code=WorkflowStage.BA_EVALUASI_HARGA,
        name='BA Evaluasi Harga',
        phase=WorkflowPhase.PENGADAAN_KONTRAK,
        description='Evaluasi dan negosiasi harga',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        template_type='word',
        template_file='ba_eval_harga.docx',
        prerequisites=[WorkflowStage.BA_EVALUASI_TEKNIS],
        outputs=['BA_EVALUASI_HARGA'],
    ),
    WorkflowStage.PENETAPAN_PENYEDIA: StageConfig(
        code=WorkflowStage.PENETAPAN_PENYEDIA,
        name='Penetapan Penyedia',
        phase=WorkflowPhase.PENGADAAN_KONTRAK,
        description='Surat penetapan penyedia terpilih',
        required=True,
        operator_can_input=True,
        ppk_approval_required=True,  # PPK approve penetapan
        template_type='word',
        template_file='penetapan_penyedia.docx',
        prerequisites=[WorkflowStage.BA_EVALUASI_HARGA],
        outputs=['PENETAPAN_PENYEDIA'],
    ),
    WorkflowStage.SPK_KONTRAK: StageConfig(
        code=WorkflowStage.SPK_KONTRAK,
        name='SPK / Surat Perjanjian',
        phase=WorkflowPhase.PENGADAAN_KONTRAK,
        description='Kontrak dengan penyedia',
        required=True,
        operator_can_input=True,
        ppk_approval_required=True,  # PPK tanda tangan kontrak
        template_type='word',
        template_file='spk.docx',
        prerequisites=[WorkflowStage.PENETAPAN_PENYEDIA],
        outputs=['SPK', 'SURAT_PERJANJIAN'],
    ),
    WorkflowStage.JAMINAN: StageConfig(
        code=WorkflowStage.JAMINAN,
        name='Jaminan',
        phase=WorkflowPhase.PENGADAAN_KONTRAK,
        description='Jaminan pelaksanaan/uang muka',
        required=False,  # Opsional tergantung nilai
        operator_can_input=True,
        ppk_approval_required=False,
        prerequisites=[WorkflowStage.SPK_KONTRAK],
        outputs=['JAMINAN_PELAKSANAAN', 'JAMINAN_UANG_MUKA'],
    ),
    WorkflowStage.SPMK: StageConfig(
        code=WorkflowStage.SPMK,
        name='SPMK',
        phase=WorkflowPhase.PENGADAAN_KONTRAK,
        description='Surat Perintah Mulai Kerja',
        required=True,
        operator_can_input=True,
        ppk_approval_required=True,
        template_type='word',
        template_file='spmk.docx',
        prerequisites=[WorkflowStage.SPK_KONTRAK],
        outputs=['SPMK'],
    ),

    # FASE C: PELAKSANAAN
    WorkflowStage.LAPORAN_PENYEDIA: StageConfig(
        code=WorkflowStage.LAPORAN_PENYEDIA,
        name='Laporan Penyedia',
        phase=WorkflowPhase.PELAKSANAAN,
        description='Laporan penyelesaian pekerjaan dari penyedia',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        prerequisites=[WorkflowStage.SPMK],
        outputs=['LAPORAN_PENYEDIA'],
    ),
    WorkflowStage.SK_TIM_PEMERIKSA: StageConfig(
        code=WorkflowStage.SK_TIM_PEMERIKSA,
        name='SK Tim Pemeriksa',
        phase=WorkflowPhase.PELAKSANAAN,
        description='Surat Keputusan Tim Pemeriksa Hasil Pekerjaan',
        required=True,
        operator_can_input=True,
        ppk_approval_required=True,
        template_type='word',
        template_file='sk_tim_pemeriksa.docx',
        prerequisites=[WorkflowStage.LAPORAN_PENYEDIA],
        outputs=['SK_TIM_PEMERIKSA'],
    ),
    WorkflowStage.BAHP: StageConfig(
        code=WorkflowStage.BAHP,
        name='BAHP',
        phase=WorkflowPhase.PELAKSANAAN,
        description='Berita Acara Hasil Pemeriksaan',
        required=True,
        operator_can_input=True,
        ppk_approval_required=True,  # PPK approve BAHP
        template_type='word',
        template_file='bahp.docx',
        prerequisites=[WorkflowStage.SK_TIM_PEMERIKSA],
        outputs=['BAHP'],
    ),
    WorkflowStage.BAST: StageConfig(
        code=WorkflowStage.BAST,
        name='BAST',
        phase=WorkflowPhase.PELAKSANAAN,
        description='Berita Acara Serah Terima',
        required=True,
        operator_can_input=True,
        ppk_approval_required=True,  # PPK tanda tangan BAST
        template_type='word',
        template_file='bast.docx',
        prerequisites=[WorkflowStage.BAHP],
        outputs=['BAST', 'PHO', 'FHO'],
    ),

    # FASE D: PEMBAYARAN
    WorkflowStage.INVOICE: StageConfig(
        code=WorkflowStage.INVOICE,
        name='Invoice',
        phase=WorkflowPhase.PEMBAYARAN,
        description='Tagihan dari penyedia',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        prerequisites=[WorkflowStage.BAST],
        outputs=['INVOICE'],
    ),
    WorkflowStage.KUITANSI: StageConfig(
        code=WorkflowStage.KUITANSI,
        name='Kuitansi',
        phase=WorkflowPhase.PEMBAYARAN,
        description='Kuitansi pembayaran',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        template_type='word',
        template_file='kuitansi.docx',
        prerequisites=[WorkflowStage.INVOICE],
        outputs=['KUITANSI'],
    ),
    WorkflowStage.SPBY: StageConfig(
        code=WorkflowStage.SPBY,
        name='SPBy',
        phase=WorkflowPhase.PEMBAYARAN,
        description='Surat Permintaan Pembayaran (SPBy)',
        required=True,
        operator_can_input=True,
        ppk_approval_required=True,  # PPK approve SPBy
        template_type='word',
        template_file='spby.docx',
        prerequisites=[WorkflowStage.KUITANSI],
        outputs=['SPBY'],
    ),
    WorkflowStage.DRPP: StageConfig(
        code=WorkflowStage.DRPP,
        name='DRPP',
        phase=WorkflowPhase.PEMBAYARAN,
        description='Daftar Rincian Permintaan Pembayaran',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        template_type='word',
        template_file='drpp.docx',
        prerequisites=[WorkflowStage.SPBY],
        outputs=['DRPP'],
    ),
    WorkflowStage.SSP_PPN: StageConfig(
        code=WorkflowStage.SSP_PPN,
        name='SSP PPN',
        phase=WorkflowPhase.PEMBAYARAN,
        description='Surat Setoran Pajak PPN',
        required=False,  # Tergantung PKP
        operator_can_input=True,
        ppk_approval_required=False,
        template_type='excel',
        template_file='ssp.xlsx',
        prerequisites=[WorkflowStage.DRPP],
        outputs=['SSP_PPN'],
    ),
    WorkflowStage.SSP_PPH: StageConfig(
        code=WorkflowStage.SSP_PPH,
        name='SSP PPh',
        phase=WorkflowPhase.PEMBAYARAN,
        description='Surat Setoran Pajak PPh',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        template_type='excel',
        template_file='ssp.xlsx',
        prerequisites=[WorkflowStage.DRPP],
        outputs=['SSP_PPH'],
    ),
    WorkflowStage.SPP: StageConfig(
        code=WorkflowStage.SPP,
        name='SPP',
        phase=WorkflowPhase.PEMBAYARAN,
        description='Surat Permintaan Pembayaran (SPP-LS/GUP/TUP/PTUP)',
        required=True,
        operator_can_input=True,
        ppk_approval_required=True,  # PPK approve SPP
        template_type='word',
        template_file='spp.docx',
        prerequisites=[WorkflowStage.SSP_PPH],
        outputs=['SPP_LS', 'SPP_GUP', 'SPP_TUP', 'SPP_PTUP'],
    ),
    WorkflowStage.SPM: StageConfig(
        code=WorkflowStage.SPM,
        name='SPM',
        phase=WorkflowPhase.PEMBAYARAN,
        description='Surat Perintah Membayar',
        required=True,
        operator_can_input=True,
        ppk_approval_required=True,  # PPK approve SPM
        template_type='word',
        template_file='spm.docx',
        prerequisites=[WorkflowStage.SPP],
        outputs=['SPM'],
    ),
    WorkflowStage.SP2D: StageConfig(
        code=WorkflowStage.SP2D,
        name='SP2D',
        phase=WorkflowPhase.PEMBAYARAN,
        description='Surat Perintah Pencairan Dana',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,  # Dari KPPN
        prerequisites=[WorkflowStage.SPM],
        outputs=['SP2D'],
    ),
    WorkflowStage.BUKTI_TRANSFER: StageConfig(
        code=WorkflowStage.BUKTI_TRANSFER,
        name='Bukti Transfer',
        phase=WorkflowPhase.PEMBAYARAN,
        description='Bukti transfer ke penyedia',
        required=True,
        operator_can_input=True,
        ppk_approval_required=False,
        prerequisites=[WorkflowStage.SP2D],
        outputs=['BUKTI_TRANSFER'],
    ),
}

# Urutan wajib pembayaran sesuai Kepmen 56/2024
PAYMENT_SEQUENCE = [
    WorkflowStage.BAHP,
    WorkflowStage.BAST,
    WorkflowStage.INVOICE,
    WorkflowStage.KUITANSI,
    WorkflowStage.SPBY,
    WorkflowStage.DRPP,
    WorkflowStage.SSP_PPN,
    WorkflowStage.SSP_PPH,
    WorkflowStage.SPP,
    WorkflowStage.SPM,
    WorkflowStage.SP2D,
    WorkflowStage.BUKTI_TRANSFER,
]
```

### 3.3 Validasi Engine (Warning Only)

```python
# app/workflow/validation.py

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from .stages import WorkflowStage, PAYMENT_SEQUENCE

class ValidationLevel(Enum):
    """Level validasi - TIDAK ADA HARD BLOCK"""
    INFO = "INFO"           # 💡 Informasi
    WARNING = "WARNING"     # ⚠️ Peringatan
    INCOMPLETE = "INCOMPLETE"  # 🔲 Belum lengkap
    COMPLETE = "COMPLETE"   # ✅ Lengkap

@dataclass
class ValidationResult:
    level: ValidationLevel
    stage: WorkflowStage
    message: str
    suggestion: str = None

    @property
    def icon(self) -> str:
        icons = {
            ValidationLevel.INFO: "💡",
            ValidationLevel.WARNING: "⚠️",
            ValidationLevel.INCOMPLETE: "🔲",
            ValidationLevel.COMPLETE: "✅",
        }
        return icons.get(self.level, "")

class ValidationEngine:
    """
    Engine validasi dengan filosofi WARNING, bukan BLOCK
    Sesuai Kepmen KP 56/2024
    """

    def validate_pembayaran(self, paket: dict, stage: WorkflowStage) -> List[ValidationResult]:
        """Validasi tahap pembayaran"""
        results = []

        # Cek BAHP sebelum SPP
        if stage == WorkflowStage.SPP:
            if not paket.get('bahp_id'):
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    stage=WorkflowStage.BAHP,
                    message="BAHP belum ada",
                    suggestion="Sebaiknya BAHP dilengkapi sebelum mengajukan SPP"
                ))

            if not paket.get('bast_id'):
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    stage=WorkflowStage.BAST,
                    message="BAST belum ada",
                    suggestion="BAST diperlukan sebagai dasar pembayaran"
                ))

        # Cek pajak sebelum SPP
        if stage == WorkflowStage.SPP:
            if paket.get('is_pkp') and not paket.get('ssp_ppn_id'):
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    stage=WorkflowStage.SSP_PPN,
                    message="SSP PPN belum disiapkan",
                    suggestion="Penyedia adalah PKP, SSP PPN perlu disiapkan"
                ))

            if not paket.get('ssp_pph_id'):
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    stage=WorkflowStage.SSP_PPH,
                    message="SSP PPh belum disiapkan",
                    suggestion="SSP PPh diperlukan untuk pemotongan pajak"
                ))

        # Cek SPBy sebelum DRPP
        if stage == WorkflowStage.DRPP:
            if not paket.get('spby_id'):
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    stage=WorkflowStage.SPBY,
                    message="SPBy belum ada",
                    suggestion="SPBy harus dibuat sebelum DRPP"
                ))

        return results

    def validate_timeline(self, paket: dict) -> List[ValidationResult]:
        """Validasi kronologi tanggal"""
        results = []

        # Tanggal BAHP harus setelah SPMK
        tgl_spmk = paket.get('tanggal_spmk')
        tgl_bahp = paket.get('tanggal_bahp')
        if tgl_spmk and tgl_bahp and tgl_bahp < tgl_spmk:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                stage=WorkflowStage.BAHP,
                message="Tanggal BAHP lebih awal dari SPMK",
                suggestion="Periksa kembali kronologi tanggal"
            ))

        # Tanggal BAST harus setelah BAHP
        tgl_bast = paket.get('tanggal_bast')
        if tgl_bahp and tgl_bast and tgl_bast < tgl_bahp:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                stage=WorkflowStage.BAST,
                message="Tanggal BAST lebih awal dari BAHP",
                suggestion="BAST seharusnya setelah BAHP"
            ))

        # Tanggal SPP harus setelah BAST
        tgl_spp = paket.get('tanggal_spp')
        if tgl_bast and tgl_spp and tgl_spp < tgl_bast:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                stage=WorkflowStage.SPP,
                message="Tanggal SPP lebih awal dari BAST",
                suggestion="SPP diajukan setelah serah terima"
            ))

        return results

    def get_stage_status(self, paket: dict, stage: WorkflowStage) -> ValidationLevel:
        """Dapatkan status stage"""
        stage_field_map = {
            WorkflowStage.KAK: 'kak_id',
            WorkflowStage.HPS: 'hps_id',
            WorkflowStage.SPK_KONTRAK: 'kontrak_id',
            WorkflowStage.BAHP: 'bahp_id',
            WorkflowStage.BAST: 'bast_id',
            WorkflowStage.SPBY: 'spby_id',
            WorkflowStage.DRPP: 'drpp_id',
            WorkflowStage.SSP_PPN: 'ssp_ppn_id',
            WorkflowStage.SSP_PPH: 'ssp_pph_id',
            WorkflowStage.SPP: 'spp_id',
            WorkflowStage.SPM: 'spm_id',
            WorkflowStage.SP2D: 'sp2d_id',
        }

        field = stage_field_map.get(stage)
        if not field:
            return ValidationLevel.INCOMPLETE

        if paket.get(field):
            return ValidationLevel.COMPLETE
        else:
            return ValidationLevel.INCOMPLETE
```

---

## 4. SKEMA DATABASE (ERD)

### 4.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATABASE SCHEMA v4.0                                │
│                      (Kepmen KP 56/2024 Compliant)                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│    satker    │       │   pegawai    │       │   penyedia   │
├──────────────┤       ├──────────────┤       ├──────────────┤
│ id           │       │ id           │       │ id           │
│ kode         │       │ nama         │       │ nama         │
│ nama         │       │ nip          │       │ alamat       │
│ alamat       │       │ jabatan      │       │ npwp         │
│ kota         │       │ pangkat      │       │ is_pkp       │
│ provinsi     │       │ golongan     │       │ rekening     │
│ telepon      │       │ role         │◄──┐   │ bank         │
│ email        │       │ is_active    │   │   │ direktur     │
│ kementerian  │       └──────────────┘   │   │ telepon      │
└──────────────┘                          │   │ email        │
       │                                  │   └──────────────┘
       │                                  │          │
       │    ┌─────────────────────────────┴──────────┘
       │    │
       ▼    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                              paket                                        │
├──────────────────────────────────────────────────────────────────────────┤
│ id               │ PRIMARY KEY                                           │
│ kode             │ Kode paket unik                                       │
│ nama             │ Nama paket pengadaan                                  │
│ tahun_anggaran   │ Tahun APBN                                            │
│ jenis_pengadaan  │ Barang/Jasa/Konstruksi                                │
│ metode_pengadaan │ PL/Tender/dll                                         │
│ sumber_dana      │ RM/PNBP/BLU                                           │
│ kode_akun        │ MAK                                                   │
│                  │                                                        │
│ -- Nilai --                                                               │
│ nilai_pagu       │ Pagu anggaran                                         │
│ nilai_hps        │ Harga Perkiraan Sendiri                               │
│ nilai_kontrak    │ Nilai kontrak final                                   │
│ nilai_ppn        │ PPN (11%)                                             │
│ nilai_pph        │ PPh                                                   │
│ nilai_bruto      │ DPP + PPN                                             │
│ nilai_bersih     │ Bruto - PPh                                           │
│                  │                                                        │
│ -- Foreign Keys --                                                        │
│ satker_id        │ FK → satker                                           │
│ ppk_id           │ FK → pegawai (role=PPK)                               │
│ penyedia_id      │ FK → penyedia                                         │
│                  │                                                        │
│ -- Status --                                                              │
│ status           │ DRAFT/AKTIF/SELESAI/BATAL                             │
│ current_phase    │ 1-4 (Perencanaan s.d. Pembayaran)                     │
│ current_stage    │ Tahap aktif                                           │
│                  │                                                        │
│ -- Timestamps --                                                          │
│ created_at       │                                                        │
│ updated_at       │                                                        │
└──────────────────────────────────────────────────────────────────────────┘
         │
         │ 1:1 atau 1:N
         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        FASE A: PERENCANAAN                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │     kak      │    │ spesifikasi  │    │survey_harga  │                  │
│  ├──────────────┤    ├──────────────┤    ├──────────────┤                  │
│  │ id           │    │ id           │    │ id           │                  │
│  │ paket_id (FK)│    │ paket_id (FK)│    │ paket_id (FK)│                  │
│  │ nomor        │    │ nomor        │    │ nomor        │                  │
│  │ tanggal      │    │ tanggal      │    │ tanggal      │                  │
│  │ latar_belakang│   │ uraian       │    │ sumber_1     │                  │
│  │ tujuan       │    │ detail       │    │ sumber_2     │                  │
│  │ ruang_lingkup│    │ filepath     │    │ sumber_3     │                  │
│  │ output       │    │ approved_by  │    │ filepath     │                  │
│  │ jangka_waktu │    │ approved_at  │    │ approved_by  │                  │
│  │ filepath     │    └──────────────┘    │ approved_at  │                  │
│  │ approved_by  │                        └──────────────┘                  │
│  │ approved_at  │                               │                          │
│  └──────────────┘                               ▼                          │
│         │                               ┌──────────────┐                   │
│         │                               │  ba_survey   │                   │
│         │                               ├──────────────┤                   │
│         │                               │ id           │                   │
│         │                               │ paket_id (FK)│                   │
│         │                               │ nomor        │                   │
│         │                               │ tanggal      │                   │
│         │                               │ kesimpulan   │                   │
│         │                               │ filepath     │                   │
│         │                               └──────────────┘                   │
│         │                                      │                           │
│         └──────────────────┬───────────────────┘                           │
│                            ▼                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │     hps      │    │     rab      │    │ nota_dinas   │                  │
│  ├──────────────┤    ├──────────────┤    ├──────────────┤                  │
│  │ id           │    │ id           │    │ id           │                  │
│  │ paket_id (FK)│    │ paket_id (FK)│    │ paket_id (FK)│                  │
│  │ nomor        │    │ nomor        │    │ nomor        │                  │
│  │ tanggal      │    │ tanggal      │    │ tanggal      │                  │
│  │ nilai_total  │    │ nilai_total  │    │ perihal      │                  │
│  │ metode_hitung│    │ detail_json  │    │ kepada       │                  │
│  │ filepath     │    │ filepath     │    │ filepath     │                  │
│  │ approved_by  │    └──────────────┘    │ approved_by  │                  │
│  │ approved_at  │                        │ approved_at  │                  │
│  └──────────────┘                        └──────────────┘                  │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                     FASE B: PENGADAAN & KONTRAK                             │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │  permintaan  │    │  ba_eval     │    │ penetapan    │                  │
│  │  penawaran   │    │  (admin/     │    │  penyedia    │                  │
│  ├──────────────┤    │  teknis/     │    ├──────────────┤                  │
│  │ id           │    │  harga)      │    │ id           │                  │
│  │ paket_id (FK)│    ├──────────────┤    │ paket_id (FK)│                  │
│  │ nomor        │    │ id           │    │ nomor        │                  │
│  │ tanggal      │    │ paket_id (FK)│    │ tanggal      │                  │
│  │ penyedia_ids │    │ jenis        │    │ penyedia_id  │                  │
│  │ filepath     │    │ nomor        │    │ nilai        │                  │
│  └──────────────┘    │ tanggal      │    │ filepath     │                  │
│                      │ hasil        │    │ approved_by  │                  │
│                      │ filepath     │    └──────────────┘                  │
│                      └──────────────┘           │                          │
│                                                 ▼                          │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                          kontrak                                    │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ id               │ PRIMARY KEY                                      │   │
│  │ paket_id (FK)    │ FK → paket                                       │   │
│  │ penyedia_id (FK) │ FK → penyedia                                    │   │
│  │ jenis            │ SPK / SURAT_PERJANJIAN                           │   │
│  │ nomor            │ Nomor kontrak                                    │   │
│  │ tanggal          │ Tanggal kontrak                                  │   │
│  │ nilai            │ Nilai kontrak                                    │   │
│  │ jangka_waktu     │ Hari kalender                                    │   │
│  │ tanggal_mulai    │                                                  │   │
│  │ tanggal_selesai  │                                                  │   │
│  │ cara_pembayaran  │ SEKALIGUS / TERMIN                               │   │
│  │ jumlah_termin    │                                                  │   │
│  │ filepath         │                                                  │   │
│  │ approved_by      │                                                  │   │
│  │ approved_at      │                                                  │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│         │                                                                  │
│         ▼                                                                  │
│  ┌──────────────┐    ┌──────────────┐                                     │
│  │   jaminan    │    │    spmk      │                                     │
│  ├──────────────┤    ├──────────────┤                                     │
│  │ id           │    │ id           │                                     │
│  │ kontrak_id   │    │ kontrak_id   │                                     │
│  │ jenis        │    │ nomor        │                                     │
│  │ nomor        │    │ tanggal      │                                     │
│  │ nilai        │    │ tanggal_mulai│                                     │
│  │ penerbit     │    │ filepath     │                                     │
│  │ masa_berlaku │    │ approved_by  │                                     │
│  │ filepath     │    └──────────────┘                                     │
│  └──────────────┘                                                          │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        FASE C: PELAKSANAAN                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐                                      │
│  │   laporan    │    │ sk_tim       │                                      │
│  │   penyedia   │    │ pemeriksa    │                                      │
│  ├──────────────┤    ├──────────────┤                                      │
│  │ id           │    │ id           │                                      │
│  │ kontrak_id   │    │ paket_id     │                                      │
│  │ nomor        │    │ nomor        │                                      │
│  │ tanggal      │    │ tanggal      │                                      │
│  │ uraian       │    │ anggota_json │                                      │
│  │ filepath     │    │ filepath     │                                      │
│  └──────────────┘    │ approved_by  │                                      │
│                      └──────────────┘                                      │
│         │                   │                                               │
│         └─────────┬─────────┘                                               │
│                   ▼                                                         │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                           bahp                                      │    │
│  ├────────────────────────────────────────────────────────────────────┤    │
│  │ id               │ PRIMARY KEY                                      │    │
│  │ kontrak_id (FK)  │ FK → kontrak                                     │    │
│  │ nomor            │ Nomor BAHP                                       │    │
│  │ tanggal          │ Tanggal pemeriksaan                              │    │
│  │ hasil            │ SESUAI / TIDAK_SESUAI                            │    │
│  │ catatan          │ Catatan hasil pemeriksaan                        │    │
│  │ tim_pemeriksa    │ JSON array                                       │    │
│  │ filepath         │                                                  │    │
│  │ foto_ids         │ FK → foto_dokumentasi                            │    │
│  │ approved_by      │ FK → pegawai (PPK)                               │    │
│  │ approved_at      │                                                  │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│         │                                                                   │
│         ▼                                                                   │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                           bast                                      │    │
│  ├────────────────────────────────────────────────────────────────────┤    │
│  │ id               │ PRIMARY KEY                                      │    │
│  │ bahp_id (FK)     │ FK → bahp                                        │    │
│  │ kontrak_id (FK)  │ FK → kontrak                                     │    │
│  │ jenis            │ BAST / PHO / FHO                                 │    │
│  │ nomor            │ Nomor BAST                                       │    │
│  │ tanggal          │ Tanggal serah terima                             │    │
│  │ nilai            │ Nilai yang diserahterimakan                      │    │
│  │ uraian_pekerjaan │ Deskripsi pekerjaan                              │    │
│  │ filepath         │                                                  │    │
│  │ approved_by      │ FK → pegawai (PPK)                               │    │
│  │ approved_at      │                                                  │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                   FASE D: PEMBAYARAN (Kepmen 56/2024)                       │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │   invoice    │    │  kuitansi    │    │    spby      │                  │
│  ├──────────────┤    ├──────────────┤    ├──────────────┤                  │
│  │ id           │    │ id           │    │ id           │                  │
│  │ bast_id (FK) │    │ invoice_id   │    │ kuitansi_id  │                  │
│  │ nomor        │    │ nomor        │    │ nomor        │                  │
│  │ tanggal      │    │ tanggal      │    │ tanggal      │                  │
│  │ nilai        │    │ nilai        │    │ nilai_bruto  │                  │
│  │ filepath     │    │ penerima     │    │ nilai_ppn    │                  │
│  └──────────────┘    │ filepath     │    │ nilai_pph    │                  │
│         │            └──────────────┘    │ nilai_bersih │                  │
│         │                   │            │ uraian       │                  │
│         └─────────┬─────────┘            │ filepath     │                  │
│                   ▼                      │ approved_by  │                  │
│                                          │ approved_at  │                  │
│                                          └──────────────┘                  │
│                                                 │                          │
│                                                 ▼                          │
│  ┌──────────────┐                        ┌──────────────┐                  │
│  │    drpp      │◄───────────────────────│   (relasi)   │                  │
│  ├──────────────┤                        └──────────────┘                  │
│  │ id           │                                                          │
│  │ spby_id (FK) │                                                          │
│  │ nomor        │                                                          │
│  │ tanggal      │                                                          │
│  │ uraian_json  │  ← Detail rincian pembayaran                             │
│  │ filepath     │                                                          │
│  └──────────────┘                                                          │
│         │                                                                  │
│         ▼                                                                  │
│  ┌──────────────┐    ┌──────────────┐                                     │
│  │   ssp_ppn    │    │   ssp_pph    │                                     │
│  ├──────────────┤    ├──────────────┤                                     │
│  │ id           │    │ id           │                                     │
│  │ drpp_id (FK) │    │ drpp_id (FK) │                                     │
│  │ nomor        │    │ nomor        │                                     │
│  │ tanggal      │    │ tanggal      │                                     │
│  │ masa_pajak   │    │ masa_pajak   │                                     │
│  │ nilai        │    │ jenis_pph    │  ← PPh 21/22/23/4(2)                │
│  │ ntpn         │    │ tarif        │                                     │
│  │ filepath     │    │ nilai        │                                     │
│  └──────────────┘    │ ntpn         │                                     │
│         │            │ filepath     │                                     │
│         │            └──────────────┘                                     │
│         │                   │                                              │
│         └─────────┬─────────┘                                              │
│                   ▼                                                        │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                            spp                                      │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ id               │ PRIMARY KEY                                      │   │
│  │ drpp_id (FK)     │ FK → drpp                                        │   │
│  │ jenis            │ LS / GUP / TUP / PTUP                            │   │
│  │ nomor            │ Nomor SPP                                        │   │
│  │ tanggal          │ Tanggal SPP                                      │   │
│  │ nilai_bruto      │                                                  │   │
│  │ nilai_potongan   │ Total potongan pajak                             │   │
│  │ nilai_bersih     │ Yang dibayarkan                                  │   │
│  │ keterangan       │                                                  │   │
│  │ filepath         │                                                  │   │
│  │ approved_by      │ FK → pegawai (PPK)                               │   │
│  │ approved_at      │                                                  │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│         │                                                                  │
│         ▼                                                                  │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                            spm                                      │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ id               │ PRIMARY KEY                                      │   │
│  │ spp_id (FK)      │ FK → spp                                         │   │
│  │ nomor            │ Nomor SPM                                        │   │
│  │ tanggal          │ Tanggal SPM                                      │   │
│  │ nilai            │ Nilai SPM                                        │   │
│  │ ppspm_nama       │ Nama PPSPM (text, bukan FK)                      │   │
│  │ ppspm_nip        │ NIP PPSPM                                        │   │
│  │ filepath         │                                                  │   │
│  │ approved_by      │ FK → pegawai (PPK)                               │   │
│  │ approved_at      │                                                  │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│         │                                                                  │
│         ▼                                                                  │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                            sp2d                                     │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ id               │ PRIMARY KEY                                      │   │
│  │ spm_id (FK)      │ FK → spm                                         │   │
│  │ nomor            │ Nomor SP2D                                       │   │
│  │ tanggal          │ Tanggal SP2D                                     │   │
│  │ nilai            │ Nilai yang dicairkan                             │   │
│  │ kppn             │ Nama KPPN penerbit                               │   │
│  │ filepath         │                                                  │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│         │                                                                  │
│         ▼                                                                  │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                       bukti_transfer                                │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │ id               │ PRIMARY KEY                                      │   │
│  │ sp2d_id (FK)     │ FK → sp2d                                        │   │
│  │ tanggal          │ Tanggal transfer                                 │   │
│  │ nilai            │ Nilai yang ditransfer                            │   │
│  │ rekening_tujuan  │ Rekening penyedia                                │   │
│  │ bank_tujuan      │ Bank penyedia                                    │   │
│  │ filepath         │ Bukti transfer                                   │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘

RELASI UTAMA (Urutan Wajib Kepmen 56/2024):
═══════════════════════════════════════════
Kontrak → BAHP → BAST → Invoice → Kuitansi → SPBy → DRPP → SSP → SPP → SPM → SP2D
```

### 4.2 SQL Schema

```sql
-- File: schema_v4.sql
-- Database Schema sesuai Kepmen KP 56/2024

-- ═══════════════════════════════════════════════════════════════════════
-- FASE D: PEMBAYARAN (Tabel baru sesuai Kepmen 56/2024)
-- ═══════════════════════════════════════════════════════════════════════

-- Invoice dari penyedia
CREATE TABLE IF NOT EXISTS invoice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bast_id INTEGER NOT NULL,
    nomor TEXT NOT NULL,
    tanggal DATE NOT NULL,
    nilai REAL NOT NULL,
    keterangan TEXT,
    filepath TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (bast_id) REFERENCES bast(id)
);

-- Kuitansi
CREATE TABLE IF NOT EXISTS kuitansi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    nomor TEXT NOT NULL,
    tanggal DATE NOT NULL,
    nilai REAL NOT NULL,
    penerima TEXT NOT NULL,
    uraian TEXT,
    filepath TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (invoice_id) REFERENCES invoice(id)
);

-- SPBy (Surat Permintaan Bayar) - BARU
CREATE TABLE IF NOT EXISTS spby (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kuitansi_id INTEGER NOT NULL,
    nomor TEXT NOT NULL,
    tanggal DATE NOT NULL,

    -- Nilai
    nilai_bruto REAL NOT NULL,
    nilai_ppn REAL DEFAULT 0,
    nilai_pph REAL DEFAULT 0,
    nilai_bersih REAL NOT NULL,

    -- Detail
    uraian TEXT,
    keperluan TEXT,

    -- File & Approval
    filepath TEXT,
    approved_by INTEGER,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (kuitansi_id) REFERENCES kuitansi(id),
    FOREIGN KEY (approved_by) REFERENCES pegawai(id)
);

-- DRPP (Daftar Rincian Permintaan Pembayaran)
CREATE TABLE IF NOT EXISTS drpp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spby_id INTEGER NOT NULL,
    nomor TEXT NOT NULL,
    tanggal DATE NOT NULL,

    -- Detail rincian (JSON)
    rincian_json TEXT,

    -- Total
    total_bruto REAL NOT NULL,
    total_potongan REAL DEFAULT 0,
    total_bersih REAL NOT NULL,

    filepath TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (spby_id) REFERENCES spby(id)
);

-- SSP PPN
CREATE TABLE IF NOT EXISTS ssp_ppn (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drpp_id INTEGER NOT NULL,
    nomor TEXT,
    tanggal DATE NOT NULL,
    masa_pajak TEXT,           -- "01-2024"

    npwp_wp TEXT NOT NULL,
    nama_wp TEXT NOT NULL,
    alamat_wp TEXT,

    kode_akun_pajak TEXT,      -- 411211
    kode_jenis_setoran TEXT,   -- 100

    nilai REAL NOT NULL,
    ntpn TEXT,                 -- Nomor Transaksi Penerimaan Negara
    tanggal_setor DATE,

    filepath TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (drpp_id) REFERENCES drpp(id)
);

-- SSP PPh
CREATE TABLE IF NOT EXISTS ssp_pph (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drpp_id INTEGER NOT NULL,
    nomor TEXT,
    tanggal DATE NOT NULL,
    masa_pajak TEXT,

    npwp_wp TEXT NOT NULL,
    nama_wp TEXT NOT NULL,
    alamat_wp TEXT,

    jenis_pph TEXT NOT NULL,   -- 'PPh 21', 'PPh 22', 'PPh 23', 'PPh 4(2)'
    tarif REAL NOT NULL,       -- 0.05, 0.015, 0.02, 0.025

    kode_akun_pajak TEXT,
    kode_jenis_setoran TEXT,

    dpp REAL NOT NULL,         -- Dasar Pengenaan Pajak
    nilai REAL NOT NULL,       -- Nilai PPh
    ntpn TEXT,
    tanggal_setor DATE,

    filepath TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (drpp_id) REFERENCES drpp(id)
);

-- SPP (Surat Permintaan Pembayaran)
CREATE TABLE IF NOT EXISTS spp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drpp_id INTEGER NOT NULL,
    jenis TEXT NOT NULL,       -- 'LS', 'GUP', 'TUP', 'PTUP'
    nomor TEXT NOT NULL,
    tanggal DATE NOT NULL,

    -- Nilai
    nilai_bruto REAL NOT NULL,
    nilai_potongan REAL DEFAULT 0,
    nilai_bersih REAL NOT NULL,

    -- Keterangan
    keterangan TEXT,

    -- File & Approval
    filepath TEXT,
    approved_by INTEGER,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (drpp_id) REFERENCES drpp(id),
    FOREIGN KEY (approved_by) REFERENCES pegawai(id)
);

-- SPM (Surat Perintah Membayar)
CREATE TABLE IF NOT EXISTS spm (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spp_id INTEGER NOT NULL,
    nomor TEXT NOT NULL,
    tanggal DATE NOT NULL,
    nilai REAL NOT NULL,

    -- PPSPM (hanya sebagai text, bukan user)
    ppspm_nama TEXT,
    ppspm_nip TEXT,
    ppspm_jabatan TEXT,

    -- Keterangan
    keterangan TEXT,

    -- File & Approval
    filepath TEXT,
    approved_by INTEGER,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (spp_id) REFERENCES spp(id),
    FOREIGN KEY (approved_by) REFERENCES pegawai(id)
);

-- SP2D (Surat Perintah Pencairan Dana)
CREATE TABLE IF NOT EXISTS sp2d (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spm_id INTEGER NOT NULL,
    nomor TEXT NOT NULL,
    tanggal DATE NOT NULL,
    nilai REAL NOT NULL,

    -- KPPN
    kppn TEXT,

    -- File
    filepath TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (spm_id) REFERENCES spm(id)
);

-- Bukti Transfer
CREATE TABLE IF NOT EXISTS bukti_transfer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sp2d_id INTEGER NOT NULL,
    tanggal DATE NOT NULL,
    nilai REAL NOT NULL,

    -- Rekening Tujuan
    rekening_tujuan TEXT NOT NULL,
    nama_rekening TEXT NOT NULL,
    bank_tujuan TEXT NOT NULL,

    -- Referensi
    no_referensi TEXT,

    -- File
    filepath TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (sp2d_id) REFERENCES sp2d(id)
);

-- Index untuk performa
CREATE INDEX IF NOT EXISTS idx_invoice_bast ON invoice(bast_id);
CREATE INDEX IF NOT EXISTS idx_kuitansi_invoice ON kuitansi(invoice_id);
CREATE INDEX IF NOT EXISTS idx_spby_kuitansi ON spby(kuitansi_id);
CREATE INDEX IF NOT EXISTS idx_drpp_spby ON drpp(spby_id);
CREATE INDEX IF NOT EXISTS idx_ssp_ppn_drpp ON ssp_ppn(drpp_id);
CREATE INDEX IF NOT EXISTS idx_ssp_pph_drpp ON ssp_pph(drpp_id);
CREATE INDEX IF NOT EXISTS idx_spp_drpp ON spp(drpp_id);
CREATE INDEX IF NOT EXISTS idx_spm_spp ON spm(spp_id);
CREATE INDEX IF NOT EXISTS idx_sp2d_spm ON sp2d(spm_id);
CREATE INDEX IF NOT EXISTS idx_transfer_sp2d ON bukti_transfer(sp2d_id);
```

---

## 5. FLOW UI PPK-OPERATOR

### 5.1 Diagram Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FLOW UI PPK - OPERATOR                              │
│                      (Kepmen KP 56/2024 Compliant)                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              LOGIN                                          │
│                    ┌─────────────────────────┐                              │
│                    │   Pilih Role:           │                              │
│                    │   ○ PPK                 │                              │
│                    │   ○ Operator            │                              │
│                    │   [Masuk]               │                              │
│                    └─────────────────────────┘                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│         DASHBOARD PPK           │ │       DASHBOARD OPERATOR        │
├─────────────────────────────────┤ ├─────────────────────────────────┤
│                                 │ │                                 │
│  ┌───────────────────────────┐  │ │  ┌───────────────────────────┐  │
│  │ Paket Menunggu Approval   │  │ │  │ Daftar Paket Aktif        │  │
│  │ ─────────────────────────│  │ │  │ ─────────────────────────│  │
│  │ ⚠ KAK Paket A    [Review]│  │ │  │ • Paket A (Persiapan)     │  │
│  │ ⚠ HPS Paket B    [Review]│  │ │  │ • Paket B (Pengadaan)     │  │
│  │ ⚠ BAHP Paket C   [Review]│  │ │  │ • Paket C (Pelaksanaan)   │  │
│  │ ⚠ SPP Paket D    [Review]│  │ │  │ • Paket D (Pembayaran)    │  │
│  └───────────────────────────┘  │ │  └───────────────────────────┘  │
│                                 │ │                                 │
│  ┌───────────────────────────┐  │ │  ┌───────────────────────────┐  │
│  │ Ringkasan Status          │  │ │  │ Quick Actions             │  │
│  │ ─────────────────────────│  │ │  │ ─────────────────────────│  │
│  │ Total Paket: 15           │  │ │  │ [+ Paket Baru]            │  │
│  │ Menunggu Approval: 4      │  │ │  │ [📝 Input Data]           │  │
│  │ Dalam Proses: 8           │  │ │  │ [📄 Generate Dokumen]     │  │
│  │ Selesai: 3                │  │ │  │ [📋 Checklist SPJ]        │  │
│  └───────────────────────────┘  │ │  └───────────────────────────┘  │
│                                 │ │                                 │
└─────────────────────────────────┘ └─────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                              DETAIL PAKET
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│  PAKET: Pengadaan Laptop Kantor                        Status: PELAKSANAAN  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    STATUS PERTANGGUNGJAWABAN                         │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                      │   │
│  │  PERENCANAAN          PENGADAAN           PELAKSANAAN    PEMBAYARAN │   │
│  │  ════════════         ════════════        ════════════   ══════════ │   │
│  │  ✅ KAK               ✅ Evaluasi         ✅ BAHP        🔲 Invoice │   │
│  │  ✅ Spesifikasi       ✅ Penetapan        ✅ BAST        🔲 Kuitansi│   │
│  │  ✅ Survey            ✅ SPK                              🔲 SPBy   │   │
│  │  ✅ HPS               ✅ SPMK                              🔲 DRPP   │   │
│  │  ✅ Nota Dinas                                            🔲 SSP    │   │
│  │                                                           🔲 SPP    │   │
│  │                                                           🔲 SPM    │   │
│  │                                                           🔲 SP2D   │   │
│  │                                                                      │   │
│  │  Progress: ████████████████░░░░░░░░░░ 65%                           │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌───────────────────────────────┐  ┌───────────────────────────────────┐  │
│  │  AKSI OPERATOR                │  │  AKSI PPK                         │  │
│  ├───────────────────────────────┤  ├───────────────────────────────────┤  │
│  │  [📝 Input Invoice]           │  │  [✅ Approve BAHP]                │  │
│  │  [📝 Input Kuitansi]          │  │  [✅ Approve BAST]                │  │
│  │  [📄 Generate SPBy]           │  │  [✅ Approve SPBy]                │  │
│  │  [📄 Generate DRPP]           │  │  [✅ Approve SPP]                 │  │
│  │  [📄 Generate SSP]            │  │  [✅ Approve SPM]                 │  │
│  │  [📄 Generate SPP]            │  │  [👁 Lihat Semua Dokumen]        │  │
│  └───────────────────────────────┘  └───────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                         APPROVAL FLOW (PPK)
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                        REVIEW & APPROVAL                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Dokumen: SPBy - Paket Pengadaan Laptop                                    │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  DETAIL DOKUMEN                                                      │   │
│  │  ───────────────────────────────────────────────────────────────────│   │
│  │  Nomor      : SPBy-001/PPK/2024                                      │   │
│  │  Tanggal    : 15 Januari 2024                                        │   │
│  │                                                                      │   │
│  │  Nilai Bruto  : Rp 45.000.000                                        │   │
│  │  PPN (11%)    : Rp  4.950.000                                        │   │
│  │  PPh 22       : Rp    675.000                                        │   │
│  │  Nilai Bersih : Rp 49.275.000                                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  VALIDASI OTOMATIS                                                   │   │
│  │  ───────────────────────────────────────────────────────────────────│   │
│  │  ✅ BAHP sudah ada (No. BAHP-001/2024)                               │   │
│  │  ✅ BAST sudah ada (No. BAST-001/2024)                               │   │
│  │  ✅ Nilai sesuai dengan kontrak                                      │   │
│  │  ✅ Kronologi tanggal valid                                          │   │
│  │  ⚠️ WARNING: Pastikan SSP sudah disetorkan                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  DOKUMEN PENDUKUNG                                                   │   │
│  │  ───────────────────────────────────────────────────────────────────│   │
│  │  📄 BAHP.pdf                    [Lihat]                              │   │
│  │  📄 BAST.pdf                    [Lihat]                              │   │
│  │  📄 Invoice.pdf                 [Lihat]                              │   │
│  │  📄 Kuitansi.pdf                [Lihat]                              │   │
│  │  📷 Foto Dokumentasi (8 foto)   [Lihat]                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Catatan PPK:                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  (opsional)                                                          │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│            [❌ Kembalikan]              [✅ Setujui / Approve]              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Pembagian Hak Akses

| Fungsi | Operator | PPK |
|--------|:--------:|:---:|
| **Input Data** |
| Input KAK, Spesifikasi | ✅ | ✅ |
| Input Survey Harga | ✅ | ✅ |
| Input HPS | ✅ | ✅ |
| Input Data Penyedia | ✅ | ✅ |
| Input BAHP, BAST | ✅ | ✅ |
| Input Invoice, Kuitansi | ✅ | ✅ |
| Input SSP (PPN/PPh) | ✅ | ✅ |
| **Generate Dokumen** |
| Generate Draft SPBy | ✅ | ✅ |
| Generate Draft DRPP | ✅ | ✅ |
| Generate Draft SPP | ✅ | ✅ |
| Generate Draft SPM | ✅ | ✅ |
| **Approval** |
| Approve KAK | ❌ | ✅ |
| Approve HPS | ❌ | ✅ |
| Approve Penetapan Penyedia | ❌ | ✅ |
| Approve Kontrak/SPK | ❌ | ✅ |
| Approve BAHP | ❌ | ✅ |
| Approve BAST | ❌ | ✅ |
| Approve SPBy | ❌ | ✅ |
| Approve SPP | ❌ | ✅ |
| Approve SPM | ❌ | ✅ |
| **Lihat Data** |
| Lihat Semua Paket | ✅ | ✅ |
| Lihat Status SPJ | ✅ | ✅ |
| Export Laporan | ✅ | ✅ |

---

## 6. DAFTAR TEMPLATE DOKUMEN

### 6.1 Template Wajib Kepmen 56/2024

| No | Kode | Nama Template | Format | Fase |
|----|------|---------------|--------|------|
| **PERENCANAAN** |
| 1 | KAK | Kerangka Acuan Kerja | Word | A |
| 2 | SPESIFIKASI | Spesifikasi Teknis | Word | A |
| 3 | SURVEY_HARGA | Tabel Survey Harga | Excel | A |
| 4 | BA_SURVEY | Berita Acara Survey | Word | A |
| 5 | HPS | Harga Perkiraan Sendiri | Excel | A |
| 6 | RAB | Rencana Anggaran Biaya | Excel | A |
| 7 | NOTA_DINAS_KPA | Nota Dinas ke KPA | Word | A |
| **PENGADAAN** |
| 8 | PERMINTAAN_PENAWARAN | Surat Permintaan Penawaran | Word | B |
| 9 | BA_EVAL_ADMIN | BA Evaluasi Administrasi | Word | B |
| 10 | BA_EVAL_TEKNIS | BA Evaluasi Teknis | Word | B |
| 11 | BA_EVAL_HARGA | BA Evaluasi Harga | Word | B |
| 12 | PENETAPAN_PENYEDIA | Surat Penetapan Penyedia | Word | B |
| 13 | SPK | Surat Perintah Kerja | Word | B |
| 14 | SURAT_PERJANJIAN | Surat Perjanjian | Word | B |
| 15 | SPMK | Surat Perintah Mulai Kerja | Word | B |
| **PELAKSANAAN** |
| 16 | SK_TIM_PEMERIKSA | SK Tim Pemeriksa | Word | C |
| 17 | BAHP | Berita Acara Hasil Pemeriksaan | Word | C |
| 18 | BAST | Berita Acara Serah Terima | Word | C |
| **PEMBAYARAN** |
| 19 | KUITANSI | Kuitansi Pembayaran | Word | D |
| 20 | **SPBY** | **Surat Permintaan Bayar** | Word | D |
| 21 | **DRPP** | **Daftar Rincian Permintaan Pembayaran** | Word | D |
| 22 | SSP_PPN | Surat Setoran Pajak PPN | Excel | D |
| 23 | SSP_PPH | Surat Setoran Pajak PPh | Excel | D |
| 24 | **SPP_LS** | **SPP Langsung** | Word | D |
| 25 | **SPP_GUP** | **SPP Ganti Uang Persediaan** | Word | D |
| 26 | **SPP_TUP** | **SPP Tambahan Uang Persediaan** | Word | D |
| 27 | **SPP_PTUP** | **SPP Pertanggungjawaban TUP** | Word | D |
| 28 | **SPM** | **Surat Perintah Membayar** | Word | D |
| 29 | REKAP_PAJAK | Rekapitulasi Pajak | Excel | D |
| 30 | REKAP_PEMBAYARAN | Rekapitulasi Pembayaran | Excel | D |

### 6.2 Placeholder Wajib

```python
# app/templates/placeholders.py

PLACEHOLDERS_PEMBAYARAN = {
    # SPBy
    'nomor_spby': {'label': 'Nomor SPBy', 'type': 'text'},
    'tanggal_spby': {'label': 'Tanggal SPBy', 'type': 'date'},

    # DRPP
    'nomor_drpp': {'label': 'Nomor DRPP', 'type': 'text'},
    'tanggal_drpp': {'label': 'Tanggal DRPP', 'type': 'date'},

    # SPP
    'nomor_spp': {'label': 'Nomor SPP', 'type': 'text'},
    'tanggal_spp': {'label': 'Tanggal SPP', 'type': 'date'},
    'jenis_spp': {'label': 'Jenis SPP', 'type': 'select',
                  'options': ['LS', 'GUP', 'TUP', 'PTUP']},

    # SPM
    'nomor_spm': {'label': 'Nomor SPM', 'type': 'text'},
    'tanggal_spm': {'label': 'Tanggal SPM', 'type': 'date'},

    # SP2D
    'nomor_sp2d': {'label': 'Nomor SP2D', 'type': 'text'},
    'tanggal_sp2d': {'label': 'Tanggal SP2D', 'type': 'date'},

    # Nilai
    'nilai_bruto': {'label': 'Nilai Bruto (DPP)', 'type': 'currency'},
    'nilai_bruto_terbilang': {'label': 'Nilai Bruto Terbilang', 'type': 'text'},
    'nilai_ppn': {'label': 'Nilai PPN', 'type': 'currency'},
    'nilai_pph': {'label': 'Nilai PPh', 'type': 'currency'},
    'nilai_potongan': {'label': 'Total Potongan', 'type': 'currency'},
    'nilai_bersih': {'label': 'Nilai Bersih', 'type': 'currency'},
    'nilai_bersih_terbilang': {'label': 'Nilai Bersih Terbilang', 'type': 'text'},

    # Pejabat (sebagai text, bukan user)
    'nama_ppk': {'label': 'Nama PPK', 'type': 'text'},
    'nip_ppk': {'label': 'NIP PPK', 'type': 'text'},
    'jabatan_ppk': {'label': 'Jabatan PPK', 'type': 'text'},

    'nama_ppspm': {'label': 'Nama PPSPM', 'type': 'text'},
    'nip_ppspm': {'label': 'NIP PPSPM', 'type': 'text'},
    'jabatan_ppspm': {'label': 'Jabatan PPSPM', 'type': 'text'},

    'nama_bendahara': {'label': 'Nama Bendahara', 'type': 'text'},
    'nip_bendahara': {'label': 'NIP Bendahara', 'type': 'text'},

    # Penyedia
    'nama_penyedia': {'label': 'Nama Penyedia', 'type': 'text'},
    'alamat_penyedia': {'label': 'Alamat Penyedia', 'type': 'text'},
    'npwp_penyedia': {'label': 'NPWP Penyedia', 'type': 'text'},
    'rekening_penyedia': {'label': 'No. Rekening', 'type': 'text'},
    'bank_penyedia': {'label': 'Nama Bank', 'type': 'text'},
    'nama_rekening': {'label': 'Nama Pemilik Rekening', 'type': 'text'},

    # Referensi
    'nomor_kontrak': {'label': 'Nomor Kontrak', 'type': 'text'},
    'tanggal_kontrak': {'label': 'Tanggal Kontrak', 'type': 'date'},
    'nomor_bahp': {'label': 'Nomor BAHP', 'type': 'text'},
    'tanggal_bahp': {'label': 'Tanggal BAHP', 'type': 'date'},
    'nomor_bast': {'label': 'Nomor BAST', 'type': 'text'},
    'tanggal_bast': {'label': 'Tanggal BAST', 'type': 'date'},

    # Pajak
    'ntpn_ppn': {'label': 'NTPN PPN', 'type': 'text'},
    'ntpn_pph': {'label': 'NTPN PPh', 'type': 'text'},
    'tanggal_setor_pajak': {'label': 'Tanggal Setor Pajak', 'type': 'date'},
}
```

---

## 7. CHECKLIST KEPATUHAN

### 7.1 Checklist per Fase

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              CHECKLIST KEPATUHAN KEPMEN KP 56/2024                          │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
FASE A: PERENCANAAN
═══════════════════════════════════════════════════════════════════════════════

□ A.1  DIPA/POK tersedia dan mencukupi
□ A.2  KAK disusun dan disetujui PPK
□ A.3  Spesifikasi teknis lengkap
□ A.4  Survey harga dilakukan (min 3 sumber)
□ A.5  BA Survey Harga ditandatangani
□ A.6  HPS disusun dan disetujui PPK
□ A.7  RAB sesuai dengan HPS
□ A.8  Nota Dinas ke KPA disetujui

Dokumen Output:
  ✓ KAK
  ✓ Spesifikasi Teknis
  ✓ Tabel Survey Harga
  ✓ BA Survey Harga
  ✓ HPS
  ✓ RAB
  ✓ Nota Dinas ke KPA

═══════════════════════════════════════════════════════════════════════════════
FASE B: PENGADAAN & KONTRAK
═══════════════════════════════════════════════════════════════════════════════

□ B.1  Permintaan penawaran dikirim
□ B.2  Evaluasi administrasi dilakukan
□ B.3  Evaluasi teknis dilakukan
□ B.4  Evaluasi harga dan negosiasi dilakukan
□ B.5  Penyedia ditetapkan
□ B.6  SPK/Surat Perjanjian ditandatangani
□ B.7  Jaminan pelaksanaan diterima (jika diperlukan)
□ B.8  SPMK diterbitkan

Dokumen Output:
  ✓ Surat Permintaan Penawaran
  ✓ BA Evaluasi Administrasi
  ✓ BA Evaluasi Teknis
  ✓ BA Evaluasi Harga
  ✓ Surat Penetapan Penyedia
  ✓ SPK / Surat Perjanjian
  ✓ Jaminan Pelaksanaan (opsional)
  ✓ SPMK

═══════════════════════════════════════════════════════════════════════════════
FASE C: PELAKSANAAN
═══════════════════════════════════════════════════════════════════════════════

□ C.1  Laporan penyelesaian dari penyedia diterima
□ C.2  SK Tim Pemeriksa diterbitkan
□ C.3  Pemeriksaan hasil pekerjaan dilakukan
□ C.4  BAHP ditandatangani (tim pemeriksa + penyedia)
□ C.5  BAST ditandatangani (PPK + penyedia)
□ C.6  Foto dokumentasi lengkap (dengan GPS tagging)

Dokumen Output:
  ✓ Laporan Penyedia
  ✓ SK Tim Pemeriksa
  ✓ BAHP
  ✓ BAST / PHO / FHO
  ✓ Foto Dokumentasi

═══════════════════════════════════════════════════════════════════════════════
FASE D: PEMBAYARAN (INTI KEPMEN 56/2024)
═══════════════════════════════════════════════════════════════════════════════

□ D.1  Invoice dari penyedia diterima
□ D.2  Kuitansi bermeterai lengkap
□ D.3  SPBy (Surat Permintaan Bayar) dibuat dan disetujui PPK
□ D.4  DRPP (Daftar Rincian Permintaan Pembayaran) dibuat
□ D.5  SSP PPN dibuat dan disetor (jika PKP)
□ D.6  SSP PPh dibuat dan disetor
□ D.7  SPP-LS/GUP/TUP/PTUP dibuat dan disetujui PPK
□ D.8  SPM diterbitkan PPSPM
□ D.9  SP2D diterbitkan KPPN
□ D.10 Bukti transfer ke penyedia

Urutan Wajib:
  BAHP → BAST → Invoice → Kuitansi → SPBy → DRPP → SSP → SPP → SPM → SP2D

Dokumen Output:
  ✓ Invoice
  ✓ Kuitansi
  ✓ SPBy
  ✓ DRPP
  ✓ SSP PPN
  ✓ SSP PPh
  ✓ SPP
  ✓ SPM
  ✓ SP2D
  ✓ Bukti Transfer

═══════════════════════════════════════════════════════════════════════════════
VALIDASI KRONOLOGI (WARNING)
═══════════════════════════════════════════════════════════════════════════════

Tanggal SPMK ≤ Tanggal Mulai Kerja
Tanggal Selesai Kerja ≤ Tanggal BAHP
Tanggal BAHP ≤ Tanggal BAST
Tanggal BAST ≤ Tanggal Invoice
Tanggal Invoice ≤ Tanggal Kuitansi
Tanggal Kuitansi ≤ Tanggal SPBy
Tanggal SPBy ≤ Tanggal DRPP
Tanggal DRPP ≤ Tanggal SSP
Tanggal SSP ≤ Tanggal SPP
Tanggal SPP ≤ Tanggal SPM
Tanggal SPM ≤ Tanggal SP2D
```

### 7.2 Dashboard Status Pertanggungjawaban

```
┌─────────────────────────────────────────────────────────────────────────────┐
│            DASHBOARD KELENGKAPAN PERTANGGUNGJAWABAN                         │
│                     Paket: Pengadaan Laptop Kantor                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PERENCANAAN                                                                │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │   ✅    │ │   ✅    │ │   ✅    │ │   ✅    │ │   ✅    │ │   ✅    │  │
│  │   KAK   │ │  SPEK   │ │ SURVEY  │ │   HPS   │ │   RAB   │ │  NOTA   │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
│                                                                             │
│  PENGADAAN & KONTRAK                                                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │   ✅    │ │   ✅    │ │   ✅    │ │   ✅    │ │   ✅    │ │   ✅    │  │
│  │ EVALUASI│ │PENETAPAN│ │   SPK   │ │ JAMINAN │ │  SPMK   │ │         │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
│                                                                             │
│  PELAKSANAAN                                                                │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                           │
│  │   ✅    │ │   ✅    │ │   ✅    │ │   ✅    │                           │
│  │ LAPORAN │ │SK PERIK │ │  BAHP   │ │  BAST   │                           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘                           │
│                                                                             │
│  PEMBAYARAN                                                                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │   ✅    │ │   ✅    │ │   ⚠️    │ │   🔲    │ │   🔲    │ │   🔲    │  │
│  │ INVOICE │ │KUITANSI │ │  SPBy   │ │  DRPP   │ │   SSP   │ │   SPP   │  │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                                       │
│  │   🔲    │ │   🔲    │ │   🔲    │                                       │
│  │   SPM   │ │  SP2D   │ │TRANSFER │                                       │
│  └─────────┘ └─────────┘ └─────────┘                                       │
│                                                                             │
│  ═══════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  LEGENDA:  ✅ Lengkap   ⚠️ Menunggu Approval   🔲 Belum Ada                │
│                                                                             │
│  PROGRESS: ████████████████████░░░░░░░░░░ 70%                              │
│                                                                             │
│  NEXT ACTION:                                                               │
│  → PPK perlu approve SPBy                                                   │
│  → Setelah itu, generate DRPP dan SSP                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. IMPLEMENTASI TEKNIS

### 8.1 Prioritas Implementasi

| Prioritas | Modul | Estimasi | Status |
|-----------|-------|----------|--------|
| **P0 - Critical** |
| 1 | Update Database Schema (tabel pembayaran) | - | 🔲 |
| 2 | Workflow Engine v4 (4 fase) | - | 🔲 |
| 3 | Validation Engine (warning only) | - | 🔲 |
| **P1 - High** |
| 4 | SPBy Manager | - | 🔲 |
| 5 | DRPP Manager | - | 🔲 |
| 6 | SSP Manager (PPN + PPh) | - | 🔲 |
| 7 | SPP Manager (LS/GUP/TUP/PTUP) | - | 🔲 |
| **P2 - Medium** |
| 8 | SPM Manager | - | 🔲 |
| 9 | SP2D Manager | - | 🔲 |
| 10 | Dashboard Status Pertanggungjawaban | - | 🔲 |
| 11 | Role Manager (PPK/Operator) | - | 🔲 |
| **P3 - Low** |
| 12 | Approval Panel | - | 🔲 |
| 13 | Rekap Pajak | - | 🔲 |
| 14 | Rekap Pembayaran | - | 🔲 |
| 15 | Export Laporan SPJ | - | 🔲 |

### 8.2 File yang Perlu Dibuat/Dimodifikasi

```
BARU:
├── app/workflow/stages.py           # Definisi 28 tahap
├── app/workflow/validation.py       # Validasi warning-only
├── app/workflow/approval.py         # Approval engine
├── app/core/roles.py                # Role PPK/Operator
├── app/pembayaran/                  # Module pembayaran baru
│   ├── __init__.py
│   ├── spby_manager.py
│   ├── drpp_manager.py
│   ├── ssp_manager.py
│   ├── spp_manager.py
│   ├── spm_manager.py
│   ├── sp2d_manager.py
│   └── calculator.py
├── app/ui/pembayaran_dashboard.py
├── app/ui/approval_panel.py
├── app/ui/status_pertanggungjawaban.py
├── app/templates/placeholders.py
└── app/reports/

MODIFIKASI:
├── app/core/database.py             # Tambah tabel pembayaran
├── app/core/config.py               # Update workflow config
├── app/workflow/engine.py           # Update ke 4 fase
├── app/ui/dashboard.py              # Tambah role & approval
└── app/templates/engine.py          # Placeholder baru
```

---

## RINGKASAN

Dokumen ini memberikan panduan lengkap untuk menyesuaikan Asisten PPK dengan Kepmen KP Nomor 56 Tahun 2024:

1. **Arsitektur Modul** - Struktur modular dengan pemisahan layer
2. **Workflow Engine** - 4 fase, 28 tahap dengan urutan wajib pembayaran
3. **Database Schema** - ERD lengkap dengan relasi terstruktur
4. **Flow UI** - Pembagian role PPK dan Operator
5. **Template Dokumen** - 30 template wajib dengan placeholder
6. **Checklist Kepatuhan** - Per fase dengan validasi kronologi

**Filosofi tetap dipertahankan:**
- Helper, not Auditor
- Suggest, not Force
- Warn, not Reject
- Fokus mempermudah PPK

---

*Dokumen Arsitektur Asisten PPK v4.0*
*Selaras dengan Kepmen KP Nomor 56 Tahun 2024*
*Versi: 1.0 | Januari 2026*
