#!/usr/bin/env python

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import argparse
import os

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# credentials = ServiceAccountCredentials.from_json_keyfile_name('key_need_4_google_Auth.txt', scope)

# gc = gspread.authorize(credentials)

# wks = gc.open('Sanford_lab_missing/new_data')

# sh = wks.worksheet('Sheet6')

# #print type(sh)

# with open('gspread_test.txt', 'wb') as f:
#     writer = csv.writer(f, delimiter="\t")
#     writer.writerows(sh.get_all_values())

# os.system("tagStormFromTab ./gspread_test.txt ./test.tags")


class googleTotagStorm:
    def __init__(self):
        self.cred = args.cred
        self.sp = args.spreadName
        self.s = args.sheetName
        self.oN = args.outName
        self.oT = args.outType


    def access_sheet(self, scope):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.cred, scope)
        gs = gspread.authorize(credentials)
        ws = gs.open(str(self.sp))
        return ws.worksheet(str(self.s))


    def convert_sheet_to(self, worksheet):
        if str(self.oT) == 'tsv':
            with open(str(self.oN), 'wb') as tab:
                writer = csv.writer(tab, delimiter="\t")
                writer.writerows(worksheet.get_all_values())
        elif str(self.oT) == 'csv':
            with open(str(self.oN), 'wb') as comma:
                writer = csv.writer(comma)
                writer.writerows(worksheet.get_all_values())
        elif str(self.oT) == 'tagStorm':
            with open('temp.tsv', 'wb') as tab:
                writer = csv.writer(tab, delimiter="\t")
                writer.writerows(worksheet.get_all_values())
            os.system("tagStormFromTab temp.tsv %s" % str(self.oN))
        else:
            print "Intial argument check didn't pick up allow output types"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script logs into a google drive and transforms a google sheet")
    parser.add_argument("--cred", "-c", required=True, help="The credential file created in google api")
    parser.add_argument("--spreadName", "-sp", help="Name of the spreadsheet/s")
    parser.add_argument("--sheetName", "-s", help="Name of the sheet/s")
    parser.add_argument("--outName", "-on", required=True, help="Name of the output file")
    parser.add_argument("--outType", "-ot", required=True, choices=['csv', 'tsv', 'tagStorm'], help="Type of output")
    args = parser.parse_args()


    Form = googleTotagStorm()

    wks = Form.access_sheet(scope)

    Form.convert_sheet_to(wks)
