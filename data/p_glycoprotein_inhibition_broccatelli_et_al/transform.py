import pandas as pd
import yaml
from tdc.single_pred import ADME


def get_and_transform_data():
    # get raw data
    target_subfolder = "Pgp_Broccatelli"
    splits = ADME(name=target_subfolder).get_split()
    df_train = splits["train"]
    df_valid = splits["valid"]
    df_test = splits["test"]
    df_train["split"] = "train"
    df_valid["split"] = "valid"
    df_test["split"] = "test"
    df = pd.concat([df_train, df_valid, df_test], axis=0)

    fn_data_original = "data_original.csv"
    df.to_csv(fn_data_original, index=False)
    del df

    # create dataframe
    df = pd.read_csv(
        fn_data_original,
        delimiter=",",
    )  # not necessary but ensure we can load the saved data

    # check if fields are the same
    fields_orig = df.columns.tolist()
    assert fields_orig == ["Drug_ID", "Drug", "Y", "split"]

    # overwrite column names = fields
    fields_clean = ["compound_name", "SMILES", "Pgp_inhibition", "split"]
    df.columns = fields_clean

    # data cleaning
    # remove leading and trailing white space characters
    df.compound_name = df.compound_name.str.strip()

    df = df.dropna()
    assert not df.duplicated().sum()

    # save to csv
    fn_data_csv = "data_clean.csv"
    df.to_csv(fn_data_csv, index=False)

    # create meta yaml
    meta = {
        "name": "p_glycoprotein_inhibition_broccatelli_et_al",
        "description": """P-glycoprotein (Pgp) is an ABC transporter protein involved in intestinal
absorption, drug metabolism, and brain penetration, and its inhibition can seriously
alter a drug's bioavailability and safety. In addition, inhibitors of Pgp can
be used to overcome multidrug resistance.""",
        "targets": [
            {
                "id": "Pgp_inhibition",  # name of the column in a tabular dataset
                "description": "whether it shows Pgp inhibition (1) or not (0)",
                "units": None,  # units of the values in this column (leave empty if unitless)
                "type": "boolean",  # can be "categorical", "ordinal", "continuous"
                "names": [  # names for the property (to sample from for building the prompts)
                    {"noun": "P-glycoprotein inhibition"},
                    {"noun": "Pgp inhibition"},
                    {"verb": "shows Pgp inhibition"},
                ],
                "uris": [
                    "http://purl.bioontology.org/ontology/CSP/4000-0278",
                ],
            },
        ],
        "benchmarks": [
            {
                "name": "TDC",  # unique benchmark name
                "link": "https://tdcommons.ai/",  # benchmark URL
                "split_column": "split",  # name of the column that contains the split information
            },
        ],
        "identifiers": [
            {
                "id": "SMILES",  # column name
                "type": "SMILES",  # can be "SMILES", "SELFIES", "IUPAC", "Other"
                "description": "SMILES",  # description (optional, except for "Other")
            },
            {
                "id": "compound_name",  # column name
                "type": "Other",  # can be "SMILES", "SELFIES", "IUPAC", "Other"
                "names": [
                    "compound name",
                    "drug name",
                    "generic drug name",
                ],
                "description": "drug name",  # description (optional, except for "Other")
            },
        ],
        "license": "CC BY 4.0",  # license under which the original dataset was published
        "links": [  # list of relevant links (original dataset, other uses, etc.)
            {
                "url": "https://doi.org/10.1021/jm101421d",
                "description": "corresponding publication",
            },
            {
                "url": "https://tdcommons.ai/single_pred_tasks/adme/#pgp-p-glycoprotein-inhibition-broccatelli-et-al",
                "description": "data source",
            },
        ],
        "num_points": len(df),  # number of datapoints in this dataset
        "bibtex": [
            """@article{Broccatelli2011,
doi = {10.1021/jm101421d},
url = {https://doi.org/10.1021/jm101421d},
year = {2011},
month = feb,
publisher = {American Chemical Society (ACS)},
volume = {54},
number = {6},
author = {Fabio Broccatelli and Emanuele Carosati and Annalisa Neri and
Maria Frosini and Laura Goracci and Tudor I. Oprea and Gabriele Cruciani},
title = {A Novel Approach for Predicting P-Glycoprotein (ABCB1) Inhibition
Using Molecular Interaction Fields},
journal = {Journal of Medicinal Chemistry}""",
        ],
    }

    def str_presenter(dumper, data):
        """configures yaml for dumping multiline strings
        Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
        """
        if data.count("\n") > 0:  # check for multiline string
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.add_representer(str, str_presenter)
    yaml.representer.SafeRepresenter.add_representer(
        str, str_presenter
    )  # to use with safe_dum
    fn_meta = "meta.yaml"
    with open(fn_meta, "w") as f:
        yaml.dump(meta, f, sort_keys=False)

    print(f"Finished processing {meta['name']} dataset!")


if __name__ == "__main__":
    get_and_transform_data()
