#
# Script to plot difference in gold files between current branch and master

from os.path import join, abspath, expanduser, basename, isdir
import os
from spatialnc.analysis import get_stats
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy
import pygit2
import shutil
from . utilities import get_logger

class GoldCompare():
    '''
    Base Class for performing comparisons. All the data here should be loaded
    into memory prior to comparisons.

    Attributes:
        gold_files: List of absolute paths representing gold files.
        compare_files: List of absolute paths to compare the gold files against
        file_type: Type of files were comparing
        output: Directory to output results
    '''

    def __init__(self, **kwargs):
        self.file_type = kwargs['file_type']

        if 'output_dir' not in kwargs.keys():
            self.output = './output'

        else:
            self.output = abspath(expanduser(kwargs['output_dir']))

        self.output = abspath(expanduser(self.output))

        self.gold_files = [abspath(expanduser(f)) for f in kwargs['gold_files']]
        self.data = {}

        self.log = get_logger('gold.compare')

        if isdir(self.output):
            self.log.warning("Removing preexisting output location {}"
                             "".format(self.output))
            shutil.rmtree(self.output)
        os.mkdir(self.output)

    def read(self):
        '''
        Abstract function to be replaced by the type of comparison being done
        The function should load in all data to be compared into dictionaries
        of dictionaries where each sub dictionary has the keys
        compare, gold, diff

        .. code-block::

        comparison_name:{
                            compare: compare_array
                            gold: gold_array
                            difference: difference_array
                        }

        '''

        pass


    def compare(self):
        '''
        Compare gold files by subtracting gold from compare.
        '''
        new_data = {}

        for name, data in self.data.items():
            new_data[name] = data.copy()

            f,v = name.split(':')
            f = f.split('-')[-1]

            pretty_title = 'File/variable: {}/{}'.format(f, v)

            self.log.info("")

            # Calculate the differences
            dd = data['compare'] - data['gold']
            new_data[name]['difference'] = dd
            stats = get_stats(dd)

            # Log them
            hdr = "{} Difference Statistics".format(pretty_title)
            banner = '=' * len(hdr)
            self.log.info(hdr)
            self.log.info(banner)
            for s, v in stats.items():
                self.log.info('{:<30}{:<20}'.format(s, v))

        return new_data

    def plot_results(self,results, plot_original_data=False, show_plots=True,
                                                     save_plots=True):
        '''
        Generate the plots showing the differences

        Dictionary of dictionaries,

        '''
        # Plot order
        labels = ['gold','compare','difference']

        # If were plotting
        ncols = 1
        if plot_original_data:
            ncols = 3

        for name, data in results.items():
            fig, axes = plt.subplots(1, ncols)

            if ncols == 1:
                axes = [axes]

            f, v = name.split(':')
            fname = f.split('-')[-1]
            variable = v

            fig_title = 'FILE: {}, Variable: {}'.format(fname, variable)

            # If were plotting the input images
            for i, ax in enumerate(axes):

                if not plot_original_data:
                    input = labels[2]
                else:
                    input = labels[i]

                d = data[input]
                self.log.debug('Plotting {} {}...'.format(variable, input))
                nd = len(d.shape)

                # 3D assume time is the first dimension, take the mean
                if nd == 3:
                    self.log.warning('Averaging {} to timeseries mean for'
                                     ' plotting only.'.format(variable))
                    plot_d = d.mean(axis=0)

                else:
                    plot_d = d

                # If we have a vector, just use normal plot
                if nd == 1:
                    im = axes[i].plot(plot_d)

                # Use image plotting
                else:
                    if i == 2 or not plot_original_data:
                        cmap = 'RdBu'
                    else:
                        cmap = 'jet'

                    im = axes[i].imshow(plot_d, cmap=cmap)
                    fig.colorbar(im, ax=axes[i])

                if plot_original_data:
                    axes[i].set_title(input.title())

            if plot_original_data:
                plt.suptitle(fig_title)

            else:
                # When plotting by itself there is only one subplot
                plt.title('{} (Compare - Gold)'.format(fig_title))

            plt.tight_layout()
            if save_plots:
                f = join(self.output, "_".join([fname, v]) + '.png')
                self.log.info("Saving figure to {}".format(f))
                plt.savefig(f)

            if show_plots:
                plt.show()
            plt.close()


class GitGoldCompare(GoldCompare):
    '''
    Compare Gold files across git branches.

    Use branch names or hashes.
    '''
    def __init__(self, **kwargs):
        super(GitGoldCompare, self).__init__(**kwargs)

        path = abspath(expanduser(kwargs['repo_path']))
        new_branch = kwargs['new_branch']
        old_branch = kwargs['old_branch']

        # NC ignore var:
        if 'ignore_vars' not in kwargs.keys():
            self.ignore_vars = ['time', 'y', 'x', 'projection']
        else:
            self.ignore_vars = kwargs['ignore_vars']

        # Git Management
        self.repo = pygit2.Repository(path)
        self.new_branch = self.repo.branches[new_branch]
        self.old_branch = self.repo.branches[old_branch]
        self.read()

    def read(self):
        '''
        Read in all the netcdfs into memory assign to the dictionary data
        '''

        self.log.info("Initializing data structure for {} files..."
                      "".format(len(self.gold_files)))

        empty_data = {'gold': None, 'compare': None, 'difference': None}

        # Key for naming the data, preserve the filename and var name
        key = 'file-{}:{}'

        # Count how many images we are looking at
        n_gold_imgs = 0

        # Loop over each file and variable, initialize the dictionary data
        for f in self.gold_files:
            name = basename(f)
            ds = Dataset(f)

            for vname, v in ds.variables.items():
                if vname not in self.ignore_vars:
                    n_gold_imgs += 1
                    self.data[key.format(name, vname)] = empty_data.copy()

            ds.close()

        self.log.info("Comparing {} arrays across {} files."
                      "".format(n_gold_imgs,len(self.gold_files)))

        # Loop over the two branches and store the data
        for i, br in enumerate([self.old_branch, self.new_branch]):
            self.log.info("Checking out branch {}...".format(br.branch_name))
            self.repo.checkout(br)

            # Gold
            if i == 0:
                input = 'gold'
            else:
                input = 'compare'

            # Loop over each file and variable, initialize the dictionary data
            self.log.info('Reading data...')
            for f in self.gold_files:
                name = basename(f)
                ds = Dataset(f)

                for vname, v in ds.variables.items():
                    if vname not in self.ignore_vars:
                        self.log.debug('Adding {}'.format(vname))
                        self.data[key.format(name, vname)][input] = v[:]