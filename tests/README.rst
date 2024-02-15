Evaluation
==========

Reproducing the evaluation
--------------------------

1. Install the packages specified in ``eval-requirements.txt``
2. Run the script ``comparison_nero.py`` to get the results of nero with all the urls
3. Run the script ``comparison_nero_skipped.py`` to get the results of nero with only the processable urls

The extracted content will be saved in the ``tests/results`` folder.
The failed urls will be saved in the ``tests/failed_urls.txt``. They are 74 of them.

Scores
------
The scores are stored in the following text files:

1. ``tests/test_results_for_all_urls.txt``
2. ``tests/test_results_for_skipped_urls.txt``


Sources
-------

Annotated HTML documents
^^^^^^^^^^^^^^^^^^^^^^^^

- BBAW collection (multilingual): Adrien Barbaresi, Lukas Kozmus, Lena Klink.
- Polish news: `tsolewski <https://github.com/tsolewski/Text_extraction_comparison_PL>`_.

HTML archives
^^^^^^^^^^^^^

- Additional German news sites: diskursmonitor.de, courtesy of Jan Oliver Rüdiger.