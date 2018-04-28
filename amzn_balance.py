#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
import collections

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams
from pdfminer.layout import LTTextLineHorizontal
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from balance_page import BalancePage


def open_pdf(file_obj):
    parser = PDFParser(file_obj)
    document = PDFDocument(parser)
    if document.is_extractable:
        return document


def search_balance_page(document):
    laparams = LAParams(
        line_overlap=0.5,
        char_margin=1.0,
        line_margin=0.5,
        word_margin=0.1,
        boxes_flow=0.5)
    rsrcmgr = PDFResourceManager()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = list(PDFPage.create_pages(document))
    for n, page in enumerate(pages):
        interpreter.process_page(page)
        layout = device.get_result()
        els = filter(
            lambda el: el.get_text().strip(' \n') != '',
            get_elements(layout, LTTextLineHorizontal))
        if len(els) > 2 \
                and els[0].get_text().startswith('AMAZON.COM, INC.') \
                and els[1].get_text().startswith('CONSOLIDATED BALANCE SHEETS'):
            return els
    return None


def get_elements(layout, clazz):
    result = []

    for elem in iter(layout):
        if isinstance(elem, clazz):
            result.append(elem)
        elif isinstance(elem, collections.Iterable):
            result.extend(get_elements(elem, clazz))

    return result


def start(file_name):
    try:
        with open(file_name, 'rb') as fp:
            document = open_pdf(fp)
            els = search_balance_page(document)
            balance = BalancePage(els).get_balance()
            print(json.dumps(balance, indent=4))
    except IOError:
        print('Unable to open file {}'.format(file_name))


if __name__ == '__main__':
    # 2014/50
    # 2015/51
    fn = 'data/AMZN_2016.pdf'
    if len(sys.argv) > 1:
        fn = sys.argv[1]
    start(fn)
