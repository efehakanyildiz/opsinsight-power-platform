-- ==============================================================================
-- OpsInsight — İleri Düzey Operasyonel & Süreç Zekası Analitik Sorguları
-- Dosya: 06_advanced_operational_analytics.sql
-- Motor: PostgreSQL / Microsoft Fabric / Spark SQL uyumlu
-- Amaç: 11 ilişkisel tablo üzerinden derinlemesine operasyonel darboğaz,
--        SLA ihlal analizi, temsilci performansı ve süreç madenciliği sorguları.
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- SORGUSAL 1: Departman ve Öncelik Bazında Ortalama İlk Yanıt (MTTA) ve Çözüm (MTTR) Süresi
-- İş Amacı: Talebe ilk dokunma hızı ile nihai çözüm hızı arasındaki farkı ölçer.
-- ------------------------------------------------------------------------------
WITH DurationMetrics AS (
    SELECT 
        d.DepartmentName,
        i.Priority,
        ROUND(AVG(EXTRACT(EPOCH FROM (i.FirstResponseAt - i.CreatedAt)) / 3600)::numeric, 2) AS Avg_First_Response_Hours,
        ROUND(AVG(EXTRACT(EPOCH FROM (i.ResolvedAt - i.CreatedAt)) / 3600)::numeric, 2) AS Avg_Resolution_Hours,
        COUNT(i.IssueId) AS Total_Resolved_Issues
    FROM issues i
    JOIN departments d ON i.DepartmentId = d.DepartmentId
    WHERE i.ResolvedAt IS NOT NULL AND i.FirstResponseAt IS NOT NULL
    GROUP BY d.DepartmentName, i.Priority
)
SELECT 
    DepartmentName,
    Priority,
    Avg_First_Response_Hours,
    Avg_Resolution_Hours,
    Total_Resolved_Issues,
    ROUND((Avg_First_Response_Hours / NULLIF(Avg_Resolution_Hours, 0) * 100)::numeric, 1) AS Response_To_Resolve_Ratio_Pct
FROM DurationMetrics
ORDER BY DepartmentName, 
    CASE Priority 
        WHEN 'Critical' THEN 1 
        WHEN 'High' THEN 2 
        WHEN 'Medium' THEN 3 
        WHEN 'Low' THEN 4 
    END;

-- ------------------------------------------------------------------------------
-- SORGUSAL 2: Kronikleşen ve Tekrar Açılan (Reopened) Taleplerin Kök Neden Analizi
-- İş Amacı: Kalıcı çözülemeyip yeniden açılan işlerin hangi kök nedenlerden kaynaklandığını bulur.
-- ------------------------------------------------------------------------------
SELECT 
    rc.RootCauseName,
    COUNT(i.IssueId) AS Reopened_Issue_Count,
    SUM(i.ReopenCount) AS Total_Reopen_Events,
    ROUND(AVG(i.ReopenCount)::numeric, 2) AS Avg_Reopens_Per_Issue,
    ROUND(AVG(EXTRACT(EPOCH FROM (i.ResolvedAt - i.CreatedAt)) / 3600)::numeric, 1) AS Avg_Resolution_Hours_For_Reopened
FROM issues i
JOIN root_causes rc ON i.RootCauseId = rc.RootCauseId
WHERE i.ReopenCount > 0
GROUP BY rc.RootCauseName
ORDER BY Total_Reopen_Events DESC;

-- ------------------------------------------------------------------------------
-- SORGUSAL 3: Ekipler Arasında Pinpon Yapan (Çoklu Transfer Edilen) Biletlerin Tespiti
-- İş Amacı: 2 veya daha fazla kez ekip değiştiren sürtünmeli biletleri listeler.
-- ------------------------------------------------------------------------------
WITH TransferCounts AS (
    SELECT 
        IssueId,
        COUNT(*) AS TransferCount,
        STRING_AGG(DISTINCT NewTeam, ' -> ' ORDER BY NewTeam) AS Team_Hop_Chain
    FROM issue_history
    WHERE EventType = 'Transferred' AND NewTeam IS NOT NULL
    GROUP BY IssueId
    HAVING COUNT(*) >= 2
)
SELECT 
    i.IssueNumber,
    i.Title,
    i.DepartmentName,
    i.Priority,
    i.Status,
    t.TransferCount,
    t.Team_Hop_Chain
FROM TransferCounts t
JOIN issues i ON t.IssueId = i.IssueId
ORDER BY t.TransferCount DESC, i.Priority;

