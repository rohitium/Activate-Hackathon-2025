# Protein Design Multi-Agent System

A multi-agent system using AgentOps to design proteins against specific drug targets.

## Features

- 🎯 Search for protein targets using RCSB PDB
- 📊 Download PDB files and extract chain information
- 🔬 Visualize protein structures with PyMOL
- 🧪 Identify protein-protein interactions at binding interfaces
- 💡 Suggest potential mutations to improve binding affinity

## Requirements

- Python 3.7+
- AgentOps
- PyMOL (installed separately - see installation instructions)
- BeautifulSoup4
- Requests
- NumPy
- BioPython
- httpx

## Installation

1. Clone this repository:
```bash
git clone https://github.com/rohitium/Activate-Hackathon-2025.git
cd Activate-Hackathon-2025
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Install PyMOL separately (NOT through pip):
   - **macOS**: `brew install brewsci/bio/pymol`
   - **Linux**: `sudo apt-get install pymol`
   - **Windows**: Download from [PyMOL website](https://pymol.org/2/)
   
   Note: PyMOL is not available as a simple pip package. The open-source version must be installed through package managers or compiled from source.

4. Set up your AgentOps API key:
```bash
export AGENTOPS_API_KEY=your_api_key
```

## Troubleshooting

If you encounter import errors:

1. **Missing httpx**: If you see `ModuleNotFoundError: No module named 'httpx'`, install it with:
   ```bash
   pip install httpx
   ```

2. **PyMOL not found**: Ensure PyMOL is properly installed and accessible in your system PATH. The visualization steps will fail if PyMOL is not correctly installed.

## Usage

Run the multi-agent system:

```bash
python protein_design_system.py
```

Or run the test script with a predefined example (CD20):

```bash
python test_agent_system.py
```

### System Features

1. **Target Selection**: Ask the user which target they want to design a binder for
2. **RCSB Search**: Search for the target on RCSB PDB and find relevant structures
3. **PDB Download**: Download the PDB file and extract chain information
4. **Structure Visualization**: Visualize the structure using PyMOL with chains colored

### Protein Improvement Agent

The system includes a protein improvement agent that can:

1. **Interface Analysis**: Identify residues at the interface between the antibody and target
2. **Mutation Suggestions**: Suggest potential mutations to improve binding affinity
3. **Mutation Visualization**: Visualize suggested mutations in PyMOL

## Example

```
Starting Protein Design Agent System
Which protein target would you like to design a binder for? CD20
Target selected: CD20
Searching for CD20 on RCSB PDB...
Found RCSB entry: https://www.rcsb.org/structure/6VJA
Downloading PDB file for 6VJA...
PDB file saved to /tmp/6VJA.pdb
Extracting chain information...
Getting chain information for 6VJA...
Chain information:
Chain C: B-lymphocyte antigen CD20
Chain D: B-lymphocyte antigen CD20
Chain I: Rituximab Fab heavy chain
Chain H: Rituximab Fab heavy chain
Visualizing structure 6VJA with PyMOL...
Structure visualization saved to /tmp/6VJA_colored.png

Do you want to analyze binding interface and suggest mutations? (y/n): y

Available chains:
Chain C: B-lymphocyte antigen CD20
Chain D: B-lymphocyte antigen CD20
Chain I: Rituximab Fab heavy chain
Chain H: Rituximab Fab heavy chain

Enter antibody chain ID: I
Enter target chain ID: C

Analyzing interface between chains I and C...
Found 42 residues at the interface
Chain I, Residue 31
Chain I, Residue 32
Chain I, Residue 33
...

Suggesting mutations for antibody chain I...
Generated 5 mutation suggestions:
1. ALA I:31 → TYR: Replacing small residue with larger aromatic to increase contacts
2. LYS I:54 → GLU: Potential salt bridge formation
...
```

## Future Developments

- Add binding site prediction
- Implement advanced protein design algorithms
- Add molecular dynamics simulation
- Integrate with AI models for drug discovery
- Support homology modeling for targets without crystal structures

## License

MIT