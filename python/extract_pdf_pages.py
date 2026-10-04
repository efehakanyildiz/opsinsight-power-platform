"""Power BI rapor PDF'ini sayfa sayfa yüksek çözünürlüklü PNG görsellere dönüştürür.

Kullanım:
    python extract_pdf_pages.py <rapor.pdf> [cikti_klasoru]

Varsayılan çıktı klasörü: ../screenshots
"""
import os
import sys

import fitz  # PyMuPDF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT_DIR = os.path.join(SCRIPT_DIR, "..", "screenshots")

PAGE_NAMES = [
    "powerbi-01-kpi-dashboard.png",
    "powerbi-02-department-category.png",
    "powerbi-03-sla-escalation.png",
    "powerbi-04-root-cause.png",
    "powerbi-05-process-intelligence.png",
    "powerbi-06-team-workbench.png",
    "powerbi-07-department-benchmarking.png",
    "powerbi-08-collaboration-comments.png",
    "powerbi-09-operational-risk-funnel.png",
]


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    pdf_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT_DIR
    os.makedirs(out_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    print(f"PDF'teki toplam sayfa: {len(doc)}")

    for i, page in enumerate(doc):
        # 2x yakınlaştırma (~144 dpi) ile net görseller
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), alpha=False)
        file_name = PAGE_NAMES[i] if i < len(PAGE_NAMES) else f"powerbi-page-{i + 1}.png"
        pix.save(os.path.join(out_dir, file_name))
        print(f"Kaydedildi: {file_name} ({pix.width}x{pix.height})")

    print("Tüm Power BI sayfaları başarıyla dışa aktarıldı.")


if __name__ == "__main__":
    main()
