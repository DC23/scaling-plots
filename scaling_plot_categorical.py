#!/usr/bin/env python
import os
import sys
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import argparse

from scaling_plot import (
    COLOURS,
    add_optional_prefix,
    add_sorted_legend,
    read_dataframe_from_excel,
    save,
)


def get_args():
    """Gets the command line arguments"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("results_file", help="The input results spreadsheet")
    parser.add_argument(
        "--worksheet_name",
        type=str,
        default="results",
        help="Worksheet containing the results to plot",
    )
    parser.add_argument(
        "--category_column",
        type=str,
        default="version",
        help="Name of the spreadsheet column containing the category labels",
    )
    parser.add_argument(
        "--baseline_category",
        type=str,
        default="baseline",
        help="The baseline category name. Plots are calculated relative to this category",
    )
    parser.add_argument(
        "--walltime_units", default="Minutes", type=str, help="Walltime units name"
    )
    parser.add_argument(
        "--filter_column",
        default="",
        type=str,
        help="""Optional filter column name. If given, the column contents will
        be cast to a boolean value. Any result group with a member filter
        that equates to False will be excluded from the plot.""",
    )
    parser.add_argument(
        "--title_prefix",
        type=str,
        help="optional prefix that will be prepended to the standard plot titles",
    )
    parser.add_argument(
        "--file_prefix",
        type=str,
        help="optional prefix that will be prepended to the standard file names",
    )
    parser.add_argument(
        "--file-extension",
        type=str,
        default="png",
        help="""The file extension. This must be supported by the activename 
        matplotlib backend (see matplotlib.backends module).  Most
        backends support 'png', 'pdf', 'ps', 'eps', and 'svg'.""",
    )
    parser.add_argument(
        "--window",
        default=False,
        help="prints plots to a window instead of to files",
        action="store_true",
    )
    parser.add_argument(
        "--plot_width", default=10, type=int, help="Plot width in inches"
    )
    parser.add_argument(
        "--style",
        default="",
        type=str,
        help="If available, use one of the matplotlib predefined styles",
    )
    parser.add_argument(
        "--log_scale",
        default=False,
        action="store_true",
        help="If true, a log scale is used on the Y axis",
    )
    parser.add_argument(
        "--tight",
        default=False,
        help="Apply the matplotlib tight_layout for smaller margins than the default.",
        action="store_true",
    )

    return parser.parse_args()


def plot_bar(
    series,
    colours,
    series_names,
    ymax,
    plot_size=None,
    bar_width=0.8,
    xlabel="Category",
    ylabel="Minutes",
    title="Walltime",
    file_name="walltime",
    file_extension="png",
    y_log_scale=False,
    show=False,
):
    """creates a bar plot as a new pyplot figure"""

    # the x locations for the bars
    x_ind = np.arange(len(series))

    # create the figure and axes
    fig = plt.figure(figsize=plot_size)
    ax = fig.add_subplot(111)

    plot_left = x_ind[0] - bar_width
    plot_right = x_ind[-1] + bar_width

    for index, walltime, colour, name in zip(x_ind, series, colours, series_names):
        ax.bar(
            index, walltime, width=bar_width, color=colour, label=name, log=y_log_scale
        )

    # apply the labels and formatting
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlim(plot_left, plot_right)
    ax.set_ylim(0, ymax)
    ax.set_xticks(x_ind)
    ax.set_xticklabels(series_names)

    add_sorted_legend(ax)

    if show:
        plt.show()
    else:
        if args.tight:
            plt.tight_layout()
        save(file_name, file_extension, close=True, verbose=True)


if __name__ == "__main__":

    # get and process the arguments
    args = get_args()

    if args.style:
        try:
            matplotlib.style.use(args.style)
        except OSError:
            print(
                "Warning: '{0}' is not a valid matplotlib style. Using default style.".format(
                    args.style
                )
            )

    # create plots in a 4:3 aspect ratio
    # matplotlib works in inches
    plot_width = args.plot_width
    plot_size = (plot_width, plot_width * 3 / 4)

    show_instead_of_save = args.window

    walltime_title = add_optional_prefix("Walltime", args.title_prefix, " - ")
    speedup_title = add_optional_prefix("Speedup", args.title_prefix, " - ")

    walltime_file = add_optional_prefix("walltime", args.file_prefix, "-")
    speedup_file = add_optional_prefix("speedup", args.file_prefix, "-")

    walltime_units = args.walltime_units

    usecols = [args.category_column, "walltime"]
    if args.filter_column:
        usecols.append(args.filter_column)

    results = read_dataframe_from_excel(
        args.results_file, worksheet=args.worksheet_name, usecols=usecols
    )

    # filter out incomplete results
    results = results[results[args.category_column].notnull() & (results.walltime > 0)]

    # apply the optional filter column
    if args.filter_column:
        results = results[results[args.filter_column] > 0]

    # if there are multiple times for each category, then calculate the mean
    results = results.groupby([args.category_column]).mean().reset_index()

    # calculate speedup
    t1 = float(
        results.loc[results[args.category_column] == args.baseline_category]["walltime"]
    )
    results["speedup"] = t1 / results["walltime"]

    # Category names as a list
    # TODO: sort list so that the baseline value is always first
    categories = list(results[args.category_column])

    # finally make the plots
    # walltime plot
    plot_bar(
        series=results["walltime"],
        colours=COLOURS,
        series_names=categories,
        ymax=results.walltime.max() * 1.2,
        bar_width=0.63,
        plot_size=plot_size,
        title=walltime_title,
        xlabel=args.category_column,
        ylabel=walltime_units,
        show=show_instead_of_save,
        file_name=walltime_file,
        file_extension=args.file_extension,
    )

    # speedup plot
    plot_bar(
        series=results["speedup"],
        colours=COLOURS,
        series_names=categories,
        ymax=results.speedup.max() * 1.2,
        bar_width=0.63,
        plot_size=plot_size,
        title=speedup_title,
        xlabel=args.category_column,
        ylabel="Speedup",
        show=show_instead_of_save,
        file_name=speedup_file,
        file_extension=args.file_extension,
    )
