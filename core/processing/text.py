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
