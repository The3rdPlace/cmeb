import argparse

from chart import chart
from rest import fetch_data


def setup_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", "-f",
                        help='Fetch latest data from https://eloverblik.dk',
                        required=False,
                        action="store_true")
    parser.add_argument("--metering-point", "-m",
                        help="Metering point id, cached if given before",
                        required=False)
    parser.add_argument("--graph-type", "-g",
                        help="'days' = KWh per day in the period | 'hour' = Total Hourly consumption",
                        required=False,
                        default="days")
    parser.add_argument("--period", "-p",
                        help="number of days into the history to graph",
                        required=False,
                        default=30,
                        type=int)
    parser.add_argument("--display", "-d",
                        help="'line' = line diagram, 'bar' = Bar diagram, 'scatter' = Scatter diagram",
                        required=False,
                        default='bar')
    parser.add_argument("--apply-filter", "-a",
                        help="Apply filtering on results",
                        required=False,
                        action="store_true")

    args = parser.parse_args()
    return args


def main():
    print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =")
    print("||    C h a r t   -   M y   -   E l e c t r i c - B i l l    ||")
    print("= = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =")
    args = setup_args()

    if args.fetch is True:
        fetch_data(args.metering_point)

    chart(args.graph_type, args.period, args.display, args.apply_filter)


if __name__ == "__main__":
    main()
