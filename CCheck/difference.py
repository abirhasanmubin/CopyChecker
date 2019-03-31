from difflib import SequenceMatcher
import difflib


def mat(self, a, b):
    m = SequenceMatcher(None, a, b)
    return m.ratio()


def rendiff(self, a, b):
    dif = difflib.HtmlDiff().make_file(a, b)
    return dif


def getresult(self, assignments):
    results = []
    for i in assignments:
        dict = {
            'student': i,
            'match': 0.0,
            'matchwith': None
        }
        ma = 0.0
        for j in assignments:
            if i == j:
                continue
            a = mat(i, j) * 100
            if(ma < a):
                dict['match'] = a
                dict['matchwith'] = j
        results.append(ma)
    return results
