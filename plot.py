#!/bin/python
import sys
import os
import copy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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

    Returns: a tuple containing the speedup and efficiency series
    """
    # get the t1 reference value
    t1 = float(rdf[rdf[compute_element_col_index] == 1][time_col_index])
    # speedup n = t1 / tn
    speedup = t1 / rdf[time_col_index]
    # efficiency n = t1 / (tn * n)
    efficiency = t1 / (rdf[time_col_index] * rdf[compute_element_col_index])

    return (speedup, efficiency)


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

    for bar_values, bar_colour in zip(series, colours):
        ax.bar(
            bar_left,
            bar_values,
            width=bar_width,
            color=bar_colour,
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
    ax.legend(series_names)
    # ax.legend().get_frame().set_facecolor('white')

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
    x_ticks = copy.deepcopy(compute_elements)
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
    ax.legend().get_frame().set_facecolor('white')
    # can also use get_frame().set_xy(x,y) to give a custom location

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
    x_ticks = copy.deepcopy(compute_elements)
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
    ax.legend(shadow=True)
    ax.legend().get_frame().set_facecolor('white')

    if show:
        plt.show()
    else:
        save(file_name, file_extension, close=True, verbose=True)


if __name__ == '__main__':

    # create plots in a 4:3 aspect ratio
    # matplotlib works in inches
    plot_width = 10
    plot_size = (plot_width, plot_width * 3 / 4)

    # show_instead_of_save = False
    show_instead_of_save = True

    # CSIRO colours
    colours = [
        '#00a9ce',  # midday blue
        '#00616c',  # midnight blue
        '#78be20',  # light forest
        '#DF1995',  # fuschia
        '#E87722',  # orange
        '#E4002B',  # vermillion
        '#FFB81C',  # gold
        '#6D2077',  # plum
        '#1E22AA',  # blueberry
    ]

    results = read_dataframe_from_excel(
        'results.xls',
        worksheet='results',
        usecols=[
            'group',
            'compute_elements',
            'walltime'])

    # I don't know an equivalent to R's completecases, but this works for now
    results = results[results['group'].notnull() & (results.walltime > 0)]

    # create new dataframes for each group of results
    groups = results.group.unique()
    group_dataframes = {}
    for group in groups:
        df = results[(results.group == group)]
        if len(df):
            group_dataframes[group] = df.sort('compute_elements', ascending=True)

    # calculate speedup and efficiency based on the total walltime, and on
    # the average time per iteration (which excludes a lot of the serial
    # code, and gives a closer look at just the model calculations)
    for data in group_dataframes.values():
        speedup, efficiency = calculate_speedup_and_efficiency(
            data,
            'compute_elements',
            'walltime')
        data['speedup'] = speedup
        data['efficiency'] = efficiency

    # extract the compute element names for grouping and labelling the charts
    compute_elements = np.sort(results.compute_elements.unique()).tolist()

    # build the collections of values for the charts
    walltimes = []
    efficiencies = []
    speedups = []
    series_names = []
    max_walltime = 0
    for name, data in group_dataframes.items():
        walltimes.append(data.walltime)
        efficiencies.append(data.efficiency)
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
        ymax=max_walltime + 50,
        group_width=0.83,
        plot_size=plot_size,
        title='ODPS Walltime',
        xlabel='Threads',
        ylabel='Seconds',
        show=show_instead_of_save,
        file_name='odps-walltime',
        file_extension='png')

    plot_efficiency(
        efficiencies,
        colours,
        series_names,
        compute_elements,
        line_width=1.5,
        xmax=140,
        ymax=1.3,
        plot_size=plot_size,
        title='ODPS - Strong Scaling Efficiency',
        show=show_instead_of_save,
        file_name='odps-efficiency',
        file_extension='png')

    # plot_speedup(
        # speedups,
        # colours,
        # series_names,
        # compute_elements,
        # line_width=1.5,
        # xmax=140,
        # ymax=140,
        # plot_size=plot_size,
        # title='Gridded Calibration - Strong Scaling Speedup',
        # show=show_instead_of_save,
        # file_name='speedup',
        # file_extension='png')

    # plot_efficiency(
        # efficiencies_it,
        # colours,
        # series_names,
        # compute_elements,
        # line_width=1.5,
        # xmax=140,
        # ymax=1.5,
        # plot_size=plot_size,
        # title='Gridded Calibration - Strong Scaling Efficiency - Model Calculations',
        # show=show_instead_of_save,
        # file_name='efficiency_iterations',
        # file_extension='png')

    # plot_speedup(
        # speedups_it,
        # colours,
        # series_names,
        # compute_elements,
        # line_width=1.5,
        # xmax=140,
        # ymax=175,
        # plot_size=plot_size,
        # title='Gridded Calibration - Strong Scaling Speedup - Model Calculations',
        # show=show_instead_of_save,
        # file_name='speedup_iterations',
        # file_extension='png')
