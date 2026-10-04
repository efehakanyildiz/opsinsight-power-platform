# OpsInsight — Semantic Model Veri Sözlüğü

**Sürüm:** 2.0 · **Tarih:** Ekim 2026  
**Kaynak:** Microsoft Fabric Lakehouse — 11 Delta tablo (`fabric_load_tables.py` ile yüklenir)

---

## 1. Modeldeki Tablolar

| Tablo | Kayıt | Rol | Açıklama |
|---|---:|---|---|
| `issues` | 2.200 | Fact | Ana talep tablosu; tüm ölçüler bu tablo üzerinde tanımlıdır |
| `issue_history` | 11.232 | Olay (Event Fact) | Statü değişikliği, atama ve transfer günlüğü |
| `escalations` | 315 | Olay (Event Fact) | SLA aşımı sonrası yöneticiye yapılan eskalasyonlar |
| `comments` | 4.073 | Bağımsız analiz tablosu | Dahili notlar ve talep sahibi yazışmaları |
| `employees` | 96 | Bağımsız analiz tablosu | Çalışan rehberi (talep sahibi, temsilci, yönetici) |
| `departments` | 6 | Boyut | Departman listesi ve yöneticileri |
| `teams` | 10 | Boyut | Operasyon ekipleri |
| `categories` | 24 | Boyut | Departmana bağlı talep kategorileri |
| `sla_rules` | 4 | Boyut | Öncelik bazlı SLA hedef saatleri ve eşikleri |
| `root_causes` | 10 | Boyut | Kök neden kataloğu |
| `resolution_codes` | 9 | Boyut | Kapanış yöntemi kataloğu |

---

## 2. `issues` Tablosu

| Sütun | Tür | Açıklama |
|---|---|---|
| `IssueId` | Metin | Birincil anahtar |
| `IssueNumber` | Metin | Talep numarası (`OPS-YYYY-NNNN`) |
| `Title` / `Description` | Metin | Talep başlığı ve açıklaması |
| `CreatedBy` / `CreatedByName` | Metin | Talep sahibi kimliği ve denormalize adı |
| `CreatedAt` | Tarih-Saat | Talebin oluşturulma zamanı |
| `DepartmentId` / `DepartmentCode` | Metin | Departman anahtarı ve kodu (`IT`, `FIN`, `HR`, `PROC`, `OPS`, `SALES`) |
| `CategoryId` / `CategoryName` | Metin | Kategori anahtarı ve adı |
| `AssignedTeamId` / `AssignedTeamName` | Metin | Atanan ekip anahtarı ve adı |
| `AssignedAgentId` / `AssignedAgentName` | Metin | Atanan temsilci anahtarı ve adı |
| `Priority` | Metin | Critical / High / Medium / Low |
| `Status` | Metin | New, Assigned, In Progress, Waiting, Resolved, Closed, Reopened, Cancelled |
| `SLAId` / `SLATargetHours` / `SLADeadline` | Metin / Ondalık / Tarih-Saat | SLA kuralı, hedef saat ve son teslim zamanı |
| `FirstResponseAt` / `ResolvedAt` / `ClosedAt` | Tarih-Saat | İlk yanıt, çözüm ve kapanış zamanları |
| `RootCauseId` / `ResolutionCodeId` | Metin | Kök neden ve çözüm kodu anahtarları |
| `ResolutionSummary` | Metin | Çözüm açıklaması |
| `ReopenCount` | Tam sayı | Yeniden açılma sayısı |
| `LastUpdatedAt` | Tarih-Saat | Son güncelleme zamanı |

### Hesaplanan Sütunlar

| Sütun | Tür | Açıklama |
|---|---|---|
| `CreatedMonth` | Tarih | Oluşturulma ayının ilk günü (trend ekseni) |
| `FirstResponseDurationHours` | Ondalık | `CreatedAt → FirstResponseAt` arası saat |
| `ResolutionDurationHours` | Ondalık | `CreatedAt → ResolvedAt` arası saat |
| `IsSLABreached` | Mantıksal | Çözüm zamanı (açık taleplerde şu an) `SLADeadline`'ı aştı mı? |

---

## 3. `issue_history` Tablosu

| Sütun | Tür | Açıklama |
|---|---|---|
| `HistoryId` | Metin | Birincil anahtar |
| `IssueId` | Metin | `issues` tablosuna yabancı anahtar |
| `EventType` | Metin | Created, Assigned, StatusChanged, Transferred, Resolved, Closed, Reopened |
| `PreviousStatus` / `NewStatus` | Metin | Geçiş öncesi ve sonrası statü |
| `PreviousTeam` / `NewTeam` | Metin | Transfer öncesi ve sonrası ekip |
| `ChangedBy` | Metin | Değişikliği yapan çalışan veya `SYSTEM` |
| `ChangeTimestamp` | Tarih-Saat | Olay zamanı |
| `Notes` | Metin | Ek açıklama |

---

## 4. İlişkiler

| Kaynak (1) | Hedef (N) | Anahtar | Durum |
|---|---|---|---|
| `departments` | `issues` | `DepartmentId` | Aktif |
| `categories` | `issues` | `CategoryId` | Aktif |
| `teams` | `issues` | `TeamId → AssignedTeamId` | Aktif |
| `sla_rules` | `issues` | `SLAId` | Aktif |
| `root_causes` | `issues` | `RootCauseId` | Aktif |
| `resolution_codes` | `issues` | `ResolutionCodeId` | Aktif |
| `issues` | `issue_history` | `IssueId` | Aktif |
| `issues` | `escalations` | `IssueId` | Aktif |
| `departments` | `teams` | `DepartmentId` | Pasif (belirsiz filtre yolunu önlemek için) |
| `departments` | `categories` | `DepartmentId` | Pasif (belirsiz filtre yolunu önlemek için) |

Tüm aktif ilişkiler **tek yönlü** çapraz filtre kullanır. `employees` ve `comments` tabloları bilinçli olarak ilişkisiz tutulmuştur; çalışan bilgisi için `issues` içindeki denormalize isim alanları kullanılır.

---

## 5. Çekirdek Ölçüler

| Ölçü | Açıklama | Biçim |
|---|---|---|
| `Total Issues` | Toplam talep sayısı | Tam sayı |
| `Open Issues` | Aktif statülerdeki talepler | Tam sayı |
| `Resolved Issues` | Resolved + Closed | Tam sayı |
| `Backlog` | Çözülmemiş iş yükü | Tam sayı |
| `SLA Breached Issues` | SLA'yı aşan talepler | Tam sayı |
| `SLA Compliance %` | Çözülenler içinde SLA'ya uyanların oranı | % |
| `Avg Resolution Time Hours` | Ortalama çözüm süresi | Ondalık |
| `Avg First Response Time Hours` | Ortalama ilk yanıt süresi | Ondalık |
| `Avg SLA Target Hours` | Ortalama SLA hedefi | Ondalık |
| `Escalation Rate %` | Eskalasyon / toplam talep | % |

Genişletilmiş ölçü tasarımları için: [`measures.md`](measures.md)

---

## 6. Veri Kalitesi Notları

- Boş zaman damgaları `null` olarak ele alınır.
- `IsSLABreached`, çözülmüş taleplerde `ResolvedAt`, açık taleplerde `NOW()` ile hesaplanır.
- `issue_history[ChangedBy]` alanı `SYSTEM` değeri alabilir; geçerli bir `EmployeeId` değildir.
- Saniye hassasiyetli zaman damgaları kategorik eksenlerde kullanılmaz; bunun yerine `CreatedMonth` kullanılır.
