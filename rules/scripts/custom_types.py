from typing import Dict, List, Tuple
from enum import Enum

class DataType(Enum):
    """Data type for MSAs.
    - DNA = DNA data
    - AA = Protein data
    - MORPH = morphological data
    """

    DNA = "DNA"
    AA = "AA"
    MORPH = "MORPH"


class FileFormat(Enum):
    """File formats for MSAs
    - PHYLIP = phylip-relaxed
    - FASTA = fasta
    """

    PHYLIP = "phylip-relaxed"
    FASTA = "fasta"

Newick = str
TreeIndex = int
TreeTreeIndexed = Dict[Tuple[TreeIndex, TreeIndex], float]