-- ------------------------------------------------------------------------------
-- SORGUSAL 4: SLA İhlal Derinliği ve Gecikme Skoru Analizi
-- İş Amacı: SLA'yı aşan biletlerin hedeften ortalama kaç saat saptığını ölçer.
-- ------------------------------------------------------------------------------
SELECT 
    i.Priority,
    COUNT(i.IssueId) AS Total_Breached_Issues,
    ROUND(AVG(EXTRACT(EPOCH FROM (i.ResolvedAt - i.SLADeadline)) / 3600)::numeric, 2) AS Avg_Breach_Overage_Hours,
    ROUND(MAX(EXTRACT(EPOCH FROM (i.ResolvedAt - i.SLADeadline)) / 3600)::numeric, 2) AS Max_Breach_Overage_Hours,
    ROUND(MIN(EXTRACT(EPOCH FROM (i.ResolvedAt - i.SLADeadline)) / 3600)::numeric, 2) AS Min_Breach_Overage_Hours
FROM issues i
WHERE i.IsSLABreached = TRUE AND i.ResolvedAt IS NOT NULL
GROUP BY i.Priority
ORDER BY Avg_Breach_Overage_Hours DESC;

-- ------------------------------------------------------------------------------
-- SORGUSAL 5: Temsilci (Ajan) Başına Düşen İş Yükü ve SLA Başarı Karnesi
-- İş Amacı: Operasyon çalışanlarının iş yükü adaleti ve başarı yüzdelerini karşılaştırır.
-- ------------------------------------------------------------------------------
SELECT 
    i.AssignedAgentName,
    i.AssignedTeamName,
    COUNT(i.IssueId) AS Total_Assigned_Issues,
    COUNT(CASE WHEN i.Status IN ('New', 'Assigned', 'In Progress', 'Waiting') THEN 1 END) AS Active_Backlog_Count,
    COUNT(CASE WHEN i.Status IN ('Resolved', 'Closed') THEN 1 END) AS Completed_Issues,
    COUNT(CASE WHEN i.IsSLABreached = TRUE THEN 1 END) AS SLA_Breach_Count,
    ROUND(
        (COUNT(CASE WHEN i.IsSLABreached = FALSE AND i.Status IN ('Resolved', 'Closed') THEN 1 END)::numeric /
        NULLIF(COUNT(CASE WHEN i.Status IN ('Resolved', 'Closed') THEN 1 END), 0) * 100)::numeric, 
    2) AS Agent_SLA_Success_Pct
FROM issues i
WHERE i.AssignedAgentName IS NOT NULL
GROUP BY i.AssignedAgentName, i.AssignedTeamName
HAVING COUNT(i.IssueId) >= 15
ORDER BY Agent_SLA_Success_Pct DESC, Active_Backlog_Count ASC;

-- ------------------------------------------------------------------------------
-- SORGUSAL 6: Süreç Darboğazı: Her Statüde Geçen Ortalama Süre (Saat)
-- İş Amacı: IssueHistory tablosundan işlerin en çok hangi statüde beklediğini hesaplar.
-- ------------------------------------------------------------------------------
WITH StatusDurations AS (
    SELECT 
        h.IssueId,
        h.NewStatus AS StageName,
        h.ChangeTimestamp AS StageStart,
        LEAD(h.ChangeTimestamp) OVER (PARTITION BY h.IssueId ORDER BY h.ChangeTimestamp) AS StageEnd
    FROM issue_history h
    WHERE h.NewStatus IS NOT NULL
)
SELECT 
    StageName,
    COUNT(*) AS Stage_Occurrence_Count,
    ROUND(AVG(EXTRACT(EPOCH FROM (StageEnd - StageStart)) / 3600)::numeric, 2) AS Avg_Hours_In_Stage,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (StageEnd - StageStart)) / 3600)::numeric, 2) AS Median_Hours_In_Stage
FROM StatusDurations
WHERE StageEnd IS NOT NULL
GROUP BY StageName
ORDER BY Avg_Hours_In_Stage DESC;

-- ------------------------------------------------------------------------------
-- SORGUSAL 7: En Çok Yönetici Eskalasyonuna Neden Olan Operasyonel Kategoriler
-- İş Amacı: Hangi kategorilerin en yüksek yönetici müdahalesi (Escalation) ürettiğini listeler.
-- ------------------------------------------------------------------------------
SELECT 
    c.CategoryName,
    d.DepartmentName,
    COUNT(e.EscalationId) AS Total_Escalations,
    COUNT(DISTINCT i.IssueId) AS Escalated_Issue_Count,
    ROUND((COUNT(e.EscalationId)::numeric / COUNT(DISTINCT i.IssueId)::numeric), 2) AS Escalations_Per_Issue
FROM escalations e
JOIN issues i ON e.IssueId = i.IssueId
JOIN categories c ON i.CategoryId = c.CategoryId
JOIN departments d ON i.DepartmentId = d.DepartmentId
GROUP BY c.CategoryName, d.DepartmentName
ORDER BY Total_Escalations DESC
LIMIT 10;

