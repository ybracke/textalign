import pytest

from Levenshtein import distance

from textalign import docsplit
from textalign.docsplit import SplitPosition
from textalign import translit


def test_find_near_matches() -> None:
    import fuzzysearch

    pattern_a = "UmUmUm"
    b_joined = "AmAmAm---AmAmAm---AmAmAm---AmOmOm---OmOmOm---OmOmOm---OmOm"
    # b_joined = "UmUmUmUmUmUmUmUmUmUmUmUmUmUmUmUmUmUmUmUmUmUmUmUm"

    max_lev_dist = 3

    near_matches = fuzzysearch.find_near_matches(
        pattern_a,
        b_joined,
        max_l_dist=max_lev_dist,
    )

    print(near_matches)


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


def test_docsplit_find_split_positions_simple() -> None:
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

    split_positions = docsplitter.find_split_positions()

    print(split_positions)
    target = 3
    assert len(split_positions) == target

    target = [
        SplitPosition(start_a=5, end_a=8, start_b=5, end_b=8),
        SplitPosition(start_a=10, end_a=13, start_b=10, end_b=13),
        SplitPosition(start_a=15, end_a=18, start_b=15, end_b=18),
    ]
    assert split_positions == target


def test_docsplit_find_split_positions_no_matches() -> None:
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
    # shuffled
    tokens_b = [
        "grüner",
        "zur",
        "sich",
        "Seite",
        "hatte",
        ".",
        "Vorrat",
        ".",
        "schieben",
        "lassen",
        "er",
        "Allmählich",
        "Den",
        "in",
        "Um",
        ".",
        "hinlegen",
        "den",
        "zu",
        "Olivenäste",
        "Flamme",
        "die",
    ]

    docsplitter = docsplit.DocSplitter(
        tokens_a, tokens_b, max_lev_dist=1, subseq_len=3, step_size=1, max_len_split=5
    )

    split_positions = docsplitter.find_split_positions()
    target = []

    assert split_positions == target


# fake test
def test_docsplit_find_split_positions_only_multiple_matches() -> None:
    tokens_a = [
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
        "Um",
    ]
    tokens_b = [
        "Am",
        "Am",
        "Am",
        "Am",
        "Am",
        "Am",
        "Am",
        "Am",
        "Am",
        "Am",
        "Om",
        "Om",
        "Om",
        "Om",
        "Om",
        "Om",
        "Om",
        "Om",
        "Om",
        "Om",
    ]
    docsplitter = docsplit.DocSplitter(
        tokens_a, tokens_b, max_lev_dist=3, subseq_len=3, step_size=1, max_len_split=5
    )
    split_positions = docsplitter.find_split_positions()
    print("Split positions:", split_positions)


def test_docsplit_find_split_positions_realdoc() -> None:
    f_hist = "tests/testdata/simplicissimus_hist.txt"
    f_norm = "tests/testdata/simplicissimus_norm.txt"
    with open(f_hist, "r", encoding="utf-8") as f:
        hist = f.read()
    with open(f_norm, "r", encoding="utf-8") as f:
        norm = f.read()

    from textalign import translit

    hist = [
        translit.german_map(line.split()[0])  # do transliteration
        for line in hist.split("\n")
        if len(line.split())
    ]
    norm = [
        translit.german_map(line.split()[0])  # do transliteration
        for line in norm.split("\n")
        if len(line.split())
    ]

    kwargs = {
        "max_lev_dist": 3,
        "subseq_len": 7,
        "step_size": 100,
        "max_len_split": 1000,
        "apply_translit": False,  # translit has already been done
    }

    docsplitter = docsplit.DocSplitter(hist, norm, **kwargs)

    for (
        idx_start_a,
        idx_end_a,
        idx_start_b,
        idx_end_b,
    ) in docsplitter.find_split_positions():
        a = hist[idx_start_a:idx_end_a]
        b = norm[idx_start_b:idx_end_b]
        a_ = "".join(a)
        b_ = "".join(b)
        # print(f"Matching:\n{a}\n{b}\n")

        # Levenshtein distance is smaller than max distance
        assert distance(a_, b_) <= kwargs["max_lev_dist"]


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
