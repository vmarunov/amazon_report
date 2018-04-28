#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


def get_layout(document, page_no):
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
    page = pages[page_no - 1]
    interpreter.process_page(page)
    layout = device.get_result()
    return layout


def get_elements(layout, clazz):
    result = []

    for elem in iter(layout):
        if isinstance(elem, clazz):
            result.append(elem)
        elif isinstance(elem, collections.Iterable):
            result.extend(get_elements(elem, clazz))

    return result


def start(file_name, page):
    try:
        with open(file_name, 'rb') as fp:
            document = open_pdf(fp)
            layout = get_layout(document, page)
            els = get_elements(layout, LTTextLineHorizontal)
            balance = BalancePage(els).get_balance()
            print(balance)
    except IOError:
        print('Unable to open file {}'.format(file_name))


if __name__ == '__main__':
    # 2014/50
    # 2015/51
    fn = 'data/AMZN_2016.pdf'
    pg = 46
    if len(sys.argv) > 1:
        fn = sys.argv[1]
    if len(sys.argv) > 2:
        pg = int(sys.argv[2])
    start(fn, pg)
