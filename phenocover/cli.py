#!/usr/bin/env python3
"""
Command Line Interface for Raster2Sensor

This module provides the command-line interface for the Raster2Sensor application,
which enables processing of raster imagery data and integration with OGC SensorThings API.

The CLI supports various operations including:
- Managing trial plots in SensorThings API
- Processing raster images with vegetation indices
- Executing OGC API Processes
- Configuration management

Author: Joseph Gitahi
Created: 2025
License: MIT License
Repository: https://github.com/joemureithi/raster2sensor

Key Dependencies:
    - typer: Modern CLI framework
    - rich: Rich text and beautiful formatting

Usage:
    python -m raster2sensor --help
    python -m raster2sensor plots create --config config.yml --file-path plots.geojson
    python -m raster2sensor process-images --config config.yml --dry-run
"""

import typer

from typing import Optional
from rich.console import Console
from raster2sensor import __app_name__, __version__
from raster2sensor.logging import configure_logging, get_logger
from raster2sensor.utils import clear

# Logger
logger = get_logger(__name__)
configure_logging(
    level="DEBUG",
    log_dir="./logs",
    enable_file_logging=True,
    enable_console_logging=True,
    use_rich=True,  # Use rich formatting if available
    suppress_third_party_debug=True  # Suppress third-party debug logs
)
# Main app
app = typer.Typer()
console = Console()

# Sub-command groups
plots_app = typer.Typer()
processes_app = typer.Typer()

# Add sub-command groups to main app
app.add_typer(plots_app, name="plots",
              help="Trial plots management in OGC SensorThings API commands")
app.add_typer(processes_app, name="processes",
              help="OGC API - Processes commands")


# Main callback


def _version_callback(value: bool) -> None:
    clear()
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    """
    Raster2Sensor - A tool for raster data processing and OGC SensorThings API integration.
    """
    return


# =============================================================================
# PLOTS COMMANDS
# =============================================================================

@plots_app.command("fetch")
def fetch_plots(
    trial_id: str = typer.Option(
        None, help="Trial identifier to fetch plots for"),
    sensorthingsapi_url: str = typer.Option(None, help="SensorThingsAPI URL"),
    config_file: str = typer.Option(
        None, "--config", help="Path to configuration file (YAML or JSON) containing sensorthingsapi_url and trial_id")
):
    """
    Fetch plots GeoJSON for a given trial ID.

    You can provide either:
    - Individual parameters: --trial-id and --sensorthingsapi-url
    - Configuration file: --config (containing sensorthingsapi_url and trial_id)

    Args:
        trial_id: The trial identifier to fetch plots for
        sensorthingsapi_url: SensorThings API URL
        config_file: Path to configuration file
    """
    clear()

    # Validate input parameters
    if config_file and (trial_id or sensorthingsapi_url):
        logger.error(
            "Cannot specify both --config and individual parameters (--trial-id, --sensorthingsapi-url). Choose one approach.")
        raise typer.Exit(1)

    if not config_file and not (trial_id and sensorthingsapi_url):
        logger.error(
            "Must specify either --config file OR both --trial-id and --sensorthingsapi-url")
        raise typer.Exit(1)

    try:
        if config_file:
            # Load configuration from file
            logger.info(f"Loading configuration from: {config_file}")
            config = ConfigParser.load_config(config_file)
            effective_trial_id = config.trial_id
            effective_sensorthingsapi_url = config.sensorthingsapi_url
            logger.info(f"Using trial_id from config: {effective_trial_id}")
            logger.info(
                f"Using sensorthingsapi_url from config: {effective_sensorthingsapi_url}")
        else:
            # Use provided arguments
            effective_trial_id = trial_id
            effective_sensorthingsapi_url = sensorthingsapi_url
            logger.info(f"Using provided trial_id: {effective_trial_id}")
            logger.info(
                f"Using provided sensorthingsapi_url: {effective_sensorthingsapi_url}")

        logger.info(f"Fetching plots for trial ID: {effective_trial_id}")
        plots_geojson = Plots.fetch_plots_geojson(
            effective_sensorthingsapi_url, effective_trial_id)

        # Log success and provide summary
        num_plots = len(plots_geojson.get('features', []))
        logger.info(
            f"✓ Successfully fetched {num_plots} plots for trial: {effective_trial_id}")

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Error fetching plots: {e}")
        raise typer.Exit(1)
