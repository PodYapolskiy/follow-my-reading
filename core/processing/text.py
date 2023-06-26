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
    return answer, lev_dp[-1][-1]


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


def match_phrases(phrases, text, margin=1.3):
    # phrases is an iterable of strings to be matched against the text
    # text is the text to match against
    # margin is the max size of the window in which we search for the phrase relative to len(phrase)
    # modify margin as

    answers = []
    for i in phrases:
        window = int(len(i) * margin)
        best_window = [[], 463784628768273]
        for j in range(window, len(text)+1):
            new_ans, lev_dist = match(i, text[j-window:j])
            if best_window[1] > lev_dist:
                best_window = [new_ans, lev_dist]
        ph_ans = best_window[0]

        first_word = find(ph_ans[0][2], len(ph_ans[0][2]) - len(ph_ans[0][1]) - 1, ' ', -1)
        ph_ans[0] = (ph_ans[0][0], ph_ans[0][1],  ph_ans[0][2][first_word+1:])

        if ph_ans[0][2] == "" and ph_ans[0][1] == "":
            ph_ans.pop(0)

        last_word = find(ph_ans[-1][2], len(ph_ans[-1][1]), ' ', 1)
        ph_ans[-1] = (ph_ans[-1][0], ph_ans[-1][1], ph_ans[-1][2][:last_word])

        if ph_ans[-1][2] == "" and ph_ans[-1][1] == "":
            ph_ans.pop()

        answers.append(ph_ans)
    return answers


# for i in match_phrases(["боится зла?» Конец", "Он нашёл Дио Брандо в кране в гимназии неподалеку от кори"],
#                        """Когда Александр Македонский пришёл в Аттику, то, разумеется, захотел познакомиться с прославленным «маргиналом» как и многие прочие. Плутарх рассказывает, что Александр долго ждал, пока сам Диоген придет к нему выразить свое почтение, но философ преспокойно проводил время у себя. Тогда Александр сам решил навестить его. Он нашёл Диогена в Крании (в гимнасии неподалёку от Коринфа), когда тот грелся на солнце. Александр подошёл к нему и сказал: «Я — великий царь Александр». «А я, — ответил Диоген, — собака Диоген». «И за что тебя зовут собакой?» «Кто бросит кусок — тому виляю, кто не бросит — облаиваю, кто злой человек — кусаю». «А меня ты боишься?» — спросил Александр. «А что ты такое, — спросил Диоген, — зло или добро?» «Добро», — сказал тот. «А кто же боится добра?» Наконец, Александр сказал: «Проси у меня чего хочешь». «Отойди, ты заслоняешь мне солнце», — сказал Диоген и продолжил греться. На обратном пути, в ответ на шутки своих приятелей, которые потешались над философом, Александр якобы даже заметил: «Если бы я не был Александром, то хотел бы стать Диогеном»."""):
#     print(i)
