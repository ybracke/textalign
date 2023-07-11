from typing import Any, Dict, List, Tuple, Union

from . import util


def split_alignment_into_sentences(
    aligned_tokens: List[util.AlignedPair],
    start_idxs: List[int],
    keep_none: str = "both",  # none|a|b|both
) -> List[List[util.AlignedPair]]:
    """
    TODO

    Currently it is assumed that sentences are aligned based on `a` (TODO: allow customization)
    """

    aligned_sents = []
    i = 0
    for next_start_idx in sorted(start_idxs)[1:]:
        aligned_sent = []
        # Check whether the current index of AlginedPair.a is None or still
        # smaller than the next sentence start
        # If so: put this token alignment in the sentence and increase iterator
        while aligned_tokens[i].a is None or aligned_tokens[i].a < next_start_idx:
            aligned_sent.append(aligned_tokens[i])
            i += 1
        aligned_sents.append(aligned_sent)

    # add final sentence (i.e. remaining tokens)
    aligned_sents.append(aligned_tokens[i:])

    return aligned_sents


def split_alignment_into_sentences_OLD(
    a: List[Union[int, None]],
    b: List[Union[int, None]],
    a_tokenized_sents: List[List[Any]],
    keep_none: str = "both",  # none|a|b|both
) -> List[Dict[str, Union[int, List[Union[int, None]]]]]:
    """
    From a token alignment `a<->b` (computed with a textalign.Aligner) and a tokenized
    and sentence-split version of `a` (created with a tokenizer), create a list of dicts where each dict represents a sentence like this:

    ```python
    {
        i : int,               # sentence index
        a : List[str|None],    # list of tokens in the sentence as indices, can be None
        b : List[str|None]     # "
    }
    ```

    # TODO allow different key names than "a" and "b"
    """

    # Whether to keep or remove None tokens
    keep_none_a = True
    keep_none_b = True
    if keep_none == "a":
        keep_none_b = False
    elif keep_none == "b":
        keep_none_a = False
    elif keep_none == "none":
        keep_none_a, keep_none_b = False, False

    aligned_sents = []

    # Token counter
    tok_cnt = 0
    for i_sent, sent in enumerate(a_tokenized_sents):
        # Create an empty entry and add tokens to a and b
        entry = {"i": i_sent, "a": [], "b": []}
        # entry["a"] = [a[tok_cnt] for _ in sent]
        for _ in sent:
            tok_a = a[tok_cnt]
            if keep_none_a or tok_a is not None:
                entry["a"].append(tok_a)
            tok_b = b[tok_cnt]
            if keep_none_b or tok_b is not None:
                entry["b"].append(tok_b)
            # entry["b"].append(b[tok_cnt])
            tok_cnt += 1
        aligned_sents.append(entry)

    return aligned_sents


def extract_sentence_as_token_list(
    sent: List[Union[int, None]], doc_tok: List[Tuple[str, int, int]]
) -> List[Tuple[str, int, int]]:
    """ """
    # TODO: Deal with None tokens
    token_list = [doc_tok[i] for i in sent if i is not None]
    return token_list


def serialize_sentence_original_whitespace(sentence: List[Tuple[str, int, int]]) -> str:
    """
    A sentence is a list of triples (token, offset, length)

    The serialized sentence inserts spaces between tokens i and j
    until `offset(i)+len(i)+n(spaces) == offset(j)`
    """

    sent_serialized = sentence[0][0]
    # store offset and length of previous token + number of leading spaces
    tok_offset_prev = sentence[0][1]
    tok_len_prev = sentence[0][2]
    n_spaces = 0

    for i, (tok_text, tok_offset, tok_len) in enumerate(sentence[1:]):
        # Add spaces to sentence until offset is reached
        while tok_offset_prev + tok_len_prev + n_spaces < tok_offset:
            sent_serialized += " "
            n_spaces += 1
        # Add token to sentence
        sent_serialized += tok_text

        # Reset variables
        tok_offset_prev = tok_offset
        tok_len_prev = tok_len
        n_spaces = 0

    return sent_serialized


def serialize_sentence_alignments_OLD(
    sents_aligned_tokidxs: List[Dict[str, Union[int, List[Union[int, None]]]]],
    a_tokenized_sents: List[Tuple[str, int, int]],
    b_tokenized_sents: List[Tuple[str, int, int]],
) -> List[Dict[str, Union[int, str]]]:
    """
    From `sents_aligned_tokidxs` (created with `split_alignment_into_sentences`) create a string version of each sentence where tokens are joined based on the whitespace information included in `a_tokenized_sents` and `b_tokenized_sents`.

    Output looks like this:

    ```python
    [
        {
        i : int,    # sentence index
        a : str,    # sentence serialized as a string
        b : str     # "
        },
        ...
    ]
    ```
    """

    aligned_sents_all = []

    for sent in sents_aligned_tokidxs:
        sent_a = extract_sentence_as_token_list(sent["a"], a_tokenized_sents)
        sent_b = extract_sentence_as_token_list(sent["b"], b_tokenized_sents)
        sent_a_serialized = serialize_sentence_original_whitespace(sent_a)
        sent_b_serialized = serialize_sentence_original_whitespace(sent_b)
        aligned_sents_all.append(
            {"i": sent["i"], "a": sent_a_serialized, "b": sent_b_serialized}
        )

    return aligned_sents_all


# New on 6.7.
def serialize_sentence_alignments(
    sents_aligned_tokidxs: List[List[util.AlignedPair]],
    a_doc: List[util.Token],
    b_doc: List[util.Token],
    drop_unaligned: bool = False,
) -> List[Tuple[str, str]]:
    sents_aligned_serialized = []

    for sent in sents_aligned_tokidxs:
        str_a, str_b = "", ""
        last_idx_a, last_idx_b = -1, -1
        # Iterate over AligendPair objects in list
        for aligned_idx in sent:
            # Optional: exclude unaligned tokens (and gaps) from serialized sentence
            if drop_unaligned and ((aligned_idx.a is None) or (aligned_idx.b is None)):
                continue

            # Add token and whitespace to serialized sentence for a
            if aligned_idx.a is not None and aligned_idx.a != last_idx_a:
                # Add initial whitespace if it exists in doc
                ws = " " if a_doc[aligned_idx.a].initial_ws else ""
                str_a += ws + a_doc[aligned_idx.a].text
            # If gaps are not excluded: Add special GAP token
            elif aligned_idx.a is None:
                str_a += " " + "[GAP]"

            # Same for b
            if aligned_idx.b is not None and aligned_idx.b != last_idx_b:
                ws = " " if b_doc[aligned_idx.b].initial_ws else ""
                str_b += ws + b_doc[aligned_idx.b].text
            elif aligned_idx.b is None:
                str_b += " " + "[GAP]"

            # Move last index
            last_idx_a, last_idx_b = aligned_idx.a, aligned_idx.b

        # ~ for
        sents_aligned_serialized.append((str_a.strip(), str_b.strip()))

    # ~ for
    return sents_aligned_serialized
