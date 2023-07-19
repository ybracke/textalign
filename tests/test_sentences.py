from typing import List

from textalign import sentences
from textalign import util
from textalign import AlignedPair


def test_aligned_sentence() -> None:
    tokens_a = [
        util.Token("Das", False),
        util.Token("iſt", True),
        util.Token("aller", True),
        util.Token("Hand", True),
    ]
    tokens_b = [
        util.Token("Das", False),
        util.Token("ist", True),
        util.Token("allerhand", True),
    ]
    alignment = [
        AlignedPair(0, 0),
        AlignedPair(1, 1),
        AlignedPair(2, 2),
        AlignedPair(3, 2),
    ]
    sent_aligned = sentences.AlignedSentence(tokens_a, tokens_b, alignment)
    assert sent_aligned.tokens_a == tokens_a
    assert sent_aligned.tokens_b == tokens_b
    assert sent_aligned.alignment == alignment


def test_serialize_aligned_sentence() -> None:
    tokens_a = [
        util.Token("Das", False),
        util.Token("iſt", True),
        util.Token("aller", True),
        util.Token("Hand", True),
    ]
    tokens_b = [
        util.Token("Das", False),
        util.Token("ist", True),
        util.Token("allerhand", True),
    ]
    alignment = [
        AlignedPair(0, 0),
        AlignedPair(1, 1),
        AlignedPair(2, 2),
        AlignedPair(3, 2),
    ]
    sent_aligned = sentences.AlignedSentence(tokens_a, tokens_b, alignment)
    serialized_a, serialized_b = sent_aligned.serialize()

    target_a = "Das iſt aller Hand"
    target_b = "Das ist allerhand"
    assert serialized_a == target_a
    assert serialized_b == target_b


def test_serizalize_list_of_aligned_sentences() -> None:
    # Document with two sentences
    doc_orig = [
        [
            util.Token("Das", False),
            util.Token("iſt", True),
            util.Token("aller", True),
            util.Token("Hand", True),
            util.Token(".", False),
        ],
        [
            util.Token("Gehts", True),
            util.Token("noch", True),
            util.Token("?", False),
        ],
    ]
    doc_norm = [
        [
            util.Token("Das", False),
            util.Token("ist", True),
            util.Token("allerhand", True),
            util.Token(".", False),
        ],
        [
            util.Token("Geht", True),
            util.Token("es", True),
            util.Token("noch", True),
            util.Token("?", False),
        ],
    ]
    # Sentence-wise alignment as list of lists of `AlignedPair`s
    alignment_sents = [
        [
            AlignedPair(0, 0),
            AlignedPair(1, 1),
            AlignedPair(2, 2),
            AlignedPair(3, 2),
            AlignedPair(4, 3),
        ],
        [
            AlignedPair(0, 0),
            AlignedPair(1, 1),
            AlignedPair(1, 2),
            AlignedPair(2, 3),
        ],
    ]
    n = 2  # Number of sentences

    target_orig = ["Das iſt aller Hand.", "Gehts noch?"]
    target_norm = ["Das ist allerhand.", "Geht es noch?"]

    for i in range(n):
        sent_aligned = sentences.AlignedSentence(
            doc_orig[i], doc_norm[i], alignment_sents[i]
        )
        serialized_orig, serialized_norm = sent_aligned.serialize()
        assert serialized_orig == target_orig[i]
        assert serialized_norm == target_norm[i]


def test_get_aligned_sentences() -> None:
    sentence_start_idxs = [0, 6, 9]
    # Document-wide alignment as list of `AlignedPair`s
    doc_aligned_tokidxs = [
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
        util.Token("Ja", True),
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
        util.Token("Ja", True),
    ]

    aligned_sents = sentences.get_aligned_sentences(
        doc_aligned_tokidxs, sentence_start_idxs, doc_orig, doc_norm
    )

    # TODO
    target: List[sentences.AlignedSentence] = [
        sentences.AlignedSentence(
            tokens_a=[
                util.Token("Das", False),
                util.Token("iſt", True),
                util.Token("aller", True),
                util.Token("Hand", True),
                util.Token("[NUR IN ORIG]", True),
                util.Token(".", False),
            ],
            tokens_b=[
                util.Token("Das", False),
                util.Token("ist", True),
                util.Token("allerhand", True),
                util.Token(".", False),
            ],
            alignment=[
                AlignedPair(0, 0),
                AlignedPair(1, 1),
                AlignedPair(2, 2),
                AlignedPair(3, 2),
                AlignedPair(4, None),
                AlignedPair(5, 3),
            ],
        ),
        sentences.AlignedSentence(
            tokens_a=[
                util.Token("Gehts", True),
                util.Token("noch", True),
                util.Token("?", False),
            ],
            tokens_b=[
                util.Token("Geht", True),
                util.Token("es", True),
                util.Token("noch", True),
                util.Token("[NUR IN NORM]", True),
                util.Token("?", False),
            ],
            alignment=[
                AlignedPair(0, 0),
                AlignedPair(0, 1),
                AlignedPair(1, 2),
                AlignedPair(None, 3),
                AlignedPair(2, 4),
            ],
        ),
        sentences.AlignedSentence(
            tokens_a=[util.Token("Ja", True)],
            tokens_b=[util.Token("Ja", True)],
            alignment=[
                AlignedPair(0, 0),
            ],
        ),
    ]

    # AlignedPair(6, 4),  -> (0,0)
    # AlignedPair(6, 5),  -> (1,1)
    # AlignedPair(7, 6),  -> (1,2)
    # AlignedPair(None, 7),  (None,3)
    # AlignedPair(8, 8),  -> (2,4)

    assert aligned_sents == target


def test_let_idxs_start_at_zero() -> None:
    s_alignment = [
        AlignedPair(6, 4),
        AlignedPair(6, 5),
        AlignedPair(7, 6),
        AlignedPair(None, 7),
        AlignedPair(8, 8),
        AlignedPair(9, 9),
    ]
    end_a_prev = 5
    end_b_prev = 3
    s_alignment = sentences.let_idxs_start_at_zero(s_alignment, end_a_prev, end_b_prev)
    assert s_alignment[0].a == 0 and s_alignment[0].b == 0

    # None throws an error
    # end_a_prev = None
    # end_b_prev = 3
    # s_alignment = sentences.let_idxs_start_at_zero(s_alignment, end_a_prev, end_b_prev)
    # assert s_alignment[0].a == 0 and s_alignment[0].b == 0
