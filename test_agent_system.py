#!/usr/bin/env python3
"""
Test script for the Protein Design Multi-Agent System
This script demonstrates the system using CD20 as a predefined example
"""

import os
from protein_design_system import AgentSystem
from protein_improvement_agent import ProteinImprovementAgent

def test_with_cd20():
    print("=== Testing Protein Design Agent System with CD20 ===")
    
    # Create agent system with predefined input
    agent_system = AgentSystem()
    agent_system.target = "CD20"
    print(f"Target selected: {agent_system.target}")
    
    # Search for target
    rcsb_link = agent_system.search_target()
    if rcsb_link:
        # Download PDB
        pdb_file = agent_system.download_pdb()
        if pdb_file:
            # Visualize structure
            agent_system.visualize_structure()
            
            print("\nAvailable chains:")
            for chain, desc in agent_system.chain_info.items():
                print(f"Chain {chain}: {desc}")
            
            # Use known antibody and target chains for CD20
            antibody_chain = None
            target_chain = None
            
            # Find the CD20 chain
            for chain, desc in agent_system.chain_info.items():
                if "CD20" in desc:
                    target_chain = chain
                    break
            
            # Find an antibody chain
            for chain, desc in agent_system.chain_info.items():
                if "heavy chain" in desc.lower() or "light chain" in desc.lower() or "fab" in desc.lower():
                    antibody_chain = chain
                    break
            
            if antibody_chain and target_chain:
                print(f"\nUsing antibody chain {antibody_chain} and target chain {target_chain}")
                
                # Create protein improvement agent
                improvement_agent = ProteinImprovementAgent(
                    pdb_file=agent_system.pdb_file_path,
                    pdb_id=agent_system.pdb_id
                )
                
                # Analyze interface
                improvement_agent.analyze_interface(antibody_chain, target_chain)
                
                # Suggest mutations
                suggestions = improvement_agent.suggest_mutations(antibody_chain)
                
                # Visualize the first mutation if there are any
                if suggestions:
                    improvement_agent.visualize_mutation(suggestions[0])
            else:
                print("Could not identify antibody and target chains automatically.")
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_with_cd20() 