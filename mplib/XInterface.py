import json
import requests
import xml.etree.ElementTree as ET
import chardet
from django.utils.http import urlquote
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import re

URL = 'http://opac.lib.whu.edu.cn/X'
ALPHA_URL = 'http://api.lib.whu.edu.cn/aleph-x/bor/oper'
PAGE_SIZE = 20
HEADERS = {'Cache-Control': "no-cache", 'Postman-Token': "0f969060-6547-41d2-8fca-40a13b2a0483"}


class XInterface(object):
    def __init__(self, username, password, alpha_psw):
        '''
        :param username:
        :param password:
        :param alpha_psw:
        '''
        super().__init__()
        self.url = URL
        self.alpha_url = ALPHA_URL
        self.un = username
        self.pw = password
        self.headers = HEADERS
        self.cn_lib = 'whu01'
        self.en_lib = 'whu09'
        self.au_lib = 'whu50'
        self.session = self.login()
        self.page_size = PAGE_SIZE
        self.alpha_psw = alpha_psw
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.update_session, 'interval', seconds=3600, id='update session')
        self.scheduler.start()

    def update_session(self):
        print(str(datetime.now()) + ': Update Session')
        self.session = self.login()

    def login(self):
        '''
        管理员用户获取session
        :return:
        '''
        params = {
            "op": "login",
            "user_name": self.un,
            "user_password": self.pw,
            "library": self.cn_lib
        }
        response = requests.request('GET', url=self.url, headers=self.headers, params=params)
        et = ET.fromstring(response.content.decode('utf-8'))
        return et.find('session-id').text

    def bor_auth(self, uid, verification):
        '''
        读者认证
        :param uid:
        :param verification:
        :return: False/True
        '''
        auth_url = "https://system.lib.whu.edu.cn/auth.php"
        params = {
            "cardno": uid,
            "password": verification
        }
        response = requests.request('GET', url=auth_url, headers=self.headers, params=params)
        et = ET.fromstring(response.content.decode('utf-8'))
        self.session = et.find('session-id').text
        return et.find('result').find('retcode').text is '0'

    def bor_auth_valid(self, uid, verification):
        '''
        读者认证
        :param uid:
        :param verification:
        :return:
        '''
        params = {
            "op": "bor-auth-valid",
            "session": self.session,
            "id": uid,
            "verification": verification,
            "library": self.au_lib
        }
        response = requests.request('GET', url=self.url, headers=self.headers, params=params)
        et = ET.fromstring(response.content.decode('utf-8'))
        self.session = et.find('session-id').text
        try:
            err_message = et.find('error').text
            return {'result': 1, 'error': err_message}
        except AttributeError as _:
            return {'result': 0, 'bor_id': et.find('./z303/z303-id').text}

    def bor_info(self, uid):
        '''
        查看读者的借阅信息和预约信息
        :param uid:
        :return:
        '''
        params = {
            "op": "bor_info",
            "id": uid,
            "library": self.au_lib,
            "session": self.session
        }
        response = requests.request('GET', url=self.url, headers=self.headers, params=params)
        et = ET.fromstring(response.content.decode('utf-8'))
        self.session = et.find('session-id').text
        loan_list = []
        # fine_list = []
        hold_list = []
        loans = et.findall('item-l')
        # fines = et.findall('fine')
        holds = et.findall('item-h')
        for hold in holds:
            hold_list.append({'hold_info': self.z37_to_dict(hold.find('z37')),
                              'book_info': self.z13_to_dict(hold.find('z13')),
                              'bar_code': hold.find('./z30/z30-barcode').text})
        for loan in loans:
            loan_list.append({'loan_info': self.z36_to_dict(loan.find('z36')),
                              'book_info': self.z13_to_dict(loan.find('z13')),
                              'bar_code': loan.find('./z30/z30-barcode').text})
        return {
            'loan': loan_list,
            'hold': hold_list
        }

    def find(self, request='', code='wrd', lang='cn'):
        '''
        默认关键词检索
        :param request:
        :param code:
        :param lang:
        :return:
        '''
        lib = self.cn_lib if lang == 'cn' else self.en_lib
        params = {
            "op": "find",
            "request": request,
            "base": lib,
            # "session": self.session,
            "code": code
        }
        response = requests.request('GET', url=self.url, headers=self.headers, params=params)
        et = ET.fromstring(response.content.decode('utf-8'))
        try:
            err_message = et.find('error').text
            print(err_message)
            return False
        except AttributeError as _:
            return {'set_number': et.find('set_number').text,
                    'no_records': int(et.find('no_records').text),
                    'no_entries': int(et.find('no_entries').text)}

    def present(self, set_number, set_entry, lang='cn'):
        '''
        查询结果显示
        :param set_number:
        :param set_entry:
        :param lang:
        :return:
        '''
        lib = self.cn_lib if lang == 'cn' else self.en_lib
        params = {
            "op": "present",
            "set_number": set_number,
            "set_entry": '%d-%d' % (set_entry, set_entry + self.page_size - 1),
            "base": lib,
            # "session": self.session
        }
        response = requests.request('GET', url=self.url, headers=self.headers, params=params)
        et = ET.fromstring(response.content.decode('utf-8'))
        records = et.findall('record')
        books = []
        if lang == 'cn':
            for record in records:
                book = {}
                book['doc_number'] = record.find('doc_number').text
                title = record.find(".//varfield[@id='200']/subfield[@label='a']")
                version = record.find(".//varfield[@id='205']/subfield[@label='a']")
                publish = record.find(".//varfield[@id='210']/subfield[@label='c']")
                year = record.find(".//varfield[@id='210']/subfield[@label='d']")
                page = record.find(".//varfield[@id='215']/subfield[@label='a']")
                description = record.find(".//varfield[@id='330']/subfield[@label='a']")
                reader = record.find(".//varfield[@id='333']/subfield[@label='a']")
                theme = record.find(".//varfield[@id='606']/subfield[@label='a']")
                author = record.find(".//varfield[@id='701']/subfield[@label='a']")
                isbn = record.find(".//varfield[@id='905']/subfield[@label='s']")
                book['title'] = '' if title is None else title.text
                book['version'] = '' if version is None else version.text
                book['publish'] = '' if publish is None else publish.text
                book['year'] = '' if year is None else year.text
                book['page'] = '' if page is None else page.text
                book['description'] = '' if description is None else description.text
                book['reader'] = '' if reader is None else reader.text
                book['author'] = '' if author is None else author.text
                book['theme'] = '' if theme is None else theme.text
                book['no_call'] = '' if isbn is None else isbn.text
                books.append(book)
        else:
            for record in records:
                book = {}
                book['doc_number'] = record.find('doc_number').text
                title = record.find(".//varfield[@id='245']/subfield[@label='a']")
                version = record.find(".//varfield[@id='250']/subfield[@label='a']")
                publish = record.find(".//varfield[@id='264']/subfield[@label='a']")
                year = record.find(".//varfield[@id='264']/subfield[@label='c']")
                page = record.find(".//varfield[@id='300']/subfield[@label='a']")
                description = record.find(".//varfield[@id='505']/subfield[@label='a']")
                reader = record.find(".//varfield[@id='333']/subfield[@label='a']")
                theme = record.find(".//varfield[@id='650']/subfield[@label='a']")
                author = record.find(".//varfield[@id='100']/subfield[@label='a']")
                isbn = record.find(".//varfield[@id='905']/subfield[@label='s']")
                book['title'] = '' if title is None else title.text
                book['version'] = '' if version is None else version.text
                book['publish'] = '' if publish is None else publish.text
                book['year'] = '' if year is None else year.text
                book['page'] = '' if page is None else page.text
                book['description'] = '' if description is None else description.text
                book['reader'] = '' if reader is None else reader.text
                book['author'] = '' if author is None else author.text
                book['theme'] = '' if theme is None else theme.text
                book['no_call'] = '' if isbn is None else isbn.text
                books.append(book)
        return books

    def circ_status(self, sys_no, lang='cn'):
        '''
        馆藏信息查询
        :param sys_no:
        :param lang:
        :return:
        '''
        lib = self.cn_lib if lang == 'cn' else self.en_lib
        params = {
            "op": "circ-status",
            "sys_no": sys_no,
            "library": lib,
            # "session": self.session
        }
        response = requests.request('GET', url=self.url, headers=self.headers, params=params)
        et = ET.fromstring(response.content.decode('utf-8'))
        items = et.findall('item-data')
        books = []
        for item in items:
            book = {}
            book['loan_status'] = item.find('loan-status').text
            book['due_date'] = item.find('due-date').text
            book['due_hour'] = item.find('due-hour').text
            book['sub_library'] = item.find('sub-library').text
            book['bar_code'] = item.find('barcode').text
            book['location'] = item.find('location').text
            book['rfid'] = 'https://opac.lib.whu.edu.cn/rfid-pos/graph.aspx?bookid=' + book['bar_code']
            books.append(book)
        return books

    def renew(self, bar_code, bor_id):
        '''
        图书续借
        :param bar_code:
        :param bor_id:
        :return:
        '''
        params = {
            "op": "renew",
            "item_barcode": bar_code,
            "library": self.au_lib,
            "bor_id": bor_id,
            "session": self.session
        }
        response = requests.request('GET', url=self.url, headers=self.headers, params=params)
        et = ET.fromstring(response.content.decode('utf-8'))
        self.session = et.find('session-id').text
        try:
            reply = et.find('reply').text
            if reply == 'ok':
                return {'result': 0}
            else:
                return {'result': 1}
        except AttributeError as _:
            print(response.content.decode('utf-8'))
            return {'result': 1}

    def hold_req_nlc(self, bar_code, bor_id, pickup_loc):
        '''
        图书预约
        :param bar_code:
        :param bor_id:
        :param pickup_loc:
        :return:
        '''
        params = {
            "op": "hold-req-nlc",
            "item_barcode": bar_code,
            "library": self.au_lib,
            "id": bor_id,
            "pickup_loc": pickup_loc,
            "session": self.session
        }
        response = requests.request('GET', url=self.url, headers=self.headers, params=params)
        et = ET.fromstring(response.content.decode('utf-8'))
        self.session = et.find('session-id').text
        try:
            reply = et.find('reply').text
            if reply == 'ok':
                return {'result': 0}
            else:
                return {'result': 1}
        except AttributeError as _:
            print(response.content.decode('utf-8'))
            return {'result': 1}

    def hold_req_cancel(self, doc_number, bor_id, item_sequence, sequence):
        '''
        预约取消
        :param doc_number:
        :param bor_id:
        :param item_sequence:
        :param sequence:
        :return:
        '''
        params = {
            "op": "hold-req-cancel",
            "doc_number": doc_number,
            "library": self.au_lib,
            "id": bor_id,
            "item_sequence": item_sequence,
            "sequence": sequence,
            "session": self.session
        }
        response = requests.request('GET', url=self.url, headers=self.headers, params=params)
        et = ET.fromstring(response.content.decode('utf-8'))
        self.session = et.find('session-id').text
        try:
            err_message = et.find('error').text
            return {'result': 1, 'error': err_message}
        except AttributeError as _:
            return {'result': 0}

    def loan_history_detail(self, bor_id):
        '''
        借阅历史查询
        :param bor_id:
        :return:
        '''
        payload = 'BorForm%5Busername%5D=' + self.un + '&BorForm%5Bpassword%5D=' + self.alpha_psw + \
                  '%40wx&BorForm%5Bop%5D=loan-history-detail&BorForm%5Bbor_id%5D=' + bor_id + \
                  '&BorForm%5Bop_param%5D=&BorForm%5Bop_param2%5D=&BorForm%5Bop_param3%5D=&undefined='
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'no-cache',
            'Postman-Token': 'cd46031b-12dd-4492-98ea-197c263adf6d'
        }
        response = requests.request("POST", self.alpha_url, data=payload, headers=headers)
        result = response.json()
        return result

    def x_bor_info(self, bor_id):
        payload = 'BorForm%5Busername%5D=' + self.un + '&BorForm%5Bpassword%5D=' + self.alpha_psw + \
                  '%40wx&BorForm%5Bop%5D=bor-info&BorForm%5Bbor_id%5D=' + bor_id + \
                  '&BorForm%5Bop_param%5D=&BorForm%5Bop_param2%5D=&BorForm%5Bop_param3%5D=&undefined='
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'no-cache',
            'Postman-Token': 'cd46031b-12dd-4492-98ea-197c263adf6d'
        }
        response = requests.request("POST", self.alpha_url, data=payload, headers=headers)
        result = response.json()
        return result

    def bor_rank(self, lang='ALL', category='ALL', time='y'):
        '''
        :param lang: ALL, 01, 09
        :param category: ALL, A-Z
        :param time: y, s, m, w
        :return:
        '''
        base_url = "http://opac.lib.whu.edu.cn/opac_lcl_chi/loan_top_ten/loan"
        url = base_url + '.' + lang + '.' + category + '.' + time
        response = requests.request("GET", url)
        soup = BeautifulSoup(response.text, 'html.parser')
        rank = []
        for ol in soup.find_all('ol'):
            for item in ol.find_all('a'):
                rank.append({'doc_number': item['url'].split('&')[-1].split('=')[1],
                             'bor_num': int(item.text.split('    ')[1].split(':')[1]),
                             'title': item.text.split('    ')[0].split('(')[0],
                             'author': re.findall('\((.*?)\)', item.text.split('    ')[0])[-1].strip()})
        return rank

    @staticmethod
    def z13_to_dict(et):
        return {
            'doc_number': et.find('z13-doc-number').text,
            'year': et.find('z13-year').text,
            'no_call': et.find('z13-call-no').text,
            'author': et.find('z13-author').text,
            'title': et.find('z13-title').text,
            'publish': et.find('z13-imprint').text,
            'isbn': et.find('z13-isbn-issn').text
        }

    @staticmethod
    def z37_to_dict(et):
        return {
            'doc_number': et.find('z37-doc-number').text,
            'item_sequence': et.find('z37-item-sequence').text,
            'sequence': et.find('z37-sequence').text,
            'request_date': et.find('z37-request-date').text,
            'end_date': et.find('z37-end-request-date').text,
            'pickup_loc': et.find('z37-pickup-location').text,
            'status': et.find('z37-status').text
        }

    @staticmethod
    def z36_to_dict(et):
        return {
            'doc_number': et.find('z36-doc-number').text,
            'item_sequence': et.find('z36-item-sequence').text,
            'material': et.find('z36-material').text,
            'sub_library': et.find('z36-sub-library').text,
            'loan_date': et.find('z36-loan-date').text,
            'loan_hour': et.find('z36-loan-hour').text,
            'due_date': et.find('z36-due-date').text,
            'due_hour': et.find('z36-due-hour').text
        }

    @staticmethod
    def z31_to_dict(et):
        return {
            'doc_number': et.find('z13-doc-number').text,
            'year': et.find('z13-year').text,
            'no_call': et.find('z13-call-no').text,
            'author': et.find('z13-author').text,
            'title': et.find('z13-title').text,
            'publish': et.find('z13-imprint').text,
            'isbn': et.find('z13-isbn-issn').text
        }


if __name__ == '__main__':
    xi = XInterface(username='miniapp', password='wdlq@2019', alpha_psw='xzw2019')
    xi.circ_status(sys_no='001350497')
    xi.bor_rank()
    xi.bor_info(uid='2016302590080')
    xi.hold_req_nlc(bor_id='ID900139600', bar_code='101101976985', pickup_loc='WL')
    xi.renew(bor_id='2016302590080', bar_code='101100356208')
    auth = xi.bor_auth_valid(uid='2015302590078', verification='16797X')
    xi.loan_history_detail(bor_id='2015302590030')
    xi.x_bor_info(bor_id='2015302590078')
    set_info = xi.find(request='东野圭吾', code='wau')
    present_info = xi.present(set_number='009410', set_entry=1, lang='cn')
    set_info = xi.find(request='高等数学')
    xi.bor_auth(uid='2015302590005', verification='180856')


