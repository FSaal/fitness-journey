import re
import warnings
from datetime import datetime
from pathlib import Path
from typing import Tuple

import pandas as pd
import vizro.models as vm
from vizro import Vizro

from pages.exercise_distribution import get_exercise_distribution_page
from pages.exercise_statistics import get_exercise_statistic_page
from pages.general_statistics import get_general_statistics_page
from pages.playground import get_playground_page
from pages.powerlifting_statistics import get_powerlifting_statistic_page
from preprocessing import BodyWeightDataProcessor, DataPaths, WorkoutDataPreprocessor

# Only for now, to silence plotly pandas groupby warning
warnings.filterwarnings("ignore", category=FutureWarning, module="plotly")

Vizro(assets_folder="src/assets")


def find_newest_file(directory: Path, pattern: str, date_format: str) -> Path:
    """Find the newest file in a directory based on a date pattern in the filename."""
    newest_file = None
    newest_date = datetime.min

    for file in directory.glob("*.csv"):
        match = re.match(pattern, file.name)
        if match:
            date_str = match.group(1)
            file_date = datetime.strptime(date_str, date_format)
            if file_date > newest_date:
                newest_date = file_date
                newest_file = file

    return newest_file


def find_newest_weight_file(directory: Path) -> Path:
    """Find the newest weight file export in the directory matching the pattern 'weight_Felix_XXXXXXXXXX.csv'."""
    pattern = r"weight_Felix_(\d+)\.csv"

    newest_file = None
    highest_number = 0

    for file in directory.glob("weight_Felix_*.csv"):
        match = re.match(pattern, file.name)
        if match:
            number = int(match.group(1))
            if number > highest_number:
                highest_number = number
                newest_file = file

    return newest_file


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load and preprocess fitness and body weight data.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing:
            - DataFrame with processed fitness data
            - DataFrame with processed body weight data
    """
    data_paths = DataPaths(
        # Training data of Android fitness app: Progression - Currently used for logging
        gym_progression=find_newest_file(
            Path("data"), r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.csv", "%Y-%m-%d %H:%M:%S"
        ),
        # Training data of iOS fitness app: Gymbook
        gym_gymbook=find_newest_file(Path("data"), r"GymBook-Logs-(\d{4}-\d{2}-\d{2})\.csv", "%Y-%m-%d"),
        # Old Body weight measurements from myFitnessPal app
        weight_myfitnesspal=Path("data/weight.csv"),
        # Body weight measurements from Eufy scale - Currently used for logging
        weight_eufy=find_newest_weight_file(Path("data")),
    )
    # Validate that all data files exist
    data_paths.validate()

    df_fitness = WorkoutDataPreprocessor(data_paths).get_fitness_dataframe()
    df_weight = BodyWeightDataProcessor(data_paths).get_body_weight_dataframe()

    return df_fitness, df_weight


def create_dashboard(df_fitness: pd.DataFrame, df_bodyweight: pd.DataFrame) -> vm.Dashboard:
    """Create the dashboard with all pages and navigation.

    Args:
        df_fitness: DataFrame containing processed fitness data
        df_bodyweight: DataFrame containing processed body weight data

    Returns:
        vm.Dashboard: Configured dashboard object
    """
    pages = {
        "exercise_statistics": get_exercise_statistic_page(df_fitness),
        "powerlifting_statistics": get_powerlifting_statistic_page(df_fitness, df_bodyweight),
        "exercise_distribution": get_exercise_distribution_page(df_fitness),
        "general_statistics": get_general_statistics_page(df_fitness),
        "playground": get_playground_page(df_fitness),
    }

    navigation_structure = {
        "Exercise specific statistics": ["Exercise Statistics", "Powerlifting Statistics"],
        "General statistics": ["Exercise Distribution", "General Statistics", "Playground"],
    }

    return vm.Dashboard(pages=list(pages.values()), navigation=vm.Navigation(pages=navigation_structure))


def main() -> None:
    """Main entry point for the dashboard application."""
    try:
        # Load and process data
        df_fitness, df_bodyweight = load_data()

        # Create and run dashboard
        dashboard = create_dashboard(df_fitness, df_bodyweight)
        Vizro().build(dashboard).run(debug=True)

    except Exception as e:
        print(f"Error starting dashboard: {str(e)}")
        raise


if __name__ == "__main__":
    main()
