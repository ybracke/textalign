from typing import List, Union, Tuple
import Levenshtein as lev
import numpy as np


class Aligner:
    def __init__(self, tokens_a, tokens_b, tok_alignments=None):
        self.tokens_a: List[str] = tokens_a
        self.tokens_b: List[str] = tokens_b
        # self.tok_alignments : List[Tuple[Union[int,None],Union[int,None]]] = tok_alignments
        # self.a, self.b = zip(*self.tok_alignments) # part 1 and 2 of tok_alignments # : List[Union[int,None]]
        self.a: List[Union[int, None]]
        self.b: List[Union[int, None]]

    def nw_align(self, x, y, gap=1):
        gap_orig = gap

        nx = len(x)
        ny = len(y)
        # Optimal score at each possible pair of characters
        F = np.zeros((nx + 1, ny + 1))
        F[:, 0] = np.linspace(0, -nx * gap, nx + 1)
        F[0, :] = np.linspace(0, -ny * gap, ny + 1)

        # Pointers to trace through an optimal aligment
        P = np.zeros((nx + 1, ny + 1))
        P[:, 0] = 3
        P[0, :] = 4

        # Temporary scores
        t = np.zeros(3)
        for i in range(nx):
            for j in range(ny):
                sim = lev.jaro(x[i], y[j])

                if sim < 0.33:
                    sim = -1
                elif sim < 0.66:
                    sim = 0
                else:
                    sim = 1

                t[0] = F[i, j] + sim

                # Set costs
                # Did I come here via a gap? If yes: decrease gap costs by a # percentage of the current costs
                if P[i, j] in [3, 4, 7]:
                    gap -= gap / 100
                # if no: restore gap costs
                else:
                    gap = gap_orig

                t[1] = F[i, j + 1] - gap
                t[2] = F[i + 1, j] - gap
                tmax = np.max(t)
                F[i + 1, j + 1] = tmax
                # Pointers anpassen
                if t[0] == tmax:
                    P[i + 1, j + 1] += 2
                if t[1] == tmax:
                    P[i + 1, j + 1] += 3
                if t[2] == tmax:
                    P[i + 1, j + 1] += 4

        # Trace through an optimal alignment
        i = nx
        j = ny
        rx = []
        ry = []
        while i > 0 or j > 0:
            if P[i, j] in [2, 5, 6, 9]:
                # rx.append(x[i-1])
                rx.append(i - 1)
                # ry.append(y[j-1])
                ry.append(j - 1)
                i -= 1
                j -= 1
            elif P[i, j] in [3, 5, 7, 9]:
                # rx.append(x[i-1])
                rx.append(i - 1)
                ry.append(None)
                i -= 1
            elif P[i, j] in [4, 6, 7, 9]:
                rx.append(None)
                # ry.append(y[j-1])
                ry.append(j - 1)
                j -= 1

        # Reverse the sequences
        rx = rx[::-1]
        ry = ry[::-1]

        # assign to class variables
        self.a = rx
        self.b = ry

        return rx, ry

    def clean_alignments(self):
        """TODO"""
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

    def distance_to_next(self, i):
        """Does a_i fit to b_i+1 better than a_i+1 to b_i+1"""
        if i < len(self.b) - 1:  # not the last element
            if self.b[i + 1] is not None:
                if self.a[i + 1] is not None:
                    # TODO
                    # hier noch ein if, ob wir a oder b korrigieren
                    # aktuell b
                    # wenn a, müsste alles umgekehrt sein

                    candidate = self.tokens_a[self.a[i]] + self.tokens_a[self.a[i + 1]]
                    dist = lev.distance(candidate, self.tokens_b[self.b[i + 1]])
                    # is it better than the current alignment?
                    # TODO: should the distance be normalized? by what token?
                    if dist < lev.distance(
                        self.tokens_a[self.a[i + 1]], self.tokens_b[self.b[i + 1]]
                    ):
                        return dist
        return float("inf")

    def distance_to_prev(self, i):
        """Does a_i fit to b_i-1 better than a_i-1 to b_i-1"""
        if i > 0:  # not the first element
            if self.b[i - 1] is not None:
                if self.a[i - 1] is not None:
                    # TODO
                    # hier noch ein if, ob wir a oder b korrigieren
                    # aktuell b
                    # wenn a, müsste alles umgekehrt sein

                    candidate = self.tokens_a[self.a[i - 1]] + self.tokens_a[self.a[i]]
                    dist = lev.distance(candidate, self.tokens_b[self.b[i - 1]])
                    # is it better than the current alignment?
                    # TODO: should the distance be normalized? by what token?
                    if dist < lev.distance(
                        self.tokens_a[self.a[i - 1]], self.tokens_b[self.b[i - 1]]
                    ):
                        return dist
        return float("inf")

    def do_all(self):
        # 1. Compute the initial 1:1 alignments
        self.nw_align(self.tokens_a, self.tokens_b)

        assert len(self.a) == len(self.b)

        # 2. Clean alignments a->b
        self.clean_alignments()

        assert len(self.a) == len(self.b)

        # Switch a and b
        tmp = self.a
        self.a = self.b
        self.b = tmp
        tmp = self.tokens_a
        self.tokens_a = self.tokens_b
        self.tokens_b = tmp
        del tmp

        # 3. Clean alignments b->a
        self.clean_alignments()

        assert len(self.a) == len(self.b)

        # Switch back
        tmp = self.a
        self.a = self.b
        self.b = tmp
        tmp = self.tokens_a
        self.tokens_a = self.tokens_b
        self.tokens_b = tmp
        del tmp

    # deprecated
    def _should_next_a_also_be_mapped_to_b(self, i) -> bool:
        """
        Checks whether multiple tokens from `tokens_a`, following index `idx_a = tok_alignments[i][0]` should be mapped to the same token from tokens_b (at position `idx_b = tok_alignments[i][1]`)

        We use edit distance to check this: Is the edit distance of (token_a(i)+token_a(i+1)+... and token_b(j) lower than that of only token_a(i) and token_b(j).

        i : int
            points to current pair in self.tok_alignments

        # TODO
        a : int; options={0,1}, default=0
            which side of the pair are we looking at, i.e. which one is token_a and which one token_b

        ------------------------------------------------------------------

        Background:

        Our initial alignment algorithm maps tokens 1:1 where a token can also be a pseudo-token (None). Therefore, we likely need post-correction to catch cases where tokens are split or joined in either of the columns.

        -------------------------------------------------------------------

        TODO:

        currently this function only works for side a, but when everything works out, it should be easy to swap it

        this function is not super-helpful yet
        it shouldn't return a bool but tell you directly which modifications to make in tok_alignments_cleaned
        it might be reasonable to the token directly

        This function is supposed to be called when iterating over the alignment pairs to find possible cases of joining.

        Note: A join on the one side is a merge on the other.

        """

        idx_a, idx_b = self.tok_alignments[i]
        a = 0
        b = 1
        tokens_a = self.tokens_a
        tokens_b = self.tokens_b

        # Don't continue if the current b_token is a None token
        if idx_b is None:
            return False

        n = len(self.tok_alignments)
        j = i + 1
        # Don't continue if we already reached the end of the mapping
        if j == n:
            return False
        # Only continue if the next b_token is a None-token
        if self.tok_alignments[j][b] is not None:
            return False

        # Move until we see a b_token_idx that is not None anymore
        n = len(self.tok_alignments)
        while j < n - 1:
            j += 1
            if self.tok_alignments[j][b] is not None:
                break

        # end := First a_token_idx where b_token_idx is not None anymore
        end = self.tok_alignments[j][a]

        # Join all a_tokens between the two points
        joined_tokens = "".join(tokens_a[idx_a:end])

        # Compute edit distances
        ld_single = lev.distance(
            tokens_a[idx_a], tokens_b[idx_b]
        )  # TODO LD muss normalisiert sein
        ld_joined = lev.distance(
            joined_tokens, tokens_b[idx_b]
        )  # TODO LD muss normalisiert sein
        if ld_joined < ld_single:
            print(joined_tokens)
            return True
        return False

    # deprecated
    def clean_alignments_old(self, both_sides=True):
        """ """

        cleaned_alignments: List[Tuple[Union[int, None], Union[int, None]]] = []

        for i, (idx_a, idx_b) in enumerate(self.tok_alignments):
            # idx_a point to elements in self.tokens_a, e.g. the first token in
            # self.tokens_a is pointed to by idx_a=0
            if self._joinable_with_next(i):
                pass

        return cleaned_alignments
