from typing import Any, Dict, List, Tuple, Union

from textalign import sentences
from textalign import util
from textalign import AlignedPair


##### 6.7.2023


def test_split_alignment_into_sentences() -> None:
    sentence_boundaries = [0, 6, 9]
    aligned_tokens: List[AlignedPair] = [
        AlignedPair(0, 0),
        AlignedPair(1, 1),
        AlignedPair(2, 2),
        AlignedPair(3, 2),
        AlignedPair(4, None),
        AlignedPair(5, 3),
        AlignedPair(6, 4),
        AlignedPair(6, 5),
        AlignedPair(7, 6),
        AlignedPair(None, 7),
        AlignedPair(8, 8),
        AlignedPair(9, 9),
    ]

    output: List[List[AlignedPair]] = sentences.split_alignment_into_sentences(
        aligned_tokens, sentence_boundaries
    )

    target: List[List[AlignedPair]] = [
        [
            AlignedPair(0, 0),
            AlignedPair(1, 1),
            AlignedPair(2, 2),
            AlignedPair(3, 2),
            AlignedPair(4, None),
            AlignedPair(5, 3),
        ],
        [
            AlignedPair(6, 4),
            AlignedPair(6, 5),
            AlignedPair(7, 6),
            AlignedPair(None, 7),
            AlignedPair(8, 8),
        ],
        [
            AlignedPair(9, 9),
        ],
    ]

    assert output == target


def test_serialize_sentence_alignments() -> None:
    # Just for me
    orig_text = "Das iſt aller Hand. Gehts noch?"
    norm_text = "Das ist allerhand. Geht es noch?"
    # Document as list of text tokens with whitespace info (no sentence split)
    doc_orig = [
        util.Token("Das", False),
        util.Token("iſt", True),
        util.Token("aller", True),
        util.Token("Hand", True),
        util.Token(".", False),
        util.Token("Gehts", True),
        util.Token("noch", True),
        util.Token("?", False),
    ]
    doc_norm = [
        util.Token("Das", False),
        util.Token("ist", True),
        util.Token("allerhand", True),
        util.Token(".", False),
        util.Token("Geht", True),
        util.Token("es", True),
        util.Token("noch", True),
        util.Token("?", False),
    ]
    # Sentence-wise alignment as list of lists of `AlignedPair`s
    sents_aligned_tokidxs = [
        [
            AlignedPair(0, 0),
            AlignedPair(1, 1),
            AlignedPair(2, 2),
            AlignedPair(3, 2),
            AlignedPair(4, 3),
        ],
        [
            AlignedPair(5, 4),
            AlignedPair(5, 5),
            AlignedPair(6, 6),
            AlignedPair(7, 7),
        ],
    ]

    serialized_sents = sentences.serialize_sentence_alignments(
        sents_aligned_tokidxs, doc_orig, doc_norm
    )

    target = [
        ("Das iſt aller Hand.", "Das ist allerhand."),
        ("Gehts noch?", "Geht es noch?"),
    ]

    assert serialized_sents == target


def test_serialize_sentence_alignments_with_unmapped_tokens_and_gaps() -> None:
    # Just for me
    orig_text = "Das iſt aller Hand. Gehts noch?"
    norm_text = "Das ist allerhand. Geht es noch?"
    # Document as list of text tokens with whitespace info (no sentence split)
    doc_orig = [
        util.Token("Das", False),
        util.Token("iſt", True),
        util.Token("aller", True),
        util.Token("Hand", True),
        util.Token("[NUR IN ORIG]", True),
        util.Token(".", False),
        util.Token("Gehts", True),
        util.Token("noch", True),
        util.Token("?", False),
    ]
    doc_norm = [
        util.Token("Das", False),
        util.Token("ist", True),
        util.Token("allerhand", True),
        util.Token(".", False),
        util.Token("Geht", True),
        util.Token("es", True),
        util.Token("noch", True),
        util.Token("[NUR IN NORM]", True),
        util.Token("?", False),
    ]
    # Sentence-wise alignment as list of lists of `AlignedPair`s
    sents_aligned_tokidxs = [
        [
            AlignedPair(0, 0),
            AlignedPair(1, 1),
            AlignedPair(2, 2),
            AlignedPair(3, 2),
            AlignedPair(4, None),
            AlignedPair(5, 3),
        ],
        [
            AlignedPair(6, 4),
            AlignedPair(6, 5),
            AlignedPair(7, 6),
            AlignedPair(None, 7),
            AlignedPair(8, 8),
        ],
    ]

    serialized_sents = sentences.serialize_sentence_alignments(
        sents_aligned_tokidxs, doc_orig, doc_norm
    )

    target = [
        ("Das iſt aller Hand [NUR IN ORIG].", "Das ist allerhand [GAP]."),
        ("Gehts noch [GAP]?", "Geht es noch [NUR IN NORM]?"),
    ]

    assert serialized_sents == target


