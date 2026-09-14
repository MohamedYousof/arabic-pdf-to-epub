---
name: arabic-pdf-to-epub
description: Autonomous end-to-end converter for Arabic PDF books into Kindle-ready EPUB3 ebooks. Performs native visual OCR, page typology classification, Arabic proofreading, Quranic verse verification, interactive footnotes linking, and RTL EPUB packaging without external API keys. Use when user wants to convert an Arabic PDF book to EPUB, create a Kindle Arabic ebook, or requests Arabic PDF to EPUB conversion.
---

# Arabic PDF to Kindle EPUB3 Converter

Converts scanned and digital Arabic book PDFs into high-quality, reflowable, Kindle-optimized **EPUB3** ebooks. The workflow is fully autonomous, utilizing native multimodal vision for OCR and transcription, offline Quranic verification, Arabic typographical styling, and strict EPUB3/Kindle packaging without external API keys.

---

## 🛠️ Prerequisites & Environment Auto-Bootstrap

The conversion pipeline relies on standard Python for rendering PDF pages and packaging EPUB archives.

1. **Environment Detection:**
   - **macOS / Linux / Windows**: The agent should verify that `python3` (or `python` on Windows) is available.
   - If a local virtual environment (`.venv`) does not exist, initialize it:
     ```bash
     python3 -m venv .venv
     .venv/bin/pip install pymupdf
     ```
   - On Windows:
     ```powershell
     python -m venv .venv
     .venv\Scripts\pip install pymupdf
     ```
2. **Offline & Self-Contained:**
   - Visual transcription is executed directly via multimodal vision (`view_file`), requiring **zero external OCR services or API keys**.

---

## 🤖 Subagent Architecture & Execution Rules

When converting full-length books (100–500+ pages), subagents should be utilized to manage context windows efficiently. Follow these strict operational rules:

### 1. Sequential Single-Subagent Pipeline (الوكيل الفردي المتتابع)
- **Do NOT spawn multiple concurrent subagents** for vision OCR. Running parallel subagents causes auth token contention and rate limits (`401 UNAUTHENTICATED`).
- Run **strictly 1 subagent at a time**. Once a subagent finishes its batch, verify XML validity, and immediately launch the next subagent.

### 2. Golden Chunk Size: 15–25 Pages per Subagent (سقف الحزمة الآمن)
- Assign **15 to 25 pages maximum** per subagent invocation.
- This bounds the subagent's tool calls to ~20–30 steps, guaranteeing completion in under 15 minutes with 100% reliability and zero risk of timeout.

### 3. Modular Sub-Chapter Splitting (تجزئة الفصول الطويلة)
- Long chapters (>30 pages) must be split into logical semantic sub-files (e.g. `ch12a_shudhudh.xhtml`, `ch12b_tafarrud.xhtml`, `ch12c_ikhtilaf.xhtml`, `ch12d_ilaal.xhtml`).
- This enhances e-reader rendering performance on Kindle e-ink displays and prevents bloated monolithic files.

### 4. Boundary Page Stitching & Footnote Isolation (ضبط الصفحات المشتركة)
- When a chapter ends in the middle of a physical page:
  - The top paragraphs and their respective footnotes belong to the **preceding** chapter.
  - The lower paragraphs start the **new** chapter with its main heading.
  - Footnote numbering **must be reset to start from `(١)`** in every chapter file.

### 5. Reflowable Text Flow & Kindle Popup Footnotes Architecture (انسيابية المتن وهندسة الحواشي المنبثقة)
- **Continuous Fluid Reading in EPUB3 (`in_progress.epub`):**
  - Text must flow naturally and continuously within each chapter without artificial pagination, page breaks, or duplicate words at page borders.
  - **Kindle Interactive Popups:** Footnotes are never rendered inline within the reading flow. Instead, each in-text reference is an anchor `<a href="#fnX" id="refX" class="footnote-ref" epub:type="noteref">(X)</a>`, while footnote contents are strictly gathered at the end of the XHTML chapter in `<div class="footnotes-section"><aside id="fnX" class="footnote-item" epub:type="footnote">`. On Kindle devices, tapping the number triggers a clean native popup modal.
