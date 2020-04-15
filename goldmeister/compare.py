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

        # Mange the output dir
        if isdir(self.output):
            self.log.warning("Removing preexisting output location {}"
                             "".format(self.output))
            shutil.rmtree(self.output)
        os.mkdir(self.output)

        # Variables in netcdfs that we want to ignore
        if 'ignore_vars' not in kwargs.keys():
            self.ignore_vars = ['time', 'y', 'x', 'projection']
        else:
            self.ignore_vars = kwargs['ignore_vars']

        # Naming convention for images in the that are loaded into self.data
        self.key = 'file-{}:{}'

        # Initialize the data structure
        self.initialize()

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

    def initialize(self):
        '''
        Initialize the data dictionary by looking at the first set of gold
        files.

        '''

        self.log.info("Initializing data structure for {} files..."
                      "".format(len(self.gold_files)))

        empty_data = {'gold': None, 'compare': None, 'difference': None}

        # Count how many images we are looking at
        n_gold_imgs = 0

        # Loop over each file and variable, initialize the dictionary data
        for f in self.gold_files:
            name = basename(f)
            ds = Dataset(f)

            for vname, v in ds.variables.items():
                if vname not in self.ignore_vars:
                    n_gold_imgs += 1
                    self.data[self.key.format(name, vname)] = empty_data.copy()

            ds.close()

    def read_netcdf_data(self, files, is_gold=False):
        '''
        Reads all netcdf files and then each variable which is added to
        self.data in the convention of

        self.data[key] = {gold: np.array, compare: np.array, difference: np.array}

        self.key is determining the top level naming convention which by
        default is:
        base_filename-netcdf_variable_name

        This function only populates the compare and gold subkeys. Use the
        boolean is_gold to assign to the gold subkey, otherwise the default
        behavior assigns to the compare subkey.

        To populate the difference subkey use self.compare.

        Args:
            files: List of files to be either used for compare or gold (basis)
                comparison.
            is_gold: Boolean indicating if the data set the basis for
                    comparison (compare - gold)
        '''

        if is_gold:
            input = 'gold'
        else:
            input = 'compare'

        # Loop over each file and variable
        self.log.info('Reading {} data...'.format(input))
        for f in files:
            # Use the basename of the file for the naming convention
            name = basename(f)

            # Load in each image to the data dictionary
            ds = Dataset(f)
            for vname, v in ds.variables.items():
                # Ignore variable
                if vname not in self.ignore_vars:
                    self.log.debug('Adding {}'.format(vname))
                    self.data[self.key.format(name, vname)][input] = v[:]
            ds.close()


    def compare(self):
        '''
        Compare gold files by subtracting gold from compare.

        Returns:
            new_data: Dictionary of keys filenames/variables of dictionaries
                      carrying the gold, compare, and difference arrays
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

    def plot_results(self, results, plot_original_data=False, show_plots=True,
                                                     save_plots=True):
        '''
        Generate the plots showing the differences

        Dictionary of dictionaries,

        Args:
            results: Dictionary as returned from compare for plotting
            plot_original_data: Boolean indicating whether to add the original
                                datasets to the subplots
            show_plots: Boolean indicating where to plt.show() or not.
            save_plots: Boolean where to save the figures to self.output
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


class GoldGitBranchCompare(GoldCompare):
    '''
    Compare Gold files across git branches. Use a single set of filenames
    and then compare them across git branches.

    Use branch names or hashes.
    '''
    def __init__(self, **kwargs):
        super(GoldGitBranchCompare, self).__init__(**kwargs)

        path = abspath(expanduser(kwargs['repo_path']))
        new_branch = kwargs['new_branch']
        old_branch = kwargs['old_branch']

        # Git Management
        self.repo = pygit2.Repository(path)
        self.new_branch = self.repo.branches[new_branch]
        self.old_branch = self.repo.branches[old_branch]
        self.read()

    def read(self):
        '''
        Read in all the netcdfs into memory assign to the dictionary data
        '''

        # Loop over the two branches and store the data
        for i, br in enumerate([self.old_branch, self.new_branch]):
            self.log.info("Checking out branch {}...".format(br.branch_name))
            self.repo.checkout(br)

            # The old branch is the basis for comparison, e.g. gold file
            if i == 0:
                is_gold = True

            # The new branch is the comparator
            else:
                is_gold = False

            self.read_netcdf_data(self.gold_files, is_gold=is_gold)

class GoldFilesCompare(GoldCompare):
    '''
    Compare Gold files across git branches.

    Use branch names or hashes.
    '''
    def __init__(self, **kwargs):
        super(GoldFilesCompare, self).__init__(**kwargs)
        self.compare_files = [abspath(expanduser(f)) for f in kwargs['compare_files']]

        N_Compare = len(self.compare_files)
        N_Gold = len(self.gold_files)

        if N_Gold != N_Compare:
            raise ValueError("Number of compare files must be the same as the "
                             "number of gold files provided.\n N_Compare = {} "
                             "vs N_Gold = {}".format(N_Compare, N_Gold))

        self.read()

    def read(self):
        '''
        Read in all the netcdfs into memory assign to the dictionary data
        '''

        # Loop over the two branches and store the data
        for i, br in enumerate([self.gold_files, self.compare_files]):

            # The old branch is the basis for comparison, e.g. gold file
            if i == 0:
                is_gold = True
                files = self.gold_files

            # Compare_files are the comparator
            else:
                is_gold = False
                files = self.compare_files

            self.read_netcdf_data(files, is_gold=is_gold)
