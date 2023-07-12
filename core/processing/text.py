from typing import List, Tuple, Any
import itertools
from math import inf


def __backtracking_levenshtein(first_text: List[str] | str,
                               second_text: List[str] | str) -> Tuple[List[str], int]:
    """
    Levenshtein distance algorithm that takes two texts and returns the optimal transitions list and the final distance
    Treats a list as a collection of words separated by spaces
    :param first_text: a text to be compared, either as a string or a list of words
    :param second_text: a text to be compared, either as a string or a list of words
    :return: Tuple[path that the dynamic programming algorithm found in format of
                   List["entry from first text or "_" if empty" + "-" + "entry from second text or "_" if empty"],
                   the levenshtein distance computed]
    """

    # If we need to compare words, we need to separate them with spaces in the final answer
    if isinstance(first_text, list):
        separator = " "
    else:
        separator = ""

    # Initialize the dynamic programming table
    levenshtein_dp = [
        [inf] * (len(second_text) + 1)
        for i in range(len(first_text) + 1)
    ]

    # Count the dynamic programming table as per the usual algorithm
    levenshtein_dp[0][0] = 0
    for i in range(1, len(first_text) + 1):
        levenshtein_dp[i][0] = i
    for i in range(1, len(second_text) + 1):
        levenshtein_dp[0][i] = i
    for i, j in itertools.product(range(1, len(first_text) + 1), range(1, len(second_text) + 1)):
        levenshtein_dp[i][j] = min(
            levenshtein_dp[i - 1][j - 1] + (first_text[i - 1] != second_text[j - 1]),
            levenshtein_dp[i - 1][j] + 1,
            levenshtein_dp[i][j - 1] + 1,
        )

    # Backtracks the result getting the list of matched words
    backtrack_result: List[str] = list()
    current_row = len(first_text)
    current_column = len(second_text)
    while current_row * current_column != 0:
        if first_text[current_row - 1] == second_text[current_column - 1]:
            backtrack_result.append(first_text[current_row - 1])
            current_row -= 1
            current_column -= 1
            continue

        optimal = min(
            levenshtein_dp[current_row - 1][current_column - 1],
            levenshtein_dp[current_row - 1][current_column],
            levenshtein_dp[current_row][current_column - 1]
        )
        if optimal == levenshtein_dp[current_row - 1][current_column - 1]:
            backtrack_result.append(first_text[current_row - 1] + "-" + second_text[current_column - 1])
            current_row -= 1
            current_column -= 1
        elif optimal == levenshtein_dp[current_row - 1][current_column]:
            backtrack_result.append(first_text[current_row - 1] + "-_")
            current_row -= 1
        elif optimal == levenshtein_dp[current_row][current_column - 1]:
            backtrack_result.append("_-" + second_text[current_column - 1])
            current_column -= 1

    # Put all the remaining symbols(words) in the answer
    if current_row != 0:
        backtrack_result.append(separator.join(first_text[:current_row]) + "-_")
    elif current_column != 0:
        backtrack_result.append("_-" + separator.join(second_text[:current_column]))

    return backtrack_result, int(levenshtein_dp[-1][-1])


def __joined_levenshtein(first_text: List[str] | str, second_text: List[str] | str) -> Tuple[List[List[str] | str], int]:
    """
    Joins the answers given by the initial levenshtein algorithm so they resemble errors more
    Treats a list as a collection of words separated by spaces
    :param first_text: a text to be compared, either as a string or a list of words
    :param second_text: a text to be compared, either as a string or a list of words
    :return: Tuple[the joined result in the format of
                   List[List[the phrase from the first text to be replaced, the replacement from the second text]
                        OR
                        str if both texts are the same at this interval],
                   the levenshtein distance computed]
    """

    # Compute the full levenshtein answer
    backtrack_result, distance = __backtracking_levenshtein(first_text, second_text)

    # If we need to compare words, we need to separate them with spaces in the final answer
    if isinstance(first_text, str):
        separator = ""
    else:
        separator = " "

    # Create the answer list and initialize it with the first element
    joined_result: List[List[str] | str] = list()

    if "-" in backtrack_result[-1]:
        joined_result.append(backtrack_result[-1].split("-"))
    else:
        joined_result.append(backtrack_result[-1])

    # Add the rest of the errors, keeping track of type to know whether we should start creating a new phrase
    for current_str in backtrack_result[-2::-1]:
        if isinstance(joined_result[-1], list) and "-" in current_str:
            # We are collecting two separate phrases and the current_str is also separate, continue the last phrase
            joined_result[-1][0] += separator + current_str[: current_str.find("-")]
            joined_result[-1][1] += separator + current_str[current_str.find("-") + 1:]
        elif isinstance(joined_result[-1], list):
            # We are collecting two separate phrases and the current_str is the same, start a new phrase
            joined_result.append(current_str)
        elif "-" in current_str:
            # We are collecting two same phrases and the current_str is separate, start a new phrase
            joined_result.append(current_str.split("-"))
        else:
            # We are collecting two same phrases and the current_str is also the same, continue the last phrase
            joined_result[-1] += separator + current_str

    # Replace any symbols that symbolise empty space with empty space
    for current_str in filter(lambda x: isinstance(x, list), joined_result):  # type: ignore
        while "_ " in current_str[0] or "_ " in current_str[1]:
            current_str[0] = current_str[0].replace("_ ", "_")
            current_str[1] = current_str[1].replace("_ ", "_")
        current_str[0] = current_str[0].replace("_", "")
        current_str[1] = current_str[1].replace("_", "")

    return joined_result, distance