- **Auditing Cards in Review Dashboard (`review.html`):**
  - In `review.html`, content is deliberately aligned into per-page comparison cards (matching each physical PDF page image side-by-side) solely for visual proofreading and accuracy auditing.
  - The agent MUST explicitly clarify to the user that the per-page division and bottom-of-card footnotes in `review.html` are strictly for side-by-side human proofreading, while the compiled EPUB book delivers 100% continuous fluid reading with native popup footnotes.

---

## 👁️ Live Review & Interim Feedback Pipeline

To allow the user to review progress and provide feedback while subsequent chapters are being transcribed:

1. **Incremental EPUB Builds (`in_progress.epub`):**
   - After each chapter is verified, automatically update a lightweight interim EPUB file.
   - The user can open and inspect this file in Apple Books, Thorium, Calibre, or Kindle Previewer at any time to verify true reflowable reading and interactive popup footnotes.
2. **Direct Chapter File Inspection:**
   - Link each completed chapter in the chat with its `file:///...` URI so the user can review formatting, styling, or footnotes.
3. **Feedback Adaptability:**
   - If the user provides styling or formatting feedback on an early chapter, immediately apply the preference to the CSS and all subsequent chapters.

---

## 📐 Arabic Typography & Formatting Standards

1. **Quranic Verses (الآيات القرآنية):**
   - Format quoted Ayahs in official Uthmani orthography with full Tashkeel inside `<span class="quran-text">﴿...﴾</span>`.
   - Append the exact Surah name and Ayah number: `<span class="ayah-ref">[سورة البقرة: ٢٥٥]</span>`.
   - **Quranic Verse Separators:** NEVER use the Unicode character `۝` (U+06DD End of Ayah) because it is an OpenType combining enclosing mark that causes severe letter-collision bugs on Amazon Kindle e-ink renderers. Always separate verses with the standard, safe Islamic star ` ۞ ` (Rub El Hizb U+06DE / `<span class="quran-sep">۞</span>`) or ornamental brackets `﴿...﴾ ﴿...﴾` which render flawlessly on all Kindle and Apple devices.

2. **Prophetic Hadiths & Honorifics:**
   - Hadith text in `<p class="hadith-text">«...»</p>`.
   - Honorifics: `ﷺ`, `ﷻ` natively.
   - `رضي الله عنه` / `رحمه الله` tagged with `<span class="honorific">`.

3. **Poetry (أبيات الشعر):**
   - Dissect couplets into balanced Sadr (صدر) and Ajuz (عجز):
     ```html
     <div class="poetry-container">
       <div class="poetry-row" id="v1">
         <span class="poetry-sadr">صدر البيت</span>
         <span class="poetry-ajuz">عجز البيت <span class="poetry-num">(١)</span></span>
       </div>
     </div>
     ```

4. **Shaded Boxes & Callouts (الصناديق المظللة):**
   - Wrap highlighted thoughts or summaries in `<blockquote class="shaded-box">`.

