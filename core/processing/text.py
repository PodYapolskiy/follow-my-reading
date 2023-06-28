from typing import List, Tuple


def match(first_text: str, second_text: str):
    # Returns a list of changes that need to be made to the first text to get the second one
    # The output format is:
    # List[Tuple(Index in the first text where the difference was found,
    #            The segment of the first text which is to be removed,
    #            The segment of the second text which is to be substituted in)]

    lev_dp = [
        [461782368126487236] * (len(second_text) + 1)
        for i in range(len(first_text) + 1)
    ]
    lev_dp[0][0] = 0
    for i in range(1, len(first_text) + 1):
        lev_dp[i][0] = i
    for i in range(1, len(second_text) + 1):
        lev_dp[0][i] = i
    for i in range(1, len(first_text) + 1):
        for j in range(1, len(second_text) + 1):
            lev_dp[i][j] = min(
                lev_dp[i - 1][j - 1] + (first_text[i - 1] != second_text[j - 1]),
                lev_dp[i - 1][j] + 1,
                lev_dp[i][j - 1] + 1,
            )

    result: List[str] = list()
    curx = len(first_text)
    cury = len(second_text)
    while curx * cury != 0:
        if first_text[curx - 1] == second_text[cury - 1]:
            result.append(first_text[curx - 1])
            curx -= 1
            cury -= 1
            continue
        optimal = min(
            lev_dp[curx - 1][cury - 1], lev_dp[curx - 1][cury], lev_dp[curx][cury - 1]
        )
        if optimal == lev_dp[curx - 1][cury - 1]:
            result.append(first_text[curx - 1] + "-" + second_text[cury - 1])
            curx -= 1
            cury -= 1
        elif optimal == lev_dp[curx - 1][cury]:
            result.append(first_text[curx - 1] + "-_")
            curx -= 1
        elif optimal == lev_dp[curx][cury - 1]:
            result.append("_-" + second_text[cury - 1])
            cury -= 1

    if curx != 0:
        result.append(first_text[:curx] + "-_")
    elif cury != 0:
        result.append("_-" + second_text[:cury])

    joined_result: List[List[str] | str] = list()

    for current_str in result[::-1]:
        if not joined_result:
            if "-" in current_str:
                joined_result.append(current_str.split("-"))
            else:
                joined_result.append(current_str)
        elif isinstance(joined_result[-1], list):
            if "-" in current_str:
                joined_result[-1][0] += current_str[0]
                joined_result[-1][1] += current_str[2]
            else:
                joined_result.append(current_str)
        else:
            if "-" in current_str:
                joined_result.append(current_str.split("-"))
            else:
                joined_result[-1] += current_str

    for current_str in joined_result:
        if isinstance(current_str, list):
            current_str[0] = current_str[0].replace("_", "")
            current_str[1] = current_str[1].replace("_", "")

    answer = []
    first_index = 0

    for current_str in joined_result:
        if type(current_str) == list:
            answer.append((first_index, current_str[0], current_str[1]))
            first_index += len(current_str[0])
        else:
            first_index += len(current_str)
    return answer


def find(lst, start_i, sym, step):
    # helper function
    # step is the step of the cycle (with backwards movement as well)
    # lst is a list
    # start_i is from which point do you need to find
    # sym is the symbol to be found

    if step < 0 and type(step) == int:
        for i in range(start_i, -1, step):
            if lst[i] == sym:
                return i

        return -1
    elif step > 0 and type(step) == int:
        for i in range(start_i, len(lst), step):
            if lst[i] == sym:
                return i

        return len(lst)
    else:
        raise ValueError("step of 0 or not int step")


def match_phrases(phrases, text):
    # phrases is an iterable of strings to be matched against the text
    # it is assumed that all the strings together resemble the text
    # text is the text to match against

    answers = [[] for i in phrases]
    full_answer = match(" ".join(phrases), text)

    y = 0
    cur_ind = 0
    for i in full_answer:
        while i[0] > cur_ind + len(phrases[y]):
            cur_ind += 1 + len(phrases[y])
            y += 1
        answers[y].append((i[0] - cur_ind, i[1], i[2]))

    return answers


def prep_audio_text(s):
    # function for preparing text parsed from audio for more reliable matching

    changed = ""
    for i in s:
        if i.isalpha() or i == " ":
            changed += i

    while "  " in s:
        s = s.replace("  ", " ")

    return s.lower().strip()


def prep_image_text(s):
    # function for preparing text parsed from text for more reliable matching

    s = s.replace("\n", " ").replace("\t", " ")

    changed = ""
    for i in s:
        if i.isalpha() or i in " .,":
            changed += i

    while "  " in s:
        s = s.replace("  ", " ")

    return s.lower().strip()

# phrases = ["В кабинете, полном дыма, шел разгaвор о войне,", "которая была объявлена манифестом, о наборе манифеста",
#                         "еще никто не читал, но все знали о его появлении. граф сидел на манке между", "двумя куреювшими и разговаривавшими соседями. Граф сам",
#                         "не курил и говорил, а, наклоняя свой амогус то на один бок, то на другой, с видимым удовольствием смотрел на куривших",
#                         "и слушал разговор двух соседей своих, которых он отравил между собой."]
# ans = match_phrases(phrases,
#     "В кабинете, полном дыма, шел разговор о войне, которая была объявлена манифестом, о наборе. Манифеста еще никто не читал, но все знали о его появлении. Граф сидел на оттоманке между двумя курившими и разговаривавшими соседями. Граф сам не курил и не говорил, а, наклоняя голову то на один бок, то на другой, с видимым удовольствием смотрел на куривших и слушал разговор двух соседей своих, которых он стравил между собой.")
# for i in range(len(phrases)):
#     print(phrases[i])
#     print(ans[i])
#     print(phrases[i][ans[i][0][0]:len(ans[i][0][1]) + ans[i][0][0]])
