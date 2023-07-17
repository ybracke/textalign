from textalign import AlignedPair
import textalign


def test_alignedpair() -> None:
    pair = AlignedPair(a=1, b=2)
    assert None not in pair
    pair = AlignedPair(a=None, b=2)
    assert None in pair
    # pair = AlignedPair(a=1,b=2)


def test_nw_align() -> None:
    tokens_a = ["Eyn", "Haus", "mann", "riefs", "ſo", "FOO"]
    tokens_b = ["Ein", "Hausmann", "rief", "es", "so"]

    target_alignments = [
        AlignedPair(0, 0),  # Eyn   <-> ein
        AlignedPair(1, 1),  # Haus  <-> Hausmann
        AlignedPair(2, None),  # mann  <-> [GAP]
        AlignedPair(3, 2),  # riefs <-> rief
        AlignedPair(None, 3),  # [GAP] <-> es
        AlignedPair(4, 4),  # ſo    <-> so
        AlignedPair(5, None),  # FOO   <-> [GAP]
    ]

    kwargs = {
        "similarity_func": textalign.aligner.jaro_rescored,
        "gap_cost_func": textalign.aligner.decreasing_gap_cost,
        "gap_cost_initial": 1,
    }
    aligner = textalign.Aligner(tokens_a, tokens_b)
    aligner.translit_tokens()
    aligner.nw_align(**kwargs)
    output = aligner.aligned_tokidxs

    assert output == target_alignments


def test_clean_alignments() -> None:
    # Checks whether gaps in b (a aligns to None) can be removed
    # (note: not the other way around)

    tokens_a = ["Eyn", "Haus", "mann", "rief's", "ſo", "FOO"]
    tokens_b = ["Ein", "Hausmann", "rief", "es", "so"]

    nw_alignments = [
        AlignedPair(0, 0),  # Eyn   <-> ein
        AlignedPair(1, 1),  # Haus  <-> Hausmann
        AlignedPair(2, None),  # mann  <-> [GAP]
        AlignedPair(3, 2),  # riefs <-> rief
        AlignedPair(None, 3),  # [GAP] <-> es
        AlignedPair(4, 4),  # ſo    <-> so
        AlignedPair(5, None),  # FOO   <-> [GAP]
    ]

    aligner = textalign.Aligner(tokens_a, tokens_b)
    aligner.translit_tokens()
    aligner.aligned_tokidxs = nw_alignments
    aligner.clean_alignments()
    output = aligner.aligned_tokidxs

    target_alignments = [
        AlignedPair(0, 0),  # Eyn    <-> ein
        AlignedPair(1, 1),  # Haus   <-> Hausmann
        AlignedPair(2, 1),  # mann   <-> Hausmann
        AlignedPair(3, 2),  # rief's <-> rief
        AlignedPair(None, 3),  # rief's <-> es
        AlignedPair(4, 4),  # ſo     <-> so
        AlignedPair(5, None),  # FOO    <-> [GAP]
    ]

    assert output == target_alignments


def test_get_bidirectional_alignments() -> None:
    f_hist = "tests/testdata/simplicissimus_hist.txt"
    f_norm = "tests/testdata/simplicissimus_norm.txt"
    with open(f_hist, "r", encoding="utf-8") as f:
        hist = f.read()
    with open(f_norm, "r", encoding="utf-8") as f:
        norm = f.read()

    hist_tok = [line.split()[0] for line in hist.split("\n")[:200] if len(line.split())]
    norm_tok = [line.split()[0] for line in norm.split("\n")[:200] if len(line.split())]

    aligner = textalign.Aligner(hist_tok, norm_tok)
    kwargs = {
        # "similarity_func": textalign.aligner.jaro_rescored,
        "similarity_func": textalign.aligner.levsim_rescored,
        "gap_cost_func": textalign.aligner.decreasing_gap_cost,
        "gap_cost_length_discount": textalign.aligner.length_discount,
        "gap_cost_initial": .5,

    }
    aligner.get_bidirectional_alignments(**kwargs)

    outfile = "tests/testdata/out/test01.out"
    with open(outfile, "w", encoding="utf-8") as fout:
        for i_a, i_b in aligner.aligned_tokidxs:
            try:
                token_a = aligner.tokens_a[i_a]
            except TypeError:
                token_a = "-----"  # None
            try:
                token_b = aligner.tokens_b[i_b]
            except TypeError:
                token_b = "-----"  # None
            for token in (token_a, token_b):
                fout.write(token.ljust(20))
            fout.write("\n")

    assert True


def test_levsim() -> None:

    for (a, b, target) in [
        ("Haus", "Maus", 0.75),
        ("ich", "nichtnichtnichtnichtnicht", 0.12),
        ("nichtnichtnichtnichtnicht", "ich", 0.12),
    ]:
        output = textalign.aligner.levsim(a,b)
        assert target == output

