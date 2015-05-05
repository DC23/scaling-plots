#!/usr/bin/env python
import os
import sys
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import argparse


def get_args():
    """Gets the command line arguments"""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'results_file',
        help='The input results spreadsheet')
    parser.add_argument(
        '--worksheet_name',
        type=str,
        default='results',
        help='Worksheet containing the results to plot')
    parser.add_argument(
        '--compute_element_name',
        type=str,
        default='Threads',
        help='Compute element name that will be used on plot labels')
    parser.add_argument(
        '--walltime_units',
        default='Minutes',
        type=str,
        help='Walltime units name')
    parser.add_argument(
        '--filter_column',
        default='',
        type=str,
        help='''Optional filter column name. If given, the column contents will
        be equated to a boolean value. Any result group with a member filter
        that equates to False will be excluded from the plot.''')
    parser.add_argument(
        '--title_prefix',
        type=str,
        help='optional prefix that will be prepended to the standard plot titles')
    parser.add_argument(
        '--file_prefix',
        type=str,
        help='optional prefix that will be prepended to the standard file names')
    parser.add_argument(
        '--window',
        default=False,
        help='prints plots to a window instead of to files',
        action='store_true')
    parser.add_argument(
        '--plot_width',
        default=10,
        type=int,
        help='Plot width in inches')
    parser.add_argument(
        '--speedup_max',
        default=16.1,
        type=float,
        help='Max Y axis scale for speedup')
    parser.add_argument(
        '--weak',
        default=False,
        help='Generate plots for weak scaling instead of strong scaling',
        action='store_true')
    parser.add_argument(
        '--style',
        default='',
        type=str,
        help='If available, use one of the matplotlib predefined styles')

    return parser.parse_args()


def save(path, ext='png', close=True, verbose=True):
    """Save a figure from pyplot.

    Parameters
    ----------
    path : string
        The path (and filename, without the extension) to save the
        figure to.

    ext : string (default='png')
        The file extension. This must be supported by the active
        matplotlib backend (see matplotlib.backends module).  Most
        backends support 'png', 'pdf', 'ps', 'eps', and 'svg'.

    close : boolean (default=True)
        Whether to close the figure after saving.  If you want to save
        the figure multiple times (e.g., to multiple formats), you
        should NOT close it in between saves or you will have to
        re-plot it.

    verbose : boolean (default=True)
        Whether to print information about when and where the image
        has been saved.

    """

    # Extract the directory and filename from the given path
    directory = os.path.split(path)[0]
    filename = "%s.%s" % (os.path.split(path)[1], ext)
    if directory == '':
        directory = '.'

    # If the directory does not exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # The final path to save to
    savepath = os.path.join(directory, filename)

    if verbose:
        print("Saving figure to '%s'..." % savepath),

    # Actually save the figure
    plt.savefig(savepath)

    # Close it
    if close:
        plt.close()

    if verbose:
        print("Done")


def read_dataframe_from_excel(
        filename,
        worksheet,
        **kwargs):
    """Reads a pandas dataframe from an Excel file
    filename: the excel file
    worksheet: worksheet name within the excel file
    The remaining named arguments are passed to pandas.read_excel
    """
    results = pd.read_excel(filename, worksheet, **kwargs)
    return results


def calculate_speedup_and_efficiency(
        rdf,
        compute_element_col_index,
        time_col_index):
    """Calculates the speedup and efficiency and
    adds them as new columns to a dataframe

    rdf: the results dataframe
    compute_element_col_index: compute elements column name
    time_col_index: column name containing the computation times

    Returns: a tuple containing the speedup, strong scaling efficiency, and
    weak scaling efficiency series
    """
    # get the t1 reference value
    t1 = float(rdf.loc[rdf[compute_element_col_index] == 1][time_col_index])

    # speedup n = t1 / tn
    speedup = t1 / rdf[time_col_index]

    # strong scaling efficiency n = t1 / (tn * n)
    strong_efficiency = t1 / (rdf[time_col_index] * rdf[compute_element_col_index])

    # weak scaling efficiency n = t1 / tn
    weak_efficiency = t1 / rdf[time_col_index]

    return (speedup, strong_efficiency, weak_efficiency)


