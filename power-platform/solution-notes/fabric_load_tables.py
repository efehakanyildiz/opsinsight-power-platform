import os
from pyspark.sql import SparkSession

# CSV dosyalarının bulunduğu yer (Lakehouse Files klasörü)
files_path = "Files/"

# Yüklenecek CSV dosyaları ve tablo isimleri
csv_tables = {
    "departments":      "departments.csv",
    "teams":            "teams.csv",
    "employees":        "employees.csv",
    "categories":       "categories.csv",
    "sla_rules":        "sla_rules.csv",
    "root_causes":      "root_causes.csv",
    "resolution_codes": "resolution_codes.csv",
    "issues":           "issues.csv",
    "issue_history":    "issue_history.csv",
    "comments":         "comments.csv",
    "escalations":      "escalations.csv",
}

print("OpsInsight — CSV to Delta Table Loader")
print("=" * 45)

for table_name, csv_file in csv_tables.items():
    try:
        csv_path = f"abfss://{mssparkutils.lakehouse.get().id}@onelake.dfs.fabric.microsoft.com/{mssparkutils.lakehouse.get().workspaceId}/Files/{csv_file}"
        
        df = spark.read.option("header", "true").option("inferSchema", "true").csv(f"{files_path}{csv_file}")
        
        df.write.mode("overwrite").format("delta").saveAsTable(table_name)
        
        print(f"  ✅ {table_name:20s} → {df.count():,} rows loaded")
    except Exception as e:
        print(f"  ❌ {table_name:20s} → ERROR: {e}")

print("\n✅ All tables loaded. Check 'Tables' section on the left.")
