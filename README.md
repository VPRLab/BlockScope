# BlockScope: Detecting and Investigating Propagated Vulnerabilities in Forked Blockchain Projects

## Overview

`BlockScope` is the implementation of the paper titled *"BlockScope: Detecting and Investigating Propagated Vulnerabilities in Forked Blockchain Projects"* published in NDSS'23. `BlockScope` is a novel tool designed to automatically detect vulnerable code clones and pinpoint the cases already fixed and their patching process information.

## Usage

You can find the NDSS paper via this [link](https://daoyuan14.github.io/papers/NDSS23_BlockScope.pdf), and please consider citing our paper if it's helpful to you.

```latex
@INPROCEEDINGS{BLKSCP23,
 AUTHOR = {Xiao Yi and Yuzhou Fang and Daoyuan Wu and Lingxiao Jiang},
 TITLE = {{BlockScope}: Detecting and Investigating Propagated Vulnerabilities in Forked Blockchain Projects},
 BOOKTITLE = {Proc. ISOC NDSS},
 YEAR = {2023},
}
```

## Get Started

### Prerequisites

- We ran our experiments on Ubuntu 18.04.
- We used Python 3.10 to develop `BlockScope`.
- `BlockScope` relies on `requests`, `GitPython`, `PyGithub`, `nltk`, `strsimpy`, `selenium` and `PyDriller`. All the essential packages are listed in `requirements.txt`. 

There are steps to locally build `BlockScope`.

```shell
git clone git@github.com:VPRLab/BlockScope.git && cd BlockScope/src
pip install -r requirements.txt
```

###  Quick Start

There are two files for specifying the inputs for investigating Bitcoin and Ethereum forked projects, i.e., `inputs_bitcoin.py` and `inputs_ethereum.py`, respectively.

You need to first config the directory's path that stores these code repositories, e.g., for `inputs_bitcoin.py`:

```python
bitcoin_repo_dir = '/Users/xiao/PyCharmProjects/BlockScopeCodebase/BitcoinForks'
```

Then, you need to set the `IS_BITCOIN` value in the `configs.py` to `True` if you want to investigate Bitcoin's forked projects:

```python
IS_BITCOIN = True # False for investigating Ethereum's forked projects
```

Moreover, if you also want to investigate the delay in fixing a clone vulnerability in the forked projects, you can specify these values in the `configs.py`:

```python
DRIVER_PATH = '' # The path for selenium web driver
GITHUB_TOKEN = '' # Token for accessing GitHub
CALC_DELAY = True
```

Finally, you can run `block_scope.py` by executing the following command:

```shell
python ./block_scope.py
```
