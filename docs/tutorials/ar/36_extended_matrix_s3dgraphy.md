# البرنامج التعليمي 36: تصدير Extended Matrix وجسر s3dgraphy

## مقدمة

ابتداءً من الإصدار **5.2.0-alpha** يدمج PyArchInit **جسرًا ثنائي الاتجاه** مع مكتبة **s3dgraphy** (نموذج بيانات Extended Matrix لإيمانويل ديميترسكو). يتيح الجسر:

- **تصدير** الرسم البياني الطبقي كـ Extended Matrix بتنسيق GraphML (مع خطوط زمنية وتقليل عابر وأنماط حواف EM 1.5)
- **إعادة استيراد** التعديلات المنفذة في yEd (تحريك الوحدات الطبقية بين الفترات/المجموعات) لتحديث قاعدة بيانات SQL
- **إرفاق البيانات الفوقية** (المؤلف / الترخيص / الحظر) على مستوى الموقع
- **تجميع** الوحدات الطبقية حسب البُعد (struttura, area, attivita, settore, ambient, saggio, quad_par أو مجموعات مخصصة)

العلامة الحالية: `phase2-ai08f2-hotfix-5.5.2-alpha` (2026-05-09).

---

## 1. المتطلبات

- قاعدة بيانات SQLite (PostgreSQL غير مدعوم بعد)
- **ترحيل المرحلة 1 node_uuid** يُطبَّق تلقائيًا عند فتح قاعدة البيانات
- **محرر yEd Graph** لعرض الإخراج (https://www.yworks.com/products/yed)

> ⚠️ بالنسبة لقواعد البيانات قبل 5.2.0-alpha قد يستلزم الترحيل إعادة تشغيل QGIS.

---

## 2. تصدير Extended Matrix (الزر الأخضر)

### 2.1 فتح الحوار

1. افتح **بطاقة الوحدة الطبقية** للموقع المطلوب
2. انقر على الزر الأخضر **"Esporta Extended Matrix"** (تحت علامة التبويب Rapporti)

### 2.2 علامة التبويب "Export"

يعرض الحوار:

- **Output formats**: حدد DOT / GraphML / JSON / phased JSON (موصى به: GraphML)
- **Group US by (optional)**: 7 مربعات اختيار للأبعاد + مربع "ad-hoc"
  - الأبعاد المملوءة في قاعدة البيانات تُحدَّد **تلقائيًا** عند الفتح
- **"Select Output Directory"**: مجلد الوجهة

### 2.3 حدّ البُعد الواحد (5.5.2-alpha)

إذا حددت **2 أو أكثر** من مربعات التجميع، يظهر تحذير:

> *"التصدير متعدد الأبعاد غير مدعوم بعد. هل تريد المتابعة باستخدام البُعد الأول فقط؟"*

اختر **نعم** (تصدير بأول بُعد محدد) أو **إلغاء** (تعديل التحديد). التداخل الهرمي (struttura > attivita > US) يصل مع AI08-F1.

### 2.4 انقر على "Export"

يتم إنشاء 4 ملفات بالبادئة `Extended_Matrix_<site>[_<area>]`:
- `.dot` — Graphviz DOT
- `.graphml` — Extended Matrix لـ yEd (الهدف الرئيسي)
- `_s3dgraphy.json` — تنسيق s3dgraphy الأصلي
- `_phased.json` — عرض حسب الحقبة

---

## 3. حوار "Manage paradata" (4 علامات تبويب)

### 3.1 الوصول
انقر على زر **"Manage paradata"** في بطاقة الوحدة الطبقية (بجانب زر التصدير الأخضر).

### 3.2 علامات التبويب الأربع

| علامة التبويب | المحتوى | الملف الناتج |
|---|---|---|
| **Authors** | إضافة المؤلفين (الاسم + ORCID + الدور) | `paradata_<site>.graphml` |
| **Licenses** | ترخيص مجموعة البيانات (مثل CC-BY-NC-4.0 + URL) | نفسه |
| **Embargoes** | تواريخ الحظر + السبب | نفسه |
| **Groups** | مجموعات مخصصة (الاسم + اختيار الوحدات الأعضاء) | `groups_<site>.graphml` |

تُحفَظ الملفات بجانب قاعدة بيانات SQLite ويمكن **التحكم في إصدارها عبر Git**.

---

## 4. نمط مرئي لكل بُعد (5.5.1-alpha)

كل بُعد تجميع له لون مميز في GraphML:

| البُعد | Fill (50% شفافية) | Border |
|---|---|---|
| `area` | وردي باستيل `#FFE0E680` | `#C84A5F` |
| `struttura` | برتقالي باستيل `#FFE6CC80` | `#C66B33` |
| `attivita` | أصفر باستيل `#FFF5CC80` | `#A89A33` |
| `settore` | أخضر باستيل `#E6FFCC80` | `#6BC633` |
| `ambient` | مائي باستيل `#CCFFE680` | `#33A86B` |
| `saggio` | أزرق باستيل `#CCF5FF80` | `#3389A8` |
| `quad_par` | بنفسجي باستيل `#E0CCFF80` | `#6633C6` |
| `adhoc` | رمادي باستيل `#F5F5F580` | `#666666` |

ألفا 50% يترك خطوط الحقب الزمنية مرئية خلف مستطيل المجموعة.

---

## 5. الذهاب والإياب (علامة التبويب Import)

لتعديل قاعدة بيانات SQL بنقل الوحدات بين المجموعات في GraphML:

1. افتح GraphML في **yEd**
2. اسحب وحدة طبقية إلى مجموعة أخرى، احفظ
3. عُد إلى الحوار → علامة التبويب **"Import"**
4. **حدد** مربع *"Update SQL on import (struttura/area/...)"*
5. حمّل GraphML المعدّل

ينفذ النظام معاملة ذرية: في حالة الفشل، **تراجع كامل** (تظل قاعدة البيانات دون تغيير). مجموعات `adhoc` لا تكتب إلى SQL أبدًا — فقط تحدِّث `groups_<site>.graphml`.

---

## 6. CLI (بديل عن الحوار)

للنصوص / الدُفعة:

```bash
# تصدير
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <name> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# قائمة المجموعات المخصصة
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <name>

# إضافة مؤلف
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <name> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

رموز الخروج: 0 = نجاح، 1 = خطأ في الجسر، 2 = خطأ في argparse.

---

## 7. حل المشكلات

| العَرَض | السبب | الحل |
|---|---|---|
| "no such column: node_uuid" | لم يُنفذ ترحيل المرحلة 1 | أعد تشغيل QGIS وافتح قاعدة البيانات مجددًا |
| GraphML فارغ | قاعدة البيانات بدون rapporti / مرشح area صارم جدًا | تحقق من us_table.rapporti |
| مجلد المجموعة فارغ في yEd | تحدّد 2+ أبعاد (حد 5.5.2-alpha) | حدّد بُعدًا واحدًا فقط، أعد المحاولة |
| "يجب أن تكون حقول rapporti نصًا" | أدخلت رقمًا كعدد صحيح | حقول US/Area هي **نص**، وليست أعدادًا صحيحة |
| كتابة بأحرف صغيرة في rapporti | "copre" بأحرف صغيرة في DB | استخدم "Copre", "Coperto da" بأحرف كبيرة |

---

## 8. الوثائق الفنية

للتعمق في البنية وقرارات التصميم وخارطة الطريق:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

العناصر المؤجلة:
- **AI07**: ترحيل `LocationNodeGroup` (الموعد النهائي 2026-05-23)
- **AI08-F1**: التداخل الهرمي (لتصدير متعدد الأبعاد نظيف)
- **AI08-F3**: استدلالات التخطيط التلقائي (تعبئة المجموعات الفرعية)
- **AI09**: ربط TimeBranchNodeGroup
- **Phase 3**: SyncEngine + REST API
- **Phase 4**: GraphDBBackend + SPARQL

---

## المراجع

- قضية upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- مستودع pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
