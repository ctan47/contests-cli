import argparse
import requests

from dataclasses import dataclass
from datetime import datetime, timedelta

from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
from rich import box
from rich.console import Console
from rich.table import Table


@dataclass
class ContestData:
    contest_platform: str
    contest_title : str
    contest_start_time : datetime
    contest_duration: timedelta


def get_atcoder_contests() -> list[ContestData]:

    URL = "https://atcoder.jp/contests"

    contests_list = []

    response = requests.get(URL)

    if response.ok:

        html = response.content.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find_all(id="contest-table-upcoming")[0].find_all("tr")

        for row in table[1:]:
            
            """
            >>> print(row)
            <tr>
            <td class="text-center"><a href="http://www.timeanddate.com/worldclock/fixedtime.html?iso=20220827T2100&amp;p1=248" target="blank"><time class="fixtime fixtime-full">2022-08-27 21:00:00+0900</time></a></td>
            <td>
            <span aria-hidden="true" data-placement="top" data-toggle="tooltip" title="Algorithm">Ⓐ</span>
            <span class="user-blue">◉</span>
            <a href="/contests/abc266">AtCoder Beginner Contest 266</a>
            </td>
            <td class="text-center">01:40</td>
            <td class="text-center"> - 1999</td>
            </tr>
            """

            contest_title = row.contents[3].contents[5].contents[0]
            contest_start_time = datetime.strptime(row.contents[1].contents[0].contents[0].contents[0], "%Y-%m-%d %H:%M:%S%z").astimezone(ZoneInfo("Asia/Kolkata"))
            hours, minutes = map(int, row.contents[5].contents[0].split(":"))
            contest_end_time = contest_start_time + timedelta(minutes=minutes, hours=hours)
            contest_duration = contest_end_time - contest_start_time

            contests_list.append(ContestData("AtCoder", contest_title, contest_start_time, contest_duration))

    return contests_list


def get_codechef_contests() -> list[ContestData]:

    URL = "https://www.codechef.com/api/list/contests/all"

    payload = {
        "sort_by": "START",
        "sorting_order": "asc",
    }

    contests_list = []  #Created List 

    response = requests.get(URL, params=payload)

    if response.ok:

        response = response.json()
        contests_data = response["future_contests"]

        for data in contests_data:
            
            """
            >>> print(data)
            {
                'contest_code': 'START54', 
                'contest_name': 'Starters 54 (Rated for Div 2, 3 & 4)', 
                'contest_start_date': '31 Aug 2022  20:00:00', 
                'contest_end_date': '31 Aug 2022  23:00:00', 
                'contest_start_date_iso': '2022-08-31T20:00:00+05:30', 
                'contest_end_date_iso': '2022-08-31T23:00:00+05:30', 
                'contest_duration': '180', 
                'distinct_users': 0
            }
            """

            contest_title = data["contest_name"]
            contest_start_time = datetime.fromisoformat(data["contest_start_date_iso"])
            contest_end_time   = datetime.fromisoformat(data["contest_end_date_iso"])
            contest_duration   = contest_end_time - contest_start_time

            contests_list.append(ContestData("CodeChef", contest_title, contest_start_time, contest_duration))

    return contests_list


def get_codeforces_contests() -> list[ContestData]:

    URL = "https://codeforces.com/api/contest.list"

    contests_list = []

    response = requests.get(URL)

    if response.ok:

        response = response.json()
        contests_data = response["result"]

        for data in contests_data:
            
            """
            >>> print(data)
            {
                'id': 1723, 
                'name': 'ICPC 2022 Online Challenge powered by HUAWEI - Problem 1', 
                'type': 'IOI', 
                'phase': 'BEFORE', 
                'frozen': False, 
                'durationSeconds': 1296000, 
                'startTimeSeconds': 1663200000, 
                'relativeTimeSeconds': -1747109
            }
            """

            contest_title = data["name"]
            contest_start_time = datetime.fromtimestamp(float(data["startTimeSeconds"]))
            contest_end_time   = contest_start_time + timedelta(seconds=float(data["durationSeconds"]))
            contest_duration   = contest_end_time - contest_start_time

            contests_list.append(ContestData("CodeForces", contest_title, contest_start_time, contest_duration))

    return contests_list


def get_geeksforgeeks_contests() -> list[ContestData]:

    URL = "https://practiceapi.geeksforgeeks.org/api/vr/events/"

    payload = {
        "type": "contest",
        "sub_type": "upcoming"
    }

    contests_list = []

    response = requests.get(URL, params=payload)

    if response.ok:

        response = response.json()
        contests_data = response["results"]["upcoming"]

        for data in contests_data:
            
            """
            >>> print(data)
            {
                'slug': 'interview-series-65', 
                'start_time': '2022-08-28T19:00:00', 
                'end_time': '2022-08-28T20:30:00', 
                'banner': {
                    'mobile_url': 'https://media.geeksforgeeks.org/img-practice/banner/interview-series-65-1661154000-mobile.png', 
                    'desktop_url': 'https://media.geeksforgeeks.org/img-practice/banner/interview-series-65-1661154005-desktop.png'
                }, 
                'name': 'Interview Series - 65', 
                'status': 'upcoming', 
                'time_diff': {
                    'days': 0, 
                    'hours': 4, 
                    'mins': 8, 
                    'secs': 13
                }, 
                'type': 3, 
                'date': 'August 28, 2022', 
                'time': '07:00 PM'
            }
            """

            contest_title: str = data["name"]

            if contest_title.startswith("GATE CS All India Scholarship Test"):
                continue

            contest_start_time = datetime.fromisoformat(data["start_time"])
            contest_end_time   = datetime.fromisoformat(data["end_time"])
            contest_duration   = contest_end_time - contest_start_time

            contests_list.append(ContestData("GeeksforGeeks", contest_title, contest_start_time, contest_duration))

    return contests_list