def test_serialize_sentence_alignments_without_unmapped_tokens_and_gaps() -> None:
    # Just for me
    orig_text = "Das iſt aller Hand. Gehts noch?"
    norm_text = "Das ist allerhand. Geht es noch?"
    # Document as list of text tokens with whitespace info (no sentence split)
    doc_orig = [
        util.Token("Das", False),
        util.Token("iſt", True),
        util.Token("aller", True),
        util.Token("Hand", True),
        util.Token("[NUR IN ORIG]", True),
        util.Token(".", False),
        util.Token("Gehts", True),
        util.Token("noch", True),
        util.Token("?", False),
    ]
    doc_norm = [
        util.Token("Das", False),
        util.Token("ist", True),
        util.Token("allerhand", True),
        util.Token(".", False),
        util.Token("Geht", True),
        util.Token("es", True),
        util.Token("noch", True),
        util.Token("[NUR IN NORM]", True),
        util.Token("?", False),
    ]
    # Sentence-wise alignment as list of lists of `AlignedPair`s
    sents_aligned_tokidxs = [
        [
            AlignedPair(0, 0),
            AlignedPair(1, 1),
            AlignedPair(2, 2),
            AlignedPair(3, 2),
            AlignedPair(4, None),
            AlignedPair(5, 3),
        ],
        [
            AlignedPair(6, 4),
            AlignedPair(6, 5),
            AlignedPair(7, 6),
            AlignedPair(None, 7),
            AlignedPair(8, 8),
        ],
    ]

    serialized_sents = sentences.serialize_sentence_alignments(
        sents_aligned_tokidxs, doc_orig, doc_norm, drop_unaligned=True
    )

    target = [
        ("Das iſt aller Hand.", "Das ist allerhand."),
        ("Gehts noch?", "Geht es noch?"),
    ]

    assert serialized_sents == target


# TODO
def test_serialize_sentence_alignments_without_unmapped_tokens_but_without_gaps() -> (
    None
):
    # Just for me
    orig_text = "Das iſt aller Hand. Gehts noch?"
    norm_text = "Das ist allerhand. Geht es noch?"
    # Document as list of text tokens with whitespace info (no sentence split)
    doc_orig = [
        util.Token("Das", False),
        util.Token("iſt", True),
        util.Token("aller", True),
        util.Token("Hand", True),
        util.Token("[NUR IN ORIG]", True),
        util.Token(".", False),
        util.Token("Gehts", True),
        util.Token("noch", True),
        util.Token("?", False),
    ]
    doc_norm = [
        util.Token("Das", False),
        util.Token("ist", True),
        util.Token("allerhand", True),
        util.Token(".", False),
        util.Token("Geht", True),
        util.Token("es", True),
        util.Token("noch", True),
        util.Token("[NUR IN NORM]", True),
        util.Token("?", False),
    ]
    # Sentence-wise alignment as list of lists of `AlignedPair`s
    sents_aligned_tokidxs = [
        [
            AlignedPair(0, 0),
            AlignedPair(1, 1),
            AlignedPair(2, 2),
            AlignedPair(3, 2),
            AlignedPair(4, None),
            AlignedPair(5, 3),
        ],
        [
            AlignedPair(6, 4),
            AlignedPair(6, 5),
            AlignedPair(7, 6),
            AlignedPair(None, 7),
            AlignedPair(8, 8),
        ],
    ]

    serialized_sents = sentences.serialize_sentence_alignments(
        sents_aligned_tokidxs, doc_orig, doc_norm
    )

    target = [
        ("Das iſt aller Hand [NUR IN ORIG].", "Das ist allerhand."),
        ("Gehts noch?", "Geht es noch [NUR IN NORM]?"),
    ]

    assert serialized_sents == target


##### DEPRECATED (before 6.7.) ######


