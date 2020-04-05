from bs4 import BeautifulSoup
from requests import get
from hashlib import md5
import vk_api
import random
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from itertools import combinations, permutations
import validators

TOKEN = open('data/config.txt', 'r').readline()


def get_ids():
    file_in = open('data/keys.txt', 'r')
    data = file_in.readlines()
    ret = list()
    for elem in data:
        ret.append(int(elem.strip()))
    return ret


dic = {md5(str(i).encode()).hexdigest(): i for i in range(-1000, 100000)}
for el in permutations('xyz'):
    el = ''.join(el)
    dic[md5(el.encode()).hexdigest()] = el
for el in permutations('xyzw'):
    el = ''.join(el)
    dic[md5(el.encode()).hexdigest()] = el
for el in combinations('abcdefgh', 4):
    el = ''.join(el)
    dic[md5(el.encode()).hexdigest()] = el
id_list = get_ids()
print(id_list)


def main():
    global id_keys
    vk_session = vk_api.VkApi(
        token=TOKEN)

    longpoll = VkBotLongPoll(vk_session, 193460928)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.obj.message[
            'from_id'] == 240314483 and 'ok' in event.obj.message['text']:
            print('Новое сообщение:')
            print('Для меня от:', event.obj.message['from_id'])
            print('Текст:', event.obj.message['text'])
            id_user = int(event.obj.message['text'].split()[1])
            new_id(id_user)
            vk = vk_session.get_api()
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message=f'Разрешен доступ пользователю {id_user}',
                             random_id=random.randint(0, 2 ** 64))
            vk = vk_session.get_api()
            vk.messages.send(user_id=id_user,
                             message=f'Вам разрешен доступ к сервису, скиньте нужную ссылку.',
                             random_id=random.randint(0, 2 ** 64))

        elif event.type == VkBotEventType.MESSAGE_NEW and event.obj.message[
            'from_id'] not in id_list:
            print('Новое сообщение:')
            print('Для меня от:', event.obj.message['from_id'])
            print('Текст:', event.obj.message['text'])
            vk = vk_session.get_api()
            vk.messages.send(user_id=event.obj.message['from_id'],
                             message="""Спасибо, что написали нам. Мы обязательно ответим в ближайшее время.
                                        Цены на бота: 50 рублей. Если вы уже оплатили, 
                                        то просим подождать, пока админ проверит оплату""",
                             random_id=random.randint(0, 2 ** 64))
            vk = vk_session.get_api()
            vk.messages.send(user_id=240314483,
                             message='Пользователь {} запращивает доступ'.format(
                                 event.obj.message['from_id']),
                             random_id=random.randint(0, 2 ** 64))

        elif event.type == VkBotEventType.MESSAGE_NEW and event.obj.message['from_id'] in id_list:
            print('Новое сообщение:')
            print('Для меня от:', event.obj.message['from_id'])
            print('Текст:', event.obj.message['text'])
            valid = validators.url(event.obj.message['text'])
            vk = vk_session.get_api()
            if valid and 'kpolyakov.spb.ru' in event.obj.message['from_id']:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=get_answers(event.obj.message['text']),
                                 random_id=random.randint(0, 2 ** 64))
            else:
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Неправильная ссылка, попробуйте еще раз',
                                 random_id=random.randint(0, 2 ** 64))


def new_id(id):
    file_out = open('data/keys.txt', 'w')
    id_list.append(id)
    print(*id_list, file=file_out, sep='\n')


def get_answers(url):
    answers = []
    resp = get(url, timeout=5)
    content = BeautifulSoup(resp.content, 'html.parser')
    quests = content.find_all('div', attrs={'class': 'q'})
    for i, qust in enumerate(quests):
        try:
            text = qust.find_all('td', attrs={'class': 'text'})
            val = text[0].find_all('input', attrs={'type': 'hidden'})
            value = val[0].get('value')
            answers.append(f'{i + 1}) {dic.get(value)}')
        except:
            table = qust.find_all('table')
            trs = table[0].find_all('tr')
            anss = []
            t = 0
            for tr in trs:
                try:
                    td = tr.find_all('td', attrs={'class': 'radio'}) + tr.find_all('td', attrs={
                        'class': 'check'})
                    inp = td[0].find_all('input')
                    val = inp[0].get('value')
                    if int(val) == 1:
                        anss.append(str(t + 1))
                    t += 1
                except Exception:
                    continue
            answers.append(f"{i + 1}) {', '.join(anss)}")
    return '\n'.join(answers)


if __name__ == '__main__':
    main()
