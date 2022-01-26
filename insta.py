from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random
from datetime import datetime,timedelta,date
import json
import urllib.request

# Функция аутетинтификации
def auth(username, password, browser):
    try:
        # Авторизация
        browser.get('https://www.instagram.com')
        time.sleep(random.randrange(3, 5))

        username_input = browser.find_element_by_name('username')
        username_input.clear()
        username_input.send_keys(username)

        time.sleep(2)

        password_input = browser.find_element_by_name('password')
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(5)
    except Exception as ex:
        print(ex)
        browser.close()
        browser.quit()


# Получение ссылок на все посты в профиле
def posts_search(browser):
    profile = ''
    profile = input('Введите название профиля\n')
    # Поиск всех постов
    try:
        browser.get(f'https://www.instagram.com/%s/' % profile)
        time.sleep(5)

        # Промежуток в данном цикле можно менять в зависимости от необходимого количества получаемых постов
        for i in range(1, 4):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randrange(3, 5))

        hrefs = browser.find_elements_by_tag_name('a')
        posts_urls = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]

        return posts_urls



    except Exception as ex:
        print(ex)
        browser.close()
        browser.quit()

#Преобразования даты и времени datetime-html в дату и время в строке
def datetime_to_date(string):
    a = list(range(0,4))
    string = string.split('T')
    string[0] = datetime.strptime(string[0], '%Y-%m-%d')
    string[1] = string[1].split('.')
    string[1][0] = datetime.strptime(string[1][0], '%H:%M:%S') + timedelta(hours=4)
    if string[1][0].hour in a:
        string[0] + timedelta(days=1)

    string = datetime.strftime(string[0], '%d-%m-%Y') + ' ' + datetime.strftime(string[1][0], '%H:%M:%S')
    return string

#Получение всех комментариев к одному посту
def comments_search(post_url, browser):
    df_info_comments = pd.DataFrame()
    comments_value = []
    comments_autor = []
    comments_date = []

    for i in range(len(post_url)):
        browser.get(post_url[i])
        time.sleep(1)
        comments_autor.append(post_url[i])  # Автор комментария
        comments_value.append(post_url[i])  # Текст комментария
        comments_date.append(post_url[i])  # Дата комментария
        qwerty = 0
        comment_scroll = True
        while comment_scroll:
            try:
                element = WebDriverWait(browser, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "dCJp8.afkep"))
                )
                element.click()
            except:
                print("Кнопка прокрутки не обнаружена")
                comment_scroll = False
        # Получение всех комментариев к посту
        comment_collect = True
        comment = 1
        while comment_collect:
            try:
                comments_value.append(browser.find_element_by_xpath(
                    '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/ul[%d]/div/li/div/div[1]/div[2]/span' % comment).text)
                comments_autor.append(browser.find_element_by_xpath(
                    '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/ul[%d]/div/li/div/div[1]/div[2]/h3/div/span/a' % comment).text)
                date = (browser.find_element_by_xpath(
                    '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/ul[%d]/div/li/div/div[1]/div[2]/div/div/a/time' % comment).get_attribute('datetime'))

                comments_date.append(datetime_to_date(date))

                print('время', comments_date)
                print('Кол-во обработанных комментариев = ', comment)
                comment += 1

            except:
                comment_collect = False

    df_info_comments['Autor'] = comments_autor
    df_info_comments['Value'] = comments_value
    df_info_comments['Date'] = comments_date

    df_info_comments.to_csv('comments_info')


# Парсинг всех комментариев из необходимого профиля
def pars_all_comments(browser):
    comments_search(posts_search(browser), browser)


# Парсинг комментариев из одного поста
def pars_comments_for_post(browser):
    post_search = []
    post_search.append(input('Введите ссылку на пост: '))
    comments_search(post_search, browser)

# Отправление сообщения пользователю в директ
def send_message(msg):
    # ищем кнопку отправить
    message = browser.find_element_by_class_name('_862NM ')
    message.click()
    time.sleep(2)

    try:

        # Not now кнопка
        browser.find_element_by_class_name('HoLwm ').click()
        time.sleep(1)

    except:

        _ = 42

    # ищем поле
    mbox = browser.find_element_by_tag_name('textarea')
    mbox.send_keys(msg)
    mbox.send_keys(Keys.RETURN)
    time.sleep(1.2)

# Отправление сообщения под пост
def send_message_in_comments(msg):

    # поле для текста
    commentArea = browser.find_element_by_class_name('Ypffh')
    commentArea.click()
    commentArea = browser.find_element_by_class_name('Ypffh')
    commentArea.send_keys(msg)

    # кнопка отправить
    send_button = browser.find_element_by_class_name("yWX7d.y3zKF")
    send_button.click()

