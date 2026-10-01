# FS-TEXT — The Gita as a text: structure, counts, verse numbering

Everything here is verified against the pinned IAST source unless noted. Writers MUST annotate
numeric claims from this sheet with `<!-- prov: FS-TEXT -->` (or a more specific FS-ID where given).

## Position inside the Mahabharata
- The Bhagavad Gita is embedded in the **Bhishma Parvan** (book 6 of 18) of the Mahabharata.
  Source: IGNCA introduction PDF (ignca.gov.in/sanskrit/bhagavad_gita_introduction.pdf); bhagwadgita.info structure page.
- Critical-edition reference: Mahabharata **6.3.23 – 6.3.40** (18 adhyāyas).
  Source: bhagwadgita.info; Ignca intro concurs (chapters 23–40 of Bhishma Parvan).

## Size and count
- Standard received count: **18 chapters, 700 verses**. Widely cited (bhagwadgita.info; IGNCA).
- The pinned Sanskrit source (sanskritdocuments.org IAST edition) parses to **701 verse units**;
  the extra unit comes from counting differences (chapter 13 is 34 verses in the received
  numbering but the source splits one verse differently; several editions count 13 as 35).
  Source: our own parse of gita_iast2.html (tools/extract.py run, 2026-10).
- Known variant totals in the tradition: the **Kumbakonam edition has 745 verses**.
  Source: Swami Chinmayananda's commentary intro, as reported in multiple secondary sources
  (bhagwadgita.info notes variant counts; not independently verified against Kumbakonam print).

## Speakers (who says what)
Counts per Rhys S. Minor / standard tallies:
- **Krishna: 574 verses**
- **Arjuna: 84 verses**
- **Sanjaya (the reporter): 41 verses**
- **Dhritarashtra (the blind king): 1 verse** (1.1)
Source: standard commentator tallies reported by bhagwadgita.info ("who spoke how many verses" table)
and repeated in IGNCA intro. Verify before quoting decimals; round numbers only.

## Chapter colophons (the text's own self-description)
Each chapter ends with a formulaic colophon preserved in the Sanskrit source, e.g. after chapter 1:
"oṃ tatsaditi śrīmadbhagavadgītāsūpaniṣatsu brahmavidyāyāṃ yogaśāstre śrīkṛṣṇārjunasaṃvāde
arthaviśādhiyogo nāma prathamo'dhyāyaḥ" — "Thus in the Śrīmad Bhagavad Gītā, the Upaniṣad, in the
science of brahman, in the scripture of yoga, in the dialogue of Śrī Kṛṣṇa and Arjuna, [chapter title],
the first chapter."
- Three recurring self-descriptors: **sūpaniṣat** (fully Upaniṣadic), **brahmavidyā** (science of
  brahman), **yogaśāstra** (scripture of yoga), framed as **saṃvāda** (dialogue).
Source: pinned IAST text (sanskritdocuments.org), verified in our extraction; colophons at every
chapter boundary.

## The 3×6 division
- **Madhusudana Sarasvati** (Gudhārtha-dīpikā, latter half of 16th c., Benares) divides the Gita
  into three hexads of six chapters: **karma** (ch. 1–6), **bhakti** (ch. 7–12), **jñāna** (ch. 13–18),
  with each hexad internally treating all three.
  Source: advaita-vedanta.org archives post quoting the Sanskrit intro of Gudhārtha-dīpikā
  ("ekamevena ṣoḍaśena..." scheme: "sāṅkhyakarmaprabhūtibhedena ṣaṭ ṣaṭ ṣaṭ kramāt").
- The same three-hexad division appears earlier in **Yāmunācārya's Gītārtha-saṅgraha**
  (916–1041 CE) — evidence the scheme predates Madhusudana by centuries.
  Source: IGNCA introduction PDF; standard Viśiṣṭādvaita scholarship.

## Pinned verse text
- All Sanskrit (IAST) quotes in this book are taken verbatim from:
  **sanskritdocuments.org, "Bhagavad Gita in IAST" (bhagvadnew_IAST.html)**, downloaded
  2026-10 to /tmp/opencode/gita/gita_iast2.html, cross-checked word-for-word against
  **kevincarmody.com's IAST Gita** (gita_iast.html). The two sources agreed on all 144
  selected verses. IAST text is sandhi-agglutinated as received; we do not split sandhi.
- English glosses in tools/verses.json are this book's own literal renderings, prepared against
  the public-domain Sir Edwin Arnold translation (1885) as a cross-check. They are deliberately
  plain and literal, not literary.