-- ------------------------------------------------------------------------------
-- SORGUSAL 8: Dahili Ekip Notları ile Çözüm Süresi Korelasyonu
-- İş Amacı: Çok tartışılan / yorum yapılan işlerin çözüm süresini inceler.
-- ------------------------------------------------------------------------------
WITH IssueCommentsSummary AS (
    SELECT 
        IssueId,
        COUNT(CommentId) AS Total_Comments,
        COUNT(CASE WHEN IsInternal = TRUE THEN 1 END) AS Internal_Notes,
        COUNT(CASE WHEN IsInternal = FALSE THEN 1 END) AS Public_Comments
    FROM comments
    GROUP BY IssueId
)
SELECT 
    CASE 
        WHEN cs.Total_Comments = 0 THEN '0 Yorum (Sessiz)'
        WHEN cs.Total_Comments BETWEEN 1 AND 2 THEN '1-2 Yorum (Düşük)'
        WHEN cs.Total_Comments BETWEEN 3 AND 5 THEN '3-5 Yorum (Orta)'
        ELSE '6+ Yorum (Yüksek Sürtünme)'
    END AS Communication_Volume_Tier,
    COUNT(i.IssueId) AS Issue_Count,
    ROUND(AVG(EXTRACT(EPOCH FROM (i.ResolvedAt - i.CreatedAt)) / 3600)::numeric, 2) AS Avg_Resolution_Hours,
    ROUND(AVG(i.ReopenCount)::numeric, 2) AS Avg_Reopen_Count,
    ROUND((COUNT(CASE WHEN i.IsSLABreached = TRUE THEN 1 END)::numeric / COUNT(i.IssueId) * 100)::numeric, 2) AS SLA_Breach_Rate_Pct
FROM issues i
LEFT JOIN IssueCommentsSummary cs ON i.IssueId = cs.IssueId
WHERE i.ResolvedAt IS NOT NULL
GROUP BY Communication_Volume_Tier
ORDER BY Avg_Resolution_Hours ASC;

-- ------------------------------------------------------------------------------
-- SORGUSAL 9: Günlük Talep Girişi ve Çıkışı ile Kümülatif Backlog Trendi
-- İş Amacı: Operasyonun günlük gelen işi karşılama hızını (Giriş vs Çıkış) izler.
-- ------------------------------------------------------------------------------
WITH DailyInflow AS (
    SELECT 
        DATE(CreatedAt) AS IssueDate,
        COUNT(*) AS InflowCount
    FROM issues
    GROUP BY DATE(CreatedAt)
),
DailyOutflow AS (
    SELECT 
        DATE(ResolvedAt) AS IssueDate,
        COUNT(*) AS OutflowCount
    FROM issues
    WHERE ResolvedAt IS NOT NULL
    GROUP BY DATE(ResolvedAt)
),
CombinedDates AS (
    SELECT IssueDate FROM DailyInflow
    UNION
    SELECT IssueDate FROM DailyOutflow
)
SELECT 
    d.IssueDate,
    COALESCE(inf.InflowCount, 0) AS New_Issues_Created,
    COALESCE(outf.OutflowCount, 0) AS Issues_Resolved,
    COALESCE(inf.InflowCount, 0) - COALESCE(outf.OutflowCount, 0) AS Daily_Net_Backlog_Change,
    SUM(COALESCE(inf.InflowCount, 0) - COALESCE(outf.OutflowCount, 0)) OVER (ORDER BY d.IssueDate) AS Cumulative_Open_Backlog
FROM CombinedDates d
LEFT JOIN DailyInflow inf ON d.IssueDate = inf.IssueDate
LEFT JOIN DailyOutflow outf ON d.IssueDate = outf.IssueDate
ORDER BY d.IssueDate DESC
LIMIT 30;

-- ------------------------------------------------------------------------------
-- SORGUSAL 10: Çözüm Kodlarının Kalite Denetimi: "Workaround" vs Kalıcı Çözüm
-- İş Amacı: Çözümlerin ne kadarının kalıcı (Bug Fix, Config) ne kadarının geçici olduğunu denetler.
-- ------------------------------------------------------------------------------
SELECT 
    rc.ResolutionName,
    COUNT(i.IssueId) AS Total_Usage_Count,
    ROUND((COUNT(i.IssueId)::numeric / SUM(COUNT(i.IssueId)) OVER () * 100)::numeric, 2) AS Usage_Share_Pct,
    ROUND(AVG(i.ReopenCount)::numeric, 3) AS Reopen_Risk_Index,
    ROUND(AVG(EXTRACT(EPOCH FROM (i.ResolvedAt - i.CreatedAt)) / 3600)::numeric, 2) AS Avg_Hours_To_Apply_Resolution
FROM issues i
JOIN resolution_codes rc ON i.ResolutionCodeId = rc.ResolutionCodeId
WHERE i.ResolvedAt IS NOT NULL
GROUP BY rc.ResolutionName
ORDER BY Total_Usage_Count DESC;