# Получение информации об 1 публикации
def pars_posts_info():
    posts_url = posts_search(browser)

    post_date = []
    post_img = []
    post_value = []
    post_hastags = []
    post_url = []
    for i in range(5):
        post_url.append(posts_url[i])
        browser.get(posts_url[i])
        time.sleep(1)

        #Дата публикации
        date = browser.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[2]/a/time').get_attribute('datetime')
        post_date.append(datetime_to_date(date))

        #Текст поста
        value = []
        try:
            browser.find_element('br')
            br_value = True
            br_i = 1
            try:
                while br_value:
                    value.append(browser.find_element_by_xpath(
                        '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span/br[%d]' % br_i).text)
                    br_i += 1
            except:
                br_value = False
            post_value.append(value)


        except:
            post_value.append(browser.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span').text)

        #Фотографии
        img = []
        try:
            browser.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/div/div[1]/article/div[2]/div/div[1]/div[2]/div/div/div/ul/li[2]')
            img_value = True
            img_i = 2
            try:
                while img_value:
                    img.append(browser.find_element_by_xpath(
                        '//*[@id="react-root"]/section/main/div/div[1]/article/div[2]/div/div[1]/div[2]/div/div/div/ul/li[%d]/div/div/div/div[1]/div[1]/img' % img_i).get_attribute('src'))
                    img_i += 1
            except:
                img_value = False
            post_img.append(img)

        except:
            try:
                post_img.append(browser.find_element_by_xpath(
                    '//*[@id="react-root"]/section/main/div/div[1]/article/div[2]/div/div/div[1]/img').get_attribute('src'))
            except:
                post_img.append('Фото материалы не обнаружены')

        #Хештеги
        hashtags = []
        try:
            browser.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span/a[1]')
            hashtags_value = True
            hash_i  = 1
            try:
                while hashtags_value:
                    hashtags.append(browser.find_element_by_xpath(
                        '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/div[1]/ul/div/li/div/div/div[2]/span/a[%d]' % hash_i).text)
                    hash_i += 1
            except:
                hashtags_value = False
            post_hastags.append(hashtags)
        except:
            post_hastags.append('Хештегов нет')

    df_info_posts = pd.DataFrame()
    df_info_posts['Date'] = post_date
    df_info_posts['Img'] = post_img
    df_info_posts['Value'] = post_value
    df_info_posts['Hashtags'] = post_hastags
    df_info_posts['Link'] = post_url
    df_info_posts.to_csv('posts_info')

# получить все сообщения из директа
def get_messages_from_direct():

    df = pd.DataFrame()
    browser.get('https://www.instagram.com/direct/inbox/')

    # собираем ники пользователей, чтобы в дальнейшем пройтись по каждому из них
    users = []
    users_collect = True
    user = 1

    try:

        # кнопка включение/отключения уведомлений
        not_now_button = browser.find_element_by_class_name('HoLwm')
        not_now_button.click()
        time.sleep(1)

    except:

        # нет кнопки выключить уведомления, ничего страшного
        _ = 42

    while users_collect:

        try:
            users.append(browser.find_element_by_xpath(
                '//*[@id="react-root"]/section/div/div[2]/div/div/div[1]/div[2]/div/div/div/div/div[%s]/a/div/div[2]/div/div/div/div/div' % user).text)

            user += 1

        except:

            users_collect = False

    messages = []

    # по каждому пользователю проходимся в директе
    for username in range(0, len(users)):

        browser.get('https://www.instagram.com/' + users[username])
        send_button = browser.find_element_by_class_name('_8A5w5')
        send_button.click()
        time.sleep(1)

        try:

            # кнопка not now
            browser.find_element_by_class_name('HoLwm').click()
            time.sleep(1)

        except:

            _ = 42

        #TODO ДОБАВИТЬ СКРОЛЛ ДО КОНЦА ЛИЧКИ

        messages.append([])
        messages_collect = True
        message = 1

        while messages_collect:

            print('messages collect')
            print(message)

            try:

                # ячейка по типу Среду 14:88
                text = browser.find_element_by_xpath(
                        '//*[@id="react-root"]/section/div/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div[%s]/div/div' % message).text
                if text != '':
                    messages[username].append(text)
                    message += 1
                else:

                    # ячейка с сообщением
                    text = browser.find_element_by_xpath(
                            '//*[@id="react-root"]/section/div/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div[%s]/div[2]/div/div/div/div/div/div/div/div/span' % message).text
                    if text != '':
                        messages[username].append(text)
                        message += 1

            except:

                messages_collect = False



# Для работы необходим ChromeDriver
# и задать путь к драйверу, например
# browser = webdriver.Chrome('F:\deep\chrome_driver\chromedriver.exe')
browser = webdriver.Chrome()

#Авторизация в аккаунте instagram
username = input('Введите имя пользователя: ')
password = input('Введите пароль: ')
auth(username, password, browser)

# 1 - Получение информации о всех постах в instagram аккаунте
# 2 - Получение информации о всех комментариях под всеми постами
# 3 - Получение информации о всех комментариях под одним постом
# 4 - Отправка сообщения в директ введенному пользователю
# 5 - Отправка комментария к определенному посту
# 6 - Сбор всех сообщений из директа пользователя (Осталось доделать)

move = int(input('Введите номер действия от 1 до 6: '))

if move == 1:
    pars_posts_info()

elif move == 2:
    comments_search(posts_search(browser), browser)

elif move == 3:
    pars_comments_for_post(browser)

elif move == 4:
    url = 'https://instagram.com/' + input('Введите имя пользователя, которому вы хотите отправить сообщение: ')
    browser.get(url)
    time.sleep(2)

    print("Введите сообщение для пользователя: ")
    msg = input()
    send_message(msg)

elif move == 5:
    print("Введите ссылку на пост: ")
    url = input()
    browser.get(url)
    time.sleep(2)

    print("Введите текст комментария: ")
    msg = input()

    send_message_in_comments(msg)

elif move == 6:
    get_messages_from_direct(browser)


browser.close()
browser.quit()