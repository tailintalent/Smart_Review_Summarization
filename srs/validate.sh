#!/bin/bash

#$ -l h_rt=02:00:00
#$ -l mem_total=2G
#$ -l normal
#$ -pe singlenode 1
#$ -N validating

TESTING_LOG_FOLDER=testing_results
VERSION_NUM=3

python predictorTest.py > $TESTING_LOG_FOLDER/testing_$VERSION_NUM.out