import GEOparse

def get_metadata(geo_accession):
    """
    Gets the metadata for the GEO Series.
    Input: geo_accession, a string representing the GEO Accession ID (possibly with the GPL)
        of the form GSEXXXXX(-GPLXXXX)
    Output: A dictionary representing the metadata parsed by GEOparse, with keys being labels and values being that value of the
        metadata label.
    """
    # Case where I have GPL in geo_accession
    if "-" in geo_accession:
        geo_accession_num = geo_accession.split("-", 1)[0]
    else:
        geo_accession_num = geo_accession
    # Get gse from GEO
    gse = GEOparse.get_GEO(geo = geo_accession_num, destdir = f'./app/static/data/{geo_accession}')

    return gse.metadata

