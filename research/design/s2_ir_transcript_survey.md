# S2: do company IR sites post earnings-call text? (feasibility survey, 2026-11-22)

Status: survey for the owner. Nothing was downloaded or collected. The question was whether
large US companies' own investor-relations (IR) sites post past earnings-call text (full
transcripts, prepared remarks, CFO commentary, shareholder letters) that could replace a paid
transcript API for sub-study S2.

## Method

24 S&P 500 members, picked by hand: 8 mega-caps, 8 large, 8 smaller members, across 20 sectors.
For each, web search plus reading the IR pages with a generic fetcher (no login, no forms, no
cookie choices, no bot-check bypass). At most one transcript PDF opened per company to check its
format. Three 8-K filing indexes read on sec.gov. Claim types: each cell is a verified fact unless
marked **(unv.)** (not verified: inferred from search snippets, filenames or one source) or
**blocked** (the site refused the fetcher, HTTP 403).

"Earliest seen" is the oldest quarter I saw with such text. It is a lower bound on archive depth,
not the true start. "Jul/Aug 2026" means the call for the quarter ended around June 2026; for
off-calendar fiscal years the nearest post-June call is named.

## Results

| Company | Sector | Size | Text on IR besides release and slides | Earliest seen | Jul/Aug 2026 text? | Q&A included? | Producer | Terms note | Page type |
|---|---|---|---|---|---|---|---|---|---|
| Microsoft (MSFT) | Software | Mega | Full transcript (HTML on event page, also .docx); prepared remarks mentioned | FY10 Q1 (Oct 2009) | Yes, FY26 Q4 call 2026-07-29 | Yes (verified on page) | Not stated | Site terms: documents for "informational and non-commercial or personal use only" | Static HTML |
| NVIDIA (NVDA) | Semiconductors | Mega | CFO commentary (PDF) | Q4 FY12 (Feb 2012, via 8-K) | Yes, Q2 FY27 commentary 2026-08-26 | No (prepared text only) | Company | None seen | JS list (Q4 Inc); PDFs on q4cdn |
| Apple (AAPL) | Hardware | Mega | None found (release, data summary, 10-Q, webcast) | n/a | n/a | n/a | n/a | n/a | JS list (Q4 Inc) |
| JPMorgan Chase (JPM) | Bank | Mega | Full transcript (PDF) | 1Q22 (unv.; older likely) | Yes, 2Q26 PDF exists at the IR document path | Likely (unv.; text layer not readable by a simple decoder) | Not stated; other JPM IR transcripts use CallStreet section headings (unv.) | None seen | JS list (feed-driven) |
| Eli Lilly (LLY) | Pharma | Mega | None found; slides only | n/a | Slides only | n/a | n/a | n/a | blocked |
| Walmart (WMT) | Retail | Mega | Management-call transcript and buy-side follow-up call transcript (PDF); "Management Commentary" PDF in some 2018-2020 quarters | FY2012 Q1 (May 2011) | Yes, FY27 Q2 (2026-08-20) | Likely (unv.) | Not stated | None seen | Static list |
| ExxonMobil (XOM) | Energy | Mega | Transcript and separate prepared remarks (PDF) | 4Q22 (oldest event in the IR calendar) | Yes, 2Q26 call 2026-07-31 | Likely (unv.) | Not stated | None seen on event page | Static event pages |
| Procter & Gamble (PG) | Consumer staples | Mega | None found (unv.) | n/a | n/a | n/a | n/a | n/a | JS list (Q4 Inc) |
| Medtronic (MDT) | Medical devices | Large | Prepared remarks ("earnings commentary", PDF); no transcript | FY23 Q3 (Feb 2023) | Yes, FY27 Q1 call 2026-09-01 (quarter ended Jul 2026) | No | Company | None seen | Static list |
| Caterpillar (CAT) | Industrial | Large | Full transcript (PDF) | Q4 2021 (Jan 2022) | Yes, 2Q26 (2026-08-04) | Likely (unv.; 22-28 page files) | ViaVid for the Q4 2021 file (unv.); current not stated | ViaVid file notes possible transcription errors (unv.) | JS list (Q4 Inc); PDFs on q4cdn |
| Union Pacific (UNP) | Rail transport | Large | None found (unv.) | n/a | n/a | n/a | n/a | n/a | blocked |
| NextEra Energy (NEE) | Utility | Large | Prepared remarks ("Remarks" script, PDF); no transcript | 2017 Q1 (archive link goes further back) | Yes, Q2 2026 (2026-07-24) | No | Company | None seen | Static HTML |
| Prologis (PLD) | REIT (industrial) | Large | None; release lists webcast, supplemental, fact sheet, 10-Q | n/a | n/a | n/a | n/a | n/a | Static release page |
| Chubb (CB) | Insurance (P&C) | Large | Full "corrected transcript" (PDF) | Not verified | Yes, 2Q26 call 2026-07-22 | Yes (verified in PDF) | FactSet CallStreet (verified) | Every page: "Copyright © 2001-2026 FactSet CallStreet, LLC" | PDFs on q4cdn; list page not checked |
| Netflix (NFLX) | Media | Large | Shareholder letter (PDF) and earnings-interview transcript (PDF) | Transcript Q4 2021 (Jan 2022); letters much older | Yes, Q2 2026 transcript and letter (2026-07-16) | Yes (interview format, analyst asks the questions) (unv.) | S&P Global Market Intelligence (unv., from snippets) | Vendor copyright (unv.) | PDFs on q4cdn; list page not checked |
| Target (TGT) | Retail | Large | Full transcript (PDF) | Q1 2016 (May 2016) | Yes, Q2 2026 (2026-08-19) | Likely (unv.) | Refinitiv / LSEG StreetEvents (PDF metadata) | LSEG transcripts carry a redistribution ban (see below) | Static HTML |
| Hormel Foods (HRL) | Consumer staples | Smaller | Full "corrected transcript" (PDF) | Q3 FY21 (Sep 2021) | Yes, Q3 FY26 call 2026-08-27 | Likely (17 pages) (unv.) | FactSet CallStreet (unv., from snippets) | Vendor copyright (unv.) | PDFs on q4cdn; list page not checked |
| Evergy (EVRG) | Utility | Smaller | Full transcript (PDF) | Q1 2023 | Yes, Q2 2026 call 2026-08-06 | Likely (unv.) | LSEG StreetEvents (unv., from snippets) | LSEG redistribution ban (unv.) | blocked (Notified platform) |
| Globe Life (GL) | Insurance (life) | Smaller | Full transcript (PDF), one page listing every year | 2006 (all four quarters) | Yes, Q2 2026 | Likely (unv.) | Not stated | Page says only "Copyright © Globe Life. All rights reserved." | Static HTML |
| Federal Realty (FRT) | REIT (retail) | Smaller | Full "corrected transcript" (PDF) | Q2 2025 (unv.) | Not confirmed (Q4 2025 and Q1 2026 found) | Likely (unv.) | FactSet (unv., from snippets) | Vendor copyright (unv.) | blocked (Notified platform) |
| J.B. Hunt (JBHT) | Trucking transport | Smaller | None; latest quarter lists release and webcast only | n/a | n/a | n/a | n/a | n/a | Static home page |
| APA Corp (APA) | Energy | Smaller | None found (unv.) | n/a | n/a | n/a | n/a | n/a | Notified platform, not fetched |
| Akamai (AKAM) | Software | Smaller | None found (unv.) | n/a | n/a | n/a | n/a | n/a | blocked |
| Teleflex (TFX) | Medical devices | Smaller | None found (unv.) | n/a | n/a | n/a | n/a | n/a | JS list (Q4 Inc) |

