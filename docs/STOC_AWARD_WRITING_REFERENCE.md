# STOC award-paper writing reference

This file is an internal writing/design reference, not a citation source for scientific claims. It records verified award papers and transferable presentation choices to emulate without copying text.

## Verified award-paper anchors

Official SIGACT STOC Best Paper Award list: https://sigact.sigact.hosting.acm.org/prizes/best_paper.html

Primary papers inspected:

1. **Breaking the Sorting Barrier for Directed Single-Source Shortest Paths** — Ran Duan, Jiayi Mao, Xiao Mao, Xinkai Shu, Longhui Yin, STOC 2025 Best Paper. Published version DOI: `10.1145/3717823.3718179`; public copy: https://pure.mpg.de/pubman/item/item_3634229_7/component/file_3662698/3717823.3718179.pdf
2. **Quasi-Linear Size PCPs with Small Soundness from HDX** — Mitali Bafna, Dor Minzer, Nikhil Vyas, Zhiwei Yun, STOC 2025 Best Paper. Published version DOI: `10.1145/3717823.3718197`; MIT record: https://dspace.mit.edu/entities/publication/9bbf3cdb-ea42-4d50-8d98-7b0f2c30432e
3. **The Randomized k-Server Conjecture Is False!** — Sébastien Bubeck, Christian Coester, Yuval Rabani, STOC 2023 Best Paper. DOI: `10.1145/3564246.3585132`; accepted manuscript: https://ora.ox.ac.uk/objects/uuid%3A29674f42-b991-4351-9a27-6ba24ee1d08c

## Transferable writing rules for TFOESUU

### 1. State the barrier before the machinery

Lead with the established problem, the exact obstacle, and what previous access/model assumptions fail to exploit. A reader should know within the first page why the result changes the state of knowledge.

For TFOESUU, the barrier is not merely 'fairness is important'. The barrier is that fresh auditing ignores two kinds of information that software evolution creates: the old executable version and localized patch information. The introduction should make the query-complexity consequence of that omission concrete.

### 2. Put the strongest theorem-level message early

Award papers state the main asymptotic improvement immediately and then explain the technique. TFOESUU should foreground the two genuine changes in complexity: the `Psi(H,nu)` graph allocation for the Gaussian core, and the replay hierarchy in which stronger synchronization can change the small-effect exponent from quadratic to linear.

### 3. Separate theorem statement, intuition, and proof burden

Do not bury intuition inside proof algebra. Each major theorem should have: (a) a precise formal statement; (b) a short paragraph explaining why it is surprising/useful; (c) proof roadmap; (d) full proof. This is especially important for P15--P17.

### 4. Make the new technique identifiable

The paper needs a memorable mechanism, not a list of lemmas. Our candidate mechanism is **replay the change, not the whole system**: reuse certificates, synchronize versions, and allocate executions on the residual fairness graph according to the information geometry exposed by the available replay primitive.

### 5. Fence novelty aggressively

Best theory papers are explicit about what is classical and what is new. Keep common random numbers, coupling, fractional covers, change-of-measure, and regression-test selection as prior tools. Novelty must be attached to the version-aware fairness-regression access model and the proved complexity consequences.

### 6. Use examples and counterexamples as proof communication

The P17 heterogeneous fair-null obstruction should be treated as a first-class explanatory object because it tells the reader exactly why the homogeneous theorem stops where it does. The positive-measure `0.15` obstruction is more informative than a vague threats-to-validity paragraph.

### 7. Keep experimental evidence subordinate to the theorem

The computational section should answer whether the executable implementation reproduces theorem geometry, finite-instance constants, error control, and scope boundaries. Do not turn the paper into a leaderboard or let dataset count substitute for theory.

### 8. Maintain compact professional prose

Prefer short declarative sentences, explicit quantifiers, and named technical objects. Avoid inflated claims, motivational repetition, generic adjectives, and long strings of em dashes. Every paragraph should have one job.

## Manuscript checklist derived from these references

- First page: problem, barrier, model, headline theorem consequences.
- Introduction: 3--5 contribution bullets with theorem identifiers or exact asymptotic consequences.
- One overview figure that encodes the evidence-reuse pipeline and replay hierarchy.
- Algorithm box only where it helps connect access assumptions to executable steps.
- Each main theorem followed by one intuition paragraph.
- Counterexamples located near the theorem boundary they constrain.
- Experimental RQs tied directly to claims in the theorem spine.
- Main result table/figure generated automatically from frozen outputs.
- Related work written as a novelty fence, not a bibliography dump.
- Conclusion states what is solved and what exact frontier remains open.