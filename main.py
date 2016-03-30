#!/usr/bin/env python

import xlrd
import requests
import json
import datetime
import os
import sys
import webbrowser
import time

DAUM_API_URL = "https://apis.daum.net/search/image?apikey={api_key}&q={search_term}&output=json"
DAUM_API_KEY = os.environ.get('DAUM_API_KEY')


def main():

    if len(sys.argv) != 2:
        sys.stdout.write("Usage: {} <menu file>\n".format(sys.argv[0]))
        sys.exit(-1)

    menu_file = sys.argv[1]
    book = xlrd.open_workbook(menu_file)
    sh = book.sheet_by_index(0)
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    weekmenu = [
        {
            "dayname": weekday_names[i - 1],
            "menu": sh.col_values(i, start_rowx=3, end_rowx=12)
        } for i in range(1, 6)
    ]

    html_doc = """
        <!doctype html>
        <head>
          <title>Menu</title>
          <meta charset="utf-8" />
          <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.0.0-alpha/css/bootstrap.min.css">
        </head>
        <body>
          <table class="table table-hover">
            <thead>
                <th>Weekday</th>
                <th>Rice</th>
                <th colspan="8">Meal</th>
            </thead>
            <tbody>
    """

    sys.stdout.write("Processing ")

    for weekday in weekmenu:

        daynumber = weekday_names.index(weekday["dayname"])
        todaynumber = datetime.datetime.today().weekday()
        html_doc += "\n<tr class='danger'>" if daynumber == todaynumber else "\n<tr>"

        html_doc += "\n<td>{}</td>".format(weekday["dayname"])

        for dish in weekday["menu"]:
            sys.stdout.write(".")
            sys.stdout.flush()

            if "(" in dish or ")" in dish:
                continue
            url = DAUM_API_URL.format(
                api_key=DAUM_API_KEY, search_term=dish)
            r = requests.get(url).text
            result = json.loads(r)
            thumbnail_url = ''
            old_dish = dish

            try:
                thumbnail_url = result['channel']['item'][0]['thumbnail']
                html_doc += '\n<td style="font-size: 10px;">{dish} <img src="{url}"/></td>'.format(dish=dish, url=thumbnail_url)
            except KeyError:
                pass
            except IndexError:
                found = False
                while not found:
                    dish = dish[:-1]
                    url = DAUM_API_URL.format(
                        api_key=DAUM_API_KEY, search_term=dish)
                    r = requests.get(url).text
                    result = json.loads(r)
                    try:
                        thumbnail_url = result['channel']['item'][0]['thumbnail']
                        html_doc += '\n<td style="font-size: 10px">{dish} <img src="{url}"/></td>'.format(dish=old_dish, url=thumbnail_url)
                        found = True
                    except IndexError:
                        found = False

        html_doc += "\n</tr>"

    html_doc += """
                </tbody>
              </table>
            </body>
    """

    # print("----------------------------------")

    html_file = open("ready.html", "w")
    html_file.write(html_doc)
    html_file.close()
    sys.stdout.write("\nDone.\n")
    sys.stdout.write("\nOpening in browser ...\n")
    webbrowser.open("file:///" + os.getcwd() + "/ready.html")
    time.sleep(2)
    os.remove(os.getcwd() + "/ready.html")


if __name__ == '__main__':
    main()
