from typing import Callable, List, Optional, Union
from dataclasses import astuple, dataclass

import Levenshtein as lev
import numpy as np

from textalign.translit import unidecode_ger


def monotonic_cost(cost=1):
    return cost


def decreasing_gap_cost(current_cost: float, pointer: int, initial_cost: float = 1):
    # Did I come here via a gap? If yes: decrease gap costs by a percentage of
    # the current costs
    if pointer in [3, 4, 7]:
        current_cost -= current_cost / 100
    # if no: restore gap costs
    return initial_cost


def jaro_rescored(a: str, b: str) -> int:
    # Compute and rescore similarity
    sim = lev.jaro(a, b)
    if sim < 0.33:
        sim = -1
    elif sim < 0.66:
        sim = 0
    else:
        sim = 1
    return sim


def levdistance_normal(a: str, b: str) -> float:
    """Normalized Levenshtein distance"""
    return lev.distance(a, b) / max(len(a), len(b))


def levsim(a: str, b: str) -> float:
    return 1 - levdistance_normal(a, b)


def levsim_rescored(a: str, b: str) -> int:
    sim = levsim(a, b)
    if sim < 0.33:
        sim = -1
    # elif sim < 0.66:
    #     sim = 0
    # else:
    #     sim = 1
    return sim


def length_discount(gap_cost, token):
    # decrease gap cost for short items (len<=2)
    return gap_cost if len(token) > 2 else gap_cost / 2


@dataclass
class AlignedPair:
    """
    Pair of aligned token indices

    `a` is None if token at `b` aligns best with a gap (and vice versa)
    """

    a: Union[int, None]
    b: Union[int, None]

    def __iter__(self):
        return iter(astuple(self))


