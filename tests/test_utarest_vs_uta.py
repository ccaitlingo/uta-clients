import src.uta_clients.utarest as utarest
import hgvs.dataproviders.uta as uta

import datetime
import os
import yaml
import pytest
import vcr as vcrpy
from vcr.filters import decode_response
from typing import List, Dict


os.environ['UTAREST_URL'] = 'http://127.0.0.1:8000' # Used in utarest.connect()

def just_values(dictionaries: List[Dict]) -> List[List]:
    """Like the opposite of dict(), when dict() can't be used.
    (i.e. to compare just the values of a dictionary against a list of values)"""
    return [list(dictionary.values()) for dictionary in dictionaries]

def equal_regardless_of_order(list, other):
    """To compare lists that are neither hashable or stortable."""
    for item in list:
        try:
            other.remove(item)
        except ValueError:
            return False
    return True

def yaml_decode(test_name : str) -> str:
    """Opens a yaml file, gets the response, and returns it decoded."""
    file_path = ('tests/cassettes/{test}.yaml').format(test=test_name)
    with open(file_path, 'r') as f:
        yam = yaml.load(f, Loader=yaml.FullLoader)
    response = yam['interactions'][0]['response']
    yam_decode = decode_response(response)['body']['string']
    if isinstance(yam_decode, bytes):
        byte_decode = yam_decode.decode("utf-8")
        piece = byte_decode.split('\n')[1]
        return piece
    return yam_decode
        
#########################################################################
# u = UTA
# r = UTA Rest
        
@pytest.mark.skip(reason="super slow")
def test_utarest_seq_e():
    """Existing seq."""
    u = uta.connect().get_seq("NC_000007.13")
    r = utarest.connect().get_seq("NC_000007.13").json()
    assert u == r

@pytest.mark.vcr  
def test_utarest_seq_ne():
    """Nonexisting seq."""
    r = utarest.connect().get_seq("fake")
    assert r.status_code == 404
    with pytest.raises(uta.HGVSDataNotAvailableError):
        uta.connect().get_seq("fake")

#@pytest.mark.skip(reason="just not fast")
@pytest.mark.vcr
def test_utarest_seq_e_indices():
    """Existing seq with start and end indices."""
    u = uta.connect().get_seq("NC_000007.13", 10000, 10050)
    #u = yaml_decode('test_seq_e_indices')
    r = utarest.connect().get_seq("NC_000007.13", 10000, 10050).json()
    assert u == r

@pytest.mark.vcr
def test_utarest_acs_for_protein_seq_e():
    """Existing seq."""
    u = uta.connect().get_acs_for_protein_seq("MRAKWRKKRMRRLKRKRRKMRQRSK")
    r = utarest.connect().get_acs_for_protein_seq("MRAKWRKKRMRRLKRKRRKMRQRSK").json()
    assert u == r

@pytest.mark.vcr    
def test_utarest_acs_for_protein_seq_ne():
    """Nonexisting seq."""
    u = uta.connect().get_acs_for_protein_seq("fake")
    r = utarest.connect().get_acs_for_protein_seq("fake").json()
    assert u == r
    
@pytest.mark.vcr
def test_utarest_acs_for_protein_seq_ne_nonalphabetical():
    """Non-alphabetic character seq."""
    r = utarest.connect().get_acs_for_protein_seq("123")
    assert r.status_code == 404
    with pytest.raises(RuntimeError):
        uta.connect().get_acs_for_protein_seq("123")
        
@pytest.mark.vcr
def test_utarest_gene_info_e():
    """Existing gene."""
    u = dict(uta.connect().get_gene_info("VHL"))
    r = utarest.connect().get_gene_info("VHL").json()
    r["added"] = datetime.datetime.fromisoformat(r["added"])
    assert u == r
    
@pytest.mark.vcr
def test_utarest_gene_info_ne():
    """Nonexistng gene."""
    u = uta.connect().get_gene_info("VH")
    r = utarest.connect().get_gene_info("VH").json()
    assert u == r
        
@pytest.mark.vcr
def test_utarest_tx_exons_e():
    """Existing seqs."""
    u = uta.connect().get_tx_exons("NM_199425.2", "NC_000020.10", "splign")
    r = just_values(utarest.connect().get_tx_exons("NM_199425.2", "NC_000020.10", "splign").json())
    assert u == r
    
