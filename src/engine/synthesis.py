from typing import Dict, List, Any
from .models import PlanetName, Sect

class ReportSynthesizer:
    """
    Synthesizes raw astrological data into a cohesive, narrative-driven "Comprehensive Forensic Audit".
    Handles conflict resolution and prioritizes findings based on traditional hierarchy.
    """

    @staticmethod
    def synthesize(raw_report: Dict[str, Any]) -> str:
        sections = []
        
        # 1. Executive Summary
        sections.append(ReportSynthesizer._generate_executive_summary(raw_report))
        
        # 2. The Constitution
        sections.append(ReportSynthesizer._generate_constitution(raw_report))

        # 3. Dignity & Almuten Breakdown
        sections.append(ReportSynthesizer._generate_dignity_breakdown(raw_report))
        
        # 4. Planetary Protocols (The Meat)
        sections.append(ReportSynthesizer._generate_planetary_protocols(raw_report))
        
        # 5. House Systems
        sections.append(ReportSynthesizer._generate_house_systems(raw_report))

        # 6. Aspect Analysis
        sections.append(ReportSynthesizer._generate_aspect_analysis(raw_report))
        
        # 7. The Fate Timeline
        sections.append(ReportSynthesizer._generate_fate_timeline(raw_report))
        
        # 8. Forensic Audit
        sections.append(ReportSynthesizer._generate_forensic_audit(raw_report))
        
        # 9. Universal Overrides
        sections.append(ReportSynthesizer._generate_universal_overrides(raw_report))
        
        return "\n\n".join(sections)

    @staticmethod
    def _generate_executive_summary(report: Dict) -> str:
        soul_guardian = report.get("soul_guardian", {})
        vitality = report.get("vitality", {})
        
        summary = "# EXECUTIVE SUMMARY: COMPREHENSIVE FORENSIC AUDIT\n"
        summary += f"**Soul Guardian (Almuten Figuris):** {soul_guardian.get('almuten', 'Unknown')}\n"
        summary += f"**Vitality Rating:** {vitality.get('vitality_rating', 'Indeterminate')}\n"
        summary += f"**Core Function:** {soul_guardian.get('job_description', 'N/A')}\n"
        
        return summary

    @staticmethod
    def _generate_constitution(report: Dict) -> str:
        summary = report.get("summary", {})
        medical = report.get("medical_analysis", {})
        
        # Temperament Fix
        temp_data = summary.get('temperament', {})
        if isinstance(temp_data, dict):
            primary_temp = temp_data.get('primary_temperament', temp_data.get('excess_humor', 'Unknown'))
        else:
            primary_temp = str(temp_data)

        text = "## I. THE CONSTITUTION: HUMORAL & PHYSICAL BASELINE\n"
        text += f"**Temperament:** {primary_temp}\n"
        text += f"**Dominant Elements:** {', '.join([f'{k} ({v})' for k, v in summary.get('dominant_elements', [])])}\n"
        text += f"**Medical Governance:** {medical.get('governed_body_part', 'Unknown')} (Sign: {medical.get('constitutional_sign', 'N/A')})\n"
        
        if medical.get("pathology_alerts"):
            alerts = []
            for alert in medical["pathology_alerts"]:
                if isinstance(alert, dict):
                    alerts.append(f"{alert.get('type', 'Alert')}: {alert.get('condition', 'Unknown')}")
                else:
                    alerts.append(str(alert))
            text += "**Pathology Alerts:** " + "; ".join(alerts) + "\n"
            
        return text

    @staticmethod
    def _generate_house_systems(report: Dict) -> str:
        text = "## IV. HOUSE CUSPS (WHOLE SIGN / PLACIDUS)\n"
        houses = report.get("houses", {})
        
        # Sort keys to ensure 1-12 order even if Dict is unordered
        sorted_keys = sorted(houses.keys(), key=lambda x: int(x))
        
        cols = []
        for k in sorted_keys:
            val = houses[k]
            cols.append(f"| {k} | {round(val, 2)}° |")
            
        text += "| House | Cusp |\n|---|---|\n" + "\n".join(cols) + "\n"
        return text

    @staticmethod
    def _generate_aspect_analysis(report: Dict) -> str:
        text = "## V. ASPECT ANALYSIS: THE GEOMETRY OF FATE\n"
        text += "---\n"
        aspects = report.get("aspects", [])
        
        if not aspects:
            text += "_No major classical aspects detected within standard orbs._\n"
            return text
            
        # Group aspects by planet to make it more narrative
        for asp in aspects:
            p1 = asp.get("planet_a", "Unknown")
            p2 = asp.get("planet_b", "Unknown")
            type_ = asp.get("type", "Unknown")
            orb = round(asp.get("orb", 0.0), 2)
            apply_str = "Applying" if asp.get("is_applying") else "Separating"
            
            # Interpret the dynamic
            narrative = ""
            if type_ in ["Conjunction", "Trine", "Sextile"]:
                narrative = f"The relationship between {p1} and {p2} is **Harmonious**. Their energies support each other, creating a natural bypass for difficulties."
            else:
                narrative = f"The relationship between {p1} and {p2} is **Frictional**. This creates tension that demands action, growth, and the resolution of internal conflicts."

            if asp.get("is_applying"):
                narrative += " This dynamic is **increasing in intensity** as the life progresses."
            else:
                narrative += " This dynamic represents a **resolved pattern** from earlier in life or ancestral inheritance."

            interp = asp.get("text", "")
            
            text += f"#### {p1} {type_} {p2} ({orb}°, {apply_str})\n"
            text += f"{narrative}\n"
            if interp:
                text += f"\n> **Dossier Entry:** {interp}\n"
            text += "\n"
                
        return text

    @staticmethod
    def _generate_dignity_breakdown(report: Dict) -> str:
        text = "## II. SOVEREIGN POWER STRUCTURE\n"
        teams = report.get("summary", {})
        
        text += f"**Constructive Team:** {', '.join(teams.get('constructive_team', []))}\n"
        text += f"**Destructive Team:** {', '.join(teams.get('destructive_team', []))}\n"
        
        receptions = teams.get("mutual_receptions", [])
        if receptions:
            text += "**Mutual Receptions:**\n"
            for r in receptions:
                text += f"- {r.get('planet_a')} <-> {r.get('planet_b')} ({r.get('type')})\n"
                
        return text

    @staticmethod
    def _generate_planetary_protocols(report: Dict) -> str:
        text = "## III. PLANETARY PROTOCOLS: THE INSTRUMENTS OF FATE\n"
        text += "---\n\n"
        planets = report.get("planets", [])
        
        node_delineations = {
            "North_Node": {
                "Aries": "AMPLIFICATION of the ego and impulsive drive. The 'Head' ingests identity with aggressive hunger. Danger of self-obsession.",
                "Taurus": "GREED for material stability and sensory permanence. A voracious appetite for accumulation that is never satisfied.",
                "Gemini": "VORACIOUS intellectual curiosity. Ingestion of data without digestion. The mind becomes 'loud' and scattered.",
                "Cancer": "HYPER-MANIFESTATION of domestic needs. An insatiable hunger for emotional security that can become smothering.",
                "Leo": "AMPLIFICATION of the creative heart and pride. Seeking the spotlight with a 'Demon Head' hunger for validation.",
                "Virgo": "OBSESSIVE refinement and ingestion of detail. A 'loud' criticism that consumes the peace of the native.",
                "Libra": "INSATIABLE hunger for the Other. Ingesting relationships to find balance, often creating codependent amplification.",
                "Scorpio": "AMPLIFICATION of deep desire and shadow. A 'loud' and voracious drive for power or intensity that borders on obsession.",
                "Sagittarius": "GREED for meaning and expansion. A hunger for the 'Big Truth' that overlooks the immediate reality. The archer's aim is loud.",
                "Capricorn": "AMPLIFICATION of ambition and structural legacy. Ingesting status and public power with a head that has no stomach.",
                "Aquarius": "VORACIOUS innovation and tribal belonging. Hungering for the future while being possessed by the collective vision.",
                "Pisces": "HYPER-DISSOLUTION. Ingesting the mystical leading to a 'loud' escapism or a voracious spiritual appetite."
            },
            "South_Node": {
                "Aries": "DIMINISHMENT of conflict. The 'Tail' releases the waste of past aggression. Learning to let go of the fight.",
                "Taurus": "RELEASE of material attachment. Purging the residue of stubborn accumulation. Spiritual detachment from the physical.",
                "Gemini": "DETACHMENT from superficiality. Releasing the scattered thoughts of previous cycles. Intellectual purging.",
                "Cancer": "PURGING emotional clinginess. Releasing the 'waste' of domestic safety to find maturity elsewhere.",
                "Leo": "DIMINISHMENT of the ego's pride. Letting go of the need for the central stage. Releasing the mask.",
                "Virgo": "RELEASE of hyper-criticism. Purging the obsession with purity that has become a burden. Detachment from the detail.",
                "Libra": "DETACHMENT from codependency. Releasing the 'waste' of indecision. Letting go of the mirror of the Other.",
                "Scorpio": "PURGING the misuse of power. Releasing the residue of past trauma or shadow. Radical spiritual detachment.",
                "Sagittarius": "DIMINISHMENT of dogmatism. Letting go of aimless wandering or 'borrowed' truths. Purging the wanderlust.",
                "Capricorn": "RELEASE of status-obsession. Releasing the cold pursuit of ambition. Detachment from the public mask.",
                "Aquarius": "PURGING detachment. Releasing the residue of rebellion without a heart. Finding the simple human pulse.",
                "Pisces": "DIMINISHMENT of escapism. Releasing the 'waste' of boundaryless surrender. Finding the structure within the void."
            }
        }

        for p in planets:
            name = p.get("name", "Unknown")
            sign = p.get("sign", "Unknown")
            lon = p.get("longitude", 0.0)
            
            dignity = p.get("dignities", {})
            total_score = dignity.get("total_score", 0)
            
            solar = p.get("solar_status", "FREE")
            solar_cond = "✅ Clear"
            if solar == "COMBUST": solar_cond = "🔥 COMBUST"
            elif solar == "UNDER_BEAMS": solar_cond = "🌥️ Under the Beams"
            elif solar == "CAZIMI": solar_cond = "👑 CAZIMI (Heart of the Sun)"
            
            maltreatments = p.get("maltreatments", [])
            
            text += f"### {name} in {sign} ({round(lon % 30, 2)}°)\n"
            
            if name not in ["North_Node", "South_Node"]:
                text += f"- **Essential Dignity:** `{total_score}` (Domicile: {dignity.get('domicile_ruler')}, Exaltation: {dignity.get('exaltation_ruler')})\n"
                text += f"- **Solar Condition:** {solar_cond}\n"
            
            if maltreatments:
                text += f"- **MALTREATMENT (KAKOSIS):**\n"
                for m in maltreatments:
                    text += f"  - ⚠️ {m.get('description')}\n"
            elif name not in ["North_Node", "South_Node"]:
                 text += "- **Status:** ✨ No Maltreatment detected.\n"
                 
            impacts = p.get("impacts", [])
            for imp in impacts:
                text += f"- **CONDITION:** {imp.get('cause')} -> {imp.get('effect')}\n"
                
            # Delineation logic
            delin = p.get("delineation", "")
            if (not delin or "not found" in delin.lower()) and name in node_delineations:
                # Normalize sign check to title case
                sign_key = sign.title() if hasattr(sign, 'title') else str(sign)
                delin = node_delineations[name].get(sign_key, "Delineation in progress.")
            
            if delin:
                text += f"\n> {delin}\n"
                
            text += "\n---\n"
            
        return text

    @staticmethod
    def _generate_fate_timeline(report: Dict) -> str:
        text = "## IV. THE FATE TIMELINE: CHRONOCRATORS & DIRECTIONS\n"
        
        # Distributor
        dist = report.get("primary_direction_distributor", {})
        if dist:
            text += f"**Current Distributor (Master Time Lord):** {dist.get('planet')} (Partner: {dist.get('partner')})\n"
            text += f"**Status:** {dist.get('description')}\n"
            
        # Profections
        prof = report.get("profections", {})
        if prof:
            text += f"**Lord of the Year:** {prof.get('lord_of_year')} (Annual Sign: {prof.get('annual_sign')})\n"

        # Firdaria
        firdaria = report.get("firdaria", {})
        if firdaria and "Major Period" in firdaria:
            current = firdaria
            text += f"**Firdaria:** {current.get('Major Period')} / {current.get('Sub Period')} (Phase: {current.get('Sub Start')} to {current.get('Sub End')})\n"

        # Solar Return
        sr = report.get("solar_return", {})
        if sr and "return_date" in sr:
            text += f"**Solar Return Date:** {sr.get('return_date')}\n"
            
        return text

    @staticmethod
    def _generate_forensic_audit(report: Dict) -> str:
        text = "## V. FORENSIC AUDIT: LIFE DOMAINS\n"
        
        lots = report.get("forensic_lots", {})
        for lot_name, data in lots.items():
            status = data.get("status", "Clear")
            sign = data.get("sign", "")
            ruler = data.get("ruler", "")
            
            line = f"**{lot_name}:** {status}."
            if "Maltreated" in status:
                details = data.get("maltreatment_details", [])
                if details:
                    line += " " + " ".join(details)
            else:
                 line += f" (in {sign}, ruled by {ruler})"
                 
            text += line + "\n"
            
        return text

    @staticmethod
    def _generate_universal_overrides(report: Dict) -> str:
        text = "## VI. UNIVERSAL OVERRIDES: ACTS OF GOD\n"
        
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
