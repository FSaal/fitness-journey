import plotly.io as pio
import vizro.models as vm
from vizro import Vizro

from pages.exercise_distribution import get_exercise_distribution_page
from pages.exercise_statistics import get_exercise_statistic_page
from pages.general_statistics import get_general_statistics_page
from pages.playground import get_playground_page
from pages.powerlifting_statistics import get_powerlifting_statistic_page
from preprocessing import PreprocessClass

pio.templates.default = "plotly_dark"


def load_data():
    """Load data and preprocess it"""
    # Training data of iOS fitness app: Gymbook
    ios_fitness_data_path = "data/GymBook-Logs-2023-04-08.csv"
    # Training data of Android fitness app: Progression - Currently active
    android_fitness_data_path = "data/2024-09-25 08:19:34.csv"
    # Body weight measurements from myFitnessPal app
    body_weight_myfitnesspal_path = "data/weight.csv"
    # Body weight measurements from Eufy scale - Currenly active
    body_weight_eufy_path = "data/weight_Felix_1727247358.csv"
    preprocess = PreprocessClass(
        ios_fitness_data_path,
        android_fitness_data_path,
        body_weight_myfitnesspal_path,
        body_weight_eufy_path,
    )
    return preprocess.main()


df_fitness, df_bodyweight = load_data()

exercise_statistic_page = get_exercise_statistic_page(df_fitness)
powerlift_statistic_page = get_powerlifting_statistic_page(df_fitness, df_bodyweight)
exercise_distribution_page = get_exercise_distribution_page(df_fitness)
playground_page = get_playground_page(df_fitness)
general_statistics_page = get_general_statistics_page(df_fitness)

dashboard = vm.Dashboard(
    pages=[
        exercise_statistic_page,
        powerlift_statistic_page,
        exercise_distribution_page,
        playground_page,
        general_statistics_page,
    ],
    navigation=vm.Navigation(
        pages={
            "Exercise specific statistics": ["Exercise Statistics", "PowerLifting Statistics"],
            "General statistics": ["Exercise Distribution", "Playground", "General Statistics"],
        },
    ),
)
Vizro().build(dashboard).run(debug=True)
