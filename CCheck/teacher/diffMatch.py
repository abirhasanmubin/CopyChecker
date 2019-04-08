# Based on Neil Frasers Diff Strategies

import urllib.parse
import time
import sys
import re


class diff_match:

    def __init__(self):

        self.Diff_Timeout = 1.0

        self.Diff_EditCost = 4

        self.Match_Threshold = 0.5

        self.Match_Distance = 1000

        self.Match_MaxBits = 32

    DIFF_DELETE = -1
    DIFF_INSERT = 1
    DIFF_EQUAL = 0

    def diff_main(self, text1, text2, checklines=True, deadline=None):

        if deadline == None:

            if self.Diff_Timeout <= 0:
                deadline = sys.maxsize
            else:
                deadline = time.time() + self.Diff_Timeout

        # Null Checking
        if text1 == None or text2 == None:
            raise ValueError("Null inputs. (diff_main)")

        # Equality Checking
        if text1 == text2:
            if text1:
                return [(self.DIFF_EQUAL, text1)]
            return []

        # Trimming Common Prefix
        commonlength = self.diff_commonPrefix(text1, text2)
        commonprefix = text1[:commonlength]
        text1 = text1[commonlength:]
        text2 = text2[commonlength:]

        # Trimming Common Suffix
        commonlength = self.diff_commonSuffix(text1, text2)
        if commonlength == 0:
            commonsuffix = ''
        else:
            commonsuffix = text1[-commonlength:]
            text1 = text1[:-commonlength]
            text2 = text2[:-commonlength]

        # Compute the diff on the middle block.
        diffs = self.diff_compute(text1, text2, checklines, deadline)

        # Restore the prefix and suffix.
        if commonprefix:
            diffs[:0] = [(self.DIFF_EQUAL, commonprefix)]
        if commonsuffix:
            diffs.append((self.DIFF_EQUAL, commonsuffix))
        self.diff_cleanupMerge(diffs)
        return diffs

    def diff_compute(self, text1, text2, checklines, deadline):

        if not text1:
            # Adding text2
            return [(self.DIFF_INSERT, text2)]

        if not text2:
            # Deleting text1
            return [(self.DIFF_DELETE, text1)]

        if len(text1) > len(text2):
            (longtext, shorttext) = (text1, text2)
        else:
            (shorttext, longtext) = (text1, text2)
        i = longtext.find(shorttext)
        if i != -1:

            diffs = [(self.DIFF_INSERT, longtext[:i]), (self.DIFF_EQUAL, shorttext),
                     (self.DIFF_INSERT, longtext[i + len(shorttext):])]

            if len(text1) > len(text2):
                diffs[0] = (self.DIFF_DELETE, diffs[0][1])
                diffs[2] = (self.DIFF_DELETE, diffs[2][1])
            return diffs

        if len(shorttext) == 1:

            return [(self.DIFF_DELETE, text1), (self.DIFF_INSERT, text2)]

        # Check to see if the problem can be split in two.
        hm = self.diff_halfMatch(text1, text2)
        if hm:

            (text1_a, text1_b, text2_a, text2_b, mid_common) = hm

            diffs_a = self.diff_main(text1_a, text2_a, checklines, deadline)
            diffs_b = self.diff_main(text1_b, text2_b, checklines, deadline)

            return diffs_a + [(self.DIFF_EQUAL, mid_common)] + diffs_b

        if checklines and len(text1) > 100 and len(text2) > 100:
            return self.diff_lineMode(text1, text2, deadline)

        return self.diff_bisect(text1, text2, deadline)

    def diff_lineMode(self, text1, text2, deadline):

        (text1, text2, linearray) = self.diff_linesToChars(text1, text2)

        diffs = self.diff_main(text1, text2, False, deadline)

        self.diff_charsToLines(diffs, linearray)

        self.diff_cleanupSemantic(diffs)

        diffs.append((self.DIFF_EQUAL, ''))
        pointer = 0
        count_delete = 0
        count_insert = 0
        text_delete = ''
        text_insert = ''
        while pointer < len(diffs):
            if diffs[pointer][0] == self.DIFF_INSERT:
                count_insert += 1
                text_insert += diffs[pointer][1]
            elif diffs[pointer][0] == self.DIFF_DELETE:
                count_delete += 1
                text_delete += diffs[pointer][1]
            elif diffs[pointer][0] == self.DIFF_EQUAL:

                if count_delete >= 1 and count_insert >= 1:

                    subDiff = self.diff_main(
                        text_delete, text_insert, False, deadline)
                    diffs[pointer - count_delete -
                          count_insert: pointer] = subDiff
                    pointer = pointer - count_delete - \
                        count_insert + len(subDiff)
                count_insert = 0
                count_delete = 0
                text_delete = ''
                text_insert = ''

            pointer += 1

        diffs.pop()

        return diffs

    def diff_bisect(self, text1, text2, deadline):

        text1_length = len(text1)
        text2_length = len(text2)
        max_d = (text1_length + text2_length + 1) // 2
        v_offset = max_d
        v_length = 2 * max_d
        v1 = [-1] * v_length
        v1[v_offset + 1] = 0
        v2 = v1[:]
        delta = text1_length - text2_length

        front = (delta % 2 != 0)

        k1start = 0
        k1end = 0
        k2start = 0
        k2end = 0
        for d in range(max_d):
            # If deadline quit
            if time.time() > deadline:
                break

            for k1 in range(-d + k1start, d + 1 - k1end, 2):
                k1_offset = v_offset + k1
                if k1 == -d or (k1 != d
                                and v1[k1_offset - 1] < v1[k1_offset + 1]):
                    x1 = v1[k1_offset + 1]
                else:
                    x1 = v1[k1_offset - 1] + 1
                y1 = x1 - k1
                while (x1 < text1_length and y1 < text2_length
                       and text1[x1] == text2[y1]):
                    x1 += 1
                    y1 += 1
                v1[k1_offset] = x1
                if x1 > text1_length:

                    k1end += 2
                elif y1 > text2_length:

                    k1start += 2
                elif front:
                    k2_offset = v_offset + delta - k1
                    if k2_offset >= 0 and k2_offset < v_length and v2[k2_offset] != -1:

                        x2 = text1_length - v2[k2_offset]
                        if x1 >= x2:

                            return self.diff_bisectSplit(text1, text2, x1, y1, deadline)

            for k2 in range(-d + k2start, d + 1 - k2end, 2):
                k2_offset = v_offset + k2
                if k2 == -d or (k2 != d
                                and v2[k2_offset - 1] < v2[k2_offset + 1]):
                    x2 = v2[k2_offset + 1]
                else:
                    x2 = v2[k2_offset - 1] + 1
                y2 = x2 - k2
                while (x2 < text1_length and y2 < text2_length
                       and text1[-x2 - 1] == text2[-y2 - 1]):
                    x2 += 1
                    y2 += 1
                v2[k2_offset] = x2
                if x2 > text1_length:

                    k2end += 2
                elif y2 > text2_length:

                    k2start += 2
                elif not front:
                    k1_offset = v_offset + delta - k2
                    if k1_offset >= 0 and k1_offset < v_length and v1[k1_offset] != -1:
                        x1 = v1[k1_offset]
                        y1 = v_offset + x1 - k1_offset

                        x2 = text1_length - x2
                        if x1 >= x2:

                            return self.diff_bisectSplit(text1, text2, x1, y1, deadline)

        return [(self.DIFF_DELETE, text1), (self.DIFF_INSERT, text2)]

    def diff_bisectSplit(self, text1, text2, x, y, deadline):

        text1a = text1[:x]
        text2a = text2[:y]
        text1b = text1[x:]
        text2b = text2[y:]

        diffs = self.diff_main(text1a, text2a, False, deadline)
        diffsb = self.diff_main(text1b, text2b, False, deadline)

        return diffs + diffsb

    def diff_linesToChars(self, text1, text2):

        lineArray = []
        lineHash = {}

        lineArray.append('')

        def diff_linesToCharsMunge(text):

            chars = []

            lineStart = 0
            lineEnd = -1
            while lineEnd < len(text) - 1:
                lineEnd = text.find('\n', lineStart)
                if lineEnd == -1:
                    lineEnd = len(text) - 1
                line = text[lineStart:lineEnd + 1]

                if line in lineHash:
                    chars.append(chr(lineHash[line]))
                else:
                    if len(lineArray) == maxLines:

                        line = text[lineStart:]
                        lineEnd = len(text)
                    lineArray.append(line)
                    lineHash[line] = len(lineArray) - 1
                    chars.append(chr(len(lineArray) - 1))
                lineStart = lineEnd + 1
            return "".join(chars)

        maxLines = 666666
        chars1 = diff_linesToCharsMunge(text1)
        maxLines = 1114111
        chars2 = diff_linesToCharsMunge(text2)
        return (chars1, chars2, lineArray)

    def diff_charsToLines(self, diffs, lineArray):

        for i in range(len(diffs)):
            text = []
            for char in diffs[i][1]:
                text.append(lineArray[ord(char)])
            diffs[i] = (diffs[i][0], "".join(text))

    def diff_commonPrefix(self, text1, text2):

        if not text1 or not text2 or text1[0] != text2[0]:
            return 0

        pointermin = 0
        pointermax = min(len(text1), len(text2))
        pointermid = pointermax
        pointerstart = 0
        while pointermin < pointermid:
            if text1[pointerstart:pointermid] == text2[pointerstart:pointermid]:
                pointermin = pointermid
                pointerstart = pointermin
            else:
                pointermax = pointermid
            pointermid = (pointermax - pointermin) // 2 + pointermin
        return pointermid

    def diff_commonSuffix(self, text1, text2):

        if not text1 or not text2 or text1[-1] != text2[-1]:
            return 0

        pointermin = 0
        pointermax = min(len(text1), len(text2))
        pointermid = pointermax
        pointerend = 0
        while pointermin < pointermid:
            if (text1[-pointermid:len(text1) - pointerend]
                    == text2[-pointermid:len(text2) - pointerend]):
                pointermin = pointermid
                pointerend = pointermin
            else:
                pointermax = pointermid
            pointermid = (pointermax - pointermin) // 2 + pointermin
        return pointermid

    def diff_commonOverlap(self, text1, text2):

        text1_length = len(text1)
        text2_length = len(text2)

        if text1_length == 0 or text2_length == 0:
            return 0

        if text1_length > text2_length:
            text1 = text1[-text2_length:]
        elif text1_length < text2_length:
            text2 = text2[:text1_length]
        text_length = min(text1_length, text2_length)

        if text1 == text2:
            return text_length

        best = 0
        length = 1
        while True:
            pattern = text1[-length:]
            found = text2.find(pattern)
            if found == -1:
                return best
            length += found
            if found == 0 or text1[-length:] == text2[:length]:
                best = length
                length += 1

    def diff_halfMatch(self, text1, text2):

        if self.Diff_Timeout <= 0:

            return None
        if len(text1) > len(text2):
            (longtext, shorttext) = (text1, text2)
        else:
            (shorttext, longtext) = (text1, text2)
        if len(longtext) < 4 or len(shorttext) * 2 < len(longtext):
            return None

        def diff_halfMatchI(longtext, shorttext, i):

            seed = longtext[i:i + len(longtext) // 4]
            best_common = ''
            j = shorttext.find(seed)
            while j != -1:
                prefixLength = self.diff_commonPrefix(
                    longtext[i:], shorttext[j:])
                suffixLength = self.diff_commonSuffix(
                    longtext[:i], shorttext[:j])
                if len(best_common) < suffixLength + prefixLength:
                    best_common = (shorttext[j - suffixLength:j]
                                   + shorttext[j:j + prefixLength])
                    best_longtext_a = longtext[:i - suffixLength]
                    best_longtext_b = longtext[i + prefixLength:]
                    best_shorttext_a = shorttext[:j - suffixLength]
                    best_shorttext_b = shorttext[j + prefixLength:]
                j = shorttext.find(seed, j + 1)

            if len(best_common) * 2 >= len(longtext):
                return (best_longtext_a, best_longtext_b,
                        best_shorttext_a, best_shorttext_b, best_common)
            else:
                return None

        hm1 = diff_halfMatchI(longtext, shorttext, (len(longtext) + 3) // 4)

        hm2 = diff_halfMatchI(longtext, shorttext, (len(longtext) + 1) // 2)
        if not hm1 and not hm2:
            return None
        elif not hm2:
            hm = hm1
        elif not hm1:
            hm = hm2
        else:

            if len(hm1[4]) > len(hm2[4]):
                hm = hm1
            else:
                hm = hm2

        if len(text1) > len(text2):
            (text1_a, text1_b, text2_a, text2_b, mid_common) = hm
        else:
            (text2_a, text2_b, text1_a, text1_b, mid_common) = hm
        return (text1_a, text1_b, text2_a, text2_b, mid_common)

    def diff_cleanupSemantic(self, diffs):

        changes = False
        equalities = []
        lastEquality = None
        pointer = 0

        length_insertions1, length_deletions1 = 0, 0

        length_insertions2, length_deletions2 = 0, 0
        while pointer < len(diffs):
            if diffs[pointer][0] == self.DIFF_EQUAL:
                equalities.append(pointer)
                length_insertions1, length_insertions2 = length_insertions2, 0
                length_deletions1, length_deletions2 = length_deletions2, 0
                lastEquality = diffs[pointer][1]
            else:
                if diffs[pointer][0] == self.DIFF_INSERT:
                    length_insertions2 += len(diffs[pointer][1])
                else:
                    length_deletions2 += len(diffs[pointer][1])

                if (lastEquality and (len(lastEquality)
                                      <= max(length_insertions1, length_deletions1)) and
                        (len(lastEquality) <= max(length_insertions2, length_deletions2))):

                    diffs.insert(equalities[-1],
                                 (self.DIFF_DELETE, lastEquality))

                    diffs[equalities[-1] + 1] = (self.DIFF_INSERT,
                                                 diffs[equalities[-1] + 1][1])

                    equalities.pop()

                    if len(equalities):
                        equalities.pop()
                    if len(equalities):
                        pointer = equalities[-1]
                    else:
                        pointer = -1

                    length_insertions1, length_deletions1 = 0, 0
                    length_insertions2, length_deletions2 = 0, 0
                    lastEquality = None
                    changes = True
            pointer += 1

        if changes:
            self.diff_cleanupMerge(diffs)
        self.diff_cleanupSemanticLossless(diffs)

        pointer = 1
        while pointer < len(diffs):
            if (diffs[pointer - 1][0] == self.DIFF_DELETE
                    and diffs[pointer][0] == self.DIFF_INSERT):
                deletion = diffs[pointer - 1][1]
                insertion = diffs[pointer][1]
                overlap_length1 = self.diff_commonOverlap(deletion, insertion)
                overlap_length2 = self.diff_commonOverlap(insertion, deletion)
                if overlap_length1 >= overlap_length2:
                    if (overlap_length1 >= len(deletion) / 2.0
                            or overlap_length1 >= len(insertion) / 2.0):

                        diffs.insert(pointer, (self.DIFF_EQUAL,
                                               insertion[:overlap_length1]))
                        diffs[pointer - 1] = (self.DIFF_DELETE,
                                              deletion[:len(deletion) - overlap_length1])
                        diffs[pointer + 1] = (self.DIFF_INSERT,
                                              insertion[overlap_length1:])
                        pointer += 1
                else:
                    if (overlap_length2 >= len(deletion) / 2.0
                            or overlap_length2 >= len(insertion) / 2.0):

                        diffs.insert(pointer, (self.DIFF_EQUAL,
                                               deletion[:overlap_length2]))
                        diffs[pointer - 1] = (self.DIFF_INSERT,
                                              insertion[:len(insertion) - overlap_length2])
                        diffs[pointer + 1] = (self.DIFF_DELETE,
                                              deletion[overlap_length2:])
                        pointer += 1
                pointer += 1
            pointer += 1

    def diff_cleanupSemanticLossless(self, diffs):

        def diff_cleanupSemanticScore(one, two):

            if not one or not two:
                # Edges are the best.
                return 6

            char1 = one[-1]
            char2 = two[0]
            nonAlphaNumeric1 = not char1.isalnum()
            nonAlphaNumeric2 = not char2.isalnum()
            whitespace1 = nonAlphaNumeric1 and char1.isspace()
            whitespace2 = nonAlphaNumeric2 and char2.isspace()
            lineBreak1 = whitespace1 and (char1 == "\r" or char1 == "\n")
            lineBreak2 = whitespace2 and (char2 == "\r" or char2 == "\n")
            blankLine1 = lineBreak1 and self.BLANKLINEEND.search(one)
            blankLine2 = lineBreak2 and self.BLANKLINESTART.match(two)

            if blankLine1 or blankLine2:
                # Five points for blank lines.
                return 5
            elif lineBreak1 or lineBreak2:
                # Four points for line breaks.
                return 4
            elif nonAlphaNumeric1 and not whitespace1 and whitespace2:
                # Three points for end of sentences.
                return 3
            elif whitespace1 or whitespace2:
                # Two points for whitespace.
                return 2
            elif nonAlphaNumeric1 or nonAlphaNumeric2:
                # One point for non-alphanumeric.
                return 1
            return 0

        pointer = 1

        while pointer < len(diffs) - 1:
            if (diffs[pointer - 1][0] == self.DIFF_EQUAL
                    and diffs[pointer + 1][0] == self.DIFF_EQUAL):

                equality1 = diffs[pointer - 1][1]
                edit = diffs[pointer][1]
                equality2 = diffs[pointer + 1][1]

                commonOffset = self.diff_commonSuffix(equality1, edit)
                if commonOffset:
                    commonString = edit[-commonOffset:]
                    equality1 = equality1[:-commonOffset]
                    edit = commonString + edit[:-commonOffset]
                    equality2 = commonString + equality2

                bestEquality1 = equality1
                bestEdit = edit
                bestEquality2 = equality2
                bestScore = (diff_cleanupSemanticScore(equality1, edit)
                             + diff_cleanupSemanticScore(edit, equality2))
                while edit and equality2 and edit[0] == equality2[0]:
                    equality1 += edit[0]
                    edit = edit[1:] + equality2[0]
                    equality2 = equality2[1:]
                    score = (diff_cleanupSemanticScore(equality1, edit)
                             + diff_cleanupSemanticScore(edit, equality2))

                    if score >= bestScore:
                        bestScore = score
                        bestEquality1 = equality1
                        bestEdit = edit
                        bestEquality2 = equality2

                if diffs[pointer - 1][1] != bestEquality1:

                    if bestEquality1:
                        diffs[pointer - 1] = (diffs[pointer - 1]
                                              [0], bestEquality1)
                    else:
                        del diffs[pointer - 1]
                        pointer -= 1
                    diffs[pointer] = (diffs[pointer][0], bestEdit)
                    if bestEquality2:
                        diffs[pointer + 1] = (diffs[pointer + 1]
                                              [0], bestEquality2)
                    else:
                        del diffs[pointer + 1]
                        pointer -= 1
            pointer += 1

    BLANKLINEEND = re.compile(r"\n\r?\n$")
    BLANKLINESTART = re.compile(r"^\r?\n\r?\n")

    def diff_cleanupEfficiency(self, diffs):

        changes = False
        equalities = []

        lastEquality = None

        pointer = 0

        pre_ins = False

        pre_del = False

        post_ins = False

        post_del = False

        while pointer < len(diffs):
            if diffs[pointer][0] == self.DIFF_EQUAL:  # Equality found.
                if (len(diffs[pointer][1]) < self.Diff_EditCost
                        and (post_ins or post_del)):
                    # Candidate found.
                    equalities.append(pointer)
                    pre_ins = post_ins
                    pre_del = post_del
                    lastEquality = diffs[pointer][1]
                else:
                    # Not a candidate, and can never become one.
                    equalities = []
                    lastEquality = None

                post_ins = post_del = False
            else:  # An insertion or deletion.
                if diffs[pointer][0] == self.DIFF_DELETE:
                    post_del = True
                else:
                    post_ins = True

                if lastEquality and ((pre_ins and pre_del and post_ins and post_del) or
                                     ((len(lastEquality) < self.Diff_EditCost / 2) and
                                         (pre_ins + pre_del + post_ins + post_del) == 3)):

                    diffs.insert(equalities[-1],
                                 (self.DIFF_DELETE, lastEquality))

                    diffs[equalities[-1] + 1] = (self.DIFF_INSERT,
                                                 diffs[equalities[-1] + 1][1])

                    equalities.pop()
                    lastEquality = None
                    if pre_ins and pre_del:

                        post_ins = post_del = True
                        equalities = []
                    else:
                        if len(equalities):

                            equalities.pop()
                        if len(equalities):
                            pointer = equalities[-1]
                        else:
                            pointer = -1
                        post_ins = post_del = False
                    changes = True
            pointer += 1

        if changes:
            self.diff_cleanupMerge(diffs)

    def diff_cleanupMerge(self, diffs):

        diffs.append((self.DIFF_EQUAL, ''))  # Add a dummy entry at the end.
        pointer = 0
        count_delete = 0
        count_insert = 0
        text_delete = ''
        text_insert = ''
        while pointer < len(diffs):
            if diffs[pointer][0] == self.DIFF_INSERT:
                count_insert += 1
                text_insert += diffs[pointer][1]
                pointer += 1
            elif diffs[pointer][0] == self.DIFF_DELETE:
                count_delete += 1
                text_delete += diffs[pointer][1]
                pointer += 1
            elif diffs[pointer][0] == self.DIFF_EQUAL:

                if count_delete + count_insert > 1:
                    if count_delete != 0 and count_insert != 0:

                        commonlength = self.diff_commonPrefix(
                            text_insert, text_delete)
                        if commonlength != 0:
                            x = pointer - count_delete - count_insert - 1
                            if x >= 0 and diffs[x][0] == self.DIFF_EQUAL:
                                diffs[x] = (diffs[x][0], diffs[x][1]
                                            + text_insert[:commonlength])
                            else:
                                diffs.insert(
                                    0, (self.DIFF_EQUAL, text_insert[:commonlength]))
                                pointer += 1
                            text_insert = text_insert[commonlength:]
                            text_delete = text_delete[commonlength:]

                        commonlength = self.diff_commonSuffix(
                            text_insert, text_delete)
                        if commonlength != 0:
                            diffs[pointer] = (diffs[pointer][0], text_insert[-commonlength:]
                                              + diffs[pointer][1])
                            text_insert = text_insert[:-commonlength]
                            text_delete = text_delete[:-commonlength]

                    new_ops = []
                    if len(text_delete) != 0:
                        new_ops.append((self.DIFF_DELETE, text_delete))
                    if len(text_insert) != 0:
                        new_ops.append((self.DIFF_INSERT, text_insert))
                    pointer -= count_delete + count_insert
                    diffs[pointer: pointer + count_delete +
                          count_insert] = new_ops
                    pointer += len(new_ops) + 1
                elif pointer != 0 and diffs[pointer - 1][0] == self.DIFF_EQUAL:

                    diffs[pointer - 1] = (diffs[pointer - 1][0],
                                          diffs[pointer - 1][1] + diffs[pointer][1])
                    del diffs[pointer]
                else:
                    pointer += 1

                count_insert = 0
                count_delete = 0
                text_delete = ''
                text_insert = ''

        if diffs[-1][1] == '':
            diffs.pop()

        changes = False
        pointer = 1

        while pointer < len(diffs) - 1:
            if (diffs[pointer - 1][0] == self.DIFF_EQUAL
                    and diffs[pointer + 1][0] == self.DIFF_EQUAL):

                if diffs[pointer][1].endswith(diffs[pointer - 1][1]):

                    if diffs[pointer - 1][1] != "":
                        diffs[pointer] = (diffs[pointer][0],
                                          diffs[pointer - 1][1]
                                          + diffs[pointer][1][:-len(diffs[pointer - 1][1])])
                        diffs[pointer + 1] = (diffs[pointer + 1][0],
                                              diffs[pointer - 1][1] + diffs[pointer + 1][1])
                    del diffs[pointer - 1]
                    changes = True
                elif diffs[pointer][1].startswith(diffs[pointer + 1][1]):

                    diffs[pointer - 1] = (diffs[pointer - 1][0],
                                          diffs[pointer - 1][1] + diffs[pointer + 1][1])
                    diffs[pointer] = (diffs[pointer][0],
                                      diffs[pointer][1][len(diffs[pointer + 1][1]):]
                                      + diffs[pointer + 1][1])
                    del diffs[pointer + 1]
                    changes = True
            pointer += 1

        if changes:
            self.diff_cleanupMerge(diffs)

    def diff_prettyHtml(self, diffs):

        html = []
        for (op, data) in diffs:
            text = (data.replace("&", "").replace("<", "")
                    .replace(">", "").replace("\n", "<br>"))
            if op == self.DIFF_INSERT:
                html.append(
                    "<ins style=\"background:#aaffaa;font-size:medium\">%s</ins>" % text)
            elif op == self.DIFF_DELETE:
                html.append(
                    "<del style=\"background:#ffaaaa;font-size:medium\">%s</del>" % text)
            elif op == self.DIFF_EQUAL:
                html.append(
                    "<span style=\"font-size:medium\">%s</span>" % text)
        return "".join(html)

    def diff_text1(self, diffs):
        # return text1
        text = []
        for (op, data) in diffs:
            if op != self.DIFF_INSERT:
                text.append(data)
        return "".join(text)

    def diff_text2(self, diffs):
        # return text2
        text = []
        for (op, data) in diffs:
            if op != self.DIFF_DELETE:
                text.append(data)
        return "".join(text)
