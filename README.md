# EasyChair-Extra

Python package to work with files exported from EasyChair. 
Useful to develop tools when running a conference.

This package came to life when Ulle Endriss was a PC chair for ECAI-2024. For this role, many tools
enhancing the functionalities provided by EasyChair were needed. The tools that could benefit the
community have been gathered there.

## The Package

The package is documented in the code and there is no current plan on provided a full-fleshed 
documentation. Roughly speaking:

- `easychair_extra.read` provides functions to read EasyChair files;
- `easychair_extra.programcommittee` provides functions relating to the committee;
- `easychair_extra.reviewassignment` provides functions relating to the assignment of 
submissions to PC members;
- `easychair_extra.submission` provides functions relating to the submissions.

## Learn by Examples

In the `examples` folder we provide example script of how to use the package. Check them out to
understand how the package works.

Example files for typical EasyChair outputs are located in the `easychair_sample_files` folder.

## Usage Policy

This package is provided as an open-source repository under a GNU 3.0 license.

If you are using this package and adding functionalities, please consider submitting pull requests.
Others may be looking for the same functionalities!