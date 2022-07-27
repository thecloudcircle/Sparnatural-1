import pandas as pd
from wikidata2df import wikidata2df


def get_tooltips_dict(list_of_wikidata_ids):
    query = f"""
  SELECT 
    ?prop_string 
    ?prop 
    ?propLabel
    ?propDescription
  WHERE{{
    VALUES ?prop_string   {{ "{'" "'.join(list_of_wikidata_ids)}" }}
    BIND (IRI (CONCAT("http://www.wikidata.org/entity/",?prop_string)) as ?prop)
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
  """

    tooltips_df = wikidata2df(query)
    tooltips_dict = {}
    for i, row in tooltips_df.iterrows():
        tooltips_dict[row.prop_string] = row.propDescription

    return tooltips_dict
