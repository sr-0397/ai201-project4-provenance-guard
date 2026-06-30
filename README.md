# ai201-project4-provenance-guard


AI Content Transparency Detector: An API that analyzes submitted text and estimates whether it was likely written by AI or a human. The system combines multiple detection signals into a single confidence score and returns one of three transparency labels:

-Likely AI-generated

-Uncertain

-Likely Human-written

The project also includes rate limiting, audit logging, and an appeals workflow to support transparency and manual review.

Features

-Two independent AI detection signals

-Weighted confidence scoring

-Three transparency label variants

-Rate limiting

-Audit logging

-Appeals workflow

-REST API built with Flask



Architecture

Submission Flow

POST /submit
        │
        ▼
 Rate Limiter
        │
        ▼
 ┌─────────────────────────────┐
 │ Signal 1 (Groq LLM)         │
 │ Signal 2 (Stylometrics)     │
 └─────────────────────────────┘
        │
        ▼
 Confidence Score
        │
        ▼
 Transparency Label
        │
        ▼
 Audit Log
        │
        ▼
 JSON Response
Appeal Flow

POST /appeal
        │
        ▼
 Status → under_review
        │
        ▼
 Audit Log
        │
        ▼
 GET /log
Submission Flow

When a user submits text through POST /submit, the request first passes through the rate limiter. The text is then analyzed by both detection signals. Their outputs are combined into a confidence score, which determines the transparency label returned to the user. The submission and its results are recorded in the audit log.



# Appeal Flow

Creators can challenge a classification using POST /appeal. The submission status changes to under_review, the appeal is stored in the audit log, and reviewers can inspect all pending appeals through GET /log.


# Detection Signals

Signal 1 — LLM Classification

Uses Groq's llama-3.3-70b-versatile model to evaluate whether the writing resembles AI-generated content.

Output

Float between 0.0–1.0

0.0 = likely human

1.0 = likely AI

Why this signal?

The LLM can recognize semantic and stylistic patterns that handcrafted rules often miss.

Weakness

- Highly polished human writing (technical reports, academic papers, legal documents) may receive higher AI scores.



Signal 2 — Stylometric Analysis

Implemented entirely in Python.

Measures:

-Sentence-length variance

-Type-token ratio (vocabulary diversity)

-Punctuation density


Each metric is normalized to a value between 0 and 1, then averaged into a stylometric score.

Why these signals?

These features are inexpensive to compute and capture measurable differences often found between AI and human writing. They also provide an independent check on the LLM's prediction.


Weakness

Formal writing by non-native English speakers may produce lower vocabulary diversity and more uniform sentence structure, leading to false positives.



Confidence Scoring

The final confidence score is calculated using:

confidence = (0.6 * llm_score) + (0.4 * stylometric_score)
The LLM receives a larger weight because it captures higher-level semantic information. The stylometric detector acts as a second opinion and helps reduce overreliance on a single model.

If this project were deployed in production, I would calibrate these weights using a labeled evaluation dataset instead of manually selecting them.

Confidence Levels

Score	Result
0.00 – 0.39	High-confidence Human
0.40 – 0.64	Uncertain
0.65 – 1.00	High-confidence AI
A score of 0.60 means the system detects some AI-like characteristics, but neither detector provides enough evidence for a confident conclusion. Instead of making a strong claim, the system reports the result as uncertain.


## Example Confidence Scores

### Example 1 — High-confidence AI

| Signal | Score |
|---|---|
| LLM | 0.88 |
| Stylometric | 0.79 |
| **Final confidence** | **0.844** |

Result: **Likely AI-generated**

Input: *"Effective time management is a critical skill in today's fast-paced professional environment. It is essential to prioritize tasks based on urgency and importance. Additionally, leveraging digital tools can significantly enhance productivity and streamline daily workflows."*

### Example 2 — Lower-confidence (uncertain)

| Signal | Score |
|---|---|
| LLM | 0.51 |
| Stylometric | 0.46 |
| **Final confidence** | **0.49** |

Result: **Uncertain**

Input: *"My grandmother used to say that patience is a skill you build, not one you're born with. I think about that a lot when I'm stuck in traffic or waiting on a slow internet connection. It's a small thing but it's stuck with me."*

These two examples show meaningfully different scores rather than a constant — the gap between 0.844 and 0.49 reflects a real difference in how strongly each piece of text matched AI-like patterns on both signals, not noise. The second example also demonstrates the intended behavior of the "uncertain" band: text with a personal anecdote but a slightly polished, generalized closing thought produces a score the system is honest about being unsure of, rather than forcing a binary call.


# Appeals Workflow

Anyone with a valid content_id may submit an appeal.

Required fields:

content_id

creator_reasoning

When an appeal is received:

The submission is located.

Status changes from classified to under_review.

The appeal is written to the audit log with:

timestamp

confidence score

creator reasoning

A reviewer viewing the appeal queue can see both the original classification and the appeal details before making a decision.

Known Limitations

This system is intentionally conservative and still has limitations.

Non-native English writing

Formal writing from non-native English speakers often has lower vocabulary diversity and more consistent sentence lengths. These characteristics overlap with AI-generated text, increasing the chance of false positives.

