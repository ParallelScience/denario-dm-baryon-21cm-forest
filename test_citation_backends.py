"""Generate paper_v3_citations using a chosen Denario citation backend.

Side-by-side comparison driver: runs the per-section citation step
(Introduction + Methods, mirroring Denario's add_citations flow) for one
backend at a time, writing tagged output files so both backends can coexist
in the same paper_output/.

Outputs (per backend):
  paper_output/paper_v3_citations_<backend>.tex
  paper_output/paper_v3_citations_<backend>.pdf
  paper_output/bibliography_<backend>.bib
  paper_output/temp/{Introduction,Methods}_w_citations_<backend>.tex
  paper_output/temp/{Introduction,Methods}_<backend>.bib
  paper_output/<backend>_run/  — LLM_calls.txt, costs.txt, run.log

Usage:
  python test_citation_backends.py --backend perplexity
  python test_citation_backends.py --backend valency
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

DENARIO = Path("/scratch/scratch-aiscientist/Denario")
ITER = Path("/scratch/scratch-aiscientist/test/denario-dm-baryon-21cm-forest/Iteration3")
PAPER_OUT = ITER / "paper_output"
TEMP = PAPER_OUT / "temp"

for env_path in [
    Path("/scratch/scratch-aiscientist/parallelscience/denario-scientists/.env"),
    DENARIO / ".env",
]:
    if env_path.exists():
        load_dotenv(env_path, override=False)

sys.path.insert(0, str(DENARIO))

from denario.key_manager import KeyManager
from denario.langgraph_agents.citation_backends import get_citation_backend


def _extract_body(tex: str) -> tuple[str, str, str]:
    begin = tex.find("\\begin{document}")
    end = tex.find("\\end{document}")
    if begin == -1 or end == -1:
        return "", tex, ""
    return (
        tex[: begin + len("\\begin{document}")],
        tex[begin + len("\\begin{document}") : end],
        tex[end:],
    )


def make_state(work_dir: Path, backend: str) -> dict:
    import yaml
    work_dir.mkdir(parents=True, exist_ok=True)
    keys = KeyManager()
    keys.get_keys_from_env()
    if backend == "perplexity" and not keys.PERPLEXITY:
        raise SystemExit("PERPLEXITY_API_KEY missing.")
    if backend == "valency" and not (keys.GEMINI or os.getenv("GOOGLE_API_KEY")):
        raise SystemExit("GOOGLE_API_KEY missing (needed by citation_inserter LLM).")

    params_yaml = ITER.parent / "params.yaml"
    params = yaml.safe_load(params_yaml.read_text())
    params.setdefault("Citations", {})
    params["Citations"]["backend"] = backend
    params["Citations"].setdefault(
        "citation_inserter", {"model": "gemini-2.5-flash", "temperature": 0.1}
    )

    return {
        "system": {
            "keys": keys,
            "params": params,
            "module_path": str(work_dir),
            "f_stream": str(work_dir / "run.log"),
            "LLM_calls": str(work_dir / "LLM_calls.txt"),
            "costs_file": str(work_dir / "costs.txt"),
            "tokens": {"i": 0, "o": 0, "ti": 0, "to": 0},
            "costs": {"i": 0.0, "o": 0.0, "ci": 0.0, "co": 0.0},
        }
    }


def run_section(state, section: str, backend: str, reuse_cached: bool = True):
    src = TEMP / f"{section}.tex"
    out_tex = TEMP / f"{section}_w_citations_{backend}.tex"
    out_bib = TEMP / f"{section}_{backend}.bib"
    if reuse_cached and out_tex.exists() and out_bib.exists():
        print(f"[{backend}/{section}] reusing cached {out_tex.name}, {out_bib.name}")
        return out_tex.read_text(), out_bib.read_text()
    print(f"[{backend}/{section}] reading {src.name}")
    text = src.read_text()
    fn = get_citation_backend(backend)
    t0 = time.time()
    result = fn(text, state)
    elapsed = time.time() - t0
    n_papers = len(result.papers) if result.papers else "n/a"
    print(f"[{backend}/{section}] done in {elapsed:.1f}s; papers={n_papers}; "
          f"bib_chars={len(result.bibtex)}")
    out_tex.write_text(result.text)
    out_bib.write_text(result.bibtex.strip() + "\n")
    return result.text, result.bibtex


def splice_v2(intro_tex: str, methods_tex: str, backend: str):
    v2 = (PAPER_OUT / "paper_v2_no_citations.tex").read_text()
    intro_src = (TEMP / "Introduction.tex").read_text()
    methods_src = (TEMP / "Methods.tex").read_text()

    def _splice(doc, src_full, annotated_full, label):
        _, src_body, _ = _extract_body(src_full)
        _, ann_body, _ = _extract_body(annotated_full)
        src_paras = [p for p in src_body.strip().split("\n\n") if p.strip()]
        ann_paras = [p for p in ann_body.strip().split("\n\n") if p.strip()]
        # Strategy A: paragraph-by-paragraph (works when annotator preserves
        # paragraph breaks — e.g. the Valency LLM-driven backend).
        if len(src_paras) == len(ann_paras):
            misses = 0
            for src_p, ann_p in zip(src_paras, ann_paras):
                if src_p in doc:
                    doc = doc.replace(src_p, ann_p, 1)
                else:
                    misses += 1
            if misses:
                print(f"WARNING [{label}]: {misses}/{len(src_paras)} paragraphs not found verbatim")
            return doc, len(src_paras) - misses
        # Strategy B: bracket-replace (works when annotator collapses
        # paragraphs — e.g. the Perplexity backend reflows the section).
        # Replace from the first src paragraph through the last src paragraph
        # with the entire annotated body.
        first, last = src_paras[0], src_paras[-1]
        i_first = doc.find(first)
        i_last = doc.find(last, i_first + 1) if i_first != -1 else -1
        if i_first == -1 or i_last == -1:
            print(f"WARNING [{label}]: bracket landmarks not found; skipping")
            return doc, 0
        end = i_last + len(last)
        new_doc = doc[:i_first] + ann_body.strip() + doc[end:]
        print(f"[{label}] bracket-replaced (collapsed to 1 paragraph)")
        return new_doc, len(src_paras)

    v2, intro_hits = _splice(v2, intro_src, intro_tex, "Introduction")
    v2, methods_hits = _splice(v2, methods_src, methods_tex, "Methods")
    print(f"spliced paragraphs: Introduction={intro_hits}, Methods={methods_hits}")

    v2 = v2.replace("\\bibliography{bibliography}", f"\\bibliography{{bibliography_{backend}}}")
    # Inject utf8 inputenc so accented Latin authors in the bib render. The
    # paper templates don't load it by default, but we have non-ASCII chars
    # in the sanitized bib that pdflatex needs help with.
    if "\\usepackage[utf8]{inputenc}" not in v2:
        v2 = v2.replace(
            "\\usepackage{amsmath}",
            "\\usepackage[utf8]{inputenc}\n\\usepackage{amsmath}",
            1,
        )
    out_paper = PAPER_OUT / f"paper_v3_citations_{backend}.tex"
    out_paper.write_text(v2)
    return out_paper


_UNICODE_TO_LATEX = {
    "Λ": r"$\Lambda$", "Ω": r"$\Omega$", "Σ": r"$\Sigma$", "Δ": r"$\Delta$",
    "Φ": r"$\Phi$", "Ψ": r"$\Psi$", "Γ": r"$\Gamma$", "Π": r"$\Pi$",
    "Θ": r"$\Theta$", "Ξ": r"$\Xi$",
    "α": r"$\alpha$", "β": r"$\beta$", "γ": r"$\gamma$", "δ": r"$\delta$",
    "ε": r"$\varepsilon$", "ζ": r"$\zeta$", "η": r"$\eta$", "θ": r"$\theta$",
    "ι": r"$\iota$", "κ": r"$\kappa$", "λ": r"$\lambda$", "μ": r"$\mu$",
    "ν": r"$\nu$", "ξ": r"$\xi$", "π": r"$\pi$", "ρ": r"$\rho$",
    "σ": r"$\sigma$", "τ": r"$\tau$", "υ": r"$\upsilon$", "φ": r"$\varphi$",
    "χ": r"$\chi$", "ψ": r"$\psi$", "ω": r"$\omega$",
    "–": "--", "—": "---",
    "“": "``", "”": "''", "‘": "`", "’": "'",
    "×": r"$\times$", "·": r"$\cdot$", "≈": r"$\approx$",
    "≤": r"$\leq$", "≥": r"$\geq$", "±": r"$\pm$",
    "ʹ": "'",
}


def sanitize_bib(path: Path):
    """Dedupe + strip MathML + replace HTML entities and common Unicode glyphs."""
    import re
    text = path.read_text()
    # 1) Dedupe by key
    entries = re.split(r"(?m)^(?=@)", text)
    seen, kept = set(), []
    for e in entries:
        e = e.strip()
        if not e:
            continue
        m = re.match(r"@\w+\{([^,\s]+)\s*,", e)
        if not m:
            continue
        if m.group(1) in seen:
            continue
        seen.add(m.group(1))
        kept.append(e)
    text = "\n\n".join(kept) + "\n"
    # 2) Strip CrossRef-style MathML blocks (keep the fallback symbol)
    text = re.sub(r"<mml:math[^>]*>(.*?)</mml:math>", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"<mml:[^>]*>", "", text)
    text = re.sub(r"</mml:[^>]*>", "", text)
    # 3) HTML entities and bare ampersands
    text = text.replace("&amp;", r"\&")
    text = re.sub(r"(?<!\\)&", r"\\&", text)
    # 4) Common Unicode glyphs to LaTeX
    for u, latex in _UNICODE_TO_LATEX.items():
        text = text.replace(u, latex)
    # 5) Drop characters outside basic Latin and Latin-1 / Latin Extended-A
    # (which inputenc-utf8 can render). This nukes CJK and other scripts
    # that pdflatex would refuse, while keeping accented Latin authors.
    def _safe_char(c: str) -> bool:
        cp = ord(c)
        if cp <= 127:
            return True
        if 0x00A0 <= cp <= 0x024F:  # Latin-1 + Latin Extended-A/B
            return True
        return False

    text = "".join(c if _safe_char(c) else "" for c in text)
    leftover = sorted(set(c for c in text if ord(c) > 127))
    if leftover:
        print(f"  kept Latin-extended chars: {''.join(leftover)}")
    path.write_text(text)
    print(f"sanitized {path.name}: {len(kept)} unique entries")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["perplexity", "valency"], required=True)
    args = ap.parse_args()
    backend = args.backend

    work_dir = PAPER_OUT / f"{backend}_run"
    state = make_state(work_dir, backend)

    intro_tex, intro_bib = run_section(state, "Introduction", backend)
    methods_tex, methods_bib = run_section(state, "Methods", backend)

    out_paper = splice_v2(intro_tex, methods_tex, backend)
    out_bib = PAPER_OUT / f"bibliography_{backend}.bib"
    out_bib.write_text((intro_bib + "\n\n" + methods_bib).strip() + "\n")
    sanitize_bib(out_bib)

    print(f"\nwrote {out_paper}")
    print(f"wrote {out_bib}")


if __name__ == "__main__":
    main()