5. **Kindle Interactive Popup Footnotes Architecture (معيار حواشي كيندل التفاعلية المعتمد من «شرح لغة المحدث»):**
   - **In-text Reference:** `<a href="#fn1" id="ref1" class="footnote-ref" epub:type="noteref">(١)</a>`
   - **End-of-Chapter Footnotes Block:**
     ```html
     <div class="footnotes-section" style="margin-top: 3em; border-top: 1px solid #ccc; padding-top: 1em;">
       <aside id="fn1" class="footnote-item" epub:type="footnote">
         <p><a href="#ref1">(١)</a> نص الحاشية بالتفصيل...</p>
       </aside>
       <aside id="fn2" class="footnote-item" epub:type="footnote">
         <p><a href="#ref2">(٢)</a> نص الحاشية بالتفصيل...</p>
       </aside>
     </div>
     ```
   - **Mandatory Footnote Rules:**
     1. **NO Hard Page-Breaks (`page-break-before: always` is STRICTLY FORBIDDEN):** Never set `page-break-before: always;` on `.footnotes-section`. Doing so forces Kindle to generate an artificial blank/isolated page displaying the footnotes as raw text at the end of the chapter. Footnotes should naturally rest at the bottom of the content after a subtle divider line (`border-top: 1px solid #ccc;`), exactly like standard printed footnotes.
     2. **NO Redundant Section Titles:** Do not insert extra arbitrary titles like `<p class="footnotes-title">الهوامش والتعليقات:</p>` before the aside tags, as this clutters the flow.
     3. **Bidirectional Anchors:** Every note reference `#refX` must link forward to `#fnX`, and the footnote inside the aside must wrap its number in `<a href="#refX">` to enable two-way jumping and clean modal dismissal on Kindle.
     4. **Reset Numbering per Chapter:** In every new XHTML chapter file, footnote numbering resets to start from `(١)`.
   - **Approved Footnotes CSS:**
     ```css
     a.footnote-ref, .footnote-ref {
         vertical-align: super;
         font-size: 0.75em;
         color: var(--accent-gold);
         text-decoration: none;
         padding: 0 3px;
         font-weight: bold;
     }

     .footnotes-section {
         margin-top: 3em;
         border-top: 1px solid #ccc;
         padding-top: 1em;
     }

     aside[epub\:type="footnote"], .footnote-item {
         font-size: 0.88em;
         color: #4b5563;
         margin-bottom: 0.6em;
         text-indent: 0;
         line-height: 1.8;
     }

     aside[epub\:type="footnote"] p, .footnote-item p {
         text-indent: 0;
         margin: 0;
         margin-bottom: 0.4em;
     }
     ```

6. **Hierarchical Tree Diagrams (المشجرات والتفريعات الهيكلية الصامدة في كيندل):**
   - In Islamic, grammatical, and educational books (e.g. Tajweed, Fiqh classifications, Hadith chains), topics are frequently structured into visual branching trees.
   - **Table-Based Tree Architecture (Approved Kindle Standard):**
     - Traditional CSS Flexbox and Grid layouts frequently collapse into vertical linear lists on Amazon Kindle e-ink rendering engines.
     - To guarantee true horizontal multi-column branching that never collapses on Kindle or Apple Books, build tree diagrams using structured HTML tables with custom CSS borders:
     ```html
     <div class="tree-table-wrap">
       <div class="tree-root-box">عنوان المشجر الرئيسي أو الباب</div>
       <div class="tree-stem"></div>
       <table class="tree-table" dir="rtl">
         <tr>
           <!-- Connector Bar Cells -->
           <td class="tree-bar-cell tree-bar-right" style="width: 33%;"><div></div></td>
           <td class="tree-bar-cell tree-bar-mid" style="width: 34%;"><div></div></td>
           <td class="tree-bar-cell tree-bar-left" style="width: 33%;"><div></div></td>
         </tr>
         <tr>
           <!-- Branch Node Cells -->
           <td class="tree-node-cell">
             <div class="tree-node-card">
               <div class="node-badge">القسم الأول</div>
               <div class="node-title">عنوان الفرع</div>
             </div>
           </td>
           <td class="tree-node-cell">
             <div class="tree-node-card">
               <div class="node-badge">القسم الثاني</div>
               <div class="node-title">عنوان الفرع</div>
             </div>
             <!-- Sub-branches -->
             <div class="tree-sub-stem"></div>
             <div class="tree-sub-card">١ - فرع تفصيلي</div>
             <div class="tree-sub-card">٢ - فرع تفصيلي</div>
           </td>
           <td class="tree-node-cell">
             <div class="tree-node-card">
               <div class="node-badge">القسم الثالث</div>
               <div class="node-title">عنوان الفرع</div>
             </div>
           </td>
         </tr>
       </table>
     </div>
     ```
