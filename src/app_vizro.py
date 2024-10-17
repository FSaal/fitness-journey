import warnings
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


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load and preprocess fitness and body weight data.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing:
            - DataFrame with processed fitness data
            - DataFrame with processed body weight data
    """
    data_paths = DataPaths(
        # Training data of Android fitness app: Progression - Currently used for logging
        gym_progression=Path("data/2024-09-25 08:19:34.csv"),
        # Training data of iOS fitness app: Gymbook
        gym_gymbook=Path("data/GymBook-Logs-2023-04-08.csv"),
        # Body weight measurements from myFitnessPal app
        weight_myfitnesspal=Path("data/weight.csv"),
        # Body weight measurements from Eufy scale - Currently used for logging
        weight_eufy=Path("data/weight_Felix_1727247358.csv"),
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
        "playground": get_playground_page(df_fitness),
        "general_statistics": get_general_statistics_page(df_fitness),
    }

    navigation_structure = {
        "Exercise specific statistics": ["Exercise Statistics", "Powerlifting Statistics"],
        "General statistics": ["Exercise Distribution", "Playground", "General Statistics"],
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
