"""

    References:
        Python3 Pandas library: `https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html`

    Usage:
        `python3 run_filter.py --input ../source.xlsx --output ../target.csv`
        `python3 run_filter.py --input ../source.xlsx --output ../target.csv --echo_number 60`

"""

from argparse import ArgumentParser
from os.path import (
    exists as path_exists,
    isfile
)
from sys import exit as process_terminate
from traceback import format_exc

from pandas import ExcelFile as ExcelReader


class JiraSheetSeeker(object):

    class JDataRecords(object):
        def __init__(self):
            self._records = []

        def append(self, key, assignee, status, desc):
            self._records.append([key, assignee, status, desc])

        def generate_CSV_line(self):
            if not self._records:
                return None

            return ','.join((p[0] for p in self._records))

        def format_output(self):
            if not self._records:
                return ''

            return r'KEYs={}'.format(','.join((p[0] for p in self._records)))

    def __init__(self, KEYs, ASSIGNEEs, STATUSs, DESCRIPTIONs):
        if len(KEYs) != len(ASSIGNEEs) or len(ASSIGNEEs) != len(STATUSs) or len(KEYs) != len(DESCRIPTIONs):
            raise Exception('Records of Jira Sheet integration tests failed')

        self._KEYs = KEYs
        self._ASSIGNEEs = ASSIGNEEs
        self._STATUSs = STATUSs
        self._DESCRIPTIONs = DESCRIPTIONs

    def count_raw_records(self):
        return len(self._KEYs)

    def find_data_by_P_ID(self, P_ID):
        P_ID = P_ID.strip()
        jira_records = JiraSheetSeeker.JDataRecords()
        last_jira_key = None
        last_assignee = None
        last_status = None
        last_desc = None
        query_flag = r'{}'.format(P_ID)

        for index, _key in enumerate(self._KEYs):
            if _key != last_jira_key and _key and isinstance(_key, str):
                last_jira_key = _key
                last_assignee = None
                last_status = None
                last_desc = None

            assignee = self._ASSIGNEEs[index]
            if assignee and assignee != last_assignee and isinstance(assignee, str):
                last_assignee = self._ASSIGNEEs[index]

            status = self._STATUSs[index]
            if status and status != last_status and isinstance(status, str):
                last_status = self._STATUSs[index]

            description = self._DESCRIPTIONs[index]
            if description and description != last_desc and isinstance(description, str):
                last_desc = self._DESCRIPTIONs[index]
                if query_flag in last_desc:
                    jira_records.append(last_jira_key, last_assignee, last_status, last_desc)

        return jira_records


def __lets_analyze(sheet_P, sheet_Jira, output, echo_number):
    sheet_P_IDs = sheet_P['ID']
    jira_seeker = JiraSheetSeeker(
        KEYs=sheet_Jira['Key'], 
        ASSIGNEEs=sheet_Jira['Assignee'], 
        STATUSs=sheet_Jira['Status'], 
        DESCRIPTIONs=sheet_Jira['Description']
    )
    print('***(sheet P) raw records was loaded, count = {}***\n***(sheet Jira) raw records was loaded, count = {}***'.format(len(sheet_P_IDs), jira_seeker.count_raw_records()))

    # Debug Mode
    def _peek_4_debug():
        for i in range(echo_number):
            P_ID = sheet_P_IDs[i]
            print(r'{}. P_ID={};{}'.format(i, P_ID, jira_seeker.find_data_by_P_ID(P_ID).format_output()))
    if echo_number > 0:
        _peek_4_debug()
        return

    # Dump to local
    with open(output, 'w') as target:
        for P_ID in sheet_P_IDs:
            new_csv_line = jira_seeker.find_data_by_P_ID(P_ID).generate_CSV_line()
            if new_csv_line:
                target.write('{};{}\n'.format(P_ID, new_csv_line))


if __name__ == "__main__":
    try:
        parser = ArgumentParser(description=r'A Simple reader of xlsx')
        parser.add_argument(
            '--input', default='../cola.xlsx', help='data source: path of raw *.xlsx file'
        )
        parser.add_argument(
            '--output', default='../cola.csv', help='path of output file'
        )
        parser.add_argument(
            '--echo_number', default=0, type=int, help='Debug mode: lines number'
        )
        args = parser.parse_args()
        if not path_exists(args.input) or not isfile(args.input):
            raise Exception(r'[Error] Invalid source file path: {}'.format(args.input))
        else:
            print(r'Arguments ===> Input:"{}" -----> Output:"{}"'.format(args.input, args.output))

        # Parsing Excel file
        with ExcelReader(args.input) as xlsx_reader:
            sheets = {
                name: xlsx_reader.parse(name) for name in xlsx_reader.sheet_names
            }
            if r'P' not in sheets.keys() or r'Jira' not in sheets.keys():
                raise Exception(r'Sheet "P" / "Jira" does not exist in Excel file. Pls check...')

            __lets_analyze(
                sheet_P=sheets['P'], sheet_Jira=sheets['Jira'], 
                output=args.output,
                echo_number=args.echo_number
            )

        print(r'Done !')

    except Exception:
        print(r'[Exception]: {err_msg}'.format(err_msg=format_exc()))
        process_terminate(10)
