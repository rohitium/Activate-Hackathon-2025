import sys
import os
import subprocess
import tempfile
import requests
import numpy as np
import agentops
from Bio.PDB import PDBParser, PDBIO, Select

class ContactSelect(Select):
    """Selection class to identify amino acids at protein-protein interfaces."""
    def __init__(self, chain_a, chain_b, cutoff=5.0):
        self.chain_a = chain_a
        self.chain_b = chain_b
        self.cutoff = cutoff
        self.contact_residues = set()
        
    def find_contacts(self, structure):
        """Find residues in contact between two chains."""
        # Get atoms from both chains
        atoms_a = [atom for atom in structure.get_atoms() if atom.get_parent().get_parent().id == self.chain_a]
        atoms_b = [atom for atom in structure.get_atoms() if atom.get_parent().get_parent().id == self.chain_b]
        
        # Calculate distances and find contacts
        for atom_a in atoms_a:
            res_a = atom_a.get_parent()
            for atom_b in atoms_b:
                res_b = atom_b.get_parent()
                distance = atom_a - atom_b  # This calculates the distance
                
                if distance <= self.cutoff:
                    self.contact_residues.add((self.chain_a, res_a.id[1]))
                    self.contact_residues.add((self.chain_b, res_b.id[1]))
        
        return self.contact_residues
    
    def accept_residue(self, residue):
        """Check if a residue should be included in the output."""
        chain_id = residue.get_parent().id
        res_id = residue.id[1]
        
        return (chain_id, res_id) in self.contact_residues

class ProteinImprovementAgent:
    def __init__(self, pdb_file=None, pdb_id=None):
        self.pdb_file = pdb_file
        self.pdb_id = pdb_id
        self.structure = None
        self.interface_residues = []
        
    def analyze_interface(self, antibody_chain, target_chain, cutoff=5.0):
        """Analyze the protein-protein interface."""
        with agentops.context("interface_analysis_agent"):
            print(f"Analyzing interface between chains {antibody_chain} and {target_chain}...")
            
            # Parse PDB structure
            parser = PDBParser(QUIET=True)
            self.structure = parser.get_structure('complex', self.pdb_file)
            
            # Find interface residues
            contact_select = ContactSelect(antibody_chain, target_chain, cutoff)
            interface_residues = contact_select.find_contacts(self.structure)
            
            # Organize residues by chain
            self.interface_residues = list(interface_residues)
            self.interface_residues.sort()
            
            print(f"Found {len(self.interface_residues)} residues at the interface")
            for chain, res_id in self.interface_residues[:10]:  # Show first 10
                print(f"Chain {chain}, Residue {res_id}")
            
            if len(self.interface_residues) > 10:
                print(f"... and {len(self.interface_residues) - 10} more residues")
            
            return self.interface_residues
    
    def save_interface_pdb(self, output_file=None):
        """Save the interface residues to a new PDB file."""
        if not self.structure or not self.interface_residues:
            print("No interface data available. Please run analyze_interface first.")
            return None
            
        if not output_file:
            output_file = os.path.join(tempfile.gettempdir(), f"{self.pdb_id}_interface.pdb")
            
        # Create a selection of interface residues
        chains = set(chain for chain, _ in self.interface_residues)
        contact_select = ContactSelect(chains.pop(), chains.pop())
        contact_select.contact_residues = set(self.interface_residues)
            
        # Save the selected residues
        io = PDBIO()
        io.set_structure(self.structure)
        io.save(output_file, contact_select)
            
        print(f"Interface saved to {output_file}")
        return output_file
    
    def suggest_mutations(self, antibody_chain):
        """Suggest mutations to improve binding affinity."""
        with agentops.context("mutation_suggestion_agent"):
            print(f"Suggesting mutations for antibody chain {antibody_chain}...")
            
            # Get interface residues in the antibody chain
            antibody_residues = [(chain, res_id) for chain, res_id in self.interface_residues 
                               if chain == antibody_chain]
            
            if not antibody_residues:
                print(f"No interface residues found in chain {antibody_chain}")
                return []
                
            # Simple rule-based suggestions (could be replaced with ML model)
            suggestions = []
            
            for chain, res_id in antibody_residues:
                # Get the residue
                for residue in self.structure[0][chain]:
                    if residue.id[1] == res_id:
                        res_name = residue.resname
                        
                        # Very simple rule-based suggestions
                        if res_name in ['ALA', 'GLY', 'SER']:
                            # Small residues could be replaced with larger ones to increase contact
                            suggestions.append({
                                'chain': chain,
                                'position': res_id,
                                'original': res_name,
                                'suggestion': 'TYR',
                                'reason': 'Replacing small residue with larger aromatic to increase contacts'
                            })
                        elif res_name in ['LYS', 'ARG']:
                            # Positively charged residues could be optimized
                            suggestions.append({
                                'chain': chain,
                                'position': res_id,
                                'original': res_name,
                                'suggestion': 'GLU',
                                'reason': 'Potential salt bridge formation'
                            })
                        
                        break
            
            # Display suggestions
            print(f"Generated {len(suggestions)} mutation suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"{i}. {suggestion['original']} {suggestion['chain']}:{suggestion['position']} → {suggestion['suggestion']}: {suggestion['reason']}")
                
            return suggestions
    
    def visualize_mutation(self, mutation):
        """Visualize a suggested mutation using PyMOL."""
        with agentops.context("mutation_visualization_agent"):
            chain = mutation['chain']
            position = mutation['position']
            new_residue = mutation['suggestion']
            
            print(f"Visualizing mutation: {mutation['original']} {chain}:{position} → {new_residue}")
            
            # Create PyMOL script
            pymol_script = os.path.join(tempfile.gettempdir(), f"mutation_vis_{chain}_{position}.pml")
            
            with open(pymol_script, 'w') as f:
                f.write(f"load {self.pdb_file}\n")
                f.write("bg_color white\n")
                f.write("show cartoon\n")
                
                # Highlight the mutation site
                f.write(f"select mutation_site, chain {chain} and resi {position}\n")
                f.write("show sticks, mutation_site\n")
                f.write("color red, mutation_site\n")
                
                # Show interface residues
                interface_selector = " or ".join([f"(chain {c} and resi {r})" for c, r in self.interface_residues])
                f.write(f"select interface, {interface_selector}\n")
                f.write("show sticks, interface\n")
                f.write("color yellow, interface\n")
                
                # Set nice view
                f.write("zoom mutation_site, 10\n")
                f.write(f"save {os.path.join(tempfile.gettempdir(), f'mutation_{chain}_{position}.png')}\n")
            
            try:
                # Run PyMOL with the script
                cmd = ["pymol", "-cq", pymol_script]
                subprocess.run(cmd, check=True)
                
                print(f"Mutation visualization saved to {os.path.join(tempfile.gettempdir(), f'mutation_{chain}_{position}.png')}")
                
                # Open the image
                if os.path.exists(os.path.join(tempfile.gettempdir(), f'mutation_{chain}_{position}.png')):
                    if os.name == 'nt':  # Windows
                        os.startfile(os.path.join(tempfile.gettempdir(), f'mutation_{chain}_{position}.png'))
                    elif os.name == 'posix':  # macOS and Linux
                        if 'darwin' in os.sys.platform:  # macOS
                            subprocess.run(['open', os.path.join(tempfile.gettempdir(), f'mutation_{chain}_{position}.png')])
                        else:  # Linux
                            subprocess.run(['xdg-open', os.path.join(tempfile.gettempdir(), f'mutation_{chain}_{position}.png')])
                
                return True
            except Exception as e:
                print(f"Failed to run PyMOL: {e}")
                return False

def main():
    # For testing purposes
    if len(sys.argv) > 1:
        pdb_file = sys.argv[1]
        pdb_id = os.path.basename(pdb_file).split('.')[0]
        
        antibody_chain = input("Enter antibody chain ID: ")
        target_chain = input("Enter target chain ID: ")
        
        agent = ProteinImprovementAgent(pdb_file=pdb_file, pdb_id=pdb_id)
        agent.analyze_interface(antibody_chain, target_chain)
        
        suggestions = agent.suggest_mutations(antibody_chain)
        
        if suggestions and input("Visualize a suggested mutation? (y/n): ").lower() == 'y':
            # Choose the first suggestion for simplicity
            agent.visualize_mutation(suggestions[0])

if __name__ == "__main__":
    main() 