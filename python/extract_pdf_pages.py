import os
import fitz  # PyMuPDF

pdf_path = "/Users/egeziyayildiz/.gemini/antigravity-ide/brain/8de78ad3-318a-414d-ae79-0d6a6adc6cbe/.user_uploaded/media_1791133188859.pdf"
out_dir = "/Users/egeziyayildiz/PARLON_Project/opsinsight/screenshots"
os.makedirs(out_dir, exist_ok=True)

page_names = [
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

doc = fitz.open(pdf_path)
print(f"Total pages in PDF: {len(doc)}")

for i, page in enumerate(doc):
    # Render page at 2x resolution (~144 dpi) for crisp clarity
    zoom = 2.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    
    file_name = page_names[i] if i < len(page_names) else f"powerbi-page-{i+1}.png"
    target_path = os.path.join(out_dir, file_name)
    pix.save(target_path)
    print(f"Saved: {file_name} ({pix.width}x{pix.height})")

print("All Power BI pages extracted successfully!")
