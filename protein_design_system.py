import os
import requests
import tempfile
import subprocess
import re
from bs4 import BeautifulSoup
from agents import Agent, Runner
import agentops

# Initialize AgentOps - simple initialization
agentops.init()

class ProteinDesignSystem:
    def __init__(self):
        self.target = None
        self.pdb_id = None
        self.pdb_file_path = None
        self.chain_info = {}
        
        # Create our agent
        self.assistant = Agent(
            name="ProteinDesignAssistant",
            instructions="You are a protein structure expert that helps find and analyze PDB structures."
        )
    
    def ask_target(self):
        """Ask user for target protein"""
        self.target = input("Which protein target would you like to design a binder for? ")
        print(f"Target selected: {self.target}")
        return self.target
    
    def search_target(self):
        """Search for target on RCSB PDB using our agent"""
        print(f"Searching for {self.target} on RCSB PDB...")
        
        # Use agent to help find PDB ID
        prompt = f"""
        Find the most relevant PDB structure ID for the protein target '{self.target}'. 
        If you know a specific PDB ID for this target, provide only that ID. 
        Common examples:
        - CD20: 6VJA
        - PD1: 6NM8
        - HER2: 6OGE
        Only respond with a 4-character PDB ID.
        """
        
        response = Runner.run_sync(self.assistant, prompt)
        result = response.final_output.strip()
        
        # Extract PDB ID (4 characters, starting with a number followed by letters/numbers)
        pdb_id_match = re.search(r'\b[1-9][A-Za-z0-9]{3}\b', result)
        if pdb_id_match:
            self.pdb_id = pdb_id_match.group(0)
            rcsb_link = f"https://www.rcsb.org/structure/{self.pdb_id}"
            print(f"Found RCSB entry: {rcsb_link}")
            return rcsb_link
        
        # Fallback for specific targets if the agent doesn't provide a valid PDB ID
        if self.target.lower() == "cd20":
            self.pdb_id = "6VJA"
            rcsb_link = f"https://www.rcsb.org/structure/{self.pdb_id}"
            print(f"Using known structure for CD20: {rcsb_link}")
            return rcsb_link
            
        print(f"No PDB ID found for {self.target}")
        return None

    def download_pdb(self):
        """Download PDB file and extract chain information"""
        if not self.pdb_id:
            print("No PDB ID available. Please search for a target first.")
            return None
            
        print(f"Downloading PDB file for {self.pdb_id}...")
        url = f"https://files.rcsb.org/download/{self.pdb_id}.pdb"
        
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                # Save PDB file
                temp_dir = tempfile.gettempdir()
                self.pdb_file_path = os.path.join(temp_dir, f"{self.pdb_id}.pdb")
                
                with open(self.pdb_file_path, 'w') as f:
                    f.write(response.text)
                
                print(f"PDB file saved to {self.pdb_file_path}")
                
                # Extract chain information
                self._extract_chain_info_simple()
                return self.pdb_file_path
            else:
                print(f"Failed to download PDB file: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading PDB file: {e}")
            return None
    
    def _extract_chain_info_simple(self):
        """Simple method to extract chain IDs from PDB file"""
        if not self.pdb_file_path:
            return
            
        chains = set()
        try:
            with open(self.pdb_file_path, 'r') as f:
                for line in f:
                    if line.startswith(('ATOM', 'HETATM')) and len(line) > 21:
                        chain_id = line[21]
                        chains.add(chain_id)
            
            # Get chain descriptions using our agent
            if chains:
                prompt = f"""
                For PDB structure {self.pdb_id}, describe what each chain represents.
                Chains: {', '.join(sorted(chains))}
                
                Example response format:
                A: Target protein
                B: Antibody heavy chain
                C: Antibody light chain
                
                Only provide chain IDs and descriptions, nothing else.
                """
                
                response = Runner.run_sync(self.assistant, prompt)
                chain_descriptions = response.final_output.strip()
                
                # Parse the response
                for line in chain_descriptions.split('\n'):
                    if ':' in line:
                        parts = line.split(':', 1)
                        chain = parts[0].strip()
                        desc = parts[1].strip()
                        self.chain_info[chain] = desc
                
                # Add any chains that weren't described
                for chain in chains:
                    if chain not in self.chain_info:
                        self.chain_info[chain] = f"Chain {chain}"
            else:
                # Default to generic chain info
                self.chain_info = {'A': 'Chain A'}
                
            print("Chain information:")
            for chain, desc in self.chain_info.items():
                print(f"Chain {chain}: {desc}")
                
        except Exception as e:
            print(f"Error extracting chain info: {e}")
            # Create generic chain info
            self.chain_info = {chain: f"Chain {chain}" for chain in chains} if chains else {'A': 'Chain A'}
            
    def visualize_structure(self):
        """Visualize the structure using PyMOL"""
        if not self.pdb_file_path:
            print("No PDB file available. Please download a PDB file first.")
            return False
            
        print(f"Visualizing structure {self.pdb_id} with PyMOL...")
        
        # Create PyMOL script
        pymol_script = os.path.join(tempfile.gettempdir(), f"{self.pdb_id}_visualization.pml")
        image_path = os.path.join(tempfile.gettempdir(), f"{self.pdb_id}_colored.png")
        
        with open(pymol_script, 'w') as f:
            f.write(f"load {self.pdb_file_path}\n")
            f.write("bg_color white\n")
            
            # Color chains
            colors = ["red", "green", "blue", "yellow", "magenta", "cyan", "orange", "purple", "pink", "lime"]
            color_idx = 0
            
            for chain in self.chain_info.keys():
                color = colors[color_idx % len(colors)]
                f.write(f"color {color}, chain {chain}\n")
                color_idx += 1
            
            f.write("show cartoon\n")
            f.write("zoom\n")
            f.write(f"save {image_path}\n")
        
        try:
            # Run PyMOL with the script
            cmd = ["pymol", "-cq", pymol_script]
            subprocess.run(cmd, check=True)
            
            print(f"Structure visualization saved to {image_path}")
            
            # Open the image
            if os.path.exists(image_path):
                if os.name == 'nt':  # Windows
                    os.startfile(image_path)
                elif os.name == 'posix':  # macOS and Linux
                    if 'darwin' in os.sys.platform:  # macOS
                        subprocess.run(['open', image_path])
                    else:  # Linux
                        subprocess.run(['xdg-open', image_path])
            
            return True
        except Exception as e:
            print(f"Failed to run PyMOL: {e}")
            print("Make sure PyMOL is installed and accessible in your PATH.")
            return False

def main():
    print("Starting Protein Design Agent System")
    
    # Verify OpenAI API key for the agent
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY=your_api_key")
        return
    
    # Create the system
    system = ProteinDesignSystem()
    
    # Run the workflow
    target = system.ask_target()
    if target:
        rcsb_link = system.search_target()
        if rcsb_link:
            pdb_file = system.download_pdb()
            if pdb_file:
                system.visualize_structure()

if __name__ == "__main__":
    main() 