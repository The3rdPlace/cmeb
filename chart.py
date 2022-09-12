from datetime import datetime

import matplotlib.pyplot as plt
import json

import charttype


def is_day_from_weekdays(day, weekdays):
    dt = datetime.strptime(str(day["timeInterval"]["start"]), '%Y-%m-%dT%H:%M:%SZ')
    if dt.weekday() in weekdays:
        return 1
    else:
        return 0


def get_day_for_weekdays(day, weekdays):
    if is_day_from_weekdays(day, weekdays):
        return day["Point"]
    else:
        a = list()
        b = dict()
        b["out_Quantity.quantity"] = "0.0"
        a += list(map(lambda point: b, range(24)))
        return a


def get_average(point, count):
    for hour in point:
        quantity = float(hour["out_Quantity.quantity"])
        quantity /= count
        hour["out_Quantity.quantity"] = quantity
    return point


def get_graph_points(period, graph_type):
    with open("data/Meterdata.csv") as file:
        data = json.loads(file.read())
        days = data["result"][0]["MyEnergyData_MarketDocument"]["TimeSeries"][0]["Period"]
        if period > len(days):
            print("  - Period must not be longer than 3 months (90 days)")
            exit()

        period_days = list(map(lambda period_slice: period_slice,
                           days[len(days) - period:: 1]))

        work_at_home_days = sum(map(lambda day: is_day_from_weekdays(day, [0, 2]), period_days))
        work_at_home_points = list(map(lambda day: get_day_for_weekdays(day, [0, 2]), period_days))
        work_at_dbc_days = sum(map(lambda day: is_day_from_weekdays(day, [1, 3, 4]), period_days))
        work_at_dbc_points = list(map(lambda day: get_day_for_weekdays(day, [1, 3, 4]), period_days))
        weekend_days = sum(map(lambda day: is_day_from_weekdays(day, [5, 6]), period_days))
        weekend_points = list(map(lambda day: get_day_for_weekdays(day, [5, 6]), period_days))

        if graph_type == "hour":
            return [map(lambda point: get_average(point, work_at_home_days), work_at_home_points),
                    map(lambda point: get_average(point, work_at_dbc_days), work_at_dbc_points),
                    map(lambda point: get_average(point, weekend_days), weekend_points)]
        else:
            return [work_at_home_points, work_at_dbc_points, weekend_points]


def get_graph_days():
    with open("data/Meterdata.csv") as file:
        data = json.loads(file.read())
        return data["result"][0]["MyEnergyData_MarketDocument"]["TimeSeries"][0]["Period"]


def get_x(graph_type, period):
    days = get_graph_days()
    if graph_type == "days":
        return charttype.get_days_x(days, period)
    elif graph_type == "hour":
        return charttype.get_hour_x(days, period)
    else:
        print("  - Unknown graph type '%s" % graph_type)
        exit(0)


def get_y(graph_type, period, apply_filter):
    points = get_graph_points(period, graph_type)
    if graph_type == "days":
        return charttype.get_days_y(points, apply_filter)
    elif graph_type == "hour":
        return charttype.get_hour_y(points, apply_filter)
    else:
        print("  - Unknown graph type '%s" % graph_type)
        exit(0)


def get_legends(graph_type):
    if graph_type == "days":
        return charttype.get_days_legends()
    elif graph_type == "hour":
        return charttype.get_hour_legends()
    else:
        print("  - Unknown graph type '%s" % graph_type)
        exit(0)


def get_graph_average(x, y, graph_type):
    total = 0

    for index, day in enumerate(y):
        for point in day:
            total += point
    if graph_type == "hour":
        return [(total / len(x)) / 3] * len(x)
    else:
        return [(total / len(x))] * len(x)


def chart(graph_type, period, display, apply_filter):
    print("  + Display '%s' char for %d days using '%s' plot type" % (graph_type, period, display))
    if apply_filter is True:
        print("  + Applying filters")

    x = get_x(graph_type, period)
    y = get_y(graph_type, period, apply_filter)
    legends = get_legends(graph_type)

    y_avg = get_graph_average(x, y, graph_type)

    if display == "line":
        for index, graph in enumerate(y):
            plt.plot(x, graph, label=legends[index])
    elif display == 'bar':
        bottom = [0] * len(x)
        width = 0.6
        for index, graph in enumerate(y):
            plt.bar(x, graph, width, label=legends[index], bottom=bottom)
            bottom = graph
    elif display == 'scatter':
        for index, graph in enumerate(y):
            plt.scatter(x, graph, s=graph, label=legends[index])
    else:
        print("  - Unknown display type '%s'" % display)
        exit()

    line, = plt.plot(x, y_avg, label="Average (%.2fKWh)" % y_avg[0])
    line.set_color('black')

    if graph_type == "days":
        plt.title('Consumption per day')
        plt.xlabel('date')
    elif graph_type == "hour":
        plt.title('Averaged consumption per hour')
        plt.xlabel('hour')
    else:
        print("  - Unknown graph type '%s'" % graph_type)
        exit()

    plt.legend()
    plt.ylabel('KWh')

    plt.gcf().autofmt_xdate()

    plt.show()
