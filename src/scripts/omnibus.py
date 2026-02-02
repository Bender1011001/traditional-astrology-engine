#!/usr/bin/env python3
import click
import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.database.db_manager import init_db, SessionLocal
from src.engine.forensic_engine import Auditor
from src.database.models import User
from dotenv import load_dotenv

load_dotenv()

@click.group()
def cli():
    """Omnibus: The Codex Caelestis Administrative CLI."""
    pass

@cli.command()
@click.option('--date', '-d', prompt='Bitrh Date (YYYY-MM-DD)', help='Birth Date')
@click.option('--time', '-t', prompt='Birth Time (HH:MM)', help='Birth Time')
@click.option('--city', '-c', prompt='City', help='City of Birth')
@click.option('--state', '-s', default="", help='State (Optional)')
@click.option('--name', '-n', default="Test Subject", help='Subject Name')
def audit(date, time, city, state, name):
    """Run a forensic audit for a test subject."""
    click.secho(f"Running Forensic Audit for {name} ({date} {time}, {city})...", fg='cyan')
    
    try:
        # Construct synchronous wrapper for async logic if needed, but Auditor is synchronous (mostly)
        # Auditor.generate_full_nativity uses run_in_threadpool in bridge but logic is static/synch.
        # However, chart_calculator might need async if it calls external APIs?
        # Let's check Auditor.generate_full_nativity code.
        # It calls calculate_chart_data which calls ChartCalculator.
        # ChartCalculator might be sync.
        
        # We can call Auditor.generate_full_nativity directly.
        result = Auditor.generate_full_nativity(
            date_str=date,
            time_str=time,
            city=city,
            state=state,
            name=name
        )
        
        if "error" in result:
             click.secho(f"Error: {result['error']}", fg='red')
             return

        # Output Summary
        tech_data = result.get("technical_data", {})
        analysis = tech_data.get("analysis", {})
        summary = {
            "Almuten": analysis.get("advanced_mechanics", {}).get("almuten", {}).get("winner"),
            "Hemisphere": analysis.get("supplemental", {}).get("hemispheres", {}).get("focus", {}).get("orientation"),
            "Vitality": "Calculated"
        }
        
        click.secho("\n--- Audit Results ---", fg='green')
        click.echo(f"Subject: {name}")
        click.echo(f"Almuten Figuris: {summary['Almuten']}")
        click.echo(f"Hemisphere Bias: {summary['Hemisphere']}")
        
        # Rule Ledger Summary
        ledger = tech_data.get("rule_ledger", [])
        click.secho(f"\nRule Ledger Entries: {len(ledger)}", fg='yellow')
        
        # Show top 3 rules
        for i, rule in enumerate(ledger[:3]):
            click.echo(f"[{rule['id']}] {rule['condition']} -> {rule['judgment'][:50]}...")
            
    except Exception as e:
        click.secho(f"Audit Failed: {e}", fg='red')
        import traceback
        traceback.print_exc()

@cli.command()
@click.confirmation_option(prompt='Are you sure you want to WIPE and reseed the database?')
def rehydrate():
    """Wipe database and re-seed with initial data."""
    click.secho("Rehydrating Database...", fg='magenta')
    
    try:
        from src.scripts.seed_db import reset_db, seed_plans
        
        reset_db()
        click.secho("Schema Intialized.", fg='green')
        
        seed_plans()
        click.secho("Seed Data Populated.", fg='green')
        
        click.secho("Database Ready.", fg='green')
        
    except Exception as e:
         click.secho(f"Rehydration Failed: {e}", fg='red')
         import traceback
         traceback.print_exc()

if __name__ == '__main__':
    cli()
