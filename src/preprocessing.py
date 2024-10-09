import csv
import re
from pathlib import Path
from typing import Dict, Iterator, List, NamedTuple, Optional, Set, Tuple

import pandas as pd

from exercise_compendium import (
    Equipment,
    ExerciseLibrary,
    ExerciseSearchCriteria,
    Force,
    Mechanic,
    MuscleCategory,
    create_exercise_library,
)


class DataPaths(NamedTuple):
    gym_progression: Path
    gym_gymbook: Path
    weight_myfitnesspal: Path
    weight_eufy: Path

    def validate(self):
        """Validate that all data files exist."""
        for field_name in self._fields:
            path = getattr(self, field_name)
            if not path.exists():
                raise FileNotFoundError(f"Required data file not found: {field_name} at {path}")


class DataLoader:
    """Load and preprocess CSV data from fitness tracking apps, fixing formatting issues and inconsistencies."""

    def load_data(self, progression_path: Path, gymbook_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load and preprocess data from Progression and GymBook CSV files."""
        fixed_progression_csv = self.fix_progression_csv(progression_path)
        df_progression = pd.read_csv(fixed_progression_csv, delimiter=",", decimal=".")
        df_gymbook = pd.read_csv(gymbook_path, delimiter=";", decimal=",")
        return df_progression, df_gymbook

    def fix_progression_csv(self, input_path: Path) -> Path:
        """Fix formatting issues in Progression app CSV export."""
        output_path = input_path.parent / f"{input_path.stem}_fixed.csv"

        with open(input_path, "r", encoding="utf-8") as infile:
            reader = csv.reader(infile)
            fixed_data = self._fix_progression_format(reader)

        with open(output_path, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerows(fixed_data)

        return output_path

    def _fix_progression_format(self, reader: csv.reader) -> List[List[str]]:
        """Fix line breaks and commas in Progression app data."""
        fixed_rows = self._fix_linebreaks(reader)
        return self._fix_commas_in_comments(fixed_rows)

    @staticmethod
    def _fix_linebreaks(reader: csv.reader) -> Iterator[List[str]]:
        """Revert line breaks and move them into one row.

        When writing a comment with a line break in the progression app, the part after the line break
        is written to a new line in the .csv file. This function detects all line breaks and replaces
        the line break with '.  '"""
        fixed_lines = [next(reader)]
        for line in reader:
            # Line break with empty line
            if not line:
                next_line = next(reader)
                last_line = fixed_lines[-1]
                fixed_lines[-1] = last_line[:-1] + [". ".join([last_line[-1], next_line[0]])] + next_line[1:]
            # Line break
            elif not re.match(r"\d{4}-\d{2}-\d{2}", line[0]):
                last_line = fixed_lines[-1]
                fixed_lines[-1] = last_line[:-1] + [". ".join([last_line[-1], line[0]])] + line[1:]
            else:
                fixed_lines.append(line)

        return iter(fixed_lines)

    def _fix_commas_in_comments(self, rows: Iterator[List[str]]) -> List[List[str]]:
        """Replace ',' in comment columns with ';' or '.' to fix faulty CSV parsing.
        When a comment in the progression app contains a ',', the CSV file incorrectly treats it as a new entry.
        This method fixes the parsing by replacing commas with semicolons for text and periods for numbers."""
        header_line = next(rows)
        expected_column_count = len(header_line)
        fixed_lines = [header_line]
        # Next to the set comment column there is the session comment column. This are all the comment columns.
        SET_COMMENT_COLUMN_INDEX = 14

        for line in rows:
            # Find lines where a comma was written in either set or session comment
            if len(line) > expected_column_count:
                fixed_line = (
                    line[:SET_COMMENT_COLUMN_INDEX]
                    + [self._fix_comment_part(line[SET_COMMENT_COLUMN_INDEX:-2])]
                    + line[-2:]
                )
            else:
                fixed_line = line
            fixed_lines.append(fixed_line)

        return fixed_lines

    @staticmethod
    def _fix_comment_part(comment_parts: List[str]) -> str:
        """Fix commas within a single comment part."""
        fixed_comment = comment_parts[0]
        for part in comment_parts[1:]:
            # If comment contains a number with comma, e.g. 2,5 kg --> replace comma with decimal point
            if re.match(r"^\s*\d", part) and fixed_comment[-1].isdigit():
                fixed_comment += "." + part.lstrip()
            # If comma is used as punctuation mark --> replace comma with semicolon
            elif part.startswith(" "):
                fixed_comment += ";" + part
            # Add missing space between comma and previous word
            else:
                fixed_comment += "; " + part
        return fixed_comment


class DataCleaner:
    """Provides methods to clean, standardize, and prepare workout data from various sources for analysis."""

    def pre_clean_data(
        self, df_progression: pd.DataFrame, df_gymbook: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Apply all data cleaning steps to the DataFrames.

        This method performs the following operations:
        1. For GymBook data:
           - Removes unused columns related to muscle groups and set types
           - Filters out inactive (skipped) sets
        2. For Progression data:
           - Removes unused columns ('Time' and 'Set Duration (s)')

        Returns a tuple of cleaned (df_progression, df_gymbook) DataFrames.
        """
        df_gymbook = self._filter_active_sets(df_gymbook)
        # Muscle groups information will be used from another source, set type was not consistently logged
        df_gymbook = self._remove_unused_columns(
            df_gymbook,
            [
                "Muskelgruppen (Primäre)",
                "Muskelgruppen (Sekundäre)",
                "Satz / Aufwärmsatz / Abkühlungssatz",
                "Ausgelassen",
            ],
        )
        # Time is workout start time and the same for all sets of the day, Set Duration is only used for cardio exercises
        df_progression = self._remove_unused_columns(df_progression, ["Time", "Set Duration (s)"])

        return df_progression, df_gymbook

    @staticmethod
    def _filter_active_sets(df: pd.DataFrame) -> pd.DataFrame:
        """Remove skipped sets from the dataFrame (they were still logged by the gymbook app)."""
        return df[df["Ausgelassen"] != "Ja"]

    @staticmethod
    def _remove_unused_columns(df: pd.DataFrame, additional_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Remove columns which do not hold any valuable information."""
        constant_columns = [col for col in df.columns if df[col].nunique() <= 1]
        columns_to_remove = constant_columns + (additional_columns or [])

        if "Set Duration (s)" in columns_to_remove:
            # Before removing Set Duration, write the info in the repetitions columns, used for time-based exercises e.g. Plank
            df["Repetitions"] = df["Repetitions"].fillna(df["Set Duration (s)"])

        return df.drop(columns=columns_to_remove, errors="ignore")

    def post_clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform final cleaning steps on the DataFrame.

        This method:
        1. Fixes data types
        2. Renames specific columns
        3. Sorts the DataFrame by time
        4. Removes implausible data
        5. Sets 'Time' as the index

        Returns a cleaned DataFrame ready for analysis.
        """
        df = self._fix_dtypes(df)
        df = self._rename_columns(df)
        df = df.sort_values("Time").reset_index(drop=True)
        df = self._clean_up_data(df)
        df = df.set_index("Time")
        return df

    @staticmethod
    def _fix_dtypes(df: pd.DataFrame) -> pd.DataFrame:
        """Convert 'Weight' to float and 'Repetitions' to int, handling missing values."""
        df["Weight"] = df["Weight"].fillna(0).astype(float)
        df["Repetitions"] = df["Repetitions"].astype(int)
        return df

    @staticmethod
    def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Rename specific columns for clarity and consistency."""
        column_mapping: Dict[str, str] = {"Session Duration (s)": "Session Duration [s]", "Weight": "Weight [kg]"}
        return df.rename(columns=column_mapping)

    @staticmethod
    def _clean_up_data(df: pd.DataFrame) -> pd.DataFrame:
        """Remove and/or edit implausible data"""
        # Limit gym session duration - Workout session of more than 3 hours must be a mistake
        SESSION_TIME_LIMIT_S = 3 * 60 * 60  # 3 hours in seconds

        # Remove outlier sets (forgot to log a set)
        df_too_long = df[df["Session Duration [s]"] > SESSION_TIME_LIMIT_S]
        outlier = df_too_long[df_too_long["Time"].diff() > pd.Timedelta(hours=1)]
        if not outlier.empty:
            df = df.drop(outlier.index[0] - 1)

        # Recalculate session duration for long sessions
        df_too_long = df[df["Session Duration [s]"] > SESSION_TIME_LIMIT_S]
        df.loc[df["Session Duration [s]"] > SESSION_TIME_LIMIT_S, "Session Duration [s]"] = (
            df_too_long.groupby(df.index.date, observed=True)["Time"].transform(lambda x: x.max() - x.min()).dt.seconds
        )

        # Handle missing comments for proper hover text in graphs
        df["Set Comment"] = df["Set Comment"].fillna("None")
        return df


class DataHarmonizer:
    """Harmonize exercise data by standardizing names, categories, and metadata across different data sources."""

    def __init__(self):
        self.name_mappings = {
            "gymbook_to_progression": {
                "Ab Wheel": "Ab Roller",
                "Alternating Dumbbell Preacher Curl": "Alternating Dumbbell Curl",
                "Arnold Press": "Arnold Dumbbell Press (Seated)",
                "Back Extension": "Machine Hyperextension",
                "Bulgarian Split Squat ": "Bulgarian Split Squat",
                "Cable Fly": "Cable Back Fly",
                "Calf Press in Leg Press": "Machine Calf Press",
                "Chin-Up": "Chinup",
                "Concentration Curl": "Dumbbell Concentration Curl",
                "Crunch": "Weighted Crunch",
                "Decline Push-Up": "Decline Pushup",
                "Dumbbell Lateral Raise": "Dumbbell Side Raise",
                "Dumbbell Press": "Dumbbell Shoulder Press",
                "Dumbbell Row": "Bent-Over Dumbbell Row",
                "Dumbbell Skullcrusher": "Lying Dumbbell Skull Crusher",
                "Hammer Curl": "Dumbbell Hammer Curl",
                "Kneeling Cable Crunch": "Cable Crunch",
                "Lat Pull-Down": "Machine Lat Pulldown",
                "Leg Extension": "Machine Leg Extension",
                "Leg Press": "Machine Leg Press",
                "Low Cable One-Arm Lateral Raise": "Cable Side Raise",
                "Lying Dumbbell Triceps Extension": "Dumbbell Triceps Extension",
                "Lying EZ-Bar Triceps Extension": "Lying Barbell Skull Crusher",
                "Lying Leg Curl": "Machine Lying Leg Curl",
                "Machine Back Extension": "Machine Hyperextension",
                "Machine Hip Abduction": "Machine Thigh Abduction (Out)",
                "Machine Trunk Rotation": "Torso Rotation Machine",
                "One-Leg Leg Extension": "Machine Single-Leg Extension",
                "Power Clean": "Barbell Power Clean",
                "Pullups Weighted ": "Weighted Pullup",
                "Push Down": "Cable Pushdown (with Bar Handle)",
                "Push Press": "Barbell Push Press",
                "Push-Up": "Pushup",
                "Seated Leg Curl": "Machine Leg Curl",
                "Seated Machine Hip Abduction": "Machine Thigh Abduction (Out)",
                "Seated Machine Row": "Machine Row",
                "Standing Calf Raise": "Machine Calf Raise",
                "Standing Machine Calf Raise": "Machine Calf Raise",
                "Wide-Grip Lat Pull-Down": "Wide-Grip Machine Lat Pulldown",
            },
            "progression_to_gymbook": {
                "Barbell Curl": "EZ-Bar Curl",
                "Bent-Over Barbell Row": "Barbell Row",
                "Butterfly Reverse": "Reverse Machine Fly",
                "Cable Row": "Seated Cable Row",
                "Dumbbell Pullover (Targeting back)": "Dumbbell Lat Pullover",
                "Farmer's Walk (with Dumbbells)": "Farmers Walk",
                "Farmer's Walk (with Weight Plate)": "Farmers Walk",
                "Machine Calf Press": "Calf Press In Leg Press",
                "Press around": "Press Around",
                "Romanian Deadlift": "Barbell Romanian Deadlift",
                "Stiff-Leg Deadlift (Wide Stance)": "Straight-Leg Barbell Deadlift",
                "Sumo Deadlift": "Barbell Sumo Deadlift",
                "Weighted pistol squat": "Pistol squat",
            },
            "rename_in_both": {
                # Gymbook
                "Close-Grip Lat Pull-Down": "Close-Grip Machine Lat Pull-Down",
                "Parallel Bar Dip": "Dip",
                # Progression
                "Barbell Shrug (Behind the Back)": "Barbell Shrug",
                "Chest Dip": "Dip",
                "Deficit Deadlift": "Barbell Deficit Deadlift",
                "Machine Bench Press": "Seated Machine Bench Press",
                "Cossaq Squat": "Cossack Squat",
                "Cable Pull Trough": "Cable Pull Through",
            },
        }

    def harmonize_data(self, df_progression, df_gymbook):
        """
        Harmonize and combine data from Progression and GymBook sources.

        This method performs the following operations:
        1. Standardizes GymBook data
        2. Combines date and time columns for both datasets
        3. Adjusts set order for Progression data
        4. Adds metadata to GymBook data
        5. Combines both datasets
        6. Matches exercise names across the combined dataset

        Returns one dataFrame with all the data combined.
        """
        df_gymbook = self._standardize_gymbook_data(df_gymbook)
        df_progression = self._combine_date_time_columns(df_progression, "%Y-%m-%d %H:%M:%S")
        df_gymbook = self._combine_date_time_columns(df_gymbook, "%d.%m.%Y %H:%M")
        df_progression["Set Order"] += 1
        df_gymbook = self._add_gymbook_metadata(df_gymbook)
        # Combine data sets
        df = pd.concat([df_progression, df_gymbook]).sort_values("Time", ascending=False)
        df = self._match_exercise_names(df)
        return df

    def _standardize_gymbook_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename and convert gymbook columns to match progression columns"""
        df = self._standardize_gymbook_columns(df)
        return self._convert_numeric_columns(df)

    @staticmethod
    def _standardize_gymbook_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Rename gymbook columns to match naming convention of progression app."""
        column_name_mapping = {
            "Datum": "Date",
            "Training": "Workout Name",
            "Zeit": "Set Timestamp",
            "Übung": "Exercise Name",
            "Wiederholungen / Zeit": "Repetitions",
            "Gewicht / Strecke": "Weight",
            "Notizen": "Set Comment",
        }
        return df.rename(columns=column_name_mapping)

    @staticmethod
    def _convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Convert 'Repetitions' and 'Weight' columns of the gymbook df to appropriate numeric types."""
        # Reps are logged as "<rep_number> Wiederholungen" (str) --> convert to only number (int)
        df["Repetitions"] = df["Repetitions"].str.extract(r"(\d+)").astype(int)
        # Weight is logged as e.g. "2,5 kg" (str) --> convert to 2.5 (float)
        df["Weight"] = df["Weight"].str.extract(r"(\d+,\d+)").replace(",", ".", regex=True).astype(float)
        return df

    @staticmethod
    def _combine_date_time_columns(
        df: pd.DataFrame, format_string: str, date_col: str = "Date", time_col: str = "Set Timestamp"
    ) -> pd.DataFrame:
        """Combine separate date and time columns into a single datetime column."""
        df["Time"] = pd.to_datetime(df[date_col] + " " + df[time_col], format=format_string)
        return df.drop(columns=[date_col, time_col])

    @staticmethod
    def _add_gymbook_metadata(df: pd.DataFrame) -> pd.DataFrame:
        """Add 'Session Duration' and 'Set Order' columns to gymbook df, to match progression df."""
        # Calculate workout time using time difference between first and last set for each day
        df["Session Duration (s)"] = (
            df.groupby(df["Time"].dt.date, observed=True)["Time"].transform(lambda x: x.max() - x.min()).dt.seconds
        )
        df["Set Order"] = df.groupby([df["Time"].dt.date, "Exercise Name"], observed=True).cumcount() + 1
        return df

    def _match_exercise_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Match exercise names between different data sources.
        Converts plural exercise names to singular, applies various name mappings, and capitalizes exercise names.
        """
        df = df.copy()
        df["Exercise Name"] = (
            df["Exercise Name"]
            .replace(self.singularize(set(df["Exercise Name"])))
            .replace(self.name_mappings["gymbook_to_progression"])
            .replace(self.name_mappings["progression_to_gymbook"])
            .replace(self.name_mappings["rename_in_both"])
        )

        df["Exercise Name"] = df["Exercise Name"].apply(self._capitalize_exercise_name)

        return df

    @staticmethod
    def singularize(exercises: Set[str]) -> Dict[str, str]:
        """Convert exercise names from plural to singular form."""
        plural_to_singular_map = {}
        for exercise in exercises:
            if exercise.endswith(("Lunges", "Raises")):
                # Example: Barbell Lunges --> Barbell Lunge, Calf Raises...
                plural_to_singular_map[exercise] = exercise[:-1]
            elif exercise.endswith("es"):
                # Example: Crunches -> Crunch, Arnold Presses...
                plural_to_singular_map[exercise] = exercise[:-2]
            elif exercise.endswith("s") and not exercise.endswith("ss"):
                # Example: Barbell Rows -> Barbell Row, Leg Extensions...
                plural_to_singular_map[exercise] = exercise[:-1]
            else:
                plural_to_singular_map[exercise] = exercise
        return plural_to_singular_map

    @staticmethod
    def _capitalize_exercise_name(name: str) -> str:
        """Capitalize each word in the exercise name, except for 'and', 'in', 'with'."""
        return " ".join(word.capitalize() if word not in ["and", "in", "with"] else word for word in name.split())


class DataEnricher:
    """Harmonizes exercise data by standardizing names, categories, and metadata across different data sources."""

    def enrich_data(self, df: pd.DataFrame, exercise_library: ExerciseLibrary) -> pd.DataFrame:
        """
        Apply all data enrichment steps to the input DataFrame.

        This method performs the following operations:
        1. Adds exercise categories for Muscle Category, Equipment, Mechanic, and Force.
        2. Adds derived columns such as weekday and volume information.

        Returns an enriched DataFrame with additional columns for exercise categories and derived metrics.
        """
        df = df.copy()
        for category_type in [MuscleCategory, Equipment, Mechanic, Force]:
            df = self._add_exercise_category(df, category_type, exercise_library)
        df = self._add_derived_columns(df)
        return df

    def _add_exercise_category(
        self, df: pd.DataFrame, category_type: type, exercise_library: ExerciseLibrary, column_name: str = None
    ) -> pd.DataFrame:
        """Add a new column to the DataFrame with exercise category information."""
        if column_name is None:
            column_name = f"{category_type.__name__} Category"

        exercise_to_category = {}
        for category in list(category_type):
            if category_type == MuscleCategory:
                search_criteria = ExerciseSearchCriteria(muscle_category=category)
            else:
                search_criteria = ExerciseSearchCriteria(**{category_type.__name__.lower(): category})

            category_exercises = exercise_library.search_exercises(search_criteria)
            for exercise in category_exercises:
                exercise_to_category[exercise.name] = category.value.capitalize()

        df[column_name] = df["Exercise Name"].map(exercise_to_category).astype("category")
        return df

    @staticmethod
    def _add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Add derived columns to the DataFrame: Weekday and Volume."""
        weekday_map = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }

        df["Weekday"] = df.index.weekday.map(weekday_map).astype("category")
        df["Volume"] = df["Weight"].astype(float) * df["Repetitions"]
        return df


class WorkoutDataPreprocessor:
    """Prepares and standardizes fitness tracking data for analysis and reporting."""

    def __init__(self, data_paths: DataPaths):
        self.data_paths = data_paths
        self.exercise_library = create_exercise_library()
        self.data_loader = DataLoader()
        self.data_cleaner = DataCleaner()
        self.data_harmonizer = DataHarmonizer()
        self.data_enricher = DataEnricher()

    def get_fitness_dataframe(self) -> pd.DataFrame:
        """
        Process and clean workout data from multiple sources to create a comprehensive fitness dataframe.

        This method performs the following steps:
        1. Loads raw data from Progression and GymBook sources.
        2. Pre-cleans the data to remove inconsistencies and irrelevant information.
        3. Merges the different data into one unified format.
        4. Enriches the data with additional exercise information and derived metrics.
        5. Performs final cleaning and formatting of the data.

        Returns a dataframe, where each row represents an exercise set.
        Key information includes the exercise name, date/time, reps, weight.
        """
        df_progression, df_gymbook = self.data_loader.load_data(
            self.data_paths.gym_progression, self.data_paths.gym_gymbook
        )
        df_progression, df_gymbook = self.data_cleaner.pre_clean_data(df_progression, df_gymbook)
        df = self.data_harmonizer.harmonize_data(df_progression, df_gymbook)
        df = self.data_cleaner.post_clean_data(df)
        df = self.data_enricher.enrich_data(df, self.exercise_library)
        return df


class BodyWeightDataProcessor:
    """Processes and combines body weight data from MyFitnessPal and Eufy sources."""

    def __init__(self, data_paths: DataPaths):
        self.data_paths = data_paths

    def get_body_weight_dataframe(self) -> pd.DataFrame:
        """
        Retrieve and process body weight data from multiple sources.

        This method:
        1. Loads data from MyFitnessPal and Eufy sources
        2. Processes each dataset to ensure consistency
        3. Combines the datasets into a single, unified format

        Returns a dataframe where each row represents a body weight measurement.
        """
        df_myfitnesspal = self._load_myfitnesspal_data()
        df_eufy = self._load_eufy_data()
        return self._combine_and_process_data(df_myfitnesspal, df_eufy)

    def _load_myfitnesspal_data(self) -> pd.DataFrame:
        """Load and preprocess MyFitnessPal data."""
        df = pd.read_csv(self.data_paths.weight_myfitnesspal, delimiter=";")
        df.index = pd.to_datetime(df["Date"] + " 09:00:00")
        return df.drop("Date", axis=1)

    def _load_eufy_data(self) -> pd.DataFrame:
        """Load and preprocess Eufy data."""
        df = pd.read_csv(self.data_paths.weight_eufy)
        return df.rename(columns={"WEIGHT (kg)": "Weight"})

    @staticmethod
    def _combine_and_process_data(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        """Combine and process data from both sources."""
        df_combined = pd.concat([df1, df2])
        df_combined["Time"] = pd.to_datetime(df_combined["Time"])
        df_combined = df_combined.sort_values("Time").reset_index(drop=True)
        return df_combined.rename(columns={"Weight": "Weight [kg]"})
