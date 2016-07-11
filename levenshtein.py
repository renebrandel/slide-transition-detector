import operator

def levenshtein(fst, snd, comp=operator.eq):
    if min(len(fst), len(snd)) == 0:
        return max(len(fst), len(snd))

    deletion = levenshtein(fst[1:], snd) + 1
    insertion = levenshtein(fst, snd[1:]) + 1
    ind = 1
    if comp(fst[0], snd[0]):
        ind = 0
    substitution = levenshtein(fst[1:], snd[1:]) + ind

    return min(deletion, insertion, substitution)
