from __future__ import division

class TfsLine(object):
    col_name_dict = {
            'name': 0,
            'type': 1,
            's_end': 7,
            'length': 8,
            'lrad': 9,
            'k0l': 14,
            'k1l': 15,
            'k2l': 16,
            'k3l': 17,
            'k4l': 18,
            }

    def __init__(self, line, vkicker_is_hkicker=True):
        rows = line.split()
        for name, ii in self.col_name_dict.iteritems():
            value = rows[ii].replace('"','')
            try:
                value = float(value)
            except ValueError:
                pass
            setattr(self, name, value)

        if vkicker_is_hkicker and 'KICKER' in self.type:
            self.type = 'KICKER'

        s_0 = self.s_end
        if self.length == 0:
            self.s_begin = s_0 - self.lrad/2
            self.s_end = s_0 + self.lrad/2
        elif self.lrad == 0:
            self.s_end = s_0
            self.s_begin = s_0 - self.length
        else:
            raise ValueError('length and lrad are defined!')
        self.s_diff = self.s_end - self.s_begin

class HalfCell(object):
    def __init__(self, name, correct_length=False):
        self.lines = []
        self.name = name
        self.overhead = 0
        self.len_type_dict = {}
        self.correct_length = correct_length

    def add_line(self, line):
        self.lines.append(line)

        # Maybe this is a silly idea. Disabled for now
        if self.correct_length and len(self.lines) > 1:
            prev_line = self.lines[-2]
            diff = prev_line.s_end - line.s_begin + self.overhead

            if diff > 1e-4:
                if 'DRIFT' in prev_line.name:
                    if not prev_line.s_begin > prev_line.s_end - diff/2:
                        prev_line.length -= diff/2
                        prev_line.s_end -= diff/2
                        print('%s has been chopped in favor of %s' % (prev_line.name, line.name))
                        self.overhead = 0
                    else:
                        print('%s could not be chopped further' % prev_line.name)
                        self.overhead += diff

                elif 'DRIFT' in line.name:
                    if not line.s_begin + diff/2 > line.s_end:
                        line.length -= diff/2
                        line.s_begin += diff/2
                        print('%s has been chopped in favor of %s' % (line.name, prev_line.name))
                        self.overhead = 0
                    else:
                        print('%s could not be chopped further' % line.name)
                        if len(self.lines) > 2 and 'DRIFT' in self.lines[-3].name:
                            prev_line_2 = self.lines[-3]
                            if prev_line_2.s_end - diff/2 > prev_line_2.s_begin:
                                prev_line_2.s_end -= diff/2
                                prev_line_2.length -= diff/2
                                prev_line.s_begin -= diff/2
                                print('%s has been chopped again in favor of %s' % (prev_line_2.name, prev_line.name))
                                self.overhead = 0
                            else:
                                raise ValueError
                else:
                    raise ValueError('%s, %s' % (line.name, prev_line.name))

        self.calc_length()

    def create_dict(self):
        self.len_type_dict = {'order':[]}
        self.calc_length()
        total_wo_drift = 0
        for line in self.lines:
            if line.s_diff > 0 and 'DRIFT' not in line.type:
                total_wo_drift += line.s_diff
                self.len_type_dict['order'].append(line.type)
                if line.type in self.len_type_dict:
                    self.len_type_dict[line.type] += line.s_diff
                else:
                    self.len_type_dict[line.type] = line.s_diff
        self.len_type_dict['DRIFT'] = self.len_type_dict['Total_sdiff'] - total_wo_drift

    def print_attrs(self, *attrs):
        print('Half cell %s' % self.name)
        for line in self.lines:
            out_list = []
            for attr in attrs:
                out_list.append(getattr(line, attr))
            print(out_list)

    def round_dict(self, precision=3):
        for key, item in self.len_type_dict.iteritems():
            if type(item) is not list:
                self.len_type_dict[key] = round(item, precision)

    def calc_length(self):
        length, s_diff = 0, 0
        for line in self.lines:
            length += line.length
            s_diff += line.s_diff
        self.length = length
        self.s_diff = s_diff

        self.len_type_dict['Total'] = length
        self.len_type_dict['Total_sdiff'] = s_diff

    def get_s_begin(self):
        return self.lines[0].s_begin
    def get_s_end(self):
        return self.lines[-1].s_end
