# Valid predictions are not valid inference

**Maxime Gourguechon** · Econometrics & ML engineering · Aubay × CNRS Fondation Science4Reefs (intern)

Paris · Revised July 2026 · JEL: C45, C52, C81, E52
Keywords: point-in-time data · temporal leakage · local projections · model evaluation · causal inference
Correspondence: [maxime.gourguechon76@gmail.com](mailto:maxime.gourguechon76@gmail.com) · [LinkedIn](https://www.linkedin.com/in/maxime-gourguechon76/) · The author is on the September 2026 job market.

> *It is better to be vaguely right than exactly wrong.*
>
> <sub>Carveth Read, *Logic: Deductive and Inductive* (1898), ch. 22</sub>

<!-- FIGURE 1 : photographie une IRF ou un DAG d'identification dessiné dans TON carnet,
     enregistre-la en assets/figure1.jpg, puis décommente les trois lignes ci-dessous.
<p align="center"><img src="assets/figure1.jpg" width="55%" alt="Hand-drawn impulse response sketch from the author's notebook"/></p>

*Figure 1. The identification problem, as first drawn.*
-->

## Abstract

I train models for a living and distrust most of them, mine included. This page collects work at the intersection of econometrics and machine learning: a pre-registered causal study of monetary policy on employment that returned a null and shipped as one; a decision platform built on a dataset that turned out to carry no signal, and says so; a coral instance segmentation pipeline evaluated the only way field imagery allows, stratified by domain. The common method is unglamorous. Point-in-time data, purged validation, and the standing assumption that a good backtest is a bug until proven otherwise. Replication files below. Comments, referee reports and job offers are equally welcome.

**Résumé.** Je construis des modèles et je m'en méfie, les miens d'abord. Ce document rassemble des travaux à l'intersection de l'économétrie et du machine learning : une étude causale pré-enregistrée de l'effet de la politique monétaire sur l'emploi, publiée avec son résultat nul ; une plateforme d'aide à la décision construite sur des données sans signal, et qui le dit ; un pipeline de segmentation d'instances de coraux évalué par stratification de domaine. La méthode commune n'a rien de spectaculaire : données point-in-time, validation purgée, et l'hypothèse permanente qu'un bon backtest est un bug jusqu'à preuve du contraire. Dossiers de réplication en Annexe A. Commentaires, rapports de referee et offres d'emploi également bienvenus.

## 1. Specifications

|                | (1) Monetary shocks on employment | (2) Sales analytics without signal | (3) Coral segmentation |
|----------------|-----------------------------------|-------------------------------------|------------------------|
| Question       | do contractionary shocks destroy jobs? | what is honest decision support? | which corals, where, how many? |
| Method         | panel LP, LP-DiD, DML, Bayesian LP | GBM benchmark, permutation tests, positive control | YOLO + SAM, domain-stratified evaluation |
| Headline       | β̂ ≈ 0 [^1]                        | R² ≈ 0 real, 0.85 on control [^2]  | results withheld [^3]  |
|                | (80 tests)                        | (73 tests)                          | (Aubay × CNRS)         |
| Data           | ALFRED vintages, BLS QCEW         | Kaggle, and it matters [^2]         | in-situ reef imagery   |
| Delivery       | [live app](https://huggingface.co/spaces/maxime2476/causal-impact-lab), v0.1.0 | [live dashboard](https://maxime2476-bmw-sales-analytics.hf.space) | production pipeline |
| Source         | [causal-impact-lab](https://github.com/maxime2476/causal-impact-lab) | [bmw-sales-analytics](https://github.com/maxime2476/bmw-sales-analytics) | reference on request |

Test-suite sizes in parentheses. The stars are withheld; see the footnotes instead.

[^1]: Pre-registered before estimation; four estimators concur on the 2014-2020 sample. Every identifying assumption is registered next to the probe that stress-tests it.
[^2]: The dataset is structurally clean and statistically empty, with one leaked target. The pipeline proves R² ≈ 0.85 on a positive control, then reports the honest zero on the real thing, permutation-tested. Value is delivered where it legitimately exists, through a scenario simulator with explicit uncertainty.
[^3]: The single transferable lesson I can share: an aggregate metric is a weighted average of your successes and your failures, and the weights are not your friends.

## 2. The estimating equation behind column (1)

$$
\Delta_h \ln E_{s,t+h} = \beta_h\left(\mathrm{Exposure}_s \times \varepsilon^{MP}_{t}\right) + \alpha_s + \lambda_t + \Gamma' X_{s,t} + u_{s,t+h}
$$

State-level rate exposure interacted with an identified monetary shock; time fixed effects absorb the aggregate. Nothing exotic. The discipline is in the data, not the estimator: ALFRED vintages so the regressors only know what was knowable, an analysis plan frozen before the first regression, and robustness checks that were allowed to kill the result. They almost did. What survived is equation (1) with a coefficient you cannot distinguish from zero, which is exactly what got published.

## 3. Minor works

A lightweight Bash monitoring daemon, [linux-sys-monitor](https://github.com/maxime2476/linux-sys-monitor), alerts to Slack or Discord, systemd unit, Grafana dashboard. Written to know exactly what runs on my own machines, kept because ShellCheck passes.

Earlier academic exercises remain public out of principle rather than pride: [text mining on FOMC transcripts](https://github.com/maxime2476/sentiment-powell-nlp) and [panel econometrics on Eurostat data](https://github.com/maxime2476/panel-project). That is where the habit comes from.

## 4. Instruments

None of the following are valid in the IV sense; they are simply what the work runs on. Calibration is self-reported.

| Tier | Toolchain | Calibration |
|------|-----------|-------------|
| Strong instruments | Python (pandas, NumPy, scikit-learn, statsmodels, PyTorch), DuckDB, pandera & pydantic, pytest, mypy, ruff, uv, Git, Docker, GitHub Actions | first-stage F comfortably above 10; used daily |
| Just-identified | Streamlit, Hugging Face Spaces, PostgreSQL, Bash, LaTeX | exactly as much as the deliverables required, no more claimed |
| Weak instruments | R, Stata, C++ | point estimates directionally correct, standard errors wide; the MSc lives on, with rust |

## 5. The apparatus

Section 4 lists the parts; this is the assembly. Every column of Table 1 runs through the same five stages, and the architecture is deliberately boring.

```
sources ──► ingest ──► validate ──► estimate ──► evaluate ──► report
ALFRED      point-in-  pandera      LP · LP-DiD  purged CV    methods,
QCEW        time,      contracts,   DML · GBM    permutation  results,
Kaggle      as-of      typed        YOLO + SAM   tests,       live app,
imagery     joins      frames                    positive     ADR
                                                 controls,
                                                 stratified
 └─────────── every artifact logged to a DuckDB provenance ledger ───────────┘
       gate on every push: uv.lock · ruff · mypy --strict · pytest · CI
```

Reading order matters less than responsibility. Ingestion is where leakage is born, so it carries the heaviest discipline: vintage data and as-of joins, and no stage downstream can know the future. Validation moves failure from runtime to import time; a frame that violates its contract never reaches an estimator. Estimation is commodity on purpose, the one block that changes across columns (1) to (3). Evaluation is adversarial: its job is to kill results, so it holds the permutation tests, positive controls and stratification. Reporting includes what died, since a buried null re-runs itself on someone else's budget.

The flagships above are earlier cuts of this pattern. From *pitfall* onward the skeleton is frozen, and uv pins every environment without exception:

```
project/
├── pyproject.toml + uv.lock
├── src/<pkg>/
│   ├── ingest/        # point-in-time loaders, as-of joins
│   ├── schemas/       # pandera contracts; failure at import time
│   ├── estimate/      # models, deliberately thin
│   ├── evaluate/      # purged CV, permutation tests, controls
│   └── report/        # renders results from run artifacts
├── tests/{unit,property,golden,synthetic}/
├── conf/              # pydantic-settings, frozen
├── runs/ (gitignored) + ledger.duckdb   # git SHA, lock hash, data vintage
├── docs/adr/
└── .github/workflows/
```

The tree is the figure above, folded into folders. Two rules travel with it: results are generated from run artifacts, never written by hand, so a report cannot drift from the code that produced it; and every run is stamped with its git SHA, lock hash and data vintage, so any number in any report re-executes by identifier. Libraries take the subset; the invariants are the lockfile, the test taxonomy and the generated results.

## 6. Open problems

Three questions currently on the desk, offered as conversation starters rather than claims.

1. **Microstructure.** Can order-flow toxicity (VPIN) be measured on DEX data, and does it explain realized loss-versus-rebalancing? The data is public; the identification is not obvious.
2. **Inference.** ML models produce excellent point predictions and naively invalid standard errors. What does honest uncertainty look like when the point estimate comes from a gradient boosting machine? A repository on this is quietly under construction.
3. **Evaluation.** Aggregate detection metrics average over domains, and the domains that matter are usually the rare ones. What is the right objective when missing the rare class is the entire failure mode?

## 7. Threats to validity

A document that audits models should survive its own audit.

*Internal validity.* Does the evidence here measure what it claims? The mitigations are structural rather than rhetorical: typed code, pinned environments, test suites gating every push, an analysis plan frozen before estimation. What no repository can show is the discarded work; the garden of forking paths is pruned in private. The pre-registration exists precisely because I do not trust myself on that point.

*External validity.* The flagships are single-author projects. Whether the discipline transfers to a team, a review culture and production constraints is not identified by this document. The closest evidence is a segmentation pipeline delivered inside an industrial partnership, which I cannot show here.

*Construct validity.* A GitHub profile measures the intersection of skill and time spent making skill visible. The two are correlated, not identical.

The out-of-sample test is an interview.

<!-- ## Selected referee comments
     Règle stricte : citations EXACTES de mainteneurs sur tes PRs, avec liens vers les threads.
     Rien d'inventé, rien de paraphrasé. Sinon, supprimer tout ce bloc.

> "citation exacte du reviewer" · *statsmodels* maintainer, [PR #____](URL_du_thread)

Addressed in [the following commit](URL_du_commit). Being reviewed by people better
than you is the entire point of open source.
-->

## References

Bu, C., Rogers, J., & Wu, W. (2021). A unified measure of Fed monetary policy shocks. *Journal of Monetary Economics*, 118.

Dube, A., Girardi, D., Jordà, Ò., & Taylor, A. M. (2023). A local projections approach to difference-in-differences event studies. NBER Working Paper 31184.

Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *Annals of Statistics*, 29(5).

Gourguechon, M. (2026). *causal-impact-lab* (v0.1.0) [software]. MIT license. <https://github.com/maxime2476/causal-impact-lab>

Gourguechon, M. (2026). *bmw-sales-analytics* [software]. MIT license. <https://github.com/maxime2476/bmw-sales-analytics>

Gourguechon, M. (2026). *linux-sys-monitor* [software]. MIT license. <https://github.com/maxime2476/linux-sys-monitor>

Gourguechon, M. (forthcoming). *pitfall*: point-in-time leakage detection for time-series ML.

Jordà, Ò. (2005). Estimation and inference of impulse responses by local projections. *American Economic Review*, 95(1).

Kirillov, A., et al. (2023). Segment anything. *Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)*.

Read, C. (1898). *Logic: Deductive and Inductive*. London: Grant Richards.

<!-- TODO: transformer en liens vers les threads de PR réels avant de pousser -->
Miscellanea: contributions to *statsmodels* (merged) and *ultralytics* (open).

## Appendix A. Claims and where to verify them

Every public claim in this document is written to be checked; column (3) is the stated exception, its evidence behind an NDA, which is why its headline says withheld rather than asserted. The table maps the rest to their evidence. Both flagships gate every push with pytest in CI; causal-impact-lab additionally pins its environment with a uv lockfile, which is why the command below works from any clean machine.

| Claim (section) | Verify at |
|-----------------|-----------|
| Analysis plan frozen before estimation (1) | [`docs/analysis_plan.md`](https://github.com/maxime2476/causal-impact-lab/blob/main/docs/analysis_plan.md) |
| Four estimators, one null (1, 2) | [`docs/methods.md`](https://github.com/maxime2476/causal-impact-lab/blob/main/docs/methods.md) · [`docs/results.md`](https://github.com/maxime2476/causal-impact-lab/blob/main/docs/results.md) |
| 80 tests (1) | [`tests/`](https://github.com/maxime2476/causal-impact-lab/tree/main/tests) |
| R² ≈ 0 on the real data, permutation-tested (1) | [`reports/model_benchmark.md`](https://github.com/maxime2476/bmw-sales-analytics/blob/main/reports/model_benchmark.md) |
| 73 tests (1) | [`tests/`](https://github.com/maxime2476/bmw-sales-analytics/tree/main/tests) |

Reproduction of column (1), end to end: `git clone https://github.com/maxime2476/causal-impact-lab && cd causal-impact-lab && uv sync --all-extras && uv run pytest`.

*Preliminary and incomplete, like every profile. Comments welcome.*