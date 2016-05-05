import unittest
from css_types import origin30, origerr30, remark30
from eqlocl_to_css3 import Converter
import logging
logging.disable(logging.CRITICAL)


class TestConverter(unittest.TestCase):

    def test_origin(self):
        converter = Converter(origin_file='sample_data/sample_css.origin',
                              origerr_file='sample_data/sample_css.origerr',
                              netmag_file='sample_data/sample_css.netmag',
                              remark_file='sample_data/sample_css.remark')

        converter.process_eqlocls(eqlocl_root='sample_data/', file_name_pattern='/**/[GA|agso|ASC|MUN]*.txt')

        expected_origin = """ -20.0270  112.8390   19.5000   971292436.69000        1        1  2000285   -1  105   -1       -1       -1 l____eq -999.0000 f -999.00       -1    5.10        1 -999.00       -1 GGCat           EHB                    1 -
 -42.5090  120.0520    9.6000   977750664.40000        2        2  2000360   -1  231   -1       -1       -1 l____ms -999.0000 f -999.00       -1    5.70        2 -999.00       -1 GGCat           EHB                    2 -
 -19.9510  133.7390   11.0000  1000480710.71000        3        3  2001257   -1   61   -1       -1       -1 l____as -999.0000 r    5.10        1 -999.00       -1 -999.00       -1 GGCat           EHB                    3 -
 -30.3990  117.3190    2.0000  1001645692.68000        4        4  2001271   -1   72   -1       -1       -1 l____ms -999.0000 g -999.00       -1 -999.00       -1    5.00        1 GGCat           ISC                    4 -
 -33.7120  120.6280   10.0000  1003513400.38000        5        5  2001292   -1   95   -1       -1       -1 l____ms -999.0000 n    5.10        2 -999.00       -1 -999.00       -1 GGCat           ISC                    5 -
 -42.7150  124.7630   11.2000  1008179560.66000        6        6  2001346   -1   72   -1       -1       -1 l____as -999.0000 - -999.00       -1    5.10        3 -999.00       -1 GGCat           EHB                    6 -
 -42.7300  124.7350   11.4000  1008228491.03000        7        7  2001347   -1   73   -1       -1       -1 l____as -999.0000 - -999.00       -1    5.40        4 -999.00       -1 GGCat           EHB                    7 -
 -30.4790  117.0840    0.5000  1015292858.90000        8        8  2002064   -1   25   -1       -1       -1 l____ms -999.0000 - -999.00       -1 -999.00       -1    5.00        2 GGCat           AUST                   8 -
 -22.7380  129.8710   12.8000  1076491079.00000        9        9  2004042   -1   -1   -1       -1       -1 l____fs -999.0000 - -999.00       -1 -999.00       -1    5.00        3 GGCat           AUST                   9 -
 -42.5660  143.6900   15.0000  1166116987.80000       10       10  2006348   -1   18   -1       -1       -1 l____eq -999.0000 g -999.00       -1 -999.00       -1    5.00        4 GGCat           MEL                   10 -
 -41.7620  125.4980 -999.0000  1270466580.00000       11       11  2010095   -1   -1   -1       -1       -1 l____eq -999.0000 - -999.00       -1 -999.00       -1    5.10        5 GGCat           ADE                   11 -
 -30.4791  117.0843    0.5012  1015292860.13000       12        8  2002064   -1   -1   -1       -1       -1 -       -999.0000 - -999.00       -1 -999.00       -1    5.00        6 EQLOCL WA2      GA  00373   ab        12 -
 -30.4791  117.0843    0.5012  1015292859.82000       13        8  2002064   -1   -1   -1       -1       -1 -       -999.0000 - -999.00       -1 -999.00       -1    5.00        7 EQLOCL WA2      GA  00373   ab        12 -
 -30.4791  117.0843    0.5012  1015292861.09000       14        8  2002064   -1   -1   -1       -1       -1 -       -999.0000 - -999.00       -1 -999.00       -1    5.00        8 EQLOCL WA2      GA  00373   ab        13 -
"""
        converted_origin_strings = []
        origin = origin30()
        for line in converter.output_origin().splitlines():
            origin.from_string(line)
            converted_origin_strings.append(origin.create_css_string().rstrip())  # rstrip because string literal
                                                                                  # is stripped on the right side

        self.assertListEqual(list(expected_origin.splitlines()), converted_origin_strings)

    def test_origerr(self):
        converter = Converter(origin_file='sample_data/sample_css.origin',
                              origerr_file='sample_data/sample_css.origerr',
                              netmag_file='sample_data/sample_css.netmag',
                              remark_file='sample_data/sample_css.remark')

        converter.process_eqlocls(eqlocl_root='sample_data/', file_name_pattern='/**/[GA|agso|ASC|MUN]*.txt')

        expected_origerr = """       1         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000    0.8800    7.2000    4.3000  65.00    4.4000    -1.00 0.000        1 -
       2         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000    0.8800    4.7000    3.7000  46.00    2.6000    -1.00 0.000        2 -
       3         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000    1.0400   -1.0000   -1.0000  -1.00   -1.0000    -1.00 0.000        3 -
       4         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000    1.3300    3.7000    3.3000  90.00   -1.0000     0.26 0.000        4 -
       5         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000    1.2500    4.6000    3.3000   0.00   -1.0000     0.25 0.000        5 -
       6         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000    1.0300   -1.0000   -1.0000  -1.00   -1.0000    -1.00 0.000        6 -
       7         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000    1.0400   -1.0000   -1.0000  -1.00   -1.0000    -1.00 0.000        7 -
       8         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000   -1.0000    2.2000    1.9000   0.00    5.5000     0.60 0.000        8 -
       9         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000   -1.0000    8.9000    7.2000   0.00   25.0000     2.90 0.000        9 -
      10         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000    1.0800    6.7000    6.5000   0.00   11.0000     1.00 0.000       10 -
      11         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000   -1.0000   -1.0000   -1.0000  -1.00   -1.0000    -1.00 0.000       11 -
      12         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000    0.4839    2.1845    2.3690   5.46   -1.0000     0.55 0.800       -1 -
      13         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000    0.4839    2.1845    2.3690   5.46   -1.0000     0.55 0.800       -1 -
      14         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000         -1.0000    0.4839    2.1845    2.3690   5.46   -1.0000     0.55 0.800       -1 -
"""

        converted_origerr_strings = []
        origerr = origerr30()
        for line in converter.output_origerr().splitlines():
            origerr.from_string(line)
            converted_origerr_strings.append(origerr.create_css_string().rstrip())  # rstrip because string literal
                                                                                    # is stripped on the right side

        self.assertListEqual(list(expected_origerr.splitlines()), converted_origerr_strings)


    def test_remark(self):
        converter = Converter(origin_file='sample_data/sample_css.origin',
                              origerr_file='sample_data/sample_css.origerr',
                              netmag_file='sample_data/sample_css.netmag',
                              remark_file='sample_data/sample_css.remark')

        converter.process_eqlocls(eqlocl_root='sample_data/', file_name_pattern='/**/[GA|agso|ASC|MUN]*.txt')

        expected_remark = """       1        1 mb 5.1 ISC 49 MS 4.4 ISC 15 Mw 5.1 HRVD                                          -
       2        1 mb 5.6 ISC 33 MS 5.5 ISC 107 Mw 5.7 HRVD                                         -
       3        1                                                                                  -
       4        1 ML 5.0 AUST mb 5.0 ISC 25 MS 3.3 ISC 2                                           -
       5        1 mb 5.1 ISC 31 MS 4.4 ISC 11                                                      -
       6        1                                                                                  -
       7        1                                                                                  -
       8        1 ML 5.0 AUST                                                                      -
       9        1                                                                                  -
      10        1 ML 5.0 MEL 7                                                                     -
      11        1 ML 5.1 ADE                                                                       -
      12        1 BURAKIN WA                                                                       -
      13        1 BURAKIN WA                                                                       -
      14        1 BURAKIN WA                                                                       -
"""

        converted_remark_strings = []
        remark = remark30()
        for line in converter.output_remark().splitlines():
            remark.from_string(line)
            converted_remark_strings.append(remark.create_css_string().rstrip())  # rstrip because string literal
                                                                                  # is stripped on the right side

        self.assertListEqual(list(expected_remark.splitlines()), converted_remark_strings)


if __name__ == '__main__':
    unittest.main()
