=====
Usage
=====

To use Goldmeister to check changes to a single set of gold files between
branches::

    from goldmeister.compare import GoldGitBranchCompare

    gc = GoldGitBranchCompare(repo_path='~/projects/smrf',
                              gold_files=['~/projects/my_sacred_code/tests/gold.nc'],
                              old_branch='master',
                              new_branch='projections_update')

    results = gc.compare()
    gc.plot_results(results, plot_original_data=True)


To use Goldmeister to check two sets of files::

    from goldmeister.compare import GoldFilesCompare

    gc = GoldFilesCompare(
                    gold_files=['~/projects/my_sacred_code/tests/gold.nc'],
                    compare_files=['~/projects/my_sacred_code/output/test.nc'])

    results = gc.compare()
    gc.plot_results(results, plot_original_data=True)
