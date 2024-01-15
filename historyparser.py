import re


def parse_dialogue_to_summary(dialogue_text):
    # Split the dialogue into lines
    lines = dialogue_text.split('\n')

    # Initialize an empty list to store dialogue entries
    dialogue_entries = []

    # Iterate through each line
    for line in lines:
        # Use regular expressions to extract role and content
        match = re.match(r'(\w+):(.+)', line)
        if match:
            role = match.group(1).strip().lower()
            content = match.group(2).strip()

            # Map the role to "system" if it's a system message
            role = "assistant" if role == "guru_ai" else "user"

            # Add the entry to the list
            dialogue_entries.append({"role": role, "content": content})
    dialogue_entries.append({"role": 'user', "content": 'Проанализируй весь диалог и подведи итоги в формате: {user_id, имя, номер телефона, итоги диалога}, обязательно подчеркни все ключевые моменты диалога в итогах, не добавляй ничего лишнего, ничего больше, только json в заданном формате'})
    print(dialogue_entries)
    return dialogue_entries

def parse_dialogue(dialogue_text, user_promt):
    # Split the dialogue into lines
    lines = dialogue_text.split('\n')

    # Initialize an empty list to store dialogue entries
    dialogue_entries = []
    dialogue_entries.append({'role': 'system', 'content': 'Ты виртуальный администратор ресторана Miki, который отвечает в мессенджерах, твоя задача консультировать гостей которые тебе пишут, и давать информацию о ресторане, выдавать правдивую информацию, не придуманную. Основная твоя цель что бы  пользователь забронировал столик в ресторане.Все цены всегда пиши в валюте доллары. - Введение: - Как только ты получаешь первую команду /start - это означает что начался новый диалог.Приветствие: Всегда начинай свой разговор с вежливого <Здравствуйте!>.- Представление: Сразу представляйся: Я администратор ресторана Miki. Всегда уточняйте в приветствии причину вашего обращения к потенциальному клиенту, с предложением узнать информацию о блюдах и конечно же забронировать столик. Также добавь, что вы можете отправлять мне сообщения тексом, или отправлять голосовые,2: Презентация решения: на основе потребностей собеседника представьте ваш продукт/услугу как решение, способное решить его проблемы, 3: Завершение: Предложи клиенту забронировать столик в ресторане. Ты должен спросить время, и в зависимости от ответа пользователя, предложить свободные окошки времени на этот день. Обязательно подведите итог обсужденному и повторите выгоды. Если вы помогли клиенту забронировать столик, знаете его имя и номер телефона, закончи ответ кодом <DIALOGUE_END>'},)
    # Iterate through each line
    for line in lines:
        # Use regular expressions to extract role and content
        match = re.match(r'(\w+):(.+)', line)

        if match:
            role = match.group(1).strip().lower()
            content = match.group(2).strip()

            role = "assistant" if role == "assistant" else "user"

            # Add the entry to the list
            dialogue_entries.append({"role": role, "content": content})
            print(match)
    # dialogue_entries.append({"role": 'user', "content": 'Проанализируй весь диалог и подведи краткие итоги в формате: {user_id, имя, номер телефона, итоги диалога} не добавляй ничего лишнего, ничего больше, только json в заданном формате'})
    dialogue_entries.append({"role": 'user', "content": user_promt})
    print(dialogue_entries)
    return dialogue_entries


