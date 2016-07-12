import operator
import pandas

from ui import ProgressController as pc
from multiprocessing import Process


def levenshtein(fst, snd, comp=operator.eq):
    # type: (Sized, Sized, callable) -> int
    if min(len(fst), len(snd)) == 0:
        return max(len(fst), len(snd))
    
    ind = 1
    if comp(fst[0], snd[0]):
        ind = 0

    deletion = levenshtein(fst[1:], snd, comp) + 1
    insertion = levenshtein(fst, snd[1:], comp) + 1
    substitution = levenshtein(fst[1:], snd[1:], comp) + ind

    return min(deletion, insertion, substitution)

def ls(s, t, comp=operator.eq):
    """
        iterative_levenshtein(s, t) -> ldist
        ldist is the Levenshtein distance between the strings
        s and t.
        For all i and j, dist[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    rows = len(s) + 1
    cols = len(t) + 1
    dist = [[0 for x in range(cols)] for x in range(rows)]
    # source prefixes can be transformed into empty strings
    # by deletions:
    for i in range(1, rows):
        dist[i][0] = i
    # target prefixes can be created from an empty source string
    # by inserting the characters
    for i in range(1, cols):
        dist[0][i] = i

    progress = pc("calculating Distance", rows * cols)
    progress.start()
    for col in range(1, cols):
        for row in range(1, rows):
            progress.increment()
            if comp(s[row - 1],t[col - 1]):
                cost = 0
            else:
                cost = 1
            dist[row][col] = min(dist[row - 1][col] + 1,  # deletion
                                 dist[row][col - 1] + 1,  # insertion
                                 dist[row - 1][col - 1] + cost)  # substitution
    # pandas.DataFrame(dist).to_csv("results")
    progress.finish()
    return dist[rows - 1][cols - 1]
