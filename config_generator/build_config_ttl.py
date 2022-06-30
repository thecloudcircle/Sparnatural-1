import os
import pandas as pd
from owlready2 import *
from pathlib import Path
import rdflib
from pull_tooltips import get_tooltips_dict

_g = globals()

order_dict = {
    "Disease": 1,
    "Gene": 2,
    "Chemical_Compound": 3,
    "Cell_Type": 4,
    "Clinical_Trial": 5,
}

HERE = Path(__file__).parent.resolve()

# Import and load Sparnatural ontologies
# region --------
onto = get_ontology(
    "http://www.semanticweb.org/lubianat/ontologies/2022/4/sparnanatural_wisecube"
)
config_core = get_ontology(
    "http://data.sparna.fr/ontologies/sparnatural-config-core"
).load()
rdfs = get_ontology("http://www.w3.org/2000/01/rdf-schema").load()
sparnatural_config_datasources = get_ontology(
    "http://data.sparna.fr/ontologies/sparnatural-config-datasources"
).load()
onto.imported_ontologies.append(config_core)
onto.imported_ontologies.append(sparnatural_config_datasources)
# endregion --------

# Prepare base properties from the Sparnatural ontologies
# region --------


with config_core:

    class sparqlString(AnnotationProperty):
        pass

    class tooltip(AnnotationProperty):
        pass

    class faIcon(AnnotationProperty):
        pass


with sparnatural_config_datasources:

    class datasource(AnnotationProperty):
        pass

    class queryTemplate(ObjectProperty, FunctionalProperty):
        pass

    class queryString(DatatypeProperty, FunctionalProperty):
        pass


with onto:

    class SPARQLQuery(Thing):
        pass

    class SparqlSearchDatasource(sparnatural_config_datasources.SparqlDatasource):
        pass


with rdfs:

    class Literal(config_core.SparnaturalClass):
        pass


# endregion --------

# Configure Wikidata-specific datasources
# region --------
query_names = [
    "search_wikidata_basic",
    "search_wikidata_in_humans",
    "search_wikidata_domain_in_humans",
    "search_wikidata_all_of_the_type",
    "search_wikidata_all_of_the_type_run_last_prop",
]

for query_name in query_names:
    query_template_name = f"query_{query_name}"
    _g[query_template_name] = SPARQLQuery(
        query_template_name,
        queryString=HERE.joinpath(f"queries/{query_name}.rq").read_text(),
    )
    _g[query_template_name].is_a.append(sparnatural_config_datasources.SPARQLQuery)

    _g[query_name] = SparqlSearchDatasource(
        query_name, queryTemplate=_g[query_template_name]
    )
    _g[query_name].is_a.append(sparnatural_config_datasources.SparqlSearchDatasource)

# endregion --------

# Create labelling property
with onto:
    prop_label = "name"
    _g[prop_label] = types.new_class(prop_label, (ObjectProperty,))

# Create classes
# region --------
os.system(
    "wget -O config.xlsx https://docs.google.com/spreadsheets/d/e/2PACX-1vQr05HsgKSLxbcghffHtYypd-sLWC6wUnfsp4BeXfwV2UeQUqOZKloZAHZo4e4pcUwyzxS7ayKqZq4-/pub?output=xlsx"
)

classes = pd.read_excel("config.xlsx", sheet_name=f"classes")
graph = []
class_tooltips_dict = get_tooltips_dict(classes["id"])
for i, row in classes.iterrows():

    with onto:
        class_label = row.label.replace(" ", "_")
        if class_label == "Date" or class_label == "Text":
            _g[class_label] = types.new_class(class_label, (rdfs.Literal,))
        else:
            _g[class_label] = types.new_class(
                class_label, (config_core.SparnaturalClass,)
            )
            _g[class_label].sparqlString = f"<http://www.wikidata.org/entity/{row.id}>"
        _g[class_label].label = [locstr(class_label.replace("_", " "), lang="en")]
        _g[class_label].faIcon = f"fas {row['font_awesome']}"
        if row["tool_tip"] != "-":
            _g[class_label].tooltip = row["tool_tip"]
        else:
            _g[class_label].tooltip = class_tooltips_dict[row["id"]]

        if class_label in order_dict:
            _g[class_label].order = order_dict[class_label]

        if class_label != "Text":
            _g[class_label].defaultLabelProperty = name
