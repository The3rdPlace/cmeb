from datetime import datetime

from dateutil.relativedelta import relativedelta


def get_days_x(days, period):
    x = []

    dt = datetime.strptime(str(days[-1]["timeInterval"]["start"]), '%Y-%m-%dT%H:%M:%SZ')
    for i in range(period):
        x += [str((dt - relativedelta(days=i)).strftime('%d/%m %a'))]

    x.reverse()
    return x


def get_days_y(points, apply_filter):
    summations = []

    for index, day in enumerate(points):
        y = []
        for day_point in day:
            value = 0
            for hour_point in day_point:
                if apply_filter is True:
                    if float(hour_point["out_Quantity.quantity"]) < 5.0:
                        value += float(hour_point["out_Quantity.quantity"])
                    else:
                        value += 0
                else:
                    value += float(hour_point["out_Quantity.quantity"])
            y += [value]
        summations += [y]

    return summations


def get_days_legends():
    return ["Work@home", "DBC", "Weekend"]


def get_hour_interval(hour):
    if hour == 0:
        return "23 - 0"
    else:
        return "%2.0d - %2.0d" % (hour - 1, hour)


def get_hour_x(days, period):
    return list(map(lambda hour: get_hour_interval(int(hour)), range(24)))


def get_hour_y(points, apply_filter):
    y = []
    for day in points:
        values = [0] * 24
        for day_index, day_point in enumerate(day):
            for index, point in enumerate(day_point):
                value = float(point["out_Quantity.quantity"])
                if apply_filter is True:
                    if value < 0.5:
                        values[index] += value
                    else:
                        values[index] += 0
                else:
                    values[index] += value

        y += [values]

    return y


def get_hour_legends():
    return ["Work@home", "DBC", "Weekend"]
