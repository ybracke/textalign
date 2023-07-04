# Needs a pip install of package (called `foo` here)

import textalign


def test_clean_alignments():
    tok_alignments = [
        (0, 0),
        (1, 1),
        (2, None),
        (None, 2),
        (3, 3),
        # (3,2),
        # (None,3),
        (4, 4),
    ]

    tokens_a = ["Eyn", "Haus", "mann", "riefs", "ſo"]

    tokens_b = ["Ein", "Hausmann", "rief", "es", "so"]

    aligner = textalign.Aligner(tokens_a, tokens_b, tok_alignments)

    cleaned_alignments = aligner.clean_alignments()

    target_alignments = [
        (0, 0),
        (1, 1),
        (2, None),
        (3, 2),  # riefs -> rief
        (3, 3),  # riefs -> es
        (4, 4),
    ]
    assert cleaned_alignments == target_alignments
    # print(cleaned_alignments)


def test_do_all():
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
    aligner.do_all()

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