## 8-K exhibits checked on sec.gov

| Company | Filing | Exhibits | Call text furnished? |
|---|---|---|---|
| NVIDIA | 8-K, 2026-08-26 (0001045810-26-000073) | EX-99.1 press release, EX-99.2 CFO commentary | Yes, CFO commentary as EX-99.2; the same exhibit exists for Q4 FY12 (2012) |
| Netflix | 8-K, 2026-07-16 (0001065280-26-000211) | EX-99.1 shareholder letter (about 15 pages, about 9 of narrative) | Yes, shareholder letter as EX-99.1; also seen for 2019 quarters |
| Medtronic | 8-K, 2026-09-01 (0001628280-26-059697) | EX-99.1 press release only | No, prepared remarks are on the IR site only |

## Summary

**Shares (24 companies).**

| Text on the IR site | All | Mega | Large | Smaller |
|---|---|---|---|---|
| Full transcript with Q&A | 12 (50%) | 4 | 4 | 4 |
| Prepared remarks or CFO commentary only | 3 (13%) | 1 (NVDA) | 2 (MDT, NEE) | 0 |
| Nothing found beyond release, slides, webcast | 9 (38%) | 3 | 2 | 4 |

Of the 9 with nothing found, 3 are verified from the page itself (AAPL, PLD, JBHT); the other 6
rest on search results because the site was blocked or rendered by JavaScript. ExxonMobil posts
both a transcript and prepared remarks; Netflix both a transcript and a shareholder letter. Q&A was
verified directly for Microsoft and Chubb only; for the other full transcripts it is likely from
the file type, page count or vendor format, not checked.

