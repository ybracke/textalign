from textalign import docsplit


# TODO
def test_get_search_pattern() -> None:
    tokens_a = [
        "Um",
        "den",
        "Vorrath",
        "grüner",
        "Olivenäſte",
        ".",
        "Den",
        "er",
        "ſich",
        "zur",
        "Seite",
        "hatte",
        "hinlegen",
        "laſſen",
        ".",
        "Allmählig",
        "in",
        "die",
        "Flamme",
        "zu",
        "ſchieben",
        ".",
    ]
    tokens_b = [
        "Um",
        "den",
        "Vorrat",
        "grüner",
        "Olivenäste",
        ".",
        "Den",
        "er",
        "sich",
        "zur",
        "Seite",
        "hatte",
        "hinlegen",
        "lassen",
        ".",
        "Allmählich",
        "in",
        "die",
        "Flamme",
        "zu",
        "schieben",
        ".",
    ]

    docsplitter = docsplit.DocSplitter(
        tokens_a, tokens_b, subseq_len=4, apply_translit=False  # 4 tokens per pattern
    )

    # Without translit
    target = "grünerOlivenäſte.Den"
    pattern = docsplitter._get_search_pattern(3)
    assert pattern == target

    # With translit
    docsplitter.apply_translit = True
    target = "grünerOlivenäste.Den"
    pattern = docsplitter._get_search_pattern(3)
    assert pattern == target

    # If pattern length exceeds the end it contains less than 4 tokens
    # In practice this does not happen because we wont iterate that far
    target = "schieben."
    pattern = docsplitter._get_search_pattern(20)
    assert pattern == target


def test_docsplit_iterfind_split_positions() -> None:
    tokens_a = [
        "Um",
        "den",
        "Vorrath",
        "grüner",
        "Olivenäſte",
        ".",
        "Den",
        "er",
        "ſich",
        "zur",
        "Seite",
        "hatte",
        "hinlegen",
        "laſſen",
        ".",
        "Allmählig",
        "in",
        "die",
        "Flamme",
        "zu",
        "ſchieben",
        ".",
    ]
    tokens_b = [
        "Um",
        "den",
        "Vorrat",
        "grüner",
        "Olivenäste",
        ".",
        "Den",
        "er",
        "sich",
        "zur",
        "Seite",
        "hatte",
        "hinlegen",
        "lassen",
        ".",
        "Allmählich",
        "in",
        "die",
        "Flamme",
        "zu",
        "schieben",
        ".",
    ]

    docsplitter = docsplit.DocSplitter(
        tokens_a, tokens_b, max_lev_dist=2, subseq_len=3, step_size=1, max_len_split=5
    )

    print()
    for idx_a, idx_b in docsplitter.iterfind_split_positions():
        print(idx_a, idx_b)
        pass

    assert True


def test_docsplit_iterfind_split_positions_realdoc() -> None:
    f_hist = "tests/testdata/simplicissimus_hist.txt"
    f_norm = "tests/testdata/simplicissimus_norm.txt"
    with open(f_hist, "r", encoding="utf-8") as f:
        hist = f.read()
    with open(f_norm, "r", encoding="utf-8") as f:
        norm = f.read()

    hist = [line.split()[0] for line in hist.split("\n") if len(line.split())]
    norm = [line.split()[0] for line in norm.split("\n") if len(line.split())]

    docsplitter = docsplit.DocSplitter(
        hist, norm, max_lev_dist=3, subseq_len=7, step_size=100, max_len_split=1000
    )

    for idx_a, idx_b in docsplitter.iterfind_split_positions():
        a = hist[idx_a : idx_a + 7]
        b = norm[idx_b : idx_b + 7]
        print(f"Matching:\n{a}\n{b}\n")

    assert True


def test_docsplit_split() -> None:
    tokens_a = [
        "Um",
        "den",
        "Vorrath",
        "grüner",
        "Olivenäſte",
        ".",
        "Den",
        "er",
        "ſich",
        "zur",
        "Seite",
        "hatte",
        "hinlegen",
        "laſſen",
        ".",
        "Allmählig",
        "in",
        "die",
        "Flamme",
        "zu",
        "ſchieben",
        ".",
    ]
    tokens_b = [
        "Um",
        "den",
        "Vorrat",
        "grüner",
        "Olivenäste",
        ".",
        "Den",
        "er",
        "sich",
        "zur",
        "Seite",
        "hatte",
        "hinlegen",
        "lassen",
        ".",
        "Allmählich",
        "in",
        "die",
        "Flamme",
        "zu",
        "schieben",
        ".",
    ]

    docsplitter = docsplit.DocSplitter(
        tokens_a, tokens_b, max_lev_dist=2, subseq_len=3, step_size=1, max_len_split=5
    )

    targets = [
        ([".", "Den", "er"], [".", "Den", "er"]),
        (["Seite", "hatte", "hinlegen"], ["Seite", "hatte", "hinlegen"]),
        (["Allmählig", "in", "die"], ["Allmählich", "in", "die"]),
    ]

    for i, (split_a, split_b) in enumerate(docsplitter.split()):
        assert split_a == targets[i][0]
        assert split_b == targets[i][1]
