import requests
from time import sleep
import json
from FL_constants import SLEEP


def make_url(method):
    '''
    :param method: метод АПИ ВК
    :return: возвращает строку со ссылкой на метод
    '''
    default_url = 'https://api.vk.com/method/'
    url = default_url+method
    return url

def get_params(params_to_add = None):
    '''
    Метод формирует словарь параметров запроса по умолчанию. Необязательный параметр
    позволяет добавить параметры или перезаписать
    :param params_to_add: параметры в виде словаря вида {'param': value}
    :return: словарь с параметрами запроса
    '''
    params = \
                {
                    'access_token': default_token,
                    'user_id': default_id,
                    'v': '5.107'
                }
    if params_to_add:
        params.update(params_to_add)
    return params

def make_request(method, params_to_add = None):
    '''
    Принимает метод, делает запрос к апи, возвращает сырой ответ
    :param method: метод АПИ ВК
    :param params_to_add: необязательно. Допольнительные параметры запроса
    :return: ответ метода ВК
    '''
    url = make_url(method)
    params = get_params(params_to_add)
    response = requests.get(url, params)
    if response.status_code == 200:
        return response
    else:
        raise Exception


def get_user_groups(user_id):

    '''
    Запрашивaет список групп, в которых состоит юзер
    :param user_id: id юзера
    :return: list со списком групп
    '''

    try:
        response = make_request('groups.get',{'user_id':user_id})
        print(f' > идет запрос к списку групп {user_id}')
        user_groups_list = response.json()['response']['items']
        print(f' + запрос успешен')
        return user_groups_list
    except:
        print(f' - Запрос к пользователю {user_id} не удался')
        print(response.json()['error']['error_msg'])

def get_friends_list(user_id):
    '''
    Запрашивает список id друзей пользователя.
    :param user_id: id юзера
    :return: list со списком друзей
    '''

    response = make_request('friends.get',{'user_id':user_id})
    print(f' > идет запрос к списку друзей {user_id}')
    friends_list = response.json()['response']['items']
    return friends_list

def all_friends_groups_set(friends_list):
    '''
    Запрашивает список групп, в которых состоят друзья пользователя
    Собирает уникальные значения
    :param friends_list: список друзей
    :return: set
    '''
    all_groups = []
    timer = len(friends_list)+1
    timer_count = 1
    for friend in friends_list:
        print(f'Запрос {timer_count}/{timer}')
        timer_count += 1
        one_user_groups = get_user_groups(friend)
        sleep(SLEEP)
        if one_user_groups == None:
            continue
        all_groups.extend(one_user_groups)
    all_groups_unique = set(all_groups)
    return all_groups_unique


def format_res_to_json(unique_groups_of_user):
    '''
    Получает на вход список id уникальных групп
    Запрашивает информацию о группах
    Формирует json
    :param unique_groups_of_user: список id груп
    :return: json
    '''
    unique_groups_of_user = list(unique_groups_of_user)
    group_string = ','.join(str(x) for x in unique_groups_of_user)
    response = make_request('groups.getById',{'group_ids': group_string,'fields': 'members_count'})
    groups_info = response.json()['response']
    final_dict = []

    for i in groups_info:
        try:
            final_dict.append({'name': i['name'], 'gid': i['id'], 'members_count': i['members_count']})
        except:
            print(f' - Запрос к группе', i['name'], 'не удался')
            print(response.json()['error']['error_msg'])
    result = json.dumps(final_dict, ensure_ascii=False)
    return result

def start(user_id, api_token):
    '''
    Вычитает из множества групп юзера множество групп друзей
    :param user_id:
    :param api_token:
    :return: возвращает итоговый json, пишет его в файл
    '''
    global default_id
    default_id = user_id
    global default_token
    default_token = api_token
    one_user_groups = set(get_user_groups(user_id))
    users_friends_groups = all_friends_groups_set(get_friends_list(user_id))
    unique_groups_of_user = one_user_groups - users_friends_groups
    final_result = format_res_to_json(unique_groups_of_user)
    print(final_result)
    with open ('groups.json', 'w') as res_file:
        res_file.write(final_result)
    return final_result

