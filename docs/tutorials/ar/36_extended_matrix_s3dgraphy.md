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

## 5. yEd-aware Import — استيراد ملفات graphml المحررة خارجياً (5.8.x)

اعتباراً من **5.8.0-alpha** أصبح الجسر (bridge) **ثنائي الاتجاه أيضاً مع ملفات graphml التي تم إنشاؤها مباشرة في yEd** (أي دون المرور أولاً عبر تصدير pyarchinit). يتعرّف pyarchinit تلقائياً على ملفات graphml من نوع «yEd-raw» — تلك التي لا تحمل data keys بصيغة `pyarchinit.*` — ويستوردها عبر dispatch مخصّص يقوم بربط بادئة label العقدة بالنوع الطبقي، ويتعرّف على صفوف TableNode باعتبارها فترات (periods)، ويسير عبر group folders كأبعاد أثرية، ويترك للمستخدم اختيار سياسة (policy) للتعامل مع الـ edges التي تلامس folders.

### 5.1 الطرح على 6 مراحل

| المرحلة | Tag | ما تضيفه |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — راية flavor `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — تعداد `ClassificationKind` بـ 13 قيمة (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + regex حساسة للترتيب |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate من صفوف TableNode) + `yed_group_walker.py` (FolderCandidate مع auto-dimension من بادئة الـ label: VA01→attivita / AR01→area / إلخ) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — المُنسِّق `import_yed_raw()` + 5 write functions + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + paradata عبر `ParadataStore` + sentinel `_DryRunRollback` + DbHandle لكل من PG وSQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` بخمس صفحات (classifier / periods / folders / policy / preview) + dataclass `YedOverrides` + حفظ sidecar `<graphml>.yed_overrides.json` |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | هذه الوثيقة + dev-log + CHANGELOG. |

### 5.2 كيف يعمل — تدفق المستخدم

