from typing import List, Tuple
from dataclasses import dataclass

from textalign import AlignedPair
from textalign import util


@dataclass
class AlignedSentence:
    tokens_a: List[util.Token]
    tokens_b: List[util.Token]
    alignment: List[AlignedPair]
    # scores: List[float]

    def __init__(self, tokens_a=[], tokens_b=[], alignment=[]):
        self.tokens_a = tokens_a
        self.tokens_b = tokens_b
        self.alignment = alignment

    def serialize(self, drop_unaligned: bool = False) -> Tuple[str, str]:
        """
        Return both sentences as strings (serialized).

        `drop_unaligned`specifies whether tokens that have no alignment to the other side get excluded from the string.
        TODO: this needs to be extended to allow exclusion of None-aligned tokens from a,b or both sides or including all and/or adding a GAP token

        """

        str_a, str_b = "", ""
        last_idx_a, last_idx_b = -1, -1
        # Iterate over AligendPair objects in list
        for aligned_idx in self.alignment:
            # Optional: exclude unaligned tokens (and gaps) from serialized sentence
            if drop_unaligned and ((aligned_idx.a is None) or (aligned_idx.b is None)):
                continue

            # Add token and whitespace to serialized sentence for a
            if aligned_idx.a is not None and aligned_idx.a != last_idx_a:
                # Check whether to add initial whitespace
                ws = " " if self.tokens_a[aligned_idx.a].initial_ws else ""
                str_a += ws + self.tokens_a[aligned_idx.a].text
            # If gaps get included: Add special GAP token
            elif aligned_idx.a is None:
                str_a += " " + "[GAP]"

            # Same for b
            if aligned_idx.b is not None and aligned_idx.b != last_idx_b:
                ws = " " if self.tokens_b[aligned_idx.b].initial_ws else ""
                str_b += ws + self.tokens_b[aligned_idx.b].text
            elif aligned_idx.b is None:
                str_b += " " + "[GAP]"

            # Move last index
            last_idx_a, last_idx_b = aligned_idx.a, aligned_idx.b

        return str_a.strip(), str_b.strip()


def get_aligned_sentences(
    aligned_tokens: List[AlignedPair],
    start_idxs: List[int],
    doc_a: List[util.Token],
    doc_b: List[util.Token],
    reset_tok_idxs: bool = True
    # keep_none: str = "both",  # none|a|b|both
) -> List[AlignedSentence]:
    """
    From a list of aligned token indices (created with Aligner), a list of
    sentence beginning indices and the lists of token strings (a and b), create
    a list of AlignedSentences.

    Sentences are aligned based on `a`.

    `reset_tok_idxs` : Whether to convert indices in sentence-wise token alignments to start at 0
    """

    aligned_sentences = []
    index_of_the_last_appended_alignment_pair = -1

    # We need the following variables, if we want to convert indices in
    # sentence-wise token alignments to start at 0
    if reset_tok_idxs:
        end_a_prev, end_b_prev = -1, -1

    for i, start_idx_a in enumerate(sorted(start_idxs)):
        # Did we reach the end of a-tokens?
        try:
            next_start_idx_a = start_idxs[i + 1]
        except IndexError:
            next_start_idx_a = len(doc_a)

        # (1) Get the a-tokens for the sentence via index
        tokens_a = doc_a[start_idx_a:next_start_idx_a]

        # (2) Get the alignment via the known a-token indices
        s_alignment = []
        # k is the index into the token alignments for the entire doc
        k = index_of_the_last_appended_alignment_pair + 1
        # Stores the current a-token's index (can become None)
        _index_a = start_idx_a
        # Only do this until we reached the end of token alignments for the entire doc
        while k < len(aligned_tokens):
            alignment_pair = aligned_tokens[k]
            _index_a = alignment_pair.a  # Get the next a-token's index

            # If we reached an a-index, where a new sentence starts, we break
            # the loop (i.e. finish building the sentence alignemnt). Since we
            # are one element to far ahead in the document alignments now, we
            # have to decrease `k` by 1, before breaking.
            if (_index_a is not None) and (_index_a >= next_start_idx_a):
                k -= 1
                break
            s_alignment.append(alignment_pair)
            k += 1
        index_of_the_last_appended_alignment_pair = k

        # (3) Get the b-tokens via the alignments
        tokens_b = get_tokens_to_alignment(doc_b, s_alignment, side="b")

        # (4) Optional: Convert indices in token alignments to start at 0
        if reset_tok_idxs:
            # Catch edge-cases: empty alignments and None in last pair
            if len(s_alignment) == 0:
                end_a, end_b = -1, -1
            else:
                # Get the highest index of the current aligned_tokidxs (not None)
                k = len(s_alignment) - 1
                end_a, end_b = None, None
                while ((end_a is None) or (end_b is None)) and (k > -1):
                    a, b = s_alignment[k]
                    if end_a is None:
                        end_a = a
                    if end_b is None:
                        end_b = b
                    # move one step away from the end of the alignment
                    k -= 1
                if end_a is None:
                    end_a = -1
                if end_b is None:
                    end_b = -1
            s_alignment = let_idxs_start_at_zero(s_alignment, end_a_prev, end_b_prev)
            # Get the last indices in the previous sentence to normalize next one
            end_a_prev = end_a
            end_b_prev = end_b

        # (5) Create sentence object and add to list
        aligned_sent = AlignedSentence(tokens_a, tokens_b, s_alignment)
        aligned_sentences.append(aligned_sent)

    return aligned_sentences


def let_idxs_start_at_zero(
    s_alignment: List[AlignedPair], end_a_prev: int, end_b_prev: int
) -> List[AlignedPair]:
    """
    Convert indices in a token alignment list to start at 0

    `end_a_prev`|`end_b_prev` will be substracted from the index given at
    a and b of the AlignedPairs in the list.
    In practice this should be values found of the final element of the previous
    sentence alignment
    """
    return [
        AlignedPair(
            a=pair.a - (end_a_prev + 1) if pair.a is not None else None,
            b=pair.b - (end_b_prev + 1) if pair.b is not None else None,
        )
        for pair in s_alignment
    ]


def get_tokens_to_alignment(
    doc: List[str], alignment: List[AlignedPair], side: str = "a"
) -> List[str]:
    """
    Returns the list of tokens from `doc` from the indices specified in

    `side` must be one of `a` or `b` to specify which side specified in the
    alignment we want
    """
    if side == "a":
        tok_indexes = [pair.a for pair in alignment]
    elif side == "b":
        tok_indexes = [pair.b for pair in alignment]
    else:
        raise ValueError(f"Unkown side: {side}, must be in {'a', 'b'}")
    # Drop doubles and None
    tok_indexes = set(tok_indexes)
    if None in tok_indexes:
        tok_indexes.remove(None)
    tok_indexes = sorted(list(tok_indexes))
    tokens = [doc[i] for i in tok_indexes]
    return tokens
