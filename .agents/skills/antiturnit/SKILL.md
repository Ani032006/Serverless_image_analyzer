---
name: antiturnit
description: Analyze, score, and rewrite academic papers, engineering reports, thesis chapters, and essays to bypass Turnitin and other neural AI detectors (GPTZero, CopyLeaks, Turnitin AI Writing Detector). Operates on linguistic perplexity, sentence burstiness, vocabulary de-cliching, asymmetric paragraph architectures, and realistic academic friction. Trigger on "antiturnit", "anti-turnitin", "anti turnitin", "bypass turnitin", "turnitin ai check", "pass turnitin", "check turnitin", or when optimizing academic submissions against AI detectors.
---

# AntiTurnit: Academic AI Detector Evasion & Humanizer Skill

Based on the linguistic architecture of academic anti-detection systems (such as `antiturnitin`) and structural AI fingerprint analysis, this skill guides the auditing, scoring, and transformation of academic and technical prose to evade Turnitin and neural AI writing detectors while preserving formal academic rigor.

---

## 1. Core Detection Mechanisms Targeted

Neural AI detectors evaluate text on four mathematical and structural signatures:

1. **Perplexity (Token Predictability)**
   * **AI Pattern**: Chooses high-probability next tokens, producing uniform, predictable, and generic phrasing.
   * **Human Target**: Uses discipline-specific, domain-precise vocabulary, occasional unconventional phrasing, and varied technical terms.
2. **Burstiness (Sentence Length & Complexity Variance)**
   * **AI Pattern**: Rigid, Gaussian distribution of sentence lengths (typically 16–22 words per sentence), following declarative subject-verb-object structures.
   * **Human Target**: High variance. Short punchy sentences (6–10 words) juxtaposed against compound-complex sentences with subordinate clauses (25–38 words).
3. **Transition & Discourse Marker Clichés**
   * **AI Pattern**: Heavy reliance on formulaic discourse markers: *"Moreover"*, *"Furthermore"*, *"Notably"*, *"Consequently"*, *"In addition"*, *"It is important to note that"*, *"This underscores/highlights"*.
   * **Human Target**: Implicit logical progression, contextual transitions, or varied fronted adverbial phrases.
4. **Paragraph Symmetry & Formulaic Rhetoric**
   * **AI Pattern**: Uniform paragraph sizes (4–5 sentences each), predictably structured as: *Topic sentence → Evidence citation → Explanation → Concluding summary sentence*.
   * **Human Target**: Natural asymmetry. 2–3 sentence transitional/interpretative paragraphs paired with 7–9 sentence deep methodological derivations.

---

## 2. Operating Modes

When invoked via `/antiturnit` or prompt:

### Mode A: Turnitin Risk Audit
Analyze an existing report, paper, or passage against Turnitin AI markers.
1. **Burstiness Score (1–10)**: Sentence length standard deviation and rhythm distribution.
2. **Perplexity & Predictability**: Identify robotic collocations, overused academic buzzwords, and lack of domain specificity.
3. **Transition Marker Density**: Flag banned AI crutches (*"Moreover"*, *"Furthermore"*, *"In conclusion"*, *"serves as a testament"*).
4. **Paragraph Geometry**: Flag monotonous 4-sentence structures and repeated sentence openings.
5. **Output**: Detailed audit table with specific line/section references and a prioritized revision checklist.

### Mode B: Academic Rewrite & Humanization
Directly rewrite content according to the following strict rules:

#### Rule 1: Dynamic Sentence Architecture (Burstiness)
* Vary sentence lengths systematically:
  * **Short Declarative (6–12 words)**: State key empirical findings, constraints, or definitions cleanly.
  * **Medium Narrative (14–20 words)**: Connect ideas or explain mechanics.
  * **Complex Compound (24–36 words)**: Use subordinate conjunctions (*"While..."*, *"Although..."*, *"Given that..."*) to express technical relationships and contingencies.
* **Vary Sentence Openings**: Never start three consecutive sentences with the subject or demonstrative pronouns (*"The system..."*, *"This demonstrates..."*, *"These findings..."*). Front with prepositional phrases, participle clauses, or temporal qualifiers (*"Across all ten stress iterations,..."*, *"Under sustained network latency,..."*).

#### Rule 2: Vocabulary Sanitization & Domain Specificity
* **Banned Words & Phrases**:
  * Filter out: *Moreover, Furthermore, In summary, It is crucial to note that, It is worth mentioning, Underscores, Serves to highlight, Delve, Paramount, Tapestry, Beacon, Seamlessly, Catalyst*.
* **Replacement Strategy**:
  * Instead of *"underscores the importance of"*, use *"points to"*, *"lends support to"*, or directly state the finding.
  * Use concrete named entities and numbers: name exact protocols, version numbers, parameter values, and error codes rather than abstract descriptors (*"high latency"* → *"a 420ms p99 round-trip delay"*).

#### Rule 3: Realistic Technical Friction & Trade-offs
* AI writing defaults to idealized, frictionless systems where everything succeeds cleanly.
* Inject authentic research friction:
  * Mention parameter tuning challenges (e.g., threshold sensitivity, boundary conditions).
  * Document edge-case failures, fallback mechanisms, or architectural compromises.
  * Include trade-offs (e.g., higher memory overhead for lower read latency).

#### Rule 4: Discipline-Appropriate Hedging
* Avoid hyper-certain robotic claims (*"This proves beyond doubt that..."*) and repetitive cowardly hedges (*"It could possibly be argued that perhaps..."*).
* Use natural academic qualifications: *"appears consistent with"*, *"suggests a modest correlation"*, *"indicates an upper bound under standard conditions"*.

---

## 3. Quick Reference Banned AI Checklist

Before submitting to Turnitin, verify that the text does NOT contain:
- [ ] Consecutive paragraphs opening with identical transition adverbs (*"Furthermore,"* / *"Moreover,"*).
- [ ] Uniform sentence lengths (all sentences between 15 and 22 words).
- [ ] Moralizing or summary conclusions that simply re-list points made in the abstract.
- [ ] Generic adjectives (*"state-of-the-art"*, *"game-changing"*, *"seamless"*, *"groundbreaking"*).
- [ ] Lack of named technical failure modes or constraints.
