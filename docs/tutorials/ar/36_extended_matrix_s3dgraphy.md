# البرنامج التعليمي 36: تصدير Extended Matrix وجسر s3dgraphy

## مقدمة

ابتداءً من الإصدار **5.2.0-alpha** يدمج PyArchInit **جسرًا ثنائي الاتجاه** مع مكتبة **s3dgraphy** (نموذج بيانات Extended Matrix لإيمانويل ديميترسكو). يتيح الجسر:

- **تصدير** الرسم البياني الطبقي كـ Extended Matrix بتنسيق GraphML (مع خطوط زمنية وتقليل عابر وأنماط حواف EM 1.5)
- **إعادة استيراد** التعديلات المنفذة في yEd (تحريك الوحدات الطبقية بين الفترات/المجموعات) لتحديث قاعدة بيانات SQL
- **إرفاق البيانات الفوقية** (المؤلف / الترخيص / الحظر) على مستوى الموقع
- **تجميع** الوحدات الطبقية حسب البُعد (struttura, area, attivita, settore, ambient, saggio, quad_par أو مجموعات مخصصة)

العلامة الحالية: `phase2-ai07-locationnodegroup-5.6.0-alpha` (2026-05-10).

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
- **مربع تحرير وسرد البعد الأساسي** (افتراضي `struttura`): عندما تكون لوحدة طبقية عضوية في بُعدين أو أكثر، يفوز البُعد الأساسي كمجلد yEd مرئي (الأصل الهرمي). تظهر الأبعاد الأخرى كشارات مضمنة أسفل عقدة الوحدة الطبقية. `toponym` ليس أساسيًا أبدًا، بصرف النظر عن الاختيار.
- **"Select Output Directory"**: مجلد الوجهة

ابتداءً من 5.6.0-alpha يمكنك تحديد **2+ أبعاد**: التصدير يعمل أصلًا بفضل النموذج m:n مع `is_primary` (انظر قسم "العضوية متعددة الأبعاد").

### 2.3 انقر على "Export"

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

## 4. نمط مرئي لكل بُعد (5.5.1-alpha + 5.6.0-alpha)

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

ابتداءً من 5.6.0-alpha، تتمايز عناصر `LocationNodeGroup` حسب `kind`:

| `kind` | Fill (50% شفافية) | Border |
|---|---|---|
| `toponym` | لافندر باستيل `#E6E6FA80` | `#9370DB` |
| `study` | عاجي باستيل `#FFFFE080` | `#888888` |
| `functional` | سماوي باستيل `#E0FFFF80` | `#008B8B` |

ألفا 50% يترك خطوط الحقب الزمنية مرئية خلف مستطيل المجموعة.

### 4.1 سلسلة الأماكن الجغرافية (5.6.0-alpha)

تُصدَّر حقول `site_table.{nazione, regione, provincia, comune}` تلقائيًا كسلسلة تكرارية من `LocationNodeGroup(kind="toponym")` (الأصل: nazione → regione → provincia → comune). يتم تجاوز المستويات الإدارية الفارغة دون كسر السلسلة. يضمن إزالة التكرار عبر المواقع أن تصبح `comune` نفسها الموجودة في موقعين **عقدة واحدة مشتركة** في GraphML.

---

## 4.2 العضوية متعددة الأبعاد (5.6.0-alpha)

ابتداءً من 5.6.0-alpha يمكن لوحدة طبقية أن تنتمي إلى **أبعاد متعددة في وقت واحد** بفضل النموذج m:n مع علم `is_primary`. يصبح البُعد الأساسي فقط مجلد yEd المرئي؛ يظهر الباقون كـ **شارات مضمنة** أسفل عقدة الوحدة الطبقية وكـ JSON في `<data key="s3d:other_locations">` للأدوات اللاحقة.

مثال: وحدة طبقية بـ `struttura=basilica` و `area=B` (الأساسي `struttura`) ينتج عنها:
- مجلد yEd "struttura: basilica" كأصل مرئي؛
- أسفل عقدة الوحدة الطبقية، شارة مضمنة `also: B (study), TestCity (toponym)`؛
- في GraphML، السمة `s3d:other_locations` بمصفوفة JSON للعضويات الثانوية.

يتم التحكم في البُعد الأساسي عبر مربع التحرير والسرد في §2.2.

---

## 5. الذهاب والإياب (علامة التبويب Import)

لتعديل قاعدة بيانات SQL بنقل الوحدات بين المجموعات في GraphML:

1. افتح GraphML في **yEd**
2. اسحب وحدة طبقية إلى مجموعة أخرى، احفظ
3. عُد إلى الحوار → علامة التبويب **"Import"**
4. **حدد** مربع *"Update SQL on import (struttura/area/...)"*
5. حمّل GraphML المعدّل

ينفذ النظام معاملة ذرية: في حالة الفشل، **تراجع كامل** (تظل قاعدة البيانات دون تغيير). مجموعات `adhoc` لا تكتب إلى SQL أبدًا — فقط تحدِّث `groups_<site>.graphml`.

ابتداءً من 5.6.0-alpha يكون walker الاستيراد **تكراريًا** ويدعم المجلدات المتداخلة (مثل سلسلة الأماكن الجغرافية `nazione > regione > provincia > comune > US`). إذا تم اكتشاف دورات في رسم المجلدات، يتم رفع استثناء `CycleDetectedError` وإجهاض الاستيراد مع التراجع.

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
| "يجب أن تكون حقول rapporti نصًا" | أدخلت رقمًا كعدد صحيح | حقول US/Area هي **نص**، وليست أعدادًا صحيحة |
| كتابة بأحرف صغيرة في rapporti | "copre" بأحرف صغيرة في DB | استخدم "Copre", "Coperto da" بأحرف كبيرة |
| `DeprecationWarning` على ملف 5.5.x | ملف قديم بـ `ActivityNodeGroup + group_kind` | يقوم projector بترقيته في الذاكرة إلى `LocationNodeGroup`. أعد التصدير لترحيل الملف على القرص. |

---

## 8. الوثائق الفنية

للتعمق في البنية وقرارات التصميم وخارطة الطريق:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

العناصر المؤجلة:
- **AI08-F3**: استدلالات التخطيط التلقائي (تعبئة المجموعات الفرعية) — لا تزال مؤجلة
- **AI09**: ربط TimeBranchNodeGroup — مستقبلي
- **Phase 3**: SyncEngine + REST API — مستقبلي
- **Phase 4**: GraphDBBackend + SPARQL — مستقبلي

تم إنجازها:
- **AI07** (5.6.0-alpha, 2026-05-10): ترحيل `LocationNodeGroup` مع تعداد `kind` + سلسلة الأماكن الجغرافية + العضويات متعددة الأبعاد
- **AI08-F1** (مدمج في AI07): تداخل هرمي أصلي عبر `is_primary`

---

## المراجع

- قضية upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- مستودع pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
