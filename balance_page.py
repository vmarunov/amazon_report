# -*- coding: utf-8 -*-


INDENT_CHARS = 2

def is_filled(element):
    string = element.get_text().strip(' \n')
    return string != '' and string != '$'


class Balance(object):

    def __init__(self):
        self.data = dict()
        self.level = self.data

    def add_root(self, name):
        self.data[name] = {}
        self.level = self.data[name]

    def add_level(self):


class BalancePage(object):

    def __init__(self, els):
        self.els = filter(is_filled, els)
        self.rows = []
        self.y_accuracy = None
        self.x_range = None
        self.indent = None
        self._format()

    def get_balance(self):
        balance = dict()
        years = None
        current = None

        for row in self.rows:
            data = self.get_data(row)
            if years is None and len(data) == 2:
                years = data
                continue
            if data[0].startswith('Total'):
                continue
            if len(data) == 1 and (1):



        return {'years': years, 'balance': balance}




    def _format(self):
        least_font_height = min(el.y1 - el.y0 for el in self.els)
        least_font_width = min(
            (el.x1 - el.x0) / len(el.get_text()) for el in self.els)
        self.indent = INDENT_CHARS * least_font_width
        self.y_accuracy = least_font_height / 2.1
        self.x_range = (
            min(el.x0 for el in self.els),
            max(el.x1 for el in self.els))
        self._marking_rows()

    def _marking_rows(self):

        def _add_row(el):
            self.rows.append({
                'y': (el.y0, el.y1), 'data': [(el.x0, el.get_text())]})

        iterator = iter(sorted(self.els, key=lambda el: -el.y0))
        prev_element = iterator.next()
        _add_row(prev_element)
        for element in iterator:
            if (abs(prev_element.y0 - element.y0) < self.y_accuracy) and (
                    abs(prev_element.y1 - element.y1) < self.y_accuracy):
                self.rows[-1]['data'].append((element.x0, element.get_text()))
            else:
                _add_row(element)
            prev_element = element

    @staticmethod
    def get_data(row):
        return [
            data[1].strip(' \n')
            for data in sorted(row['data'], key=lambda el: el[0])]
