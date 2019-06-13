import json
import requests
import xml.etree.ElementTree as ET
import chardet
from django.utils.http import urlquote

URL = 'http://opac.lib.whu.edu.cn/X'
ALPHA_URL = 'http://api.lib.whu.edu.cn/aleph-x/bor/oper'
PAGE_SIZE = 10
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
        self.lib = 'whu01'
        self.session = self.login()
        self.page_size = PAGE_SIZE
        self.alpha_psw = alpha_psw

    def login(self):
        '''
        管理员用户获取session
        :return:
        '''
        params = {
            "op": "login",
            "user_name": self.un,
            "user_password": self.pw,
            "library": self.lib
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
            "library": "WHU50"
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
            "library": "whu50",
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
                              'book_info': self.z13_to_dict(hold.find('z13'))})
        for loan in loans:
            loan_list.append({'loan_info': self.z36_to_dict(loan.find('z36')),
                              'book_info': self.z13_to_dict(loan.find('z13'))})
        return {
            'loan': loan_list,
            'hold': hold_list
        }

    def find(self, request=''):
        '''
        默认关键词检索
        :param request:
        :return:
        '''
        params = {
            "op": "find",
            "request": request,
            "base": self.lib,
            "session": self.session,
            "code": "wrd"
        }
        response = requests.request('GET', url=self.url, headers=self.headers, params=params)
        et = ET.fromstring(response.content.decode('utf-8'))
        self.session = et.find('session-id').text
        try:
            err_message = et.find('error').text
            print(err_message)
            return False
        except AttributeError as _:
            return {'set_number': et.find('set_number').text,
                    'no_records': int(et.find('no_records').text),
                    'no_entries': int(et.find('no_entries').text)}

    def present(self, set_number, set_entry):
        '''
        查询结果显示
        :param set_number:
        :param set_entry:
        :return:
        '''
        params = {
            "op": "present",
            "set_number": set_number,
            "set_entry": '%d-%d' % (set_entry, set_entry + self.page_size - 1),
            "base": self.lib,
            "session": self.session
        }
        response = requests.request('GET', url=self.url, headers=self.headers, params=params)
        et = ET.fromstring(response.content.decode('utf-8'))
        self.session = et.find('session-id').text
        records = et.findall('record')
        books = []
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
        return books

    def circ_status(self, sys_no):
        '''
        馆藏信息查询
        :param sys_no:
        :return:
        '''
        params = {
            "op": "circ-status",
            "sys_no": sys_no,
            "library": self.lib,
            "session": self.session
        }
        response = requests.request('GET', url=self.url, headers=self.headers, params=params)
        et = ET.fromstring(response.content.decode('utf-8'))
        self.session = et.find('session-id').text
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
            book['rfid'] = 'http://opac.lib.whu.edu.cn/rfid-pos/graph.aspx?bookid=' + book['bar_code']
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
            "library": "whu50",
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
            return {'result': 0}

    def hold_req_nlc(self, bar_code, bor_id, pickup_loc):
        '''
        图书预约
        :param bar_code:
        :param bor_id:
        :param pickup_loc:
        :return:
        '''
        params = {
            "op": "hold-req-cancel",
            "item_barcode": bar_code,
            "library": "whu50",
            "id": bor_id,
            "pickup_loc": pickup_loc,
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
            "library": "whu50",
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
    xi.x_bor_info(bor_id='2016302590080')
    xi.loan_history_detail(bor_id='2016302590080')
    xi.bor_info(uid='2016302590080')
    xi.renew(bor_id='2016302590080', bar_code='101100356208')
    auth = xi.bor_auth_valid(uid='2015302590005', verification='180856')
    xi.hold_req_nlc(bor_id=auth['bor_id'], bar_code='101102121871', pickup_loc='XX')
    set_info = xi.find(request='高等数学')
    present_info = xi.present(set_number=set_info['set_number'], set_entry=1)
    xi.circ_status(sys_no=present_info[0]['doc_number'])
    xi.bor_auth(uid='2015302590005', verification='180856')

