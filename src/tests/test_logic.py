from unittest.mock import patch, MagicMock
from src.engine.logic import perform_forensic_audit
from src.engine.models import Chart, Planet, PlanetName, Sect

def test_perform_forensic_audit():
    # Mocking a Chart
    dummy_planet = Planet(name=PlanetName.SUN, longitude=0.0, latitude=0.0, speed=1.0)
    chart = Chart(
        sun_altitude=10.0,
        planets=[dummy_planet],
        ascendant=0.0, 
        mc=270.0
    )
    
    with patch("src.engine.logic.Auditor.perform_audit") as mock_audit, \
         patch("src.engine.logic.ReportSynthesizer.synthesize") as mock_synth:
        
        mock_audit.return_value = {
            "analysis": {
                "fate": {"hermetic_lots": {}},
                "supplemental": {},
                "advanced_mechanics": {},
                "temperament": {},
                "teams": {},
                "enhanced_profections": {},
                "solar_return": {},
                "aspects": [],
                "horary_physics": {}
            },
            "planets_forensic": [
                {"name": "Sun", "maltreatments": []}
            ],
            "rule_ledger": []
        }
        
        mock_synth.return_value = "Synthesized Report"
        
        report = perform_forensic_audit(chart)
        
        assert "dossier_text" in report
        assert report["dossier_text"] == "Synthesized Report"
        assert report["summary"]["sect"] == Sect.DAY.value
        assert mock_audit.called
        assert mock_synth.called
