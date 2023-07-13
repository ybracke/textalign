from typing import Callable, List, Union

import Levenshtein as lev
import numpy as np

from textalign.translit import unidecode_ger
from textalign import util


def monotonic_cost(cost=1):
    return cost


def decreasing_gap_cost(current_cost: float, pointer: int, initial_cost: float=1):
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


class Aligner:
    def __init__(self, tokens_a, tokens_b):
        """ """
        self.tokens_a: List[str] = tokens_a
        self.tokens_b: List[str] = tokens_b
        self._tokens_a: List[str]  # modified version of tokens
        self._tokens_b: List[str]
        self.a: List[Union[int, None]]
        self.b: List[Union[int, None]]

    def nw_align(
        self,
        x: List[str],
        y: List[str],
        similarity_func: Callable = jaro_rescored,
        gap_cost_func: Callable = decreasing_gap_cost,
        gap_cost_initial: float = 0.5,
    ) -> None:
        """
        Needleman-Wunsch algorithm
        """

        gap_cost = gap_cost_initial

        nx = len(x)
        ny = len(y)
        # Optimal score at each possible pair
        F = np.zeros((nx + 1, ny + 1))
        F[:, 0] = np.linspace(0, -nx * gap_cost_initial, nx + 1)
        F[0, :] = np.linspace(0, -ny * gap_cost_initial, ny + 1)

        # Pointers to trace through an optimal aligment
        P = np.zeros((nx + 1, ny + 1))
        P[:, 0] = 3
        P[0, :] = 4

        # Temporary scores
        t = np.zeros(3)
        for i in range(nx):
            for j in range(ny):
                sim = similarity_func(x[i], y[j])

                # Similarity as score for moving down-right in the matrix
                t[0] = F[i, j] + sim

                # Set costs
                gap_cost_func_args = {
                    "current_cost": gap_cost,
                    "pointer": P[i, j],
                    "initial_cost": gap_cost_initial,
                }
                gap_cost = gap_cost_func(**gap_cost_func_args)

                # Enter best score
                t[1] = F[i, j + 1] - gap_cost
                t[2] = F[i + 1, j] - gap_cost
                tmax = np.max(t)
                F[i + 1, j + 1] = tmax

                # Adjust pointer
                if t[0] == tmax:
                    P[i + 1, j + 1] += 2
                if t[1] == tmax:
                    P[i + 1, j + 1] += 3
                if t[2] == tmax:
                    P[i + 1, j + 1] += 4

        # Trace through an optimal alignment from bottom-right to top-left
        i = nx
        j = ny
        rx : List[Union[int, None]] = []
        ry : List[Union[int, None]] = []
        while i > 0 or j > 0:
            if P[i, j] in [2, 5, 6, 9]:
                rx.append(i - 1)
                ry.append(j - 1)
                i -= 1
                j -= 1
            elif P[i, j] in [3, 5, 7, 9]:
                rx.append(i - 1)
                ry.append(None)
                i -= 1
            elif P[i, j] in [4, 6, 7, 9]:
                rx.append(None)
                ry.append(j - 1)
                j -= 1

        # Reverse the sequences
        rx = rx[::-1]
        ry = ry[::-1]

        # assign to class variables
        self.a = rx
        self.b = ry

        # return rx, ry

    def translit_tokens(self, function: Callable = unidecode_ger) -> None:
        self._tokens_a = [function(t) for t in self.tokens_a]
        self._tokens_b = [function(t) for t in self.tokens_b]

    def clean_alignments(self) -> List[Union[int,None]]:
        """
        TODO
        """

        cleaned_alignments = []
        for i in range(len(self.a)):
            # Add all alignments, where neither side is None, to cleaned alignments
            if self.b[i] is not None:
                cleaned_alignments.append((self.a[i], self.b[i]))
                continue

            # b[i] is None
            # Get distances
            dist_to_prev = self.distance_to_prev(i)
            dist_to_next = self.distance_to_next(i)

            # Decide which pair to add to the cleaned alignments
            if dist_to_prev == float("inf"):
                if dist_to_next == float("inf"):
                    # nothing is better than the current alignement
                    # either add (a_i,b_i) to cleaned or remove it
                    # TODO (currently just keeping the None pair)
                    cleaned_alignments.append((self.a[i], self.b[i]))
                    pass
                else:
                    cleaned_alignments.append((self.a[i], self.b[i + 1]))
            else:
                if dist_to_next == float("inf"):
                    cleaned_alignments.append((self.a[i], self.b[i - 1]))
                # neither distance is None - take smaller distance
                else:
                    if dist_to_next <= dist_to_prev:
                        try:
                            cleaned_alignments.append((self.a[i], self.b[i + 1]))
                        # FIXME
                        except IndexError:
                            print(dist_to_next, dist_to_prev)
                            print(i)
                            print(self.a[i], self.b[i])
                    else:
                        cleaned_alignments.append((self.a[i], self.b[i - 1]))

        # assign cleaned_alignments to a and b
        (self.a, self.b) = zip(*cleaned_alignments)
        self.a = list(self.a)
        self.b = list(self.b)
        # print(self.a[:10])
        # import sys; sys.exit()

        return cleaned_alignments

    def distance_to_next(self, i: int) -> float:
        """Does a_i fit to b_i+1 better than a_i+1 to b_i+1"""
        if i < len(self.b) - 1:  # not the last element
            if self.b[i + 1] is not None:
                if self.a[i + 1] is not None:
                    this = self.a[i]
                    next = self.a[i + 1] 
                    if this is not None and next is not None:
                        candidate = (
                            self._tokens_a[this] + self._tokens_a[next]
                        )
                        # candidate = (
                        #     self._tokens_a[self.a[i]] + self._tokens_a[self.a[i + 1]]
                        # )
                        dist = lev.distance(candidate, self._tokens_b[self.b[i + 1]])
                        # is it better than the current alignment?
                        # TODO: should the distance be normalized? by what token?
                        if dist < lev.distance(
                            self._tokens_a[self.a[i + 1]], self._tokens_b[self.b[i + 1]]
                        ):
                            return dist
        return float("inf")


    def distance_to_next_old(self, i: int) -> float:
        """Does a_i fit to b_i+1 better than a_i+1 to b_i+1"""
        if i < len(self.b) - 1:  # not the last element
            if self.b[i + 1] is not None:
                if self.a[i + 1] is not None:
                    candidate = (
                        self._tokens_a[self.a[i]] + self._tokens_a[self.a[i + 1]]
                    )
                    # candidate = (
                    #     self._tokens_a[self.a[i]] + self._tokens_a[self.a[i + 1]]
                    # )
                    dist = lev.distance(candidate, self._tokens_b[self.b[i + 1]])
                    # is it better than the current alignment?
                    # TODO: should the distance be normalized? by what token?
                    if dist < lev.distance(
                        self._tokens_a[self.a[i + 1]], self._tokens_b[self.b[i + 1]]
                    ):
                        return dist
        return float("inf")


    def distance_to_prev(self, i: int) -> float:
        """Does a_i fit to b_i-1 better than a_i-1 to b_i-1"""
        if i > 0:  # not the first element
            if self.b[i - 1] is not None:
                if self.a[i - 1] is not None:
                    candidate = (
                        self._tokens_a[self.a[i - 1]] + self._tokens_a[self.a[i]]
                    )
                    dist = lev.distance(candidate, self._tokens_b[self.b[i - 1]])
                    # is it better than the current alignment?
                    # TODO: should the distance be normalized? by what token?
                    if dist < lev.distance(
                        self._tokens_a[self.a[i - 1]], self._tokens_b[self.b[i - 1]]
                    ):
                        return dist
        return float("inf")

    def get_bidirectional_alignments(self, **kwargs) -> None:
        """
        Computes an alignment stored in (self.a, self.b) and the tokens (self.tokens_a and self.tokens_b) by applying sequence alignment followed by a two-sided refinement of the alignment.

        """
        # 0. transliterate tokens for distance metric
        self.translit_tokens(function=unidecode_ger)  # TODO customizable function

        # 1. Compute the initial 1:1 alignments
        self.nw_align(self._tokens_a, self._tokens_b, **kwargs)

        assert len(self.a) == len(self.b)

        # 2. Clean alignments a->b
        self.clean_alignments()

        assert len(self.a) == len(self.b)

        # Switch a and b
        tmp = self.a
        self.a = self.b
        self.b = tmp
        tmp = self._tokens_a
        self._tokens_a = self._tokens_b
        self._tokens_b = tmp
        del tmp

        # 3. Clean alignments b->a
        self.clean_alignments()

        assert len(self.a) == len(self.b)

        # Switch back
        tmp = self.a
        self.a = self.b
        self.b = tmp
        tmp = self._tokens_a
        self._tokens_a = self._tokens_b
        self._tokens_b = tmp
        del tmp

        return

    # TODO
    # Übergangslösung bis das alignment gleich als List[AlignedPair] erstellt wird
    def get_aligned_pairs(self) -> List[util.AlignedPair]:
        aligned_pairs = [util.AlignedPair(a, b) for (a, b) in zip(self.a, self.b)]
        return aligned_pairs

    # TODO Function to add the aligned pairs from another aligner to this one's
    # aligned pairs.
    # Should be used before applying clean_alignments to for the entire doc
    def append_aligned_pairs(self) -> None:
        return