def match(
    first_text_str: str, second_text_str: str, separate_words: bool
) -> Tuple[List[Tuple[int, str, str]], int]:
    """
    Matches two texts and returns the difference via a list of errors
    (i.e. the changes that need to be made to the first text to obtain the second)
    :param first_text_str: the text in which we try to find the errors
    :param second_text_str: the "correct" text
    :param separate_words: whether the algorithm matches using whole words or just symbols
    :return: a Tuple[List[Tuple(the index at which the error occurs (the beginning of the phrase to replace),
                          the incorrect phrase,
                          the correct phrase)],
                     the distance between the texts]
    """

    # Split the text if needed so the algorithm compares whole words
    if separate_words:
        first_text = first_text_str.split()
        second_text = second_text_str.split()
    else:
        first_text = first_text_str
        second_text = second_text_str

    # This algorithm uses levenshtein distance to determine the most probable matching
    joined_result, distance = __joined_levenshtein(first_text, second_text)

    # Calculating the final answer by cross-referencing the joined answers with the initial text
    answer: List[Tuple[int, str, str]] = []
    first_index = 0

    for current_str in joined_result:  # type: ignore
        if type(current_str) == list:
            answer.append((first_index, current_str[0], current_str[1]))
            first_index += len(current_str[0])
            if separate_words and current_str[0] != "":
                first_index += 1
        else:
            first_index += len(current_str) + 1
    return answer, distance


def __match_symbols(first_text: str, second_text: str) -> Tuple[List[Tuple[int, str, str]], int]:
    """
    Interface for match() that matches using symbols
    Used for symbol matching for finding short phrases in text more reliably
    :param first_text: the text in which we try to find the errors
    :param second_text: the "correct" text
    :return: a Tuple[List[Tuple(the index at which the error occurs (the beginning of the phrase to replace),
                          the incorrect phrase,
                          the correct phrase)],
                     the distance between the texts]
    """
    return match(first_text, second_text, False)


def match_words(first_text: str, second_text: str) -> List[Tuple[int, str, str]]:
    """
        Interface for match() that matches using whole words
        Used for finding errors in most cases
        :param first_text: the text in which we try to find the errors
        :param second_text: the "correct" text
        :return: List[Tuple(the index at which the error occurs (the beginning of the phrase to replace),
                            the incorrect phrase,
                            the correct phrase)]
        """
    return match(first_text, second_text, True)[0]


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

    # Preparing the texts so that capital letters and non-letter symbols are ignored
    better_text, text_indices = __prep_text(text)
    better_phrases, phrase_indices = __prep_text(" ".join(phrases))

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
                    - cur_ind: phrase_indices[i[0] + len(i[1]) - 1]
                    + 1
                    - cur_ind
                ],
                i[2],
            )
        )

    return answers


def __prep_text(text: str) -> Tuple[str, List[int]]:
    """
    Prepares the text, so it is fully lowercase and does not contain any non-letter symbols
    It is using inbuilt isalpha() and lower() functions, so it should support multiple languages
    :param text: the text to be prepared
    :return: the changed text and a list of indices that map the changed text to the initial one
    """

    changed: str = ""
    indices: List[int] = []

    # Remove any non-letter symbols
    for i in range(len(text)):
        if text[i].isalpha() or text[i] == " " and (len(changed) == 0 or changed[-1] != " "):
            changed += text[i]
            indices.append(i)

    # Cut off any unnecessary spaces in the beginning and end
    indices = indices[len(changed) - len(changed.lstrip()):]

    if changed.rstrip() != changed:
        indices = indices[: len(changed.rstrip()) - len(changed)]

    return changed.lower().strip(), indices


def __find(iterable: List[Any] | str, start_index: int, to_find: Any, step: int) -> int:
    """
    Helper function for finding the index of a certain element in a list
    Works with any initial position and step(whole, non-zero)
    :param iterable: The list or string to search
    :param start_index: The initial position for the search
    :param to_find: The element or symbol to be found
    :param step: The step with which to search for (can be negative)
    :return: The index of the first found instance that follows the search parameters
             returns len(iterable) (or -1 with negative step) if nothing was found
    """

    # Check for validness of step
    if type(step) != int or step == 0:
        raise ValueError("Step of 0 or not int step")

    # Set iteration bound so negative steps work
    if step < 0:
        iteration_end = -1
    else:
        iteration_end = len(iterable)

    # Iterate to find the element
    for i in range(start_index, iteration_end, step):
        if iterable[i] == to_find:
            return i

    # If it was not found, return the end of iteration
    return iteration_end