def plot_walltime(
        series,
        colours,
        series_names,
        compute_elements,
        ymax,
        plot_size=None,
        group_width=0.8,
        xlabel='Processes',
        ylabel='Minutes',
        title='Walltime',
        file_name='walltime',
        file_extension='png',
        y_log_scale=False,
        show=False):
    """creates a bar plot as a new pyplot figure"""

    # the x locations for the groups.
    x_ind = np.arange(len(compute_elements))

    # create the figure and axes
    fig = plt.figure(figsize=plot_size)
    ax = fig.add_subplot(111)

    # create the individual bars
    bars_per_group = len(series)
    bar_width = group_width / bars_per_group
    bar_left = x_ind - (group_width / 2)  # centre the group on the ticks
    plot_left = x_ind[0] - group_width
    plot_right = x_ind[-1] + group_width

    for values, colour, name in zip(series, colours, series_names):
        ax.bar(
            bar_left,
            values,
            width=bar_width,
            color=colour,
            label=name,
            log=y_log_scale)
        bar_left += bar_width

    # apply the labels and formatting
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xlim(plot_left, plot_right)
    ax.set_ylim(0, ymax)
    ax.set_xticks(x_ind)
    ax.set_xticklabels(compute_elements)
    ax.legend()
    ax.get_legend().get_frame().set_facecolor('white')

    if show:
        plt.show()
    else:
        save(file_name, file_extension, close=True, verbose=True)


def plot_speedup(
        series,
        colours,
        series_names,
        compute_elements,
        xmax,
        ymax,
        line_width=1,
        plot_size=None,
        xlabel='Processes',
        ylabel='Speedup',
        title='Speedup',
        file_name='speedup',
        file_extension='png',
        show=False):
    """creates a speedup plot"""

    # create the figure and axes
    fig = plt.figure(figsize=plot_size)
    ax = fig.add_subplot(111)

    # define the sizes and locations of things
    x_ticks = list(compute_elements)
    x_ticks.append(xmax)
    plot_left = x_ticks[0]
    plot_right = x_ticks[-1]
    ax.set_xlim(plot_left, plot_right)
    ax.set_ylim(plot_left, ymax)

    # create the ideal speedup reference line
    ax.plot(
        x_ticks,
        x_ticks,
        color='red',
        linewidth=line_width,
        label='_nolegend_')

    # plot each series
    for values, colour, name in zip(series, colours, series_names):
        ax.plot(
            compute_elements,
            values,
            label=name,
            color=colour,
            linewidth=line_width,
            marker='o')

    # apply the labels and formatting
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(compute_elements)
    ax.set_xticklabels(compute_elements)
    ax.legend()
    ax.get_legend().get_frame().set_facecolor('white')

    if show:
        plt.show()
    else:
        save(file_name, file_extension, close=True, verbose=True)


def plot_efficiency(
        series,
        colours,
        series_names,
        compute_elements,
        xmax,
        ymax=1.2,
        line_width=1,
        plot_size=None,
        xlabel='Processes',
        ylabel='Efficiency',
        title='Efficiency',
        file_name='efficiency',
        file_extension='png',
        show=False):
    """creates an efficiency plot"""

    # create the figure and axes
    fig = plt.figure(figsize=plot_size)
    ax = fig.add_subplot(111)

    # define the sizes and locations of things
    x_ticks = list(compute_elements)
    x_ticks.append(xmax)
    plot_left = x_ticks[0]
    plot_right = x_ticks[-1]
    ax.set_xlim(plot_left, plot_right)
    ax.set_ylim(0, ymax)

    # create a horizontal ideal efficiency reference line
    ax.hlines(
        1,
        plot_left,
        plot_right,
        colors='red',
        linestyles='solid',
        linewidth=line_width,
        label='_nolegend_')

    # plot each series
    for values, colour, name in zip(series, colours, series_names):
        ax.plot(
            compute_elements,
            values,
            label=name,
            color=colour,
            linewidth=line_width,
            marker='o')

    # apply the labels and formatting
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(compute_elements)
    ax.set_xticklabels(compute_elements)
    ax.legend()
    ax.get_legend().get_frame().set_facecolor('white')

    if show:
        plt.show()
    else:
        save(file_name, file_extension, close=True, verbose=True)


def add_optional_prefix(base_string, prefix, separator):
    result = str(base_string)
    if prefix:
        result = prefix + separator + base_string
    return result


