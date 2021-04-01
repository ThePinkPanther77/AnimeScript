import re
import sqlite3
import ssl
import urllib.error
import urllib.parse
import urllib.request
import subprocess
import pyperclip
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import webbrowser

find_list = list()
select_list = list()
find_dic = dict()
select_dic = dict()
find_cnt_dic = dict()
select_cnt_dic = dict()
show_dic = dict()
search = dict()
search['type'] = 'anime'

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def create():
    con = sqlite3.connect('anime_database.db')
    cur = con.cursor()
    cur.execute('''
    CREATE TABLE  IF NOT EXISTS Favourite (
        F_name TEXT,
        F_URL TEXT
    )''')


def find(add_to):
    while True:
        find_cnt = 1
        print('Enter the', search['type'], 'name.')
        search['s'] = input()
        print()

        url = 'https://anime-list9.site/search?' + urllib.parse.urlencode(search)
        req = requests.get(url).text
        a = BeautifulSoup(req, 'html.parser')
        b = a('a')
        try:
            for i in b:
                i = str(i).split(',')
                for j in i:
                    if re.search('(href=".*" title=".*")', j):
                        c = re.findall('href="(.*)" title="(.*)"', j)
                        find_list.append(c)

            for i in find_list:
                if re.search('(دانلود انیمه .*)', i[0][1]):
                    e = i[0][1].replace('دانلود انیمه ', '')
                    find_dic[e] = i[0][0]
            if len(find_dic) > 0:
                break
            else:
                print("No search results for this", search['type'], ".")
                print()
                continue
        except:
            print("Something went wrong.")
            continue

    print("Search results:")
    for i in find_dic:
        find_cnt_dic[find_cnt] = i
        print(find_cnt, i)
        find_cnt += 1
    print()
    find_bool = True
    while find_bool:
        print('Choose an', search['type'], 'from the list:')
        try:
            n = int(input())
        except:
            print('Enter a number.')
            continue
        if n in find_cnt_dic and find_cnt_dic[n] in find_dic:
            url2 = find_dic[find_cnt_dic[n]]
            if add_to:
                name2 = find_cnt_dic[n]
                return url2, name2
            else:
                return url2

        else:
            print()
            print("The name is not from the list.")


def select(url2):
    select_cnt = 1

    PATTERN = r"""data\s*:\s*{\s*p\s*:\s*(\d+)\s*,\s*p2\s*:\s*(\d+)\s*},"""

    req = requests.get(url=url2)

    p, p2 = re.findall(PATTERN, req.content.decode())[0]

    base_url = "https://anime-list9.site/ajax-dlink/?p=%s&p2=%s" % (p, p2)

    req = requests.get(url=base_url)

    res = [unquote(i) for i in re.findall("href='(.*?)'", req.content.decode())]

    urls, urls_by_qual = [], {}
    for i in res:
        x = re.sub(r'\\', '', i)
        if '?dir' in x and '//cf' in x:
            urls.append(x)
            quality = re.findall('/(\d+p)/', x)[0]
            urls_by_qual[quality] = urls_by_qual.get(quality, [])
            urls_by_qual[quality].append(x)
        elif 'cf' in x:
            urls.append(x)
            quality = re.findall('/(\d+p)/', x)[0]
            urls_by_qual[quality] = urls_by_qual.get(quality, [])
            urls_by_qual[quality].append(x)

    while True:
        print("Enter the resolution you want:")
        print('1 480p')
        print('2 720p')
        print('3 1080p')
        res = input()
        if res == '1' or res == '2' or res == '3':
            print()
            for i in urls_by_qual:
                for j in urls_by_qual[i]:
                    if res == '1':
                        if re.search('(http.*480p.*)', j):
                            select_list.append(j)
                    elif res == '2':
                        if re.search('(http.*720p.*)', j):
                            select_list.append(j)
                    elif res == '3':
                        if re.search('(http.*1080p.*)', j):
                            select_list.append(j)

            for i in select_list:
                select_dic[select_cnt] = i
                select_cnt += 1

        else:
            print('No such resolution.')
            continue

        print("Search results:")
        for i in select_dic:
            if i > int(len(select_list) / 2):
                if re.search('.*mkv', select_dic[i - int(len(select_list) / 2)]):
                    print(i - int(len(select_list) / 2), 'Episode', i - int(len(select_list) / 2))
                else:
                    print(i - int(len(select_list) / 2), 'Episodes',
                          re.findall('.*p/([-0-9]*)', select_dic[i - int(len(select_list) / 2)])[0])
        print()

        print('Choose an episode from the list.')
        while True:
            try:
                n2 = int(input())
            except:
                print('Enter a number.')
                continue
            if n2 in select_dic:
                n2 - int(len(select_list) / 2)
                return select_dic[n2]
            else:
                print()
                print("The episode does not exist.")