def find_phrases(phrases: List[str], to_find: str, margin: float = 1.05) -> List[int]:
    """
    Finds a piece of text in a list of phrases and returns the indices of the phrases in which the text appears in
    :param phrases: a list of phrases
    :param to_find: the text to be found
    :param margin: the margin for error, used for bloating the search window if to_find has contractions
    :return: the indices of the phrases which compose to_find
    """

    # Prepare text to ignore multiple spaces and non-letter symbols
    better_text, text_indices = __prep_text(to_find)
    better_phrases, phrase_indices = __prep_text(" ".join(phrases))

    # Compute the size of a window to compare to the text
    window = int(len(better_text) * margin)

    # Find the window that best fits the string
    best_window = [[], inf]
    best_end = 0
    for j in range(window, len(better_phrases) + 1):
        new_ans, lev_dist = __match_symbols(better_text, better_phrases[j - window:j])
        if best_window[1] > lev_dist:
            best_window = [new_ans, lev_dist]
            best_end = j
    best_beg = best_end - window

    # Trim the window to exclude unnecessary symbols (trims using full words)
    optimal_ans = best_window[0]

    first_word = __find(optimal_ans[0][2], len(optimal_ans[0][2]) - len(optimal_ans[0][1]) - 1, ' ', -1)
    best_beg += first_word + 1

    last_word = __find(optimal_ans[-1][2], len(optimal_ans[-1][1]), ' ', 1)
    best_end -= len(optimal_ans[-1][2]) - last_word

    # Transform the indices from prepared text to initial text
    actual_beg = phrase_indices[best_beg]
    actual_end = phrase_indices[best_end - 1] + 1

    # Iterate through phrases to compute the final answer
    answer = []

    current_index = 0
    for phrase in range(len(phrases)):
        current_index += len(phrases[phrase]) + 1
        if current_index > actual_beg and current_index - len(phrases[phrase]) - 1 <= actual_end:
            answer.append(phrase)

    return answer

tests = {
    "test_cases": [
        {
            "phrases": [
                "The headache won't go away. She's taking medicine but even that didn't help.",
                "The monster's throbbing in her head continued.",
                "This happened to her only once before in her life and she realized that only one thing could be happening."
            ],
            "to_find": "she realized that only one thing could be happening",
            "answer": [
                2
            ]
        },
        {
            "phrases": [
                "The headache won't go away. She's taking medicine but even that didn't help.",
                "The monster's throbbing in her head continued.",
                "This happened to her only once before in her life and she realized that only one thing could be happening."
            ],
            "to_find": "she has taken medicine",
            "answer": [
                1
            ]
        },
        {
            "phrases": [
                "The headache won't go away. She's taking medicine but even that didn't help.",
                "The monster's throbbing in her head continued.",
                "This happened to her only once before in her life and she realized that only one thing could be happening."
            ],
            "to_find": "throbbing in her head continued this happened to her",
            "answer": [
                2,
                3
            ]
        }
    ]
}

for test in tests["test_cases"]:
    print(find_phrases(test["phrases"], test["to_find"]))
    print(test["answer"])

phrases = [
 " The headache won't go away. She's taking medicine but even that didn't help.",
 " The monster's throbbing in her head continued.",
 " This happened to her only once before in her life and she realized that only one thing could be happening."
 ]
ans = match_phrases(phrases,
    "The headache wouldn't go away. She's taken medicine but even that didn't help. The monstrous throbbing in her head continued. She had this happen to her only once before in her life and she realized that only one thing could be happening. 21:210")

phrases = ["В кабинете, полном дыма, шел разгaвор о войне,", "которая была объявлена манифестом, о наборе манифеста",
                        "еще никто не читал, но все знали о его появлении. граф сидел на манке между", "двумя куреювшими и разговаривавшими соседями. Граф сам",
                        "не курил и говорил, а, наклоняя свой амогус то на один бок, то на другой, с видимым удовольствием смотрел на куривших",
                        "и слушал разговор двух соседей своих, которых он отравил между собой."]
ans = match_phrases(phrases,
    "В кабинете, полном дыма, шел разговор о войне, которая была объявлена манифестом, о наборе. Манифеста еще никто не читал, но все знали о его появлении. Граф сидел на оттоманке между двумя курившими и разговаривавшими соседями. Граф сам не курил и не говорил, а, наклоняя голову то на один бок, то на другой, с видимым удовольствием смотрел на куривших и слушал разговор двух соседей своих, которых он стравил между собой.")

for i in range(len(phrases)):
    print(phrases[i])
    print(ans[i])
    for j in ans[i]:
        print(phrases[i][j[0]:j[0] + len(j[1])])

print(match_phrases(["this is soft wear project follow my reading"], "This is software project Follow My Reading."))
