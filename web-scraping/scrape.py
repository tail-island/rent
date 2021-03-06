import pandas as pd
import re
import requests

from bs4 import BeautifulSoup
from funcy import first, keep, last, mapcat
from time import sleep
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse


URLS = (('https://suumo.jp/jj/chintai/kensaku/FR301FB001/?ar=030&bs=040&ta=13&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=',
         'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13101&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&pc=50'),
        ('https://suumo.jp/jj/chintai/kensaku/FR301FB001/?ar=030&bs=040&ta=14&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=',
         'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=14&sc=14101&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&pc=50'),
        ('https://suumo.jp/jj/chintai/kensaku/FR301FB001/?ar=030&bs=040&ta=11&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=',
         'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=11&sc=11101&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&pc=50'),
        ('https://suumo.jp/jj/chintai/kensaku/FR301FB001/?ar=030&bs=040&ta=12&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=',
         'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=12&sc=12101&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&pc=50'),
        ('https://suumo.jp/jj/chintai/kensaku/FR301FB001/?ar=030&bs=040&ta=08&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=',
         'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=08&sc=08201&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&pc=50'),
        ('https://suumo.jp/jj/chintai/kensaku/FR301FB001/?ar=030&bs=040&ta=09&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=',
         'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=09&sc=09201&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&pc=50'),
        ('https://suumo.jp/jj/chintai/kensaku/FR301FB001/?ar=030&bs=040&ta=10&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=',
         'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=10&sc=10201&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&pc=50'))


def get_soup(url):
    sleeping_time = 1

    while True:
        try:
            sleep(sleeping_time)

            html = requests.get(url)
            html.encoding = 'UTF8'

            break

        except requests.exceptions.ConnectionError:
            print('requests.exceptions.ConnectionError')
            sleeping_time *= 2
            continue

    return BeautifulSoup(html.text, 'html.parser')


def get_municipalities(condition):
    return keep(lambda input_element: input_element.get('value'),
                condition.select('.searchitem input[type="checkbox"]'))


def get_property_urls(condition_url, list_url):
    url = urlparse(list_url)
    query = parse_qs(url.query)
    query['sc'] = tuple(get_municipalities(get_soup(condition_url)))

    for i in range(1, int(last(get_soup(urlunparse(url._replace(query=urlencode(query, doseq=True)))).select('ol.pagination-parts > li')).select_one('a').get_text().strip())):
        query['page'] = i

        for a in get_soup(urlunparse(url._replace(query=urlencode(query, doseq=True)))).select('tr.js-cassette_link a.js-cassette_link_href'):
            yield urljoin('https://suumo.jp', a['href'])


def get_rent(property):
    s = property.select_one('div.section_h1-body div.property_view_note-info').get_text().strip().split()[0]

    return int(float(re.search(r'([\d.]+)??????', s).group(1)) * 10000)


def get_management_fee(property):
    s = property.select_one('div.section_h1-body div.property_view_note-info').get_text().strip().split()[2]
    m = re.search(r'(\d+)???', s)

    if not m:
        return 0

    return int(m.group(1))


def get_security_deposit(property, rent):
    s = property.select_one('div.section_h1-body div.property_view_note-info').get_text().strip().split()[4]
    m = re.search(r'([\d.]+)??????', s)

    if not m:
        return 0

    return int(float(m.group(1)) * 10000) / rent


def get_key_money(property, rent):
    s = property.select_one('div.section_h1-body div.property_view_note-info').get_text().strip().split()[6]
    m = re.search(r'([\d.]+)??????', s)

    if not m:
        return 0

    return int(float(m.group(1)) * 10000) / rent


def get_table_specification(property, css_selector, name):
    th = first(filter(lambda th: th.get_text().strip() == name, property.select(f'{css_selector} th')))

    if not th:
        return '-'

    td = first(filter(lambda sibling: sibling != '\n', th.next_siblings))

    return td.get_text().strip()


def get_property_specifications(url):
    property = get_soup(url)

    return (url,
            property.select_one('div.section_h1 h1.section_h1-header-title').get_text().strip(),  # ??????
            get_rent(property) + get_management_fee(property),  # ?????? + ?????????????????????
            get_security_deposit(property, get_rent(property)),  # ??????
            get_key_money(property, get_rent(property)),  # ??????
            get_table_specification(property, 'table.property_view_table', '?????????'),
            get_table_specification(property, 'table.property_view_table', '?????????'),
            get_table_specification(property, 'table.property_view_table', '?????????'),
            get_table_specification(property, 'table.property_view_table', '????????????'),
            get_table_specification(property, 'table.property_view_table', '?????????'),
            get_table_specification(property, 'table.property_view_table', '???'),
            get_table_specification(property, 'table.property_view_table', '??????'),
            get_table_specification(property, 'table.property_view_table', '????????????'),
            first(filter(lambda sibling: sibling != '\n', property.select_one('div#contents h2').next_siblings)).select_one('li').get_text().strip(),  # ????????????????????????
            get_table_specification(property, 'table.table_gaiyou', '???????????????'),
            get_table_specification(property, 'table.table_gaiyou', '??????'),
            get_table_specification(property, 'table.table_gaiyou', '??????'),
            get_table_specification(property, 'table.table_gaiyou', '?????????'),
            get_table_specification(property, 'table.table_gaiyou', '??????'),
            get_table_specification(property, 'table.table_gaiyou', '?????????'),
            get_table_specification(property, 'table.table_gaiyou', '??????'),
            get_table_specification(property, 'table.table_gaiyou', '????????????'),
            get_table_specification(property, 'table.table_gaiyou', '??????'),
            get_table_specification(property, 'table.table_gaiyou', '?????????????????????????????????'),
            get_table_specification(property, 'table.table_gaiyou', 'SUUMO???????????????'),
            get_table_specification(property, 'table.table_gaiyou', '?????????'),
            get_table_specification(property, 'table.table_gaiyou', '???????????????'),
            get_table_specification(property, 'table.table_gaiyou', '???????????????'),
            get_table_specification(property, 'table.table_gaiyou', '??????'))


def get_rows():
    result = []

    for i, url in enumerate(mapcat(lambda urls: get_property_urls(*urls), URLS)):
        print(i, url)

        try:
            specifications = get_property_specifications(url)
            result.append(specifications)

            print(specifications[1:])

        except AttributeError:
            # SUUMO????????????????????????????????????HTML???????????????????????????AttributeError??????????????????
            # ????????????????????????????????????????????????????????????SUUMO?????????????????????????????????????????????
            continue

    return result


dataFrame = pd.DataFrame(get_rows(),
                         columns=('URL',
                                  '??????',
                                  '?????? + ?????????????????????',
                                  '??????', '??????',
                                  '?????????', '?????????',
                                  '?????????', '????????????',
                                  '?????????', '???',
                                  '??????', '????????????',
                                  '????????????????????????',
                                  '???????????????',
                                  '??????',
                                  '??????',
                                  '?????????',
                                  '??????',
                                  '?????????',
                                  '??????',
                                  '????????????',
                                  '??????',
                                  '?????????????????????????????????',
                                  'SUUMO???????????????',
                                  '?????????',
                                  '???????????????',
                                  '???????????????',
                                  '??????'))

dataFrame.to_csv('data/rent-raw.csv')
