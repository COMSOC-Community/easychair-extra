# EasyChair-Extra

[![Build badge](https://github.com/COMSOC-Community/easychair-extra/workflows/build/badge.svg)](https://github.com/COMSOC-Community/easychair-extra/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/COMSOC-Community/easychair-extra/branch/main/graphs/badge.svg)](https://codecov.io/gh/COMSOC-Community/easychair-extra/tree/main)

This repository contains a Python package for working with files exported from EasyChair.
It provides ready-made functionalities to develop tools useful for organizing large-scale
conferences.

This package was created when Ulle Endriss served as the PC Chair for ECAI 2024. In this role,
many tools were needed to enhance EasyChair's functionality. The tools with potential benefit
for the broader community have been gathered here.

The files in this repository serve as building blocks for scripts used in conference management.
We provide functions for reading and generating EasyChair files, as well as performing useful
tasks (e.g., creating review assignments).

We provide example scripts show-casing how they can be used. We have for instances scripts to:

- Compute the minimum "review quota", that is, the smallest maximum number of reviews per reviewers 
so that it is still possible to assign each paper 3 reviewers who did not bid negatively for it;
- Form a pool of emergency reviewers, these are reviewers with versatile skills that can be used
last minute for emergency reviews;
- Group submissions by similarity as an intermediary step before constructing the conference schedule.

The files in this repository are designed to help you kick-start the development of the scripts 
needed for your conference!

## The Package

The package is documented in the code and there is no current plan on providing a full-fledged 
documentation. Roughly speaking:

- `easychair_extra.read` provides functions to read EasyChair files;
- `easychair_extra.generate` provides functions to generate random EasyChair files;
- `easychair_extra.programcommittee` provides functions relating to the committee;
- `easychair_extra.reviewassignment` provides functions relating to the assignment of 
submissions to PC members;
- `easychair_extra.submission` provides functions relating to the submissions.

## Learn by Examples

In the `examples` folder ([link](https://github.com/COMSOC-Community/easychair-extra/tree/main/examples))
we provide example scripts making use of the package. 
Check them out to understand how the package works.

Example files for typical EasyChair outputs are located in the `easychair_sample_files` folder.

## Usage Policy

This package is provided as an open-source repository under a GNU 3.0 license.

If you are using this package and adding functionalities, please consider submitting pull requests.
Others may be looking for the same functionalities!