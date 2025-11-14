import sys, os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import pytest
import json

from paperglass.usecases.toc import createFirstPageProfile



def test_createFirstPageProfile():
    o = createFirstPageProfile("Test Medication")


def main():
    
    test_createFirstPageProfile()

if __name__ == "__main__":
    main()
