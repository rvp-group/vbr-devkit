<div align="center">
    <h1>VBR Development Kit</h1>    

</div>
This kit contains utilities to work on the VBR SLAM dataset

# Install

```shell
pip install vbr-devkit
```

# Usage
You will find here the list of available commands to interact with our dataset

## Download sequences

```shell
vbr_download --dataset <sequence_name> --save-dir <output_path>
```

You can get the list of all the available sequences by using the `-h | --help` flag

```shell
❯ vbr_download -h
usage: vbr_download [-h] --dataset
                    {all,campus_test0,campus_test1,campus_train0,campus_train1,ciampino_test0,ciampino_t
est1,ciampino_train0,ciampino_train1,colosseo_test0,colosseo_train0,diag_test0,diag_train0,pincio_test0,
pincio_train0,spagna_test0,spagna_train0}
                    --save-dir PATH

╭─ options ────────────────────────────────────────────────────────────────────────────────────────────╮
│ -h, --help             show this help message and exit                                               │
│ --dataset                                                                                            │
│ {all,campus_test0,campus_test1,campus_train0,campus_train1,ciampino_test0,ciampino_test1,ciampino_t… │
│                        (required)                                                                    │
│ --save-dir PATH        (required)                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────╯
```


