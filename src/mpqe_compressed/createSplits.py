import pathlib
import pickle
import rdflib
from typing import Iterator, List, Mapping, Set, Tuple

def intersect(split, validTriples, entitymapping, relationMapping) -> Tuple[Set[str], Set[str], Mapping[str, str], Set[Tuple[str, str, str]]]:
    '''
    Parameters
    ---------

    split:
        the data as provided in mpqe
    validTriples:
        a set of triples which really exist in the dataset.
        The predicate of these triples must have '.' replace by '' because that it how mpqe encoded them
    entitiMapping;
        a map from integer ID to URL for all entities in the split
    relationMapping:
        a mapping from all predicates with '.' replaced by '' to their original form. Used to restore the original form.

    Return
    ------

    A tuple with:
        * the set of entities used in the split
        * the set of relations used in the split
        * a mapping from each entity to its type
        * a set with all real triples from the split. Added inverses are removed, the relation URL has been mapped back to the original one.
    '''
    all_entities = set()
    all_relations = set()
    split_triples = set()
    type_info = {}
    for line in split:
        ((_chain, (subject_id, (subject_type, relation, object_type), object_id)), _, _) = line
        sub = entitymapping[subject_id]
        pre = relation
        obj = entitymapping[object_id]
        all_entities.add(sub)
        all_entities.add(obj)
        type_info[sub] = subject_type
        type_info[obj] = object_type
        triple = (sub, pre, obj)
        if triple in validTriples:
            pre = relationMapping[pre]
            all_relations.add(pre)
            triple = (sub, pre, obj)
            split_triples.add(triple)
    return all_entities, all_relations, type_info, split_triples


if __name__ == "__main__":
    data = pathlib.Path("./data/")
    datasets = ["AIFB", "AM", "MUTAG"]
    for dataset in datasets:
        rawTriplesFile = data / dataset / "raw" / (dataset.lower()+ "_stripped.nt")
        g = rdflib.Graph()
        with open(rawTriplesFile, 'rb') as f:
            g.parse(file=f, format='nt')
        triples = set()
        relationMapping = {}
        for s, p, o in g.triples((None, None, None)):
            # doing the same hack as mpqe. Otherwise nothing matches
            # Remove period from relations as they cannot occur in parameter
            # names in PyTorch
            predicate = str(p)
            strippedPredicate = predicate.replace('.', '')
            relationMapping[strippedPredicate] = predicate
            triples.add((str(s),strippedPredicate,str(o)))
        print (len(triples))
        processed = data / dataset / "processed"

        entitymappingFile = processed / "entity_ids.pkl"
        with open(entitymappingFile, 'rb') as f:
            ids = pickle.load(f)
        inv_ids = {v:k for k,v in ids.items()}


        used_entities = {}
        used_relations = {}
        valid_triples = {}
        type_infos = {}
        for split in ["train", "val", "test"]:
            splitDataPath = processed / (split + "_edges.pkl")
            with open(splitDataPath, "rb") as f:
                splitData = pickle.load(f)
            split_entities_used, split_relations_used, split_type_info, split_valid_triples = intersect(splitData, triples, inv_ids, relationMapping)
            used_entities[split] = split_entities_used
            used_relations[split] = split_relations_used
            valid_triples[split] = split_valid_triples
            type_infos[split] = split_type_info
        # computing some stats for information
        missing = used_entities["test"].difference(used_entities["train"])
        print (f"{dataset} has {len(missing)} entites in the test set which are not in training")


        # output stuff
        output_dir = data / dataset / "triple_split"
        output_dir.mkdir(exist_ok=True)


        # save all valid triples, split by set
        for split, corrected_name in [("train", "train"), ("val", "valid"), ("test", "test")]:
            triples = valid_triples[split]
            with open (output_dir / (corrected_name + ".nt"), "w") as f:
                for s,p,o in triples:
                    # note: all data in the mpqe sets are entities, s we can jsut wrap them with < >
                    f.write(f"<{s}> <{p}> <{o}> .\n")

        # save the entitiy list with their new ID
        merged_entities = list(used_entities["train"].union(used_entities["val"].union(used_entities["test"])))
        merged_entities.sort()
        with open(output_dir / "entoid", "w") as f:
            for index, entity in enumerate(merged_entities):
                f.write(f"{entity}\t{str(index)}\n")

        # save the relation list with their ID
        merged_relations = list(used_relations["train"].union(used_relations["val"].union(used_relations["test"])))
        merged_relations.sort
        with open(output_dir / "reltoid", "w") as f:
            for index, rel in enumerate(merged_relations):
                f.write(f"{rel}\t{str(index)}\n")

        # save the mapping from entity URL to type
        merged_type_info = {**type_infos["train"], **type_infos["val"], **type_infos["test"]}
        assert set(merged_entities) == set(merged_type_info.keys())
        with open (output_dir / "entity_url_typing.txt", "w") as f:
            # we will go over them in order of the merged_entities. this is maybe easier to keep an overview
            for entity in merged_entities:
                f.write(f"{entity}\t{merged_type_info[entity]}\n")

        # save the mapping from entity ID to type
        with open (output_dir / "entity_id_typing.txt", "w") as f:
            # we will go over them in order of the merged_entities. this is maybe easier to keep an overview
            for index, entity in enumerate(merged_entities):
                f.write(f"{index}\t{merged_type_info[entity]}\n")







