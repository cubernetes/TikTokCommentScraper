from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


from openpyxl.cell import get_column_letter
from openpyxl.descriptors import Tuple, NoneSet, Strict


class Reference(Strict):
    """ a simple wrapper around a serie of reference data """

    data_type = NoneSet(values=['n', 's', 'f'])
    pos1 = Tuple()
    pos2 = Tuple(allow_none=True)

    def __init__(self, sheet, pos1, pos2=None, data_type=None, number_format=None):
        """Create a reference to a cell or range of cells

        :param sheet: the worksheet referred to
        :type sheet: string

        :type pos1: cell coordinate
        :type pos1: tuple

        :param pos2: optional second coordinate for a range
        :type row: tuple

        :param data_type: optionally specify the data type
        :type data_type: string

        :param number_format: optional formatting style
        :type number_format: string

        """

        self.sheet = sheet
        self.pos1 = pos1
        self.pos2 = pos2
        self.data_type = data_type
        self.number_format = number_format

    @property
    def number_format(self):
        return self._number_format

    @number_format.setter
    def number_format(self, value):
        self._number_format = value

    @property
    def values(self):
        """ read data in sheet - to be used at writing time """
        if hasattr(self, "_values"):
            return self._values
        if self.pos2 is None:
            cell = self.sheet.cell(row=self.pos1[0], column=self.pos1[1])
            self.data_type = cell.data_type
            self._values = [cell.internal_value]
        else:
            self._values = []

            for row in range(self.pos1[0], self.pos2[0] + 1):
                for col in range(self.pos1[1], self.pos2[1] + 1):
                    cell = self.sheet.cell(row=row, column=col)
                    self._values.append(cell.internal_value)
                    if cell.internal_value == '':
                        continue
                    if self.data_type is None and cell.data_type:
                        self.data_type = cell.data_type
        return self._values

    def __str__(self):
        """ format excel reference notation """

        if self.pos2 is not None:
            return "'%s'!$%s$%s:$%s$%s" % (self.sheet.title,
                get_column_letter(self.pos1[1]), self.pos1[0],
                get_column_letter(self.pos2[1]), self.pos2[0])
        else:
            return "'%s'!$%s$%s" % (self.sheet.title,
                get_column_letter(self.pos1[1]), self.pos1[0])
