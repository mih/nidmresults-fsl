#!/usr/bin/env python
"""
Test of NIDM FSL export tool


@author: Camille Maumet <c.m.j.maumet@warwick.ac.uk>
@copyright: University of Warwick 2013-2014
"""
import unittest
import os
from rdflib.graph import Graph
import sys
import glob

import logging
logger = logging.getLogger(__name__)
# Display log messages in console
logging.basicConfig(filename='debug.log', level=logging.DEBUG, filemode='w',
                    format='%(levelname)s - %(message)s')

RELPATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add FSL NIDM export to python path
sys.path.append(RELPATH)

# Add nidm common testing code folder to python path
NIDM_DIR = os.path.join(RELPATH, "nidm")
# In TravisCI the nidm repository will be created as a subtree, however locally
# the nidm directory will be accessed directly
logging.debug(NIDM_DIR)
if not os.path.isdir(NIDM_DIR):
    NIDM_DIR = os.path.join(os.path.dirname(RELPATH), "nidm")

NIDM_RESULTS_DIR = os.path.join(NIDM_DIR, "nidm", "nidm-results")
TERM_RESULTS_DIRNAME = "terms"
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(TEST_DIR, "data")

path = os.path.join(NIDM_RESULTS_DIR, "test")
sys.path.append(path)


from TestResultDataModel import TestResultDataModel
from TestCommons import *
from CheckConsistency import *

from ddt import ddt, data

# Find all test examples to be compared with ground truth
test_files = glob.glob(os.path.join(TEST_DIR, 'ex*', '*.ttl'))
# For test name readability remove path to test file
test_files = [x.replace(TEST_DIR, "") for x in test_files]
logging.info("Test files:\n\t" + "\n\t".join(test_files))


@ddt
class TestFSLResultDataModel(unittest.TestCase, TestResultDataModel):

    def setUp(self):
        # Retreive owl file for NIDM-Results
        owl_file = os.path.join(NIDM_RESULTS_DIR, TERM_RESULTS_DIRNAME,
                                'nidm-results.owl')
        import_files = glob.glob(
            os.path.join(os.path.dirname(owl_file),
                         os.pardir, os.pardir, "imports", '*.ttl'))

        TestResultDataModel.setUp(self, owl_file, import_files, test_files,
                                  TEST_DIR, NIDM_RESULTS_DIR)

    @data(*test_files)
    def test_class_consistency_with_owl(self, ttl):
        """
        Test: Check that the classes used in the ttl file are defined in the
        owl file.
        """
        ex = self.ex_graphs[ttl]
        ex.owl.check_class_names(ex.graph, ex.name, True)

    @data(*test_files)
    def test_attributes_consistency_with_owl(self, ttl):
        """
        Test: Check that the attributes used in the ttl file comply with their
        definition (range, domain) specified in the owl file.
        """
        ex = self.ex_graphs[ttl]
        ex.owl.check_attributes(ex.graph, "FSL example001", True)

    @data(*test_files)
    def test_examples_match_ground_truth(self, ttl):
        """
        Test03: Comparing that the ttl file generated by FSL and the expected
        ttl file (generated manually) are identical
        """

        ex = self.ex_graphs[ttl]

        for gt_file in ex.gt_ttl_files:
            logging.info("Ground truth ttl: " + gt_file)

            # RDF obtained by the ground truth export
            gt = Graph()
            gt.parse(gt_file, format='turtle')

            self.compare_full_graphs(gt, ex.graph, ex.exact_comparison, True)

if __name__ == '__main__':
    unittest.main()