if __name__ == '__main__':

    # get and process the arguments
    args = get_args()

    # If we have a new enough version of matplotlib to support styles, use ggplot
    if args.style:
        try:
            matplotlib.style.use(args.style)
        except:
            pass

    # create plots in a 4:3 aspect ratio
    # matplotlib works in inches
    plot_width = args.plot_width
    plot_size = (plot_width, plot_width * 3 / 4)

    show_instead_of_save = args.window

    walltime_title = add_optional_prefix('Walltime', args.title_prefix, ' - ')
    speedup_title = add_optional_prefix('Speedup', args.title_prefix, ' - ')

    efficiency_title = add_optional_prefix(
        'Efficiency',
        args.title_prefix,
        ' - ')

    walltime_file = add_optional_prefix('walltime', args.file_prefix, '-')
    speedup_file = add_optional_prefix('speedup', args.file_prefix, '-')
    efficiency_file = add_optional_prefix(
        'weak-efficiency' if args.weak else 'strong-efficiency',
        args.file_prefix,
        '-')

    compute_element_name = args.compute_element_name
    walltime_units = args.walltime_units

    # CSIRO colours
    colours = [
        '#00a9ce',  # midday blue
        '#78be20',  # light forest
        '#DF1995',  # fuschia
        '#E87722',  # orange
        '#E4002B',  # vermillion
        '#00616c',  # midnight blue
        '#FFB81C',  # gold
        '#6D2077',  # plum
        '#1E22AA',  # blueberry
    ]

    usecols = [
        'group',
        'compute_elements',
        'walltime']
    if args.filter_column:
        usecols.append(args.filter_column)

    results = read_dataframe_from_excel(
        args.results_file,
        worksheet=args.worksheet_name,
        usecols=usecols)

    # filter out incomplete results
    results = results[results.group.notnull() & (results.walltime > 0)]

    # apply the optional filter column
    if args.filter_column:
        results = results[results[args.filter_column] > 0]

    # if there are multiple times for each (group,compute_element) tuple,
    # calculate the mean
    results = results.groupby(['group','compute_elements']).mean().reset_index()

    # create new dataframes for each group of results
    groups = results.group.unique()
    group_dataframes = {}
    for group in groups:
        df = results[(results.group == group)]
        if len(df):
            group_dataframes[group] = df.sort(
                'compute_elements',
                ascending=True)

    # calculate speedup and efficiency
    for data in group_dataframes.values():
        data['speedup'], data['strong_efficiency'], data['weak_efficiency'] = \
            calculate_speedup_and_efficiency(
                data,
                'compute_elements',
                'walltime')

    # extract the compute element names for grouping and labelling the charts
    compute_elements = np.sort(results.compute_elements.unique())

    # build the collections of values for the charts
    walltimes = []
    strong_efficiencies = []
    weak_efficiencies = []
    speedups = []
    series_names = []
    max_walltime = 0
    for name, data in group_dataframes.items():
        walltimes.append(data.walltime)
        strong_efficiencies.append(data.strong_efficiency)
        weak_efficiencies.append(data.weak_efficiency)
        speedups.append(data.speedup)
        series_names.append(name)
        local_max_walltime = max(data.walltime)
        if local_max_walltime > max_walltime:
            max_walltime = local_max_walltime

    # finally make the plots

    plot_walltime(
        walltimes,
        colours,
        series_names,
        compute_elements,
        ymax=max_walltime * 1.2,
        group_width=0.83,
        plot_size=plot_size,
        title=walltime_title,
        xlabel=compute_element_name,
        ylabel=walltime_units,
        show=show_instead_of_save,
        file_name=walltime_file,
        file_extension='png')

    plot_efficiency(
        weak_efficiencies if args.weak else strong_efficiencies,
        colours,
        series_names,
        compute_elements,
        line_width=1.5,
        xmax=compute_elements.max() * 1.1,
        ymax=1.3,
        plot_size=plot_size,
        xlabel=compute_element_name,
        title=efficiency_title,
        show=show_instead_of_save,
        file_name=efficiency_file,
        file_extension='png')

    # The Speedup plot makes no sense for weak scaling.
    # I could create a new plot for weak scaling that shows the percentage
    # increase in walltime as the compute elements increase
    if not args.weak:
        plot_speedup(
            speedups,
            colours,
            series_names,
            compute_elements,
            line_width=1.5,
            xmax=compute_elements.max() * 1.05,
            ymax=args.speedup_max,
            plot_size=plot_size,
            xlabel=compute_element_name,
            title=speedup_title,
            show=show_instead_of_save,
            file_name=speedup_file,
            file_extension='png')
