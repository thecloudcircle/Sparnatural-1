import pandas as pd 
from wikidata2df import wikidata2df


def get_tooltips_dict(properties_df):

  prop_strings = properties_df["id"]

  query = f"""
  SELECT 
    ?prop_string 
    ?prop 
    ?propLabel
    ?propDescription
  WHERE{{
    VALUES ?prop_string   {{ "{'" "'.join(prop_strings)}" }}
    BIND (IRI (CONCAT("http://www.wikidata.org/entity/",?prop_string)) as ?prop)
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
  """

  tooltips_df = wikidata2df(query)
  tooltips_dict = {}
  for i, row in tooltips_df.iterrows():
    tooltips_dict[row.prop_string] = row.propDescription

  return tooltips_dict