import json
from datetime import datetime,timedelta
from functools import reduce
import uuid

def create_ics_from_txt(file):
    courses = create_courses(file)
    lessons = create_lessons(courses)
    events = create_events(lessons)
    print("events",len(events))
    ics_strs = create_strs(events)
    write_ics(ics_strs)


def create_courses(file):
    courses=[]
    with open(file,"r",encoding="UTF-8") as f:
        strs = f.read().split("\n")
    for i in range(len(strs)):
        sub_str=strs[i].split(" ")
        course={
            "name":sub_str[0],
            "begin_week":int(sub_str[1]),
            "end_week":int(sub_str[2]),
            "day":int(sub_str[3]),
            "begin_lesson_index":int(sub_str[4]),
            "end_lesson_index":int(sub_str[5]),
            "location":sub_str[6]
        }
        courses.append(course)
    return courses


def create_lessons(courses):
    lessons=[]
    for course in courses:
        lesson = course.copy()
        del lesson["begin_week"]
        del lesson["end_week"]
        for week in range(course["begin_week"],course["end_week"]+1):
            lesson["week"]=week
            lessons.append(lesson)
            lesson=lesson.copy()
    return lessons


def create_events(lessons):
    with open("config.json","r",encoding="utf-8") as f:
        paras=json.load(f)
    events = []
    begin_date=datetime(int(paras["begin_date"][0:4]),int(paras["begin_date"][4:6]), int(paras["begin_date"][6:8]),0,0)
    for lesson in lessons:
        lesson_date=begin_date+timedelta(days=(lesson["week"]-1)*7+lesson["day"]-1)
        season = get_season(lesson_date)
        begin_time = paras["lesson_time"][season][lesson["begin_lesson_index"]]
        begin_time = lesson_date + timedelta(hours=int(begin_time[0:2]), minutes=int(begin_time[2:4]))
        end_time = paras["lesson_time"][season][lesson["end_lesson_index"]]
        end_time = lesson_date + timedelta(hours=int(end_time[0:2]), minutes=int(end_time[2:4])) + timedelta(
            minutes = paras["lesson_length"])
        event = {
            "begin_time": begin_time.strftime("%Y%m%dT%H%M%S"),
            "end_time": end_time.strftime("%Y%m%dT%H%M%S"),
            "location": lesson["location"],
            "name": lesson["name"]
        }
        events.append(event)
    return events


def get_season(lesson_date):
    if 5 <= lesson_date.month < 10:
        return "summer"
    else:
        return "winter"


def create_strs(events):
    ics_strs = []
    for ics_event in events:
        ics_str = "BEGIN:VEVENT\n"
        ics_str += "DTEND;TZID=Asia/Shanghai:" + ics_event["end_time"] + "\n"
        ics_str += "DTSTART;TZID=Asia/Shanghai:" + ics_event["begin_time"] + "\n"
        ics_str += "LOCATION:" + ics_event["location"] + "\n"
        ics_str += "SUMMARY:" + ics_event["name"] + "\n"
        ics_str += "UID:" + str(uuid.uuid1().bytes) + "\n"
        ics_str += "BEGIN:VALARM\nTRIGGER:-PT30M\nDESCRIPTION:Event remind\nACTION:DISPLAY\nEND:VALARM\n"
        ics_str += "END:VEVENT\n"
        ics_strs.append(ics_str)
    return ics_strs


def write_ics(ics_strs):
    sum_str = reduce(lambda a,b:a+b,ics_strs)
    sum_str = "BEGIN:VCALENDAR\nMETHOD:PUBLISH\nVERSION:2.0\nX-WR-CALNAME:Course Table\nPRODID:-//Apple Inc.//Mac OS X 10.12//EN\nX-APPLE-CALENDAR-COLOR:#FC4208\nX-WR-TIMEZONE:Asia/Shanghai\nCALSCALE:GREGORIAN\n" + sum_str
    sum_str += "END:VCALENDAR"
    with open("out.ics","w",encoding="utf-8") as f:
        f.write(sum_str)


if __name__ == "__main__":
    create_ics_from_txt("courses.txt")
    print("Done")
