# GBSBFORYOU Shared Knowledge Base — Data Standard

**Owner:** GBSBFORYOU  
**Purpose:** Make research, education and publishing material discoverable across related GitHub repositories without copying or losing source provenance.

## 1. Core record fields

Each knowledge item should use the following fields:

| Field | Meaning |
|---|---|
| `record_id` | Stable unique ID, e.g. `BANJARA-0001` |
| `title` | Document or knowledge item title |
| `project_id` | Main project identifier |
| `topic_tags` | Searchable subject tags |
| `record_type` | Primary source, secondary source, manuscript, lesson, code, media, policy, dataset |
| `source_repository` | Original GitHub repository |
| `source_path` | Exact file path or external source link |
| `author_or_issuer` | Author, institution or issuing authority |
| `created_or_published_date` | Date on source, if known |
| `accessed_date` | Date source was checked |
| `language` | Hindi, English, Sanskrit, Banjara, etc. |
| `status` | Inbox, reviewed, approved, published, archived |
| `evidence_level` | Primary, secondary, interpretation, proposal, unverified |
| `summary` | Short factual summary |
| `rights_and_license` | Copyright/license or permission status |
| `sensitivity` | Public, internal, restricted |
| `last_verified` | Last content verification date |

## 2. Project-specific metadata

### Education
- Board/curriculum, class, subject, chapter, learning objective, prerequisite, difficulty, question type, answer key, review status.

### Publishing
- Book ID, author, edition, language, ISBN (if assigned), manuscript version, editorial status, cover asset, format, distribution status.

### Banjara research
- Community/topic, historical period, jurisdiction, source authority, legal status, citation/page, evidence level, review notes. Distinguish enacted law from draft/proposal and advocacy.

## 3. Folder convention

Recommended structure for future content (do not move existing files automatically):

```text
knowledge-base/
  README.md
  projects/
    education/
      index.json
    publishing/
      catalogue.json
    banjara-research/
      evidence-register.csv
  schemas/
    knowledge-record.schema.json
  templates/
    source-record-template.md
```

## 4. Safe integration rules
1. Preserve each original file in its source repository.
2. Store a canonical source link and metadata in the shared index; avoid uncontrolled duplicate copies.
3. Never store API keys, passwords, personal identity numbers or confidential records in the public knowledge base.
4. Respect copyright and licenses; a public GitHub file is not automatically public domain.
5. Record the exact page/section for factual claims whenever available.
6. Require human review before marking legal, historical or educational content as approved.
7. Keep public and restricted material in separate repositories/access scopes.

## 5. Status workflow

`INBOX → METADATA_CHECKED → CONTENT_REVIEWED → APPROVED → PUBLISHED`

Any item may be marked `NEEDS_CORRECTION` or `ARCHIVED`. Approval must record reviewer and date.

## 6. Current implementation status

This file defines the common metadata standard only. It does not yet create a database, ingest files, synchronize repositories or expose an AI search API. Those require a separate implementation and security review.