def add(name, url):
    con = sqlite3.connect('anime_database.db')
    cur = con.cursor()
    cur.execute('INSERT OR IGNORE INTO Favourite (F_Name,F_URL) VALUES ( ?, ?)', (name, url))
    con.commit()


def show():
    show_cnt = 1
    con = sqlite3.connect('anime_database.db')
    cur = con.cursor()
    cur.execute('SELECT F_name FROM Favourite')
    show_list = cur.fetchall()
    if len(show_list) == 0:
        print('Empty list.')
        print()
        return
    for i in show_list:
        print(show_cnt, i[0])
        show_dic[show_cnt] = i[0]
        show_cnt += 1
    while True:
        print()
        print('Choose a', search['type'], 'from the list.')
        show_num = int(input())
        if show_num in show_dic:
            show_name = show_dic[show_num]
            break
        else:
            print('Wrong number.')
            continue
    cur.execute('SELECT F_URL FROM Favourite WHERE F_name=?', (show_name,))
    show_url = cur.fetchone()[0]
    ep_url = select(show_url)
    print('The URL:')
    print(ep_url)
    pyperclip.copy(ep_url)
    print('Do you want to download it using your defult browser? [y/n]')
    if input() == 'y':
        webbrowser.open(ep_url)


def remove():
    remove_cnt = 1
    con = sqlite3.connect('anime_database.db')
    cur = con.cursor()
    cur.execute('SELECT F_name FROM Favourite')
    remove_list = cur.fetchall()
    if len(remove_list) == 0:
        print('Empty list.')
        print()
        return
    for i in remove_list:
        print(remove_cnt, i[0])
        show_dic[remove_cnt] = i[0]
        remove_cnt += 1
    while True:
        print()
        print('Choose a', search['type'], 'from the list.')
        show_num = int(input())
        if show_num in show_dic:
            remove_name = show_dic[show_num]
            break
        else:
            print('Wrong number.')
            continue
    cur.execute('DELETE FROM Favourite WHERE F_name=?', (remove_name,))
    con.commit()
    print('Done.')
    return


# print("Enter the type:")
# search['type']=input()

def main():
    while True:
        create()
        cont = False
        big_series = False
        print('1 Search for', search['type'], '.')
        print('2 Add', search['type'], 'to favourite.')
        print('3 Remove', search['type'], 'from your favourite list.')
        print('4 Download from favourite', search['type'], 'list.')
        ans = input()
        print()
        if ans == '1':
            add_to = False
            url = find(add_to)
            url2 = select(url)
            print('The URL:')
            print(url2)
            pyperclip.copy(url2)
            print('Do you want to download it using your defult browser? [y/n]')
            if input() == 'y':
                webbrowser.open(url2)

        elif ans == '2':
            add_to = True
            url, name2 = find(add_to)
            add(name2, url)
            print('Done.')
            print()

        elif ans == '3':
            remove()
        elif ans == '4':
            show()


        else:
            print('Enter a number from the list.')
            continue

        while True:
            print("Want to search for another", search['type'], "?[y/n]")
            ans = input()
            if ans == 'y':
                find_list.clear()
                select_list.clear()
                find_dic.clear()
                select_dic.clear()
                find_cnt_dic.clear()
                select_cnt_dic.clear()
                show_dic.clear()
                cont = True
                big_series = False
                break
            elif ans == 'n':
                break
            else:
                print('Not a valid answer.')
                continue
        if cont:
            continue
        else:
            break


if __name__ == '__main__':
    main()