class Aligner:
    def __init__(self, tokens_a: List[str] = [], tokens_b: List[str] = []):
        """
        Class for creating alignments of two tokenized texts
        """

        # String representation of tokens
        self.tokens_a: List[str] = tokens_a
        self.tokens_b: List[str] = tokens_b
        # Modified version of tokens
        self._tokens_a: List[str]
        self._tokens_b: List[str]
        # Alignment of token indices
        # e.g. [(0,0), (1,None), (2,1), (None,2)]
        # where token at index 1 in a is aligned to a gap in b
        # and the token at index 2 in b is aligned to a gap in a
        self.aligned_tokidxs: List[AlignedPair]

    def nw_align(
        self,
        a: Optional[List[str]] = None,
        b: Optional[List[str]] = None,
        similarity_func: Callable = jaro_rescored,
        gap_cost_func: Callable = decreasing_gap_cost,
        gap_cost_length_discount: Callable = length_discount,
        gap_cost_initial: float = 0.5,
    ) -> None:
        """
        Needleman-Wunsch algorithm for global alignment
        """

        if a is None:
            a = self._tokens_a
        if b is None:
            b = self._tokens_b

        gap_cost = gap_cost_initial

        n_a = len(a)
        n_b = len(b)
        # Optimal score at each possible pair
        scores = np.zeros((n_a + 1, n_b + 1))
        scores[:, 0] = np.linspace(0, -n_a * gap_cost_initial, n_a + 1)
        scores[0, :] = np.linspace(0, -n_b * gap_cost_initial, n_b + 1)

        # Pointers to trace through an optimal aligment
        pointers = np.zeros((n_a + 1, n_b + 1))
        pointers[:, 0] = 3
        pointers[0, :] = 4

        # Temporary scores
        t = np.zeros(3)
        for i in range(n_a):
            for j in range(n_b):
                sim = similarity_func(a[i], b[j])

                # Similarity as score for moving down right in the matrix
                t[0] = scores[i, j] + sim

                # Set costs
                gap_cost_func_args = {
                    "current_cost": gap_cost,
                    "pointer": pointers[i, j],
                    "initial_cost": gap_cost_initial,
                }
                gap_cost = gap_cost_func(**gap_cost_func_args)

                # Enter best score
                # Optional: cost discount for short elements
                # i.e. penalize dropping a short token less than dropping a longer one
                if gap_cost_length_discount is not None:
                    gap_cost_1 = gap_cost_length_discount(gap_cost, a[i])
                    gap_cost_2 = gap_cost_length_discount(gap_cost, b[j])
                else:
                    gap_cost_1, gap_cost_2 = gap_cost
                t[1] = scores[i, j + 1] - gap_cost_1
                t[2] = scores[i + 1, j] - gap_cost_2
                tmax = np.max(t)
                scores[i + 1, j + 1] = tmax

                # Adjust pointer
                if t[0] == tmax:
                    pointers[i + 1, j + 1] += 2
                if t[1] == tmax:
                    pointers[i + 1, j + 1] += 3
                if t[2] == tmax:
                    pointers[i + 1, j + 1] += 4

        # Trace through an optimal alignment from bottom-right to top-left
        i = n_a
        j = n_b
        rev_a: List[Union[int, None]] = []
        rev_b: List[Union[int, None]] = []
        while i > 0 or j > 0:
            if pointers[i, j] in [2, 5, 6, 9]:
                rev_a.append(i - 1)
                rev_b.append(j - 1)
                i -= 1
                j -= 1
            elif pointers[i, j] in [3, 5, 7, 9]:
                rev_a.append(i - 1)
                rev_b.append(None)
                i -= 1
            elif pointers[i, j] in [4, 6, 7, 9]:
                rev_a.append(None)
                rev_b.append(j - 1)
                j -= 1

        # Reverse the sequences and assign to class variable
        self.aligned_tokidxs = [
            AlignedPair(a, b) for (a, b) in zip(rev_a[::-1], rev_b[::-1])
        ]

        return

    def translit_tokens(self, function: Callable = unidecode_ger) -> None:
        self._tokens_a = [function(t) for t in self.tokens_a]
        self._tokens_b = [function(t) for t in self.tokens_b]

    def clean_alignments(self) -> None:
        """
        Improves the alignments produced by the NW algorithm (`nw_align`),
        by checking for possible 1:2 alignments

        """

        aligned_tokidxs_cleaned = []
        for i in range(len(self.aligned_tokidxs)):
            # Add all alignments, where neither side is None, to cleaned alignments
            if self.aligned_tokidxs[i].b is not None:
                pair = self.aligned_tokidxs[i]

            # b is None
            else:
                # Get distances
                dist_to_prev = self.distance_to_prev(i)
                dist_to_next = self.distance_to_next(i)

                # Decide which pair to add to the cleaned alignments
                # Distance to previous token is worse
                if dist_to_prev == float("inf"):
                    #  Distance to next token is worse
                    if dist_to_next == float("inf"):
                        # nothing is better than the current alignment
                        # either add (a_i,b_i) to cleaned or remove it
                        # TODO (currently just keeping the None pair)
                        pair = self.aligned_tokidxs[i]
                    else:
                        pair = AlignedPair(
                            a=self.aligned_tokidxs[i].a,
                            b=self.aligned_tokidxs[i + 1].b,
                        )
                # Distance to previous token is better
                else:
                    #  Distance to next token is worse
                    if dist_to_next == float("inf"):
                        pair = AlignedPair(
                            a=self.aligned_tokidxs[i].a,
                            b=self.aligned_tokidxs[i - 1].b,
                        )
                    # Both distances are better - take smaller distance
                    else:
                        if dist_to_next <= dist_to_prev:
                            pair = AlignedPair(
                                a=self.aligned_tokidxs[i].a,
                                b=self.aligned_tokidxs[i + 1].b,
                            )
                        else:
                            pair = AlignedPair(
                                a=self.aligned_tokidxs[i].a,
                                b=self.aligned_tokidxs[i - 1].b,
                            )

            # append the selected pair
            aligned_tokidxs_cleaned.append(pair)

        # ~ end of for loop

        # Assign cleaned_alignments to instance variable
        self.aligned_tokidxs = aligned_tokidxs_cleaned

    def distance_to_next(self, i: int) -> float:
        """Does (a_i+a_i+1) fit to b_i+1 better than a_i+1 to b_i+1"""
        if i < len(self.aligned_tokidxs) - 1:
            # no gaps in the next token AND current a-token is not None
            if (
                None not in self.aligned_tokidxs[i + 1]
                and self.aligned_tokidxs[i].a is not None
            ):
                this_a = self._tokens_a[self.aligned_tokidxs[i].a]
                next_a = self._tokens_a[self.aligned_tokidxs[i + 1].a]
                candidate = this_a + next_a
                next_b = self._tokens_b[self.aligned_tokidxs[i + 1].b]
                dist = lev.distance(candidate, next_b)
                # Is it better than the current alignment?
                dist = levdistance_normal(candidate, next_b)
                if dist < levdistance_normal(next_a, next_b):
                    return dist

        return float("inf")

    def distance_to_prev(self, i: int) -> float:
        """Does a_i fit to b_i-1 better than a_i-1 to b_i-1"""
        if i > 0:  # not the first element
            # no gaps in the prev token AND current a-token is not None
            if (
                None not in self.aligned_tokidxs[i - 1]
                and self.aligned_tokidxs[i].a is not None
            ):
                this_a = self._tokens_a[self.aligned_tokidxs[i].a]
                prev_a = self._tokens_a[self.aligned_tokidxs[i - 1].a]
                candidate = prev_a + this_a
                prev_b = self._tokens_b[self.aligned_tokidxs[i - 1].b]
                dist = lev.distance(candidate, prev_b)
                # Is it better than the current alignment?
                dist = levdistance_normal(candidate, prev_b)
                if dist < levdistance_normal(prev_a, prev_b):
                    return dist

        return float("inf")

    def get_bidirectional_alignments(self, **kwargs) -> None:
        """
        Computes an alignment stored in `self.aligned_tokidxs` and the tokens (self.tokens_a and self.tokens_b) by applying sequence alignment followed by a two-sided refinement of the alignment.

        """
        # 0. transliterate tokens for distance metric
        self.translit_tokens(function=unidecode_ger)  # TODO customizable function

        # 1. Compute the initial 1:1 alignments
        self.nw_align(**kwargs)

        # 2. Clean alignments a->b
        self.clean_alignments()

        # Switch a and b
        tmp = [AlignedPair(a=b, b=a) for (a, b) in self.aligned_tokidxs]
        self.aligned_tokidxs = tmp
        tmp = self._tokens_a
        self._tokens_a = self._tokens_b
        self._tokens_b = tmp
        del tmp

        # 3. Clean alignments b->a
        self.clean_alignments()

        # Switch back
        tmp = [AlignedPair(a=b, b=a) for (a, b) in self.aligned_tokidxs]
        self.aligned_tokidxs = tmp
        tmp = self._tokens_a
        self._tokens_a = self._tokens_b
        self._tokens_b = tmp

        return

    # TODO Function to add the aligned pairs from another aligner to this one's
    # aligned pairs.
    # Should be used before applying clean_alignments to for the entire doc
    def append_aligned_pairs(self) -> None:
        return