**Post-June-2026 text exists.** Of the 15 companies that post call text, 14 have it for the call
held in July to September 2026 (13 in July/August; Medtronic's is 2026-09-01 because its fiscal
quarter ended in July). Federal Realty's Q2 2026 file was not found. Many also have the
October/November 2026 call. So the clean post-cutoff window is covered wherever the company posts
text at all.

**8-K exhibits are a parallel free source, but only for company-written text.** NVIDIA's CFO
commentary and Netflix's shareholder letter are furnished as 8-K exhibits, so they carry an EDGAR
acceptance timestamp and fit the project's one-clock rule (AGENTS.md rule 1) directly. Vendor
transcripts and Medtronic's prepared remarks were not furnished. IR-posted transcripts have no
EDGAR timestamp; using them would need a separate dating rule (for example, the call date or the
date the file first appears), which the project does not have yet.

**What a scripted collection would need.**
- Per-site adapters. There is no common layout, filename scheme or metadata. At least 6 of the
  24 sites (5 on the Q4 Inc platform, plus JPMorgan) build the quarterly list with JavaScript, so
  a script needs a headless browser or the platform's data feed. I did not test the feed: a query
  to it was refused by this session's permission layer, and I did not retry.
- Five sites answered the fetcher with HTTP 403: four on the Notified platform (LLY, EVRG, FRT,
  AKAM) and Union Pacific. A collector would have to stop there, not work around it.
- PDF handling. Most files are PDFs (Microsoft also uses .docx). The JPMorgan and Target PDFs
  have font-encoded text that a simple stream decoder cannot read, so a proper PDF text extractor
  (and possibly OCR) is needed.
- Coverage is uneven: half the sample has full transcripts, and depth varies from 2006 (Globe
  Life) to 2023 (Evergy, Medtronic) in what I saw. A free collection would give a self-selected
  subset of companies, which matters for S2's sampling.

**Legal and terms caveats** (judgement, not legal advice).
- Posting on an IR site does not grant reuse rights. Vendor transcripts carry the vendor's
  copyright: FactSet CallStreet on every page of Chubb's file; LSEG's transcripts state that
  redistribution is "prohibited without the prior written consent of LSEG" (seen on LSEG's own
  transcript PDFs; assumed, not checked, for Target and Evergy).
- Microsoft's site terms allow its documents for informational, non-commercial or personal use
  and forbid posting copies on network computers.
- Other sites' terms of use were not read.
- For this repo: any such text stays outside git under rule 12, as licensed transcripts already
  do, and the owner should decide whether internal research use of vendor-copyright files is
  acceptable before any bulk collection.

The pattern was clear by 24 companies, so I stopped there.
