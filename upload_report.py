from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    ]

credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scopes) 
file = gspread.authorize(credentials) 

def upload_report(all_rows):
    sheet1 = file.open("Telegram Bot Invites - Report")
    sheet1 = sheet1.worksheet("Main")
    
    for row in all_rows:
        if len(row) == 9:
            sheet1.append_row(row)



def upload_individual_invite_count(individual_report):
    sheet2 = file.open("Telegram Bot Invites - Report")
    sheet2 = sheet2.worksheet("Invites Count")
    not_added = True
    
    for row in range(2,sheet2.row_count+1):
        r = sheet2.row_values(row)
        if r[0] == individual_report[0]:
            current_score = r[2]
            new_score = int(current_score) + int(individual_report[2])
            sheet2.update_cell(row, 3, new_score)
            sheet2.update_cell(row, 2, individual_report[1])
            not_added = False
        
    if not_added:
        sheet2.append_row(individual_report)