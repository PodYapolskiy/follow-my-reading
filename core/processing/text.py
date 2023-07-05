from typing import List, Tuple


def match_words(
    first_text_str: str, second_text_str: str
) -> list[tuple[int, str, str]]:
    # Returns a list of changes that need to be made to the first text to get the second one
    # Matches using whole words
    # The output format is:
    # List[Tuple(Index in the first text where the difference was found,
    #            The segment of the first text which is to be removed,
    #            The segment of the second text which is to be substituted in)]

    first_text = first_text_str.split()
    second_text = second_text_str.split()

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
        result.append(" ".join(first_text[:curx]) + "-_")
    elif cury != 0:
        result.append("_-" + " ".join(second_text[:cury]))

    joined_result: List[list[str] | str] = list()

    for current_str in result[::-1]:
        if not joined_result:
            if "-" in current_str:
                joined_result.append(current_str.split("-"))
            else:
                joined_result.append(current_str)
        elif isinstance(joined_result[-1], list):
            if "-" in current_str:
                if joined_result[-1][0][-1] != "_":
                    joined_result[-1][0] += " "
                joined_result[-1][0] += current_str[: current_str.find("-")]

                if joined_result[-1][1][-1] != "_":
                    joined_result[-1][1] += " "
                joined_result[-1][1] += current_str[current_str.find("-") + 1 :]
            else:
                joined_result.append(current_str)
        else:
            if "-" in current_str:
                joined_result.append(current_str.split("-"))
            else:
                joined_result[-1] += " " + current_str

    for current_str in joined_result:  # type: ignore
        if isinstance(current_str, list):
            current_str[0] = current_str[0].replace("_", "")
            current_str[1] = current_str[1].replace("_", "")

    answer = []
    first_index = 0

    for current_str in joined_result:  # type: ignore
        if type(current_str) == list:
            answer.append((first_index, current_str[0], current_str[1]))
            first_index += len(current_str[0])
            if current_str[0] != "":
                first_index += 1
        else:
            first_index += len(current_str) + 1
    return answer


def match_phrases(phrases: list[str], text: str) -> list[list]:
    # phrases is an iterable of strings to be matched against the text
    # it is assumed that all the strings together resemble the text
    # text is the text to match against

    answers: list[list[tuple[int, str, str]]] = [[] for i in phrases]

    better_text, text_indices = prep_text(text)
    better_phrases, phrase_indices = prep_text(" ".join(phrases))

    full_answer = match_words(better_phrases, better_text)

    y = 0
    cur_ind = 0
    for i in full_answer:
        while phrase_indices[i[0]] > cur_ind + len(phrases[y]):
            cur_ind += 1 + len(phrases[y])
            y += 1
        answers[y].append(
            (
                phrase_indices[i[0]] - cur_ind,
                phrases[y][
                    phrase_indices[i[0]]
                    - cur_ind : phrase_indices[i[0] + len(i[1]) - 1]
                    + 1
                    - cur_ind
                ],
                i[2],
            )
        )

    return answers


def prep_text(s: str) -> tuple[str, list[int]]:
    # function for preparing text parsed from audio for more reliable matching

    changed = ""
    indices = []

    for i in range(len(s)):
        if s[i].isalpha() or s[i] == " " and (len(changed) == 0 or changed[-1] != " "):
            changed += s[i]
            indices.append(i)

    indices = indices[len(changed) - len(changed.lstrip()) :]

    if changed.rstrip() != changed:
        indices = indices[: len(changed.rstrip()) - len(changed)]

    return changed.lower().strip(), indices


# phrases = [
#  " The headache won't go away. She's taking medicine but even that didn't help.",
#  " The monster's throbbing in her head continued.",
#  " This happened to her only once before in her life and she realized that only one thing could be happening."
#  ]
# ans = match_phrases(phrases,
#     "The headache wouldn't go away. She's taken medicine but even that didn't help. The monstrous throbbing in her head continued. She had this happen to her only once before in her life and she realized that only one thing could be happening. 21:210")
#
# phrases = ["В кабинете, полном дыма, шел разгaвор о войне,", "которая была объявлена манифестом, о наборе манифеста",
#                         "еще никто не читал, но все знали о его появлении. граф сидел на манке между", "двумя куреювшими и разговаривавшими соседями. Граф сам",
#                         "не курил и говорил, а, наклоняя свой амогус то на один бок, то на другой, с видимым удовольствием смотрел на куривших",
#                         "и слушал разговор двух соседей своих, которых он отравил между собой."]
# ans = match_phrases(phrases,
#     "В кабинете, полном дыма, шел разговор о войне, которая была объявлена манифестом, о наборе. Манифеста еще никто не читал, но все знали о его появлении. Граф сидел на оттоманке между двумя курившими и разговаривавшими соседями. Граф сам не курил и не говорил, а, наклоняя голову то на один бок, то на другой, с видимым удовольствием смотрел на куривших и слушал разговор двух соседей своих, которых он стравил между собой.")
#
# for i in range(len(phrases)):
#     print(phrases[i])
#     print(ans[i])
#     for j in ans[i]:
#         print(phrases[i][j[0]:j[0] + len(j[1])])
#
# print(match_phrases(["this is soft wear project follow my reading"], "This is software project Follow My Reading."))
