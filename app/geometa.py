import GEOparse
import ftfy

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

    # Add link to gse (put in a list for consistency)
    gse.metadata['gse_link'] = ['https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + geo_accession_num]

    # Fix text
    gse.metadata['title'][0] = ftfy.fix_text(gse.metadata['title'][0])
    gse.metadata['summary'][0] = ftfy.fix_text(gse.metadata['summary'][0])
    gse.metadata['overall_design'][0] = ftfy.fix_text(gse.metadata['overall_design'][0])

    # Add Pubmed ID, if exists
    if 'pubmed_id' in gse.metadata:
        gse.metadata['pubmed_link'] = ["https://pubmed.ncbi.nlm.nih.gov/" + gse.metadata['pubmed_id'][0]]
    
    return gse.metadata

# def open_metadata(geo_accession):
#     """
#     Gets the metadata for the GEO Series.
#     Input: geo_accession, a string representing the GEO Accession ID (possibly with the GPL)
#         of the form GSEXXXXX(-GPLXXXX)
#     Output: A dictionary representing the metadata parsed by GEOparse, with keys being labels and values being that value of the
#         metadata label.
#     """
#     # Case where I have GPL in geo_accession
#     if "-" in geo_accession:
#         geo_accession_num = geo_accession.split("-", 1)[0]
#     else:
#         geo_accession_num = geo_accession
#     # Get gse from GEO
#     gse = GEOparse.get_GEO(filepath=f'./app/static/data/{geo_accession}/{geo_accession_num}_family.soft.gz')

#     return gse.metadata