Short submissions

Texts under about 50 words do not contain enough information for reliable stylometric analysis. Scores become much less stable.

Lightly edited AI writing

If AI-generated text is substantially rewritten by a human, both detection signals become weaker. These submissions often fall into the uncertain category.

Legal and technical documents

Contracts and technical documentation naturally use repetitive language and rigid formatting, which can resemble AI-generated writing.

Spec Reflection

How the specification helped

The project specification emphasized transparency over simple AI detection. It encouraged building confidence scoring, audit logging, and an appeals process rather than returning a binary AI/human decision.

Where my implementation differed

The specification did not prescribe a confidence scoring method. Instead of training a calibrated statistical model, I implemented a weighted average (60% LLM, 40% stylometric) because it was practical for the scope of this project while still producing meaningful confidence variation.

AI Usage

Instance 1

I used Cluade to generate the initial Flask API structure, including endpoint routing.

After reviewing the generated code, I reorganized functions, improved validation, and added my own error handling.

Instance 2

I used Claude to help implement the stylometric detection functions and confidence scoring formula.

I later modified the weights, adjusted the thresholds, and rewrote portions of the code to better match the project requirements and reduce false positives. They got the weights wrong so I adjusted.






VIDEO SCRIPT:
https://www.loom.com/share/dd38b28e326e479985a378b8a7b8e0e5?live_rewind=1

"Hi, I'm Shriya, and this is Provenance Guard — a backend API that detects whether submitted text was written by a human or generated by AI, and returns a transparency label that a creative platform could show to readers.

Let me start by submitting a piece of clearly AI-generated text.
(run the curl command for the AI sample)

-run curl command

You can see the response comes back with a content ID, a confidence score of around 0.84, an attribution of likely_ai, and the label text that would actually be shown to a reader: 'This content was likely generated with AI assistance. Our analysis detected patterns consistent with AI-generated text. If this is your original work, you can file an appeal below.'

Now let me submit something clearly human-written — a casual, personal piece.
(run the curl command for the human sample)

-run curl command

Completely different score — down around 0.21 — and the label switches to 'This content appears to be human-written. No AI-generation indicators were detected.' That score difference is the system working correctly.

Let me also show the uncertain case — something that sits in the middle.
(run the curl command for the borderline sample)
Score around 0.49, attribution is uncertain, and the label reflects that honestly: 'Our system was unable to determine with confidence whether this content is human- or AI-written.' 

-run curl command

I designed the system to have that middle band intentionally — forcing a binary call on ambiguous text would produce false positives, and a false positive on a human writer's work is the worst outcome on a creative platform.


- show llm file and sstylometric files
Now let me show how the scoring works. There are two independent signals. The first is an LLM call to Groq — it reads the text semantically and returns a score between 0 and 1 based on whether the writing patterns match AI-generated content. The second is a stylometric analyzer I wrote in pure Python — it measures sentence length variance, average word length, and punctuation density. AI text tends to be more uniform, use longer formal words, and have very little expressive punctuation. The two signals are then combined — 60% LLM, 40% stylometric — because the LLM captures meaning and the stylometrics capture structure, and together they're more reliable than either alone.

- show audit logs
Let me pull up the audit log.
(run GET /log)

Every submission is logged with a timestamp, content ID, both individual signal scores, the combined confidence, and the current status. You can see the three submissions I just made are all here.

-appeal
Finally, let me file an appeal on that last submission.
(run the appeal curl with the content ID from the uncertain submission)
The system confirms the appeal was received. If I check the log again — (run GET /log) — that entry now shows status under_review and the creator's reasoning is stored alongside the original classification. A human reviewer could open this queue and see everything they need to evaluate the appeal.
The key design decision throughout was honesty over confidence — the system acknowledges uncertainty, gives creators a path to appeal, and biases against false positives rather than maximizing detection rate. That felt like the right tradeoff for a platform where attribution really matters to creators."






# 2 — Human sample
curl -s -X POST http://127.0.0.1:8000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "My grandmother used to say that patience is a skill you build, not one youre born with. I think about that a lot when Im stuck in traffic or waiting on a slow internet connection. Its a small thing but its stuck with me.", "creator_id": "demo-human"}' | python3 -m json.tool

# 3 — Borderline sample
curl -s -X POST http://127.0.0.1:8000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Ive been thinking a lot about remote work lately. There are genuine tradeoffs - flexibility and no commute on one side, isolation and blurred work-life boundaries on the other. Studies show productivity varies widely by individual and role type.", "creator_id": "demo-border"}' | python3 -m json.tool

# 4 — Audit log
curl -s http://127.0.0.1:8000/log | python3 -m json.tool

# 5 — Appeal (paste content_id from demo-border response)
curl -s -X POST http://127.0.0.1:8000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "PASTE-ID-HERE", "creator_reasoning": "I wrote this from my own experience. My writing style tends to be slightly formal but this is entirely my own work."}' | python3 -m json.tool

# 6 — Log again to show under_review
curl -s http://127.0.0.1:8000/log | python3 -m json.tool