@pytest.mark.vcr
def test_utarest_tx_exons_ne():
    """Nonexisting seq."""
    r = utarest.connect().get_tx_exons("NM_199425.2", "fake", "splign")
    assert r.status_code == 404
    with pytest.raises(uta.HGVSDataNotAvailableError):
        uta.connect().get_tx_exons("NM_199425.2", "fake", "splign")
        
@pytest.mark.vcr
def test_utarest_tx_exons_e_params():
    """Existing seqs with missing param"""
    with pytest.raises(TypeError):
        utarest.connect().get_tx_exons("NM_199425.2", "NC_000020.10")
    with pytest.raises(TypeError):
        uta.connect().get_tx_exons("NM_199425.2", "NC_000020.10")
        
@pytest.mark.vcr
def test_utarest_tx_exons_ne_params():
    """Existing seqs with missing param"""
    with pytest.raises(TypeError):
        utarest.connect().get_tx_exons("NM_199425.2", "fake")
    with pytest.raises(TypeError):
        uta.connect().get_tx_exons("NM_199425.2", "fake")
        
@pytest.mark.vcr
def test_utarest_tx_for_gene_e():
    """Existing gene."""
    u = uta.connect().get_tx_for_gene("VHL")
    r = utarest.connect().get_tx_for_gene("VHL").json()
    assert equal_regardless_of_order(u, r)
    
@pytest.mark.vcr
def test_utarest_tx_for_gene_ne():
    """Nonexisitng gene."""
    u = uta.connect().get_tx_for_gene("VH")
    r = utarest.connect().get_tx_for_gene("VH").json()
    assert u == r
    
@pytest.mark.vcr
def test_utarest_tx_for_region_e(): # Need example
    """Existing region."""
    u = uta.connect().get_tx_for_region("NC_000007.13", "splign", 0, 50)
    r = utarest.connect().get_tx_for_region("NC_000007.13", "splign", 0, 50).json()
    assert u == r
    
@pytest.mark.vcr
def test_utarest_tx_for_region_ne():
    """Nonexisting region"""
    u = uta.connect().get_tx_for_region("fake", "splign", 0, 50)
    r = utarest.connect().get_tx_for_region("fake", "splign", 0, 50).json()
    assert u == r
    
@pytest.mark.vcr
def test_utarest_tx_for_region_e_params():
    """Existing region with only some params."""
    with pytest.raises(TypeError):
        utarest.connect().get_tx_for_region("NC_000007.13", "splign")
    with pytest.raises(TypeError):
        uta.connect().get_tx_for_region("NC_000007.13", "splign")
        
@pytest.mark.vcr
def test_utarest_tx_for_region_ne_params():
    """Existing region with only some params."""
    with pytest.raises(TypeError):
        utarest.connect().get_tx_for_region("fake", "splign")
    with pytest.raises(TypeError):
        uta.connect().get_tx_for_region("fake", "splign")
    
@pytest.mark.vcr
def test_utarest_alignments_for_region_e(): # Need example
    """Existing region."""
    u = uta.connect().get_alignments_for_region("NC_000007.13", 0, 50)
    r = utarest.connect().get_alignments_for_region("NC_000007.13", 0, 50).json()
    assert u == r
    
@pytest.mark.vcr
def test_utarest_alignments_for_region_ne():
    """Nonexisting region"""
    u = uta.connect().get_alignments_for_region("fake", 0, 50)
    r = utarest.connect().get_alignments_for_region("fake", 0, 50).json()
    assert u == r
    
@pytest.mark.vcr
def test_utarest_alignments_region_e_params():
    """Existing region with only some params."""
    with pytest.raises(TypeError):
        utarest.connect().get_alignments_for_region("NC_000007.13")
    with pytest.raises(TypeError):
        uta.connect().get_alignments_for_region("NC_000007.13")
        
@pytest.mark.vcr
def test_utarest_alignments_region_ne_params():
    """Existing region with only some params."""
    with pytest.raises(TypeError):
        utarest.connect().get_alignments_for_region("fake")
    with pytest.raises(TypeError):
        uta.connect().get_alignments_for_region("fake")
    
@pytest.mark.vcr
def test_utarest_tx_identity_info_e():
    """Existing transcript."""
    u = dict(uta.connect().get_tx_identity_info("NM_199425.2"))
    r = utarest.connect().get_tx_identity_info("NM_199425.2").json()
    assert u == r
    
