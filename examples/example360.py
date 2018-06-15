#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
"""
To run, simply point the script to one of the video files in the directory

    $ python gopro_gyro_dataset_example.py /path/to/dataset/video.MP4
"""
__author__ = "Hannes Ovrén"
__copyright__ = "Copyright 2015, Hannes Ovrén"
__license__ = "GPL"
__email__ = "hannes.ovren@liu.se"


import os
import sys
import argparse

import numpy as np

import crisp
import crisp.rotations
from crisp.calibration import PARAM_ORDER

CAMERA_IMAGE_SIZE = (1920, 960)
CAMERA_READOUT = 0.00001
CAMERA_FRAME_RATE = 29.997
GYRO_RATE_GUESS = 450

def to_rot_matrix(r):
    "Convert combined axis angle vector to rotation matrix"
    theta = np.linalg.norm(r)
    v = r/theta
    R = crisp.rotations.axis_angle_to_rotation_matrix(v, theta)
    return R

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('video')
    args = parser.parse_args()

    gyro_file = os.path.splitext(args.video)[0] + '_gyro.csv'
    # gyro_file = args.video + '.txt'
    camera = crisp.PanoramicCameraModel(CAMERA_IMAGE_SIZE, CAMERA_FRAME_RATE, CAMERA_READOUT)

    print('Creating video stream from {}'.format(args.video))
    video = crisp.VideoStream.from_file(camera, args.video)

    print('Creating gyro stream from {}'.format(gyro_file))
    gyro = crisp.GyroStream.from_csv(gyro_file)

    # print('Post processing L3G4200D gyroscope data to remove frequency spike noise')
    # gyro.data = post_process_L3G4200D_data(gyro.data.T).T

    print('Creating calibrator')
    calibrator = crisp.AutoCalibrator(video, gyro)

    print('Estimating time offset and camera to gyroscope rotation. Guessing gyro rate = {:.2f}'.format(GYRO_RATE_GUESS))
    try:
        calibrator.initialize(gyro_rate=GYRO_RATE_GUESS)
    except crisp.InitializationError as e:
        print('Initialization failed. Reason "{}"'.format(e.message))
        sys.exit(-1)

    print('Running calibration. This can take a few minutes.')
    try:
        calibrator.calibrate()
        calibrator.print_params()
    except crisp.CalibrationError as e:
        print('Calibration failed. Reason "{}"'.format(e.message))
        sys.exit(-2)

    # Compare with reference data
    # reference_data = np.loadtxt(reference_file, delimiter=',')
    # reference_data[[2,3,4,5,6,7]] = reference_data[[5,6,7,2,3,4]] # Swap order of bias and rot
    # param_data = np.array([calibrator.parameter[p] for p in PARAM_ORDER])
    # print('\nCompare with reference data')
    # print()
    # print('{:^15s} {:^12s} {:^12s} {:^12s}'.format('Parameter', 'Reference', 'Optimized', 'Difference'))
    # for param, ref, data in zip(PARAM_ORDER, reference_data, param_data):
    #     print("{:>15s}  {:E}  {:E}  {:E}".format(param, ref, data, ref-data))
    #
    # R_ref = to_rot_matrix(reference_data[5:])
    # R_data = to_rot_matrix(param_data[5:])
    # dR = np.dot(R_ref.T, R_data)
    # v, theta = crisp.rotations.rotation_matrix_to_axis_angle(dR)
    # print('Reference rotation')
    # print(R_ref)
    # print('Optimized rotation')
    # print(R_data)
    # print("Angle difference: {:.4f} degrees".format(np.rad2deg(theta)))