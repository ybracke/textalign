# Utilities for splitting documents at positions where they match
#
# This is useful in order to then apply token-wise alignment to the parts of the
# split documents

from typing import Dict, Generator, List, Tuple
from fuzzysearch import find_near_matches

from textalign import util, translit


class DocSplitter:
    def __init__(
        self,
        tokens_a,
        tokens_b,
        max_lev_dist=7,
        subseq_len=7,
        max_len_split=2000,
        step_size=20,  # could change dynamically (increase when using it)
        apply_translit=True,
    ):
        # Texts, tokenized
        self.tokens_a: List[str] = tokens_a
        self.tokens_b: List[str] = tokens_b

        # Text B, serialized
        self.b_joined = "".join(self.tokens_b)  # TODO apply directly here or elsewhere

        # For text B: mapping of offsets to token index
        self.offset2tokidx_b: Dict[int, int] = util.get_offset2tokidx_from_strlist(
            self.tokens_b
        )  # TODO apply directly here or elsewhere
        self.offset2tokidx_b_keys: List[int] = list(
            self.offset2tokidx_b.keys()
        )

        # Parameters
        # Maximum Levenshtein distance for fuzzy search
        self.max_lev_dist: int = max_lev_dist
        # Number of tokens from text A to fuzzy search in text B
        self.subseq_len: int = subseq_len
        # Maximum split length (in tokens) for splitting the documents
        self.max_len_split: int = max_len_split
        # Step size for setting a new index during the search for a pattern_a
        self.step_size: int = step_size
        # Apply transliteration before fuzzy search
        self.apply_translit: bool = apply_translit

    def iterfind_split_positions(self) -> Generator[Tuple[int, int], None, None]:
        """
        Generates pairs (start_a, start_b) where start_a [start_b] is the index of the
        first token in tokens_a [tokens_b] that should go in the next split.

        About the index pair (start_a, start_b) we know that, starting at start_a and start_b, there is a token sequence of length `k` in both documents that aligns uniquely well with the other one.

        Use the output as follows: Create a split from
        tokens_a[prev_start_a:start_a] (and do so accordingly for tokens_b)

        TODO: What if that, for some reason this is still not the best match overall...
        """

        tokidx_a = 0
        tokidx_b = 0
        
        while tokidx_a <= len(self.tokens_a) - self.max_len_split - self.subseq_len:
            tokidx_a += self.max_len_split

            # Get the candidate token sequence from text a
            pattern_a = "".join(self.tokens_a[tokidx_a : tokidx_a + self.subseq_len])
            pattern_a = (
                translit.unidecode_ger(pattern_a) if self.apply_translit else pattern_a
            )

            # Get offsets of near matches of pattern_a in b
            near_matches = find_near_matches(
                pattern_a,
                self.b_joined[:], # TODO only look at the remaining part of b
                max_l_dist=self.max_lev_dist,
            )

            # Look for a single candidate
            while len(near_matches) != 1:
                # decrease index (look for a matching pattern earlier)
                tokidx_a -= self.step_size
                if tokidx_a < 0:
                    break
                # generate new pattern
                pattern_a = "".join(self.tokens_a[tokidx_a : tokidx_a + self.subseq_len])
                pattern_a = (
                    translit.unidecode_ger(pattern_a)
                    if self.apply_translit
                    else pattern_a
                )
                near_matches = find_near_matches(
                    pattern_a,
                    self.b_joined[:], # TODO only look at the remaining part of b
                    max_l_dist=self.max_lev_dist,
                )
            # ~ while loop ends once we have a single candidate

            # TODO: Could the while loop never end?
            # Possible if none of the pattern candidates have exactly 1 match (either always 0 or multiple)
            # Break the loop after n attemps and say: sorry, this does not work?!

            # Our matching function gave us a character offset, but we need a token index. Use the mapping to get the token index from the offset
            offset_b = near_matches[0].start
            try:
                tokidx_b = self.offset2tokidx_b[offset_b]
            # If the offset does not match with the beginning of a token in b, i.e. is located within a token, we need to take the find the closest offset
            except KeyError:
                closest_offset_b = find_closest(
                    self.offset2tokidx_b_keys, offset_b
                )
                tokidx_b = self.offset2tokidx_b[closest_offset_b]

            yield tokidx_a, tokidx_b


def find_closest(arr, target):
    """
    Find index of element closest to given target using binary search
    """

    n = len(arr)

    # Corner cases
    if target <= arr[0]:
        return arr[0]
    if target >= arr[n - 1]:
        return arr[n - 1]

    # Doing binary search
    i = 0
    j = n
    mid = 0
    while i < j:
        mid = (i + j) // 2

        if arr[mid] == target:
            return arr[mid]

        # If target is less than array
        # element, then search in left
        if target < arr[mid]:
            # If target is greater than previous
            # to mid, return closest of two
            if mid > 0 and target > arr[mid - 1]:
                return get_closest(arr[mid - 1], arr[mid], target)

            # Repeat for left half
            j = mid

        # If target is greater than mid
        else:
            if mid < n - 1 and target < arr[mid + 1]:
                return get_closest(arr[mid], arr[mid + 1], target)

            # update i
            i = mid + 1

    # Only index of single element left after search
    return arr[mid]


# Method to compare which one is the more close.
# We find the closest by taking the difference
# between the target and both values. It assumes
# that val2 is greater than val1 and target lies
# between these two.
def get_closest(val1, val2, target):
    if target - val1 >= val2 - target:
        return val2
    else:
        return val1
