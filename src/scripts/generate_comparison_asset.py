
def generate_comparison():
    print("="*60)
    print(" [MARKET ANALYSIS: FLUFF VS. FORENSICS]")
    print("="*60)
    
    comparisons = [
        {
            "scenario": "Saturn Transit to 6th House",
            "competitor": "You are navigating a period of deep internal transformation. Take time for self-care.",
            "codex": "Saturn activates the 6th House (Injury/Labor). Expect increased workload and potential bone/tooth issues. Remediation: Disciplined routine."
        },
        {
            "scenario": "Mars Square Sun",
            "competitor": "Energy levels are high! Channel this into something creative.",
            "codex": "Mars (Sectional Malefic) squares Sun. Acute conflict with authority figures. Risk of fever or inflammation. Avoid impulsive actions."
        },
         {
            "scenario": "Venus in 2nd House (Detriment)",
            "competitor": "Your values are shifting. Listen to your heart.",
            "codex": "Venus in Scorpio (Detriment). Financial scarcity due to overspending on luxuries. Asset liquidation likely."
        }
    ]
    
    print(f"{'THEM (The Fluff)':<50} | {'US (The Math)':<50}")
    print("-" * 105)
    
    for item in comparisons:
        them = item['competitor']
        us = item['codex']
        
        # Simple wrapping simulation
        print(f"{them:<50} | {us:<50}")
        print("-" * 105)

    print("\n[VERDICT]")
    print("We respect you enough to tell the truth.")
    print("="*60 + "\n")

if __name__ == "__main__":
    generate_comparison()