7. **Fidelity and Zero Redundancy Protocol (بروتوكول الأمانة الهيكلية ومنع الازدواجية):**
   - **1:1 Structural Fidelity in Book Outlines (مطابقة خطط الأبواب والفصول):**
     - When transcribing an author's preface or introductory syllabus listing the book's parts (الأبواب) and chapters (الفصول), NEVER compress or collapse chapters into inline comma-separated summaries. Every single Part and Chapter must be listed line-by-line with full numbering and title fidelity (1:1 with the original PDF).
   - **Zero Image Redundancy (منع ازدواجية الصور والمكونات البرمجية):**
     - When a visual element (such as a Title Plate, Part Divider, Tree Diagram, or Isnad Chain) is converted into an interactive HTML/CSS component, DO NOT include the original scanned bitmap image alongside it. Retain ONLY the clean, crisp HTML/CSS structure to keep the EPUB lightweight and eliminate jarring duplicate presentations.
   - **Natural Paragraph Styling (أصالة التنسيق ومنع التزيين المبتكر):**
     - Normal body paragraphs (such as opening du'aas, introductory remarks, or rhetorical questions) must remain standard paragraphs (`<p>`) without unprompted callout containers (`class="shaded-box"`), arbitrary borders, or artificial bolding (`<strong>`).
     - Do NOT center-align body-level inline parenthetical notes (e.g. `(من حيث عموم الوحي)`) unless specifically styled as centered standalone headings in the original PDF.

---

## 🔍 Triple-Check Verification Protocol (بروتوكول التدقيق ثلاثي المستويات)

Before final packaging, execute an automated verification script to validate:

1. **Sequential Element Check:**
   - Verify that all numbered poem verses (e.g. 1 to 165) or hadith entries are present in unbroken sequence.
2. **Boundary Stitching Check:**
   - Verify that the last paragraph of file `N` seamlessly connects with the opening of file `N+1`.
3. **Bi-directional Footnote & XML Audit:**
   - Verify that every `<a href="#fnX">` has a corresponding `<aside id="fnX">` and vice versa.
   - Ensure 100% valid XML across all XHTML files using `xml.etree.ElementTree`.

---

## 📦 EPUB3 Packaging Specifications

- **Spine Progression Standard:** Use standard `<spine toc="ncx">` (avoid `page-progression-direction="rtl"` on spine as it triggers reverse horizontal column offset bugs in Kindle/Apple Books/Kobo, causing chapters to open from their last page). Text direction is strictly governed by `dir="rtl"` in `<html>` and CSS `body { direction: rtl; text-align: justify; }`.
- **Embedded Typography:** Pack `Amiri-Regular.ttf` and `Amiri-Bold.ttf` in `fonts/`.
- **Dual Navigation:** Generate `nav.xhtml` (EPUB3) and `toc.ncx` (Kindle legacy).
- **Mimetype:** Uncompressed `application/epub+zip` as the first entry in the ZIP archive.

---

## ⏱️ Progress Tracking & ETA Metrics Reporting (تتبع الإنجاز وتقدير الوقت)

When executing multi-batch conversions via sequential subagents, the agent MUST include a standardized execution metrics card in each interim response to the user:

1. **الوقت المستغرق في الحزمة الأخيرة (Last Batch Duration):** Exact minutes and seconds taken by the subagent.
2. **عدد الحزم المكتملة (Completed Batches):** e.g., 12 / 22 batches (X pages completed).
3. **عدد الحزم المتبقية (Remaining Batches):** e.g., 10 batches (Y pages remaining).
4. **متوسط سرعة المعالجة (Average Speed per Batch):** Calculated from previous completed batches.
5. **الوقت المتوقع المتبقي للانتهاء (Estimated Time of Arrival - ETA):** Projected completion time based on average batch pace.