@pytest.mark.vcr
def test_utarest_tx_identity_info_ne():
    """Nonexisting transcript."""
    r = utarest.connect().get_tx_identity_info("fake")
    assert r.status_code == 404
    with pytest.raises(uta.HGVSDataNotAvailableError):
        uta.connect().get_tx_identity_info("fake")
        
@pytest.mark.vcr
def test_utarest_tx_info_e():
    """Existing seqs."""
    u = dict(uta.connect().get_tx_info("NM_199425.2", "NC_000020.10", "splign"))
    r = utarest.connect().get_tx_info("NM_199425.2", "NC_000020.10", "splign").json()
    assert u == r
    
@pytest.mark.vcr
def test_utarest_tx_info_ne():
    """Nonexisting seq."""
    r = utarest.connect().get_tx_info("NM_199425.2", "fake", "splign")
    assert r.status_code == 404
    with pytest.raises(uta.HGVSDataNotAvailableError):
        uta.connect().get_tx_info("NM_199425.2", "fake", "splign")
        
@pytest.mark.vcr
def test_utarest_tx_info_e_param():
    """Existing seqs."""
    with pytest.raises(TypeError):
        utarest.connect().get_tx_info("NM_199425.2", "NC_000020.10")
    with pytest.raises(TypeError):
        uta.connect().get_tx_info("NM_199425.2", "NC_000020.10")   
    
@pytest.mark.vcr
def test_utarest_tx_info_ne_param():
    """Existing seqs."""  
    with pytest.raises(TypeError):
        utarest.connect().get_tx_info("NM_199425.2", "fake")
    with pytest.raises(TypeError):
        uta.connect().get_tx_info("NM_199425.2", "fake")    
        
@pytest.mark.vcr
def test_utarest_tx_mapping_options_e():
    """Existing transcript."""
    u = uta.connect().get_tx_mapping_options("NM_000051.3")
    r = just_values(utarest.connect().get_tx_mapping_options("NM_000051.3").json())
    assert u == r
       
@pytest.mark.vcr
def test_utarest_tx_mapping_options_ne():
    """Nonexisting transcript."""
    u = uta.connect().get_tx_mapping_options("fake")
    r = just_values(utarest.connect().get_tx_mapping_options("fake").json())
    assert u == r
    
@pytest.mark.vcr
def test_utarest_similar_transcripts_e():
    """Existing transcript."""
    u = uta.connect().get_similar_transcripts("NM_000051.3")
    r = just_values(utarest.connect().get_similar_transcripts("NM_000051.3").json())
    assert u == r
    
@pytest.mark.vcr
def test_utarest_similar_transcripts_ne():
    """Nonexisting transcript."""
    u = uta.connect().get_similar_transcripts("fake")
    r = just_values(utarest.connect().get_similar_transcripts("fake").json())
    assert u == r
    
@pytest.mark.vcr
def test_utarest_pro_ac_for_tx_ac_e():
    """Existing transcript."""
    u = uta.connect().get_pro_ac_for_tx_ac("NM_000051.3")
    r = utarest.connect().get_pro_ac_for_tx_ac("NM_000051.3").json()
    assert u == r
    
@pytest.mark.vcr
def test_utarest_pro_ac_for_tx_ac_ne():
    """Nonexisting transcript."""   
    u = uta.connect().get_pro_ac_for_tx_ac("fake")
    r = utarest.connect().get_pro_ac_for_tx_ac("fake").json()
    assert u == r
    
@pytest.mark.vcr
def test_utarest_assembly_map_e():
    """Existing assembly name."""
    u = dict(uta.connect().get_assembly_map("GRCh38.p5"))
    r = utarest.connect().get_assembly_map("GRCh38.p5").json()
    assert u == r
    
@pytest.mark.vcr
def test_utarest_assembly_map_ne():
    """Nonexisting assembly name."""
    r = utarest.connect().get_assembly_map("GROUCH")
    assert r.status_code == 404
    with pytest.raises(Exception):
        uta.connect().get_assembly_map("GROUCH")
     
@pytest.mark.vcr
def test_utarest_data_version():
    u = uta.connect().data_version()
    r = utarest.connect().data_version()
    assert u == r
    
@pytest.mark.vcr
def test_utarest_schema_version():
    u = uta.connect().schema_version()
    r = utarest.connect().schema_version()
    assert u == r
    
@pytest.mark.vcr
def test_utarest_sequence_source():
    u = uta.connect().sequence_source()
    r = utarest.connect().sequence_source()
    assert u == r