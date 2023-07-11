# Needs a pip install of package (called `foo` here)

import textalign


def test_clean_alignments():
    tok_alignments = [(0, 0), (1, 1), (2, None), (None, 2), (3, 3), (4, 4), (5, None)]

    tokens_a = ["Eyn", "Haus", "mann", "riefs", "ſo", "FOO"]

    tokens_b = ["Ein", "Hausmann", "rief", "es", "so"]

    aligner = textalign.Aligner(tokens_a, tokens_b)
    aligner.a, aligner.b = list(zip(*tok_alignments))
    aligner.translit_tokens()

    cleaned_alignments = aligner.clean_alignments()

    target_alignments = [
        (0, 0),
        (1, 1),
        (2, 1),
        (3, 2),  # riefs -> rief
        (3, 3),  # riefs -> es
        (4, 4),
        (5, None),
    ]
    assert cleaned_alignments == target_alignments
    # print(cleaned_alignments)


def test_get_bidirectional_alignments():
    f_hist = "tests/testdata/simplicissimus_hist.txt"
    f_norm = "tests/testdata/simplicissimus_norm.txt"
    with open(f_hist, "r", encoding="utf-8") as f:
        hist = f.read()
    with open(f_norm, "r", encoding="utf-8") as f:
        norm = f.read()

    hist = [line.split()[0] for line in hist.split("\n")[:200] if len(line.split())][:]
    norm = [line.split()[0] for line in norm.split("\n")[:200] if len(line.split())][:]

    # remove punctuation (billo)
    # hist = [token for token in hist if token not in ".,/;()"]
    # norm = [token for token in norm if token not in ".,/;()"]

    aligner = textalign.Aligner(hist, norm)
    kwargs = {
        "similarity_func": textalign.aligner.jaro_rescored,
        "gap_cost_func": textalign.aligner.decreasing_gap_cost,
        "gap_cost_initial": 1,
    }
    aligner.get_bidirectional_alignments(**kwargs)

    outfile = "tests/testdata/out/test01.out"
    with open(outfile, "w", encoding="utf-8") as fout:
        for i_a, i_b in zip(aligner.a, aligner.b):
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


# fake test
def test_get_aligned_pairs() -> None:
    f_hist = "tests/testdata/simplicissimus_hist.txt"
    f_norm = "tests/testdata/simplicissimus_norm.txt"
    with open(f_hist, "r", encoding="utf-8") as f:
        hist = f.read()
    with open(f_norm, "r", encoding="utf-8") as f:
        norm = f.read()

    hist = [line.split()[0] for line in hist.split("\n")[:] if len(line.split())][
        4754:4760
    ]  # take short sequence from hist
    # print(hist[4754:4760])
    norm = [line.split()[0] for line in norm.split("\n")[:] if len(line.split())][:]

    aligner = textalign.Aligner(hist, norm)
    kwargs = {
        "similarity_func": textalign.aligner.jaro_rescored,
        "gap_cost_func": textalign.aligner.decreasing_gap_cost,
        "gap_cost_initial": 1,
    }
    aligner.get_bidirectional_alignments(**kwargs)

    aligned_pairs = aligner.get_aligned_pairs()

    for i, pair in enumerate(aligned_pairs):
        if pair.a is not None:
            break
    print(aligned_pairs[i - 10 : i + 10])

    # print(aligned_pairs)

    assert True
