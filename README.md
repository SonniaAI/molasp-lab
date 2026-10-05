# molasp-lab

Public lab notebook for a research programme on **compiling answer set
programs to molecular substrates** — and, in the more promising direction,
using answer set programming to *specify* molecular systems.

## Programme

Two questions, one programme:

1. **What can molecular substrates compute for ASP?** DNA strand
   displacement (DSD) and seeded algorithmic self-assembly can propagate,
   sample, and (via thermodynamics) optimise — but not learn clauses. The
   defensible architecture keeps a classical ASP solver in the outer loop
   and the molecules in the inner one.
2. **What can ASP do for molecular design?** Tile-set synthesis and DSD
   circuit design under leak budgets are NP-hard combinatorial design
   problems currently handled by ad hoc methods. They have exactly the
   shape (choice, hard constraints, weak constraints as objective) that
   ASP handles well.

## Falsifiable claims under investigation

- **C1** — a compiled DSD network's stable reporter configuration equals
  the well-founded model of the source program (compute-only check).
- **C2** — seeded tile assembly computes *stable* models, not merely
  supported models (the key experiment; compute-first via kTAM simulation).
- **C3** — expected tile mass to first witness scales with the search tree
  `S(P)`, not with `2^n`.
- **C4–C7** — in-vitro propagation, learnability of stall profiles, hybrid
  crossover behaviour, annealing-as-optimisation. See the lab log for
  current status of each.

## Status

Pre-alpha. **Nothing in this repo is a validated result until a log entry
says so and names its evidence.** Entries in `log/` are working notes.

## Layout

- `log/` — dated lab notebook entries (the record of the programme)
- `molasp/` — code: resource arithmetic, tightness analysis, and (in time)
  the compiler pipeline
- `tests/` — the checks that make the numbers reproducible

Run the checks with stdlib only:

```sh
python3 -m unittest discover -s tests -v
```

## Key prior work

- Brun — [3-SAT in the tile assembly model](https://people.cs.umass.edu/~brun/pubs/pubs/Brun12natcomp.pdf) (Θ(1.8393ⁿ) assemblies, Θ(1) tile types)
- Qian, Winfree, Bruck — [DNA strand displacement neural networks](https://link.springer.com/article/10.1038/nature10262) (dual-rail monotone construction)
- Wang, Thachuk, Ellington, Winfree, Soloveichik — [leakless strand displacement design](https://resolver.caltech.edu/CaltechAUTHORS:20181213-151040513)
- Winfree, Bekbolatov — proofreading tile systems (k×k transform)
- [Minimum tile set problem is NP-complete](https://core.ac.uk/works/2249929); [binary pattern tile set synthesis is NP-hard](https://csd.uwo.ca/~lkari/pdfs/2PATS_Algorithmica.pdf)

## Standing rules

1. The tube is a sampler, not an enumerator. One-sided claims only.
2. Name all three resources every time: species count, copy number,
   search multiplicity. Never let one stand in for another.
3. Compute before synthesis: C1/C2 die in simulation (KinDA, Xgrow)
   before anyone orders an oligo.
4. No wet work happens from this repo. A wet-lab submission is drafted
   here and escalated to a human gate, never executed.
5. Direct pushes to `main` are the norm — this is a lab notebook, not
   product code. History rewrites are reserved for purges (e.g. removing
   an internal document published by mistake) and every rewrite lands
   with a receipt naming what was purged and why.

## License

Code: MIT (see `LICENSE`). Lab notes: CC BY 4.0.