1. **افتح ملف graphml في QGIS من قائمة Import GraphML** (نفس مسار تدفق pyarchinit-projected الموجود).
2. يكتشف pyarchinit تلقائياً أنه yEd-raw (لا توجد keys بصيغة `pyarchinit.*`) → يحوِّل إلى الـ branch الجديد بدلاً من السقوط إلى المسار القديم.
3. يفتح المعالج `YedImportDialog` بـ **5 صفحات**:
   - **1/5 Classifier** — جدول، صف واحد لكل leaf node. يعرض كل صف `label` + `auto_kind` (مثلاً `us_real` / `usv_virtual` / `property`) + combobox تجاوز `user_kind`. زر **Accept auto** يُعيد كل الصفوف إلى قيم `auto_kind` (يمسح كل التجاوزات).
   - **2/5 Periods** — صف واحد لكل TableNode-row تم تحليله، وأعمدة قابلة للتعديل `periodo` + `fase`. تبقى التواريخ (`datazione_iniziale`/`finale`) فارغة: ملفات graphml من نوع yEd-raw لا تحمل تواريخ.
   - **3/5 Folders** — صف واحد لكل group folder. Combobox للقيمة `dimension` (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` للاستبعاد). الحقل `value` قابل للتعديل (الافتراضي = `auto_value` المشتقّ من بادئة الـ label).
   - **4/5 Rapporti policy** — أربعة radio buttons لطريقة التعامل مع الـ edges الملامِسة لـ folders:
     - **SKIP** (الافتراضي): إسقاط الـ edges الملامِسة لـ folders. تمرّ edges leaf-to-leaf دون تغيير.
     - **FAN_OUT**: تتمدّد edge `folder_A → folder_B` إلى `N×M` زوجاً من الـ leaves (الجداء الديكارتي للأعضاء).
     - **REPRESENTATIVE**: استخدام العضو الأول لكل folder كوكيل (proxy).
     - **SYNTHETIC**: إنشاء صف us_table واحد لكل folder (`unita_tipo='VA'` virtual activity) + إعادة توجيه الـ edges عبر هذه المراسي.
   - **5/5 Preview** — تشغيل تجريبي (dry-run) لـ `import_yed_raw(overrides=..., dry_run=True)`. يعرض العدّادات (us / inv / period / paradata) **دون commit**. النقر على **Finish** يثبّت، و**Cancel** يلغي.
4. عند **Finish** يحفظ المعالج تجاوزاتك في **sidecar JSON** باسم `<graphml>.yed_overrides.json` بجوار الملف. إعادة فتح نفس الـ graphml تُحمِّل الـ sidecar مسبقاً، فتعود تجاوزاتك السابقة مطبَّقة.

### 5.3 توجيه الوجهات

يستخدم الـ dispatch دالة `_classify_destination` (في `yed_import_pipeline.py`) لتصنيف كل leaf:

| ClassificationKind | الوجهة | ملاحظة |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | من label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | من `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | من `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | من `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` مشتق من بادئة الـ label: USVs/USVn/USVc) | من `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | من `^RSF\d+` (s3dgraphy 0.1.42، spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | من `^SF\d+` |
| VIRTUAL_FIND | `paradata` (عبر `ParadataStore`) | من `^VSF\d+` |
| DOCUMENT | `paradata` | من `^D\.\d+` |
| COMBINER | `paradata` | من `^C\.\d+` |
| PROPERTY | `paradata` | كلمة مفتاحية في الـ label (`material`/`position`/`width`/...) |

**قرار مستخدم 2026-05-13**: عناصر USV* (الافتراضية) هي «unità tipo» (تظل وحدات طبقية) وتنتمي إلى `us_table` لا إلى paradata. فقط DOC/COMB/PROP/VIRTUAL_FIND تبقى في paradata.

### 5.4 Sidecar JSON — المخطط

مُرقّم الإصدار لضمان التوافق المستقبلي:

```json
{
  "version": 1,
  "saved_at": "2026-05-13T17:57:00+00:00",
  "graphml_path": "/absolute/path/to/file.graphml",
  "classifier": {
    "n0::n0::n0": "us_real",
    "n0::n0::n2": "us_real"
  },
  "periods": {
    "p0": {"periodo": 5, "fase": 7}
  },
  "folders": {
    "f0": {"dimension": "struttura", "value": "S01"}
  },
  "policy": "fan_out"
}
```

تُحفَظ فقط الحقول التي عدّلها المستخدم (diff). تُتجاهَل قيم `ClassificationKind` غير المعروفة (مثل ما قد يأتي من إصدارات لاحقة من s3dgraphy) بصمت عند التحميل.

### 5.5 CLI للاستيراد عبر سكربتات

لاستخدامات CI / إعادة التشغيل بالدُّفعات:

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

تنافٍ متبادل بين `--db` و`--conn-str` لاختيار backend SQLite أو PostgreSQL. `--overrides` اختياري (بدون overrides = الافتراضيات في yE-D). `--auto-defaults` هي no-op للتوافق المستقبلي.

### 5.6 قيود معروفة

- **لا تحرير للتواريخ في المعالج**: ملفات graphml من نوع yEd-raw لا تحمل `datazione_iniziale`/`datazione_finale`. تحرّر صفحة Periods فقط `periodo` + `fase` (وهي أهداف FK).
- **API ParadataStore جزئية**: لا توفّر مكتبة s3dgraphy الأصلية بعد دوال `add_virtual_us` / `add_document` / `add_combiner` / `add_property`. يسجّل yE-D «skip — method missing» لكل paradata leaf لكنه يُحصي المحاولات في الـ preview.
- **PropertyNode → Path B (بدون ربط بـ US)**: تُكتب عقد PROPERTY دون US هدف. يُصدر المعالج تحذيراً. مستقبلاً: متابعة yE-Closure لإضافة «assign target» في الواجهة.
- **متعدد قواعد البيانات**: ملف sidecar JSON مرتبط بـ graphml وليس بـ DB. استيراد نفس الـ graphml إلى قواعد بيانات مختلفة يستخدم نفس الـ overrides لجميعها.

### 5.7 تغطية الاختبارات النهائية

| Suite | Test | Coverage |
|---|---|---|
| yE-A | `test_yed_detector.py` | كشف الـ flavor |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + regex حساسة للترتيب |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | parse PeriodCandidate + FolderCandidate |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 بما فيها 2 L1 overrides e2e) | السياسات + write functions + dispatch |
| yE-E | `test_yed_import_dialog.py` (5 sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | حفظ الـ sidecar + CLI |

**مجموع الـ suite بعد الطرح**: 354 passed / 42 skipped (PG-L1 تتطلّب psycopg2).

### 5.8 تحديث 5.8.5-alpha (yed-fastfix)

حزمة إصلاحات سلوكية فوق `5.8.3-alpha` تُحسّن جودة إعادة تصدير GraphML بعد استيراد yEd-aware. تغييرات تهمّ المستخدم النهائي:

- **paradata متعدد الـ folders**: تسميات DOC / Combinar / Extractor / property المشتركة بين عدّة folders في yEd (مثلاً `material` المُشار إليها من VA01 + VA04 + VA05) تُنشئ الآن سطراً واحداً في `us_table` لكل ظهور — استعادة الرؤية متعددة الـ folders في GraphML المُعاد تصديره. مقايضة: لم يعد dedup الهوية (دمج `D.01` / `D.01-2` / `D.01bis` في سطر واحد) ينطبق على الظهور الثاني/الثالث.
- **rapporti متبادلة**: كل edge في yEd `a → b` يكتب الـ rapporto الأمامي على سطر `a` والعكسي على سطر `b` (`<<` / «Coperto da» / إلخ). تُظهر الآن DOCs جميع اتصالات extractor الواردة في نموذج Scheda US.
- **إزالة بادئة `us` الرقمية**: `US100` → `us='100'` `unita_tipo='US'` (سابقاً `us='US100'`). تُكتب SF/VSF/RSF بكتابة مزدوجة في `us_table` + `inventario_materiali`.
- **تعبئة تلقائية للـ periodo/fase**: انتماء صف TableNode في yEd إلى فترة ينتشر إلى `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **classifier متوافق مع BPMN**: `D.NN` (BPMN data-object) → `DocumentNode`، و`D.NN.MM` (plain) → `ExtractorNode` — يحافظ على التمييز الدلالي لـ EM 1.5.
- **إعادة استيراد idempotent**: إعادة تشغيل نفس الاستيراد تتخطّى الصفوف الموجودة مسبقاً؛ لا rollback بسبب تصادم UNIQUE في الجولة المُكرَّرة.
- **لوحة ألوان USV**: تُرسم عقد USV الآن بمتوازي الأضلاع الأزرق القانوني الخاص بـ EM (سابقاً مستطيل بحدود حمراء).

### 5.9 yE-F paradata متعدد المجلدات (5.9.0-alpha)

تطوّر بنيوي لـ `yed-fastfix-5.8.5-alpha`: تمّ تجاوز مقايضة Bug R B1 (سطر `us_table` لكل ظهور، مع `us='D.01_2'` / `us='D.01_3'`). أصبحت ورقة paradata (DOC / Combinar / Extractor / property) المُشتركة بين عدّة مجلدات yEd تُنتج الآن **سطراً واحداً فقط** في `us_table` لكل label قانوني، ويتم الحفاظ على الانتماء المتعدد في عمود جديد `other_locations`.

تغييرات ظاهرة للمستخدم النهائي:

1. **widget جديد "أنشطة أخرى" في نموذج US/USM**: في تبويب *Periodizzazione* يظهر `QListWidget` بعنوان "أنشطة أخرى" — مرئي **فقط** عندما يكون `unita_tipo` من نوع paradata (`DOC`، `Combinar`، `Extractor`، `property`). يمكن للمستخدم اختيار عدّة رموز أنشطة؛ يتم تخزين الاختيار كقائمة JSON في العمود الجديد `other_locations`.
2. **عنصر قائمة QGIS جديد**: `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. يجب تشغيله **مرّة واحدة** على كل قاعدة بيانات سابقة لإضافة العمود الجديد (قواعد البيانات المُنشأة بعد 5.9 تحتوي على العمود بالفعل).
3. **استيراد yEd-aware مُحسَّن**: ورقة paradata تظهر في N مجلداً يEd تُنتج الآن **سطراً واحداً فقط** في `us_table` (لم تعد N أسطر باللاحقة `_2`/`_3` كما في 5.8.5). المجلد الأول الذي تتم مصادفته يصبح الـ `attivita` الأساسي؛ المجلدات الثانوية تُدرج في `other_locations`. عند **التصدير** تُصدَّر N نسخ بصرية من yEd (واحدة لكل مجلد)، جميعها تشترك في نفس `node_uuid` القانوني لضمان هوية round-trip.

**التوافق الرجعي**: البيانات المُنتَجة بواسطة Bug R B1 في 5.8.5-alpha (أسطر باللاحقة `_2`/`_3`) تبقى قابلة للقراءة دون أي تحويل تلقائي. المنطق الجديد يُطبَّق على الاستيرادات الجديدة؛ الأسطر القديمة تواصل التصرّف كما كانت سابقاً.

السلف: انظر القسم 5.8 (`yed-fastfix-5.8.5-alpha`) للسلوك المُستبدَل.

---

## المراجع

- قضية upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- مستودع pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
