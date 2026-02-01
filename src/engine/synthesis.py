from typing import Dict, List, Any
from .models import PlanetName, Sect

class ReportSynthesizer:
    """
    Synthesizes raw astrological data into a cohesive, narrative-driven "God Mode" dossier.
    Handles conflict resolution and prioritizes findings based on traditional hierarchy.
    """

    @staticmethod
    def synthesize(raw_report: Dict[str, Any]) -> str:
        sections = []
        
        # 1. Executive Summary
        sections.append(ReportSynthesizer._generate_executive_summary(raw_report))
        
        # 2. The Constitution
        sections.append(ReportSynthesizer._generate_constitution(raw_report))
        
        # 3. The Fate Timeline
        sections.append(ReportSynthesizer._generate_fate_timeline(raw_report))
        
        # 4. Forensic Audit
        sections.append(ReportSynthesizer._generate_forensic_audit(raw_report))
        
        # 5. Universal Overrides
        sections.append(ReportSynthesizer._generate_universal_overrides(raw_report))
        
        return "\n\n".join(sections)

    @staticmethod
    def _generate_executive_summary(report: Dict) -> str:
        soul_guardian = report.get("soul_guardian", {})
        vitality = report.get("vitality", {})
        
        summary = "# EXECUTIVE SUMMARY: THE SOVEREIGN AUDIT\n"
        summary += f"**Soul Guardian (Almuten Figuris):** {soul_guardian.get('almuten', 'Unknown')}\n"
        summary += f"**Vitality Rating:** {vitality.get('vitality_rating', 'Indeterminate')}\n"
        summary += f"**Core Function:** {soul_guardian.get('job_description', 'N/A')}\n"
        
        return summary

    @staticmethod
    def _generate_constitution(report: Dict) -> str:
        summary = report.get("summary", {})
        medical = report.get("medical_analysis", {})
        
        text = "## I. THE CONSTITUTION: HUMORAL & PHYSICAL BASELINE\n"
        text += f"**Temperament:** {summary.get('temperament', {}).get('primary_temperament', 'Unknown')}\n"
        text += f"**Dominant Elements:** {', '.join([f'{k} ({v})' for k, v in summary.get('dominant_elements', [])])}\n"
        text += f"**Medical Governance:** {medical.get('governed_body_part', 'Unknown')} (Sign: {medical.get('constitutional_sign', 'N/A')})\n"
        
        if medical.get("pathology_alerts"):
            text += "**Pathology Alerts:** " + "; ".join(medical["pathology_alerts"]) + "\n"
            
        return text

    @staticmethod
    def _generate_fate_timeline(report: Dict) -> str:
        text = "## II. THE FATE TIMELINE: CHRONOCRATORS & DIRECTIONS\n"
        
        # Distributor
        dist = report.get("primary_direction_distributor", {})
        if dist:
            text += f"**Current Distributor (Master Time Lord):** {dist.get('planet')} (Partner: {dist.get('partner')})\n"
            text += f"**Status:** {dist.get('description')}\n"
            
        # Profections
        prof = report.get("profections", {})
        if prof:
            text += f"**Lord of the Year:** {prof.get('lord_of_year')} (Annual Sign: {prof.get('annual_sign')})\n"
            
        return text

    @staticmethod
    def _generate_forensic_audit(report: Dict) -> str:
        text = "## III. FORENSIC AUDIT: LIFE DOMAINS\n"
        
        lots = report.get("forensic_lots", {})
        for lot_name, data in lots.items():
            status = data.get("status", "Clear")
            text += f"**{lot_name}:** {status}. {data.get('verification', '')}\n"
            
        return text

    @staticmethod
    def _generate_universal_overrides(report: Dict) -> str:
        text = "## IV. UNIVERSAL OVERRIDES: ACTS OF GOD\n"
        
        events = report.get("summary", {}).get("universal_events", [])
        if not events:
            text += "No major universal overrides active in this period.\n"
        else:
            for ev in events:
                text += f"- **{ev.get('type')}:** {ev.get('longitude')}°. Impacting {ev.get('sign', 'N/A')}.\n"
                
        audit = report.get("summary", {}).get("universal_causation_audit", [])
        for a in audit:
            text += f"- **{a.get('cause')}:** {a.get('rule')}\n"
            
        return text