# endregion --------

# Create properties
# region --------
properties = pd.read_excel("config.xlsx", sheet_name=f"properties")
properties = properties.dropna(subset=["label"])
tooltips_dict = get_tooltips_dict(properties["id"])
for i, row in properties.iterrows():

    with onto:
        prop_label = row.label.replace(" ", "_")
        _g[prop_label] = types.new_class(prop_label, (ObjectProperty,))
        _g[prop_label].is_a.append(config_core[row.superproperty])

        if "&" in row.domain:
            domain_names = [
                name.strip().replace(" ", "_") for name in row.domain.split("&")
            ]
            domain_classes = [_g[prop_name] for prop_name in domain_names]
            prop_domains = Or(domain_classes)
        else:
            prop_domains = [_g[row.domain.replace(" ", "_")]]

        if "&" in row.range:
            range_names = [
                name.strip().replace(" ", "_") for name in row.range.split("&")
            ]
            range_classes = [_g[prop_name] for prop_name in range_names]
            prop_ranges = Or(range_classes)
        else:
            prop_ranges = [_g[row.range.replace(" ", "_")]]

        _g[prop_label].domain = prop_domains
        _g[prop_label].range = prop_ranges
        if row.id[0] != "P":
            _g[prop_label].sparqlString = row.id
        else:
            _g[
                prop_label
            ].sparqlString = f"<http://www.wikidata.org/prop/direct/{row.id}>"

        if row.tool_tip == "-":
            _g[prop_label].tooltip = tooltips_dict[row.id]
        else:
            _g[prop_label].tooltip = row.tool_tip

        if row.datasource != "-":
            _g[prop_label].datasource = _g[row.datasource]

        if row.superproperty == "SearchProperty":
            _g[prop_label].isMultilingual = True
        else:
            _g[prop_label].enableNegation = [locstr("true", lang="en")]
            _g[prop_label].enableOptional = [locstr("true", lang="en")]

        _g[prop_label].label = [locstr(prop_label.replace("_", " "), lang="en")]

        if row.infer_inverse == "yes":

            inverse_prop_label = row.inverse_label.replace(" ", "_")
            _g[inverse_prop_label] = types.new_class(
                inverse_prop_label, (config_core.AutocompleteProperty,)
            )

            # Note that domain and range are now swithced.
            _g[inverse_prop_label].domain = prop_ranges
            _g[inverse_prop_label].range = prop_domains
            _g[
                inverse_prop_label
            ].sparqlString = f"^<http://www.wikidata.org/prop/direct/{row.id}>"
            _g[inverse_prop_label].tooltip = [locstr(row.inverse_tool_tip, lang="en")]

            # Inverse datasources that need to be inverted, other than that, go to default
            if row.datasource == "search_wikidata_in_humans":
                _g[inverse_prop_label].datasource = _g[
                    "search_wikidata_domain_in_humans"
                ]
            elif row.datasource == "search_wikidata_domain_in_humans":
                _g[inverse_prop_label].datasource = _g["search_wikidata_in_humans"]
            else:
                _g[inverse_prop_label].datasource = search_wikidata_basic

            _g[inverse_prop_label].label = [
                locstr(inverse_prop_label.replace("_", " "), lang="en")
            ]
            _g[inverse_prop_label].enableNegation = [locstr("true", lang="en")]
            _g[inverse_prop_label].enableOptional = [locstr("true", lang="en")]


# endregion --------


onto.save(file=f"{HERE}/config_python_test.rdf", format="rdfxml")

g = rdflib.Graph()
onto_path = HERE.joinpath("config_python_test.rdf").resolve()
g.parse(onto_path, format="xml")
g.serialize(
    destination=HERE.parent.joinpath("src")
    .joinpath("config_python_test.ttl")
    .resolve(),
    format="turtle",
)
