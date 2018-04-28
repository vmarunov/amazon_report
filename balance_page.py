# -*- coding: utf-8 -*-
INDENT_CHARS = 2


def dict_to_tuples(data):
    if isinstance(data, dict):
        return [
            (key[1], dict_to_tuples(value))
            for key, value in sorted(data.items())]
    return data


def is_filled(element):
    string = element.get_text().strip(' \n')
    return string != '' and string != '$'


def to_num(value):
    value = value.strip(' \n').replace(',', '')
    sign = 1
    if value.startswith('('):
        sign = -1
        value = value.strip('()')
    try:
        return int(value) * sign
    except ValueError:
        return 0


def get_value(row, pos, is_num=False):
    try:
        value = row[pos].strip(' \n')
    except IndexError:
        value = ''
    return to_num(value) if is_num else value


class Balance(object):

    def __init__(self):
        self.counter = 0
        self.data = dict()
        self.level = None
        self.chain = []

    def add_root(self, row):
        name = (self.counter, get_value(row, 0))
        self.counter += 1
        self.data[name] = dict()
        self.level = self.data[name]
        self.chain = []

    def add_level(self, row):
        name = (self.counter, get_value(row, 0))
        self.counter += 1
        self.chain.append(self.level)
        self.level[name] = dict()
        self.level = self.level[name]

    def remove_level(self):
        if self.chain:
            self.level = self.chain.pop(-1)

    def add_data(self, row):
        name = (self.counter, get_value(row, 0))
        self.counter += 1
        self.level[name] = [
            get_value(row, 1, True), get_value(row, 2, True)]

    def get_balance(self):
        return dict_to_tuples(self.data)


class BalancePage(object):

    def __init__(self, els):
        self.els = filter(is_filled, els)
        self.rows = []
        self.y_accuracy = None
        self.x_min = None
        self.indent = None
        self._format()

    def get_balance(self):
        iterator = iter(self.rows[:-1])
        x_max = None
        years = None
        for row in iterator:
            data = self.get_data(row)
            if len(data) == 2:
                years = data
                x_max = row['data'][0][0]
                break
        balance = Balance()
        center = (x_max - self.x_min) / 2 + self.x_min
        items = []
        current = iterator.next()
        try:
            while True:
                next_item = iterator.next()
                items.append((
                    current,
                    next_item,
                    self.get_indent(current),
                    self.get_indent(next_item)))
                current = next_item
        except StopIteration:
            items[-1] = (items[-1][0], None, None, None)

        for row, next_row, indent, next_indent in items:
            data = self.get_data(row)
            if next_row is None:
                balance.add_data(data)
                break
            next_data = self.get_data(next_row)
            if len(next_data) == 1 and self.is_center(next_row, center):
                balance.add_data(data)
                continue
            if len(data) == 1 and self.is_center(row, center):
                balance.add_root(data)
                continue
            if (next_indent - indent) > self.indent:
                balance.add_level(data)
                continue
            if (indent - next_indent) > self.indent:
                balance.add_data(data)
                balance.remove_level()
                continue
            balance.add_data(data)
        return {'years': years, 'balance': balance.get_balance()}

    def _format(self):
        least_font_height = min(el.y1 - el.y0 for el in self.els)
        least_font_width = min(
            (el.x1 - el.x0) / len(el.get_text()) for el in self.els)
        self.indent = INDENT_CHARS * least_font_width
        self.y_accuracy = least_font_height / 2.1
        self.x_min = min(el.x0 for el in self.els)
        self._marking_rows()

    def _marking_rows(self):
        rows = []

        def _add_row(el):
            rows.append({
                'y': (el.y0, el.y1), 'data': [(el.x0, el.x1, el.get_text())]})

        iterator = iter(sorted(self.els, key=lambda el: -el.y0))
        prev_element = iterator.next()
        _add_row(prev_element)
        for element in iterator:
            if (abs(prev_element.y0 - element.y0) < self.y_accuracy) and (
                    abs(prev_element.y1 - element.y1) < self.y_accuracy):
                rows[-1]['data'].append(
                    (element.x0, element.x1, element.get_text()))
            else:
                _add_row(element)
            prev_element = element

        self.rows = [
            row for row in rows
            if not self.get_data(row)[0].startswith('Total')]

    @staticmethod
    def get_data(row):
        return [
            data[2].strip(' \n')
            for data in sorted(row['data'], key=lambda el: el[0])]

    @staticmethod
    def get_indent(row):
        return sorted(row['data'], key=lambda el: el[0])[0][0]

    @staticmethod
    def is_center(row, center):
        u"""Разница между координатой x двух точек не превышает 10% """
        x0 = row['data'][0][0]
        x1 = row['data'][0][1]
        string_center = (x1 - x0) / 2 + x0
        diff = abs(
            (center - string_center) / ((center + string_center) / 2.0)) * 100
        return diff < 10
