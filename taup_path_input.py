#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : taup_path_input.py
Purpose : make input file for taup_path from stream object
Creation Date : 20-12-2017
Last Modified : Fri 11 May 2018 12:57:49 PM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
import argparse

def main():
    parser = argparse.ArgumentParser(
                       description='make input file for taup_path')
    parser.add_argument('-f','--stream', metavar='H5_FILE',type=str,
                        help='any h5 stream ')
main()


