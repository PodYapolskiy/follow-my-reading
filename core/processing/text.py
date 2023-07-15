from typing import List, Tuple

from loguru import logger

logger.add("./logs/text.log", format="{time:DD-MM-YYYY HH:mm:ss zz} {level} {message}", enqueue=True)


def match_words(
    first_text_str: str, second_text_str: str
) -> List[Tuple[int, str, str]]:
    """
    Matches two texts and returns the difference via a list of errors
    (i.e. the changes that need to be made to the first text to obtain the second)
    :param first_text_str: the text in which we try to find the errors
    :param second_text_str: the "correct" text
    :return: a List[Tuple(the index at which the error occurs (the beginning of the phrase to replace),
                          the incorrect phrase,
                          the correct phrase)]
    """

    logger.info("Starting match_words algorithm.")

    # Split the text so the algorithm compares whole words
    first_text = first_text_str.split()
    second_text = second_text_str.split()

    # This algorithm uses levenshtein distance to determine the most probable matching
    levenshtein_dp = [
        [461782368126487236] * (len(second_text) + 1)
        for i in range(len(first_text) + 1)
    ]

    # Count the dynamic programming table as per the usual algorithm
    levenshtein_dp[0][0] = 0
    for i in range(1, len(first_text) + 1):
        levenshtein_dp[i][0] = i
    for i in range(1, len(second_text) + 1):
        levenshtein_dp[0][i] = i
    for i in range(1, len(first_text) + 1):
        for j in range(1, len(second_text) + 1):
            levenshtein_dp[i][j] = min(
                levenshtein_dp[i - 1][j - 1]
                + (first_text[i - 1] != second_text[j - 1]),
                levenshtein_dp[i - 1][j] + 1,
                levenshtein_dp[i][j - 1] + 1,
            )

    # Backtracks the result getting the list of matched words
    word_result: List[str] = list()
    current_row = len(first_text)
    current_column = len(second_text)
    while current_row * current_column != 0:
        if first_text[current_row - 1] == second_text[current_column - 1]:
            word_result.append(first_text[current_row - 1])
            current_row -= 1
            current_column -= 1
            continue
        optimal = min(
            levenshtein_dp[current_row - 1][current_column - 1],
            levenshtein_dp[current_row - 1][current_column],
            levenshtein_dp[current_row][current_column - 1],
        )
        if optimal == levenshtein_dp[current_row - 1][current_column - 1]:
            word_result.append(
                first_text[current_row - 1] + "-" + second_text[current_column - 1]
            )
            current_row -= 1
            current_column -= 1
        elif optimal == levenshtein_dp[current_row - 1][current_column]:
            word_result.append(first_text[current_row - 1] + "-_")
            current_row -= 1
        elif optimal == levenshtein_dp[current_row][current_column - 1]:
            word_result.append("_-" + second_text[current_column - 1])
            current_column -= 1

    if current_row != 0:
        word_result.append(" ".join(first_text[:current_row]) + "-_")
    elif current_column != 0:
        word_result.append("_-" + " ".join(second_text[:current_column]))

    # joining all separate words so we have a unified answer
    joined_result: List[List[str] | str] = list()

    for current_str in word_result[::-1]:
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

    # Calculating the final answer by cross-referencing the joined answers with the initial text
    answer: List[Tuple[int, str, str]] = []
    first_index = 0

    for current_str in joined_result:  # type: ignore
        if type(current_str) == list:
            answer.append((first_index, current_str[0], current_str[1]))
            first_index += len(current_str[0])
            if current_str[0] != "":
                first_index += 1
        else:
            first_index += len(current_str) + 1

    logger.info("Process match_words has ended. Returning the result.")
    return answer


def match_phrases(phrases: List[str], text: str) -> List[List[Tuple[int, str, str]]]:
    """
    Matches a list of phrases with a text and returns the errors in the phrases
    Assumes that the list of phrases combines into the text
    :param phrases: a list of phrases to be checked
    :param text: the "correct" text
    :return: the list of errors by phrases, i.e.
            List[List[Tuple[the index at which the error occurs (the beginning of the phrase to replace],
                          the incorrect phrase,
                          the correct phrase]]]
    """

    logger.info("Starting match_phrases algorithm.")

    # Preparing the texts so that capital letters and non-letter symbols are ignored
    better_text, text_indices = prep_text(text)
    better_phrases, phrase_indices = prep_text(" ".join(phrases))

    # Calculating the full answer using levenshtein distance
    full_answer = match_words(better_phrases, better_text)

    # Cross-referencing the indices in the full answer to distribute the errors by phrases
    answers: List[List[Tuple[int, str, str]]] = [[] for i in phrases]
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

    logger.info("Process match_phrases has ended. Returning the result.")
    return answers


def prep_text(text: str) -> Tuple[str, List[int]]:
    """
    Prepares the text, so it is fully lowercase and does not contain any non-letter symbols
    It is using inbuilt isalpha() and lower() functions so it should support multiple languages
    :param text: the text to be prepared
    :return: the changed text and a list of indices that map the changed text to the initial one
    """

    logger.info("Starting prep_text algorithm.")

    changed: str = ""
    indices: List[int] = []

    # Remove any non-letter symbols
    for i in range(len(text)):
        if (
            text[i].isalpha()
            or text[i] == " "
            and (len(changed) == 0 or changed[-1] != " ")
        ):
            changed += text[i]
            indices.append(i)

    # Cut off any unnecessary spaces in the beginning and end
    indices = indices[len(changed) - len(changed.lstrip()) :]

    if changed.rstrip() != changed:
        indices = indices[: len(changed.rstrip()) - len(changed)]

    logger.info("Process prep_text has ended. Returning the result.")
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