def test_split_alignment_into_sentences_trivial_case() -> None:
    orig: List[Union[int, None]] = []
    norm: List[Union[int, None]] = []
    orig_tokenized_sents: List[List[Any]] = []

    filetext_orig_waste = """Disz 
    iſt
    der 
    erſte
    Satzz
    .

    Unt
    disz
    der 
    zweyte
    ."""

    orig_tokenized_sents = [
        [tok.strip() for tok in sent.split("\n")]
        for sent in filetext_orig_waste.split("\n\n")
    ]

    orig = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    norm = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    alignment_sent_idxs = sentences.split_alignment_into_sentences(
        orig, norm, orig_tokenized_sents
    )

    target = [
        {"i": 0, "a": [0, 1, 2, 3, 4, 5], "b": [0, 1, 2, 3, 4, 5]},
        {"i": 1, "a": [6, 7, 8, 9, 10], "b": [6, 7, 8, 9, 10]},
    ]

    assert alignment_sent_idxs == target


def test_split_alignment_into_sentences_keep_none_both() -> None:
    orig: List[Union[int, None]] = []
    norm: List[Union[int, None]] = []
    orig_tokenized_sents: List[List[Any]] = []

    filetext_orig_waste = """Disz 
    iſt
    der 
    erſte
    Satzz
    .

    Unt
    disz
    der 
    zweyte
    ."""

    orig_tokenized_sents = [
        [tok.strip() for tok in sent.split("\n")]
        for sent in filetext_orig_waste.split("\n\n")
    ]

    orig = [0, 1, 2, 3, 4, 5, 6, 7, 8, None, 10]
    norm = [None, None, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    alginment_sent_idxs = sentences.split_alignment_into_sentences(
        orig, norm, orig_tokenized_sents, keep_none="both"
    )

    target = [
        {"i": 0, "a": [0, 1, 2, 3, 4, 5], "b": [None, None, 2, 3, 4, 5]},
        {"i": 1, "a": [6, 7, 8, None, 10], "b": [6, 7, 8, 9, 10]},
    ]

    assert alginment_sent_idxs == target


def test_split_alignment_into_sentences_drop_none_both() -> None:
    orig: List[Union[int, None]] = []
    norm: List[Union[int, None]] = []
    orig_tokenized_sents: List[List[Any]] = []

    filetext_orig_waste = """Disz 
    iſt
    der 
    erſte
    Satzz
    .

    Unt
    disz
    der 
    zweyte
    ."""

    orig_tokenized_sents = [
        [tok.strip() for tok in sent.split("\n")]
        for sent in filetext_orig_waste.split("\n\n")
    ]

    orig = [0, 1, 2, 3, 4, 5, 6, 7, 8, None, 10]
    norm = [None, None, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    alginment_sent_idxs = sentences.split_alignment_into_sentences(
        orig, norm, orig_tokenized_sents, keep_none="none"
    )

    target = [
        {"i": 0, "a": [0, 1, 2, 3, 4, 5], "b": [2, 3, 4, 5]},
        {"i": 1, "a": [6, 7, 8, 10], "b": [6, 7, 8, 9, 10]},
    ]

    assert alginment_sent_idxs == target


def test_split_alignment_into_sentences_keep_none_b() -> None:
    orig: List[Union[int, None]] = []
    norm: List[Union[int, None]] = []
    orig_tokenized_sents: List[List[Any]] = []

    filetext_orig_waste = """Disz 
    iſt
    der 
    erſte
    Satzz
    .

    Unt
    disz
    der 
    zweyte
    ."""

    orig_tokenized_sents = [
        [tok.strip() for tok in sent.split("\n")]
        for sent in filetext_orig_waste.split("\n\n")
    ]

    orig = [0, 1, 2, 3, 4, 5, 6, 7, 8, None, 10]
    norm = [None, None, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    alginment_sent_idxs = sentences.split_alignment_into_sentences(
        orig, norm, orig_tokenized_sents, keep_none="b"
    )

    target = [
        {"i": 0, "a": [0, 1, 2, 3, 4, 5], "b": [None, None, 2, 3, 4, 5]},
        {"i": 1, "a": [6, 7, 8, 10], "b": [6, 7, 8, 9, 10]},
    ]

    assert alginment_sent_idxs == target


def test_split_alignment_into_sentences_keep_none_a() -> None:
    orig: List[Union[int, None]] = []
    norm: List[Union[int, None]] = []
    orig_tokenized_sents: List[List[Any]] = []

    filetext_orig_waste = """Disz 
    iſt
    der 
    erſte
    Satzz
    .

    Unt
    disz
    der 
    zweyte
    ."""

    orig_tokenized_sents = [
        [tok.strip() for tok in sent.split("\n")]
        for sent in filetext_orig_waste.split("\n\n")
    ]

    orig = [0, 1, 2, 3, 4, 5, 6, 7, 8, None, 10]
    norm = [None, None, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    alginment_sent_idxs = sentences.split_alignment_into_sentences(
        orig, norm, orig_tokenized_sents, keep_none="a"
    )

    target = [
        {"i": 0, "a": [0, 1, 2, 3, 4, 5], "b": [2, 3, 4, 5]},
        {"i": 1, "a": [6, 7, 8, None, 10], "b": [6, 7, 8, 9, 10]},
    ]

    assert alginment_sent_idxs == target


# deprecated
def test_serialize_sentence_alignments_OLD_trivial_case() -> None:
    sents_aligned_tokidxs: List[Dict[str, Union[int, List[Union[int, None]]]]] = [
        {"i": 0, "a": [0, 1, 2, 3, 4, 5], "b": [0, 1, 2, 3, 4, 5]},
        {"i": 1, "a": [6, 7, 8, 9, 10], "b": [6, 7, 8, 9, 10]},
    ]

    a_tokenized: List[Tuple[str, int, int]] = [
        ("Disz", 0, 4),
        ("iſt", 5, 4),
        ("der", 10, 3),
        ("erſte", 14, 6),
        ("Satzz", 21, 5),
        (".", 26, 1),
        ("Unt", 28, 3),
        ("disz", 32, 4),
        ("der", 37, 3),
        ("zweyte", 41, 6),
        (".", 47, 1),
    ]
    b_tokenized: List[Tuple[str, int, int]] = [
        ("Das", 0, 3),
        ("ist", 4, 3),
        ("der", 8, 3),
        ("erste", 12, 5),
        ("Satz", 18, 4),
        (".", 22, 1),
        ("Und", 24, 3),
        ("das", 28, 3),
        ("der", 32, 3),
        ("zweite", 36, 6),
        (".", 42, 1),
    ]

    output = sentences.serialize_sentence_alignments(
        sents_aligned_tokidxs, a_tokenized, b_tokenized
    )

    target = [
        {"i": 0, "a": "Disz iſt der erſte Satzz.", "b": "Das ist der erste Satz."},
        {"i": 1, "a": "Unt disz der zweyte.", "b": "Und das der zweite."},
    ]

    assert output == target


# deprecated
def test_serialize_sentence_alignments_OLD_drop_none_both() -> None:
    sents_aligned_tokidxs: List[Dict[str, Union[int, List[Union[int, None]]]]] = [
        {"i": 0, "a": [0, 1, 2, 3, 4, 5], "b": [0, 1, 2, 3, 4, 5]},
        {"i": 1, "a": [6, 7, 8, 9, None, 11], "b": [6, 7, 8, 9, 10]},
    ]

    a_tokenized: List[Tuple[str, int, int]] = [
        ("Disz", 0, 4),
        ("iſt", 5, 4),
        ("der", 10, 3),
        ("erſte", 14, 6),
        ("Satzz", 21, 5),
        (".", 26, 1),
        ("Unt", 28, 3),
        ("disz", 32, 4),
        ("der", 37, 3),
        ("zweyte", 41, 6),
        ("[Seite]", 47, 7),
        (".", 54, 1),
    ]
    b_tokenized: List[Tuple[str, int, int]] = [
        ("Das", 0, 3),
        ("ist", 4, 3),
        ("der", 8, 3),
        ("erste", 12, 5),
        ("Satz", 18, 4),
        (".", 22, 1),
        ("Und", 24, 3),
        ("das", 28, 3),
        ("der", 32, 3),
        ("zweite", 36, 6),
        (".", 42, 1),
    ]

    output = sentences.serialize_sentence_alignments(
        sents_aligned_tokidxs, a_tokenized, b_tokenized
    )

    target = [
        {"i": 0, "a": "Disz iſt der erſte Satzz.", "b": "Das ist der erste Satz."},
        {"i": 1, "a": "Unt disz der zweyte.", "b": "Und das der zweite."},
    ]

    assert output == target
