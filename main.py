
# -*- coding: utf-8 -*-
#--author-- = Urska Rifelj

import os
import jinja2
import webapp2
#from google.appengine.api import users # model za google log in
from models import *
from datetime import *
from dateutil.relativedelta import *
import random


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        today = datetime.today().weekday()
        if today == 0:
            today = "ponedeljek"
        elif today == 1:
            today = "torek"
        elif today == 2:
            today = "sreda"
        elif today == 3:
            today = "četrtek"
        elif today == 4:
            today = "petek"
        elif today == 5:
            today = "sobota"
        else:
            today = "nedelja"

        datum = datetime.today().strftime('%d.%m.%Y')

        quotes = ["Life is 10% what happens to you and 90% how you react to it.",
                  "Good, better, best. Never let it rest. 'Til your good is better and your better is best.",
                  "With the new day comes new strength and new thoughts.",
                  "Optimism is the faith that leads to achievement. Nothing can be done without hope and confidence."]
        quote = random.choice(quotes)
        params = {"today": today, "datum": datum, "quote": quote}
        return self.render_template("home.html", params=params)


class PravnomocnostHandler(BaseHandler):
    def get(self):
        return self.render_template("pravnomocnost.html")

    def post(self):
        user_selected_date = self.request.get("selected_date_by_user")              #date as string
        user_selected_number = int(self.request.get("selected_number_by_user"))     #number as integer
        user_selected_unit = self.request.get("selected_unit_by_user")              #unit as string

        def velikonocni_ponedeljek(year):
            a = year % 19
            b = year >> 2
            c = b // 25 + 1
            d = (c * 3) >> 2
            e = ((a * 19) - ((c * 8 + 5) // 25) + d + 15) % 30
            e += (29578 - a - e * 32) >> 10
            e -= ((year % 7) + b - d + e + 2) % 7
            d = e >> 5
            day = str(e - d * 31)
            month = str(d + 3)
            sunday = day + "." + month + "." + str(year)
            monday = str((datetime.strptime(sunday, "%d.%m.%Y") + timedelta(days=1)).strftime("%d.%m.%Y"))
            return monday

        # holidays as list (item is string)
        holidays = ["01.01.",
                    "02.01.",
                    "08.02.",
                    "27.04.",
                    "01.05.",
                    "02.05.",
                    "25.06.",
                    "15.08.",
                    "31.10.",
                    "01.11.",
                    "25.12.",
                    "26.12."]

        # zadnji dan roka
        if user_selected_unit == "day":
            last_day = datetime.strptime(user_selected_date, "%d.%m.%Y") + timedelta(days=user_selected_number)
        elif user_selected_unit == "month":
            last_day = datetime.strptime(user_selected_date, "%d.%m.%Y") + relativedelta(months=+user_selected_number)
        elif user_selected_unit == "year":
            last_day = datetime.strptime(user_selected_date, "%d.%m.%Y") + relativedelta(years=+user_selected_number)
        else:
            last_day = datetime.strptime(user_selected_date, "%d.%m.%Y")

        day_of_the_week = int(last_day.weekday())                           # (0=ponedeljek...6=nedelja)

        year_of_next_year = (datetime.date(last_day) + timedelta(days=1)).year
        year_of_last_day = str(datetime.date(last_day).year)
        last_day = str(last_day.strftime("%d.%m.%Y"))
        holidays = [holiday + year_of_last_day for holiday in holidays]

        holidays.append("01.01." + str(year_of_next_year))                  #dodan 1. januar naslednjega leta
        holidays.append("02.01." + str(year_of_next_year))                  #dodan 2. januar naslednjega leta
        holidays.append(velikonocni_ponedeljek(int(year_of_last_day)))      #dodan velikonočni ponedeljek

        # preveri zadnji dan roka
        if day_of_the_week == 5 or day_of_the_week == 6 or last_day in holidays:
            while day_of_the_week == 5 or day_of_the_week == 6 or last_day in holidays:
                last_day = (datetime.strptime(str(last_day), "%d.%m.%Y") + timedelta(days=1)).date()
                day_of_the_week = int(last_day.weekday())
                last_day = last_day.strftime("%d.%m.%Y")
        else:
            last_day = last_day


        # datum pravnomočnosti oz. dan po zadnjem dnevu roka
        day_after_last_day = (datetime.strptime(str(last_day), "%d.%m.%Y") + timedelta(days=1)).date()
        day_after_last_day = str(day_after_last_day.strftime("%d.%m.%Y"))

        if day_of_the_week == 6 or day_after_last_day in holidays:
            while day_of_the_week == 6 or day_after_last_day in holidays:
                day_after_last_day = (datetime.strptime(str(day_after_last_day), "%d.%m.%Y") + timedelta(days=1)).date()
                day_of_the_week = int(day_after_last_day.weekday())
                day_after_last_day = str(day_after_last_day.strftime("%d.%m.%Y"))
        else:
            day_after_last_day = day_after_last_day

        params = {"user_selected_date": user_selected_date, "day1": day_of_the_week,  "user_selected_number": last_day, "day2": user_selected_number, "user_selected_unit": day_after_last_day, "day3": holidays}
        return self.render_template("pravnomocnost.html", params=params)


class DobaHandler(BaseHandler):
    def get(self):
        return self.render_template("doba.html")



class ZpizHandler(BaseHandler):
    def get(self):
        return self.render_template("zpiz.html")


class Zpiz1Handler(BaseHandler):
    def get(self):
        return self.render_template("zpiz1.html")


class Zpiz2Handler(BaseHandler):
    def get(self):
        return self.render_template("zpiz2.html")


class Zmepiz1Handler(BaseHandler):
    def get(self):
        return self.render_template("zmepiz1.html")


app = webapp2.WSGIApplication([
    webapp2.Route("/", MainHandler),
    webapp2.Route("/pravnomocnost", PravnomocnostHandler),
    webapp2.Route("/doba", DobaHandler),
    webapp2.Route("/zpiz", ZpizHandler),
    webapp2.Route("/zpiz1", Zpiz1Handler),
    webapp2.Route("/zpiz2", Zpiz2Handler),
    webapp2.Route("/zmepiz1", Zmepiz1Handler)
], debug=True)