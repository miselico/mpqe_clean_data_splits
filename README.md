
The splits provided in [mpqe](https://github.com/dfdazac/mpqe) are very tailored to that implementation.
This script takes that data (the three sets AM, AIFB, MUTAG) and converts it into a more accessible form.

The generated files, for each of these datasets are:

The triples

* `test.nt` : the test triples in n-triples format
* `train.nt` : the training triples in n-triples format
* `valid.nt` : the validation triples in n-triples format

Mappings to unique IDs

* `entoid` : a mapping from each entity used in any of the three files above to a unique ID
* `reltoid`  : a mapping from each relation used in any of the three files above to a unique ID

The types of entities

* `entity_url_typing.txt` : a type label for each entity occurring in the files above
* `entity_id_typing.txt` : a type label for each entity occurring in the files above, indexed by the ID from `entiod`

These datasets are also in this repository `./data/compressed_triple_splits.zip`

To run things yourself, get the data from mpqe and extract them in the folder called data
Then, install the dependencies using
`pip install -e .`

Then run
`mpqe-