def get_leetcode_contests() -> list[ContestData]:

    URL  = "https://leetcode.com/graphql"

    body = """
    {
        allContests {
            title
            startTime
            duration
        }
    }
    """

    contests_list = []

    response = requests.get(URL, json={"query" : body})

    if response.ok:

        response = response.json()
        contests_data = response["data"]["allContests"]
        
        contests_list = []

        for data in contests_data:

            """
            >>> print(data)
            {
                'title': 'Biweekly Contest 86', 
                'startTime': 1662215400, 
                'duration': 5400
            }
            """
            contest_title = data["title"]
            contest_start_time = datetime.fromtimestamp(int(data["startTime"]))
            contest_end_time = contest_start_time + timedelta(seconds=int(data["duration"]))
            contest_duration = contest_end_time - contest_start_time

            contests_list.append(ContestData("LeetCode", contest_title, contest_start_time, contest_duration))

    return contests_list


def show_contests(today: bool=False, tomorrow: bool=False, date: str=None, all_platforms: bool=False, atcoder: bool=False, codechef: bool=False, codeforces: bool=False, geeksforgeeks: bool=False, leetcode: bool=False) -> None:

    contests_list = []

    if all_platforms or atcoder:
        contests_list.extend(get_atcoder_contests())
    if all_platforms or codechef:
        contests_list.extend(get_codechef_contests())
    if all_platforms or codeforces:
        contests_list.extend(get_codeforces_contests())
    if all_platforms or leetcode:
        contests_list.extend(get_leetcode_contests())
    if all_platforms or geeksforgeeks:
        contests_list.extend(get_geeksforgeeks_contests())

    day_start_time = None
    day_end_time   = None

    if today:
        _today = datetime.today()
        day_start_time = datetime(_today.year, _today.month, _today.day)
        day_end_time   = day_start_time + timedelta(days=1) - timedelta(seconds=1)
    elif tomorrow:
        _today = datetime.today()
        day_start_time = datetime(_today.year, _today.month, _today.day) + timedelta(days=1)
        day_end_time   = day_start_time + timedelta(days=1) - timedelta(seconds=1)
    else:
        year, month, day = date.split("-")
        day_start_time = datetime(int(year), int(month.lstrip("0")), int(day.lstrip("0")))
        day_end_time   = day_start_time + timedelta(days=1) - timedelta(seconds=1)

    required_contests_list = []
    
    for contest_data in contests_list:            
        if day_start_time.timestamp() <= contest_data.contest_start_time.timestamp() <= day_end_time.timestamp():
            required_contests_list.append(contest_data)

    weekday, month, day = day_start_time.strftime("%A-%B-%d").split("-")

    date_panel = Table(box=box.SQUARE, expand=True, show_header=False)
    date_panel.add_column("Date", justify="center")
    date_panel.add_row(f"{weekday}, {month} {day.lstrip('0')}")

    console = Console()

    console.print(date_panel)

    if required_contests_list:

        contests_table = Table(box=box.SQUARE, expand=True)
        contests_table.add_column("Platform")
        contests_table.add_column("Contest Title")
        contests_table.add_column("Start Time")
        contests_table.add_column("Duration")

        for contest_data in required_contests_list:

            contests_table.add_row(
                contest_data.contest_platform,
                contest_data.contest_title,
                contest_data.contest_start_time.strftime("%I:%M %p").lstrip("0"),
                f"{str(contest_data.contest_duration)[:-3]} hours"
            )

        console.print(contests_table)

    else:

        no_contest_panel = Table(box=box.SQUARE, expand=True, show_header=False)
        no_contest_panel.add_column("Date", justify="center")
        no_contest_panel.add_row(f"No Contests Scheduled!")
        
        console.print(no_contest_panel)


def main() -> None:

    parser = argparse.ArgumentParser()

    date_parser = parser.add_mutually_exclusive_group(required=True)
    date_parser.add_argument("-td", "--today", action="store_true", help="show today's contests")
    date_parser.add_argument("-tm", "--tomorrow", action="store_true", help="show tomorrow's contests")
    date_parser.add_argument("-d", "--date", type=str, help="show contests for date YYYY-MM-DD", metavar="YYYY-MM-DD")

    platform_parser = parser.add_mutually_exclusive_group(required=True)
    platform_parser.add_argument("-a", "--all-platforms", action="store_true", help="show contests on all platforms")
    platform_parser.add_argument("-ac", "--atcoder", action="store_true", help="show contests on AtCoder")
    platform_parser.add_argument("-cc", "--codechef", action="store_true", help="show contests on CodeChef")
    platform_parser.add_argument("-cf", "--codeforces", action="store_true", help="show contests on CodeForces")
    platform_parser.add_argument("-gfg", "--geeksforgeeks", action="store_true", help="show contests on GeeksforGeeks")
    platform_parser.add_argument("-lc", "--leetcode", action="store_true", help="show contests on LeetCode")

    args = parser.parse_args()

    show_contests(args.today, args.tomorrow, args.date, args.all_platforms, args.atcoder, args.codechef, args.codeforces, args.geeksforgeeks, args.leetcode)

if __name__ == "__main__":

    try:
        main()
    except Exception as e:
        print(e)
