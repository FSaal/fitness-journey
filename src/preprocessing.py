import csv
import re
from pathlib import Path

import pandas as pd


class PreprocessClass:
    def __init__(
        self,
        gymbook_path: str,
        progression_path: str,
        weight_myfitnesspal_path: str,
        weight_eufy_path: str,
    ):
        self.progression_path = Path(progression_path)
        self.gymbook_path = Path(gymbook_path)
        self.PROGRESSION_NAME = "progression"
        self.GYMBOOK_NAME = "gymbook"
        self.weight_myfitnesspal_path = Path(weight_myfitnesspal_path)
        self.weight_eufy_path = Path(weight_eufy_path)

    def fix_progression_csv(self, input_file_path: Path, output_file_path=None) -> Path:
        """Makes the progression csv readable and returns the path to the fixed csv"""
        with open(input_file_path, "r") as input_file:
            reader = csv.reader(input_file)
            first_fix = self.fix_linebreaks(reader)
            second_fix = self.replace_comma_in_comments(first_fix)

        if not output_file_path:
            output_file_path = f"{input_file_path.stem}_fixed.csv"
        with open(output_file_path, "w") as output_file:
            writer = csv.writer(output_file, lineterminator="\n")
            [writer.writerow(row) for row in second_fix]
        return output_file_path

    @staticmethod
    def fix_linebreaks(reader: csv.reader):
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
            elif not re.match("\d{4}-\d{2}-\d{2}", line[0]):
                last_line = fixed_lines[-1]
                fixed_lines[-1] = last_line[:-1] + [". ".join([last_line[-1], line[0]])] + line[1:]
            else:
                fixed_lines.append(line)

        return iter(fixed_lines)

    @staticmethod
    def replace_comma_in_comments(rows) -> list[list]:
        """Replace ',' in comments with ';'"2022-04-18 20 04 14.csv"

        When writing a comment with a ',' in the progression app, the .csv file treats it as new entry.
        This leads to a faulty parsing of the lines.
        To fix this, the comma is replaced with ';'"""
        header_line = next(rows)
        column_count = ",".join(header_line).count(",")
        fixed_lines = [header_line]

        for i, line in enumerate(rows):
            # Convert from list to string
            line = ",".join(line)
            comma_count = line.count(",")
            # Lines where a comma was written in either set or session comment
            if comma_count > column_count:
                first_parts = line.split(",")[:14]
                comment_parts = line.split(",")[14:-2]
                end_parts = line.split(",")[-2:]

                fixed_parts = [comment_parts[0]]
                for part in comment_parts[1:]:
                    if part and part[0] == " ":
                        fixed_parts[-1] += ";" + part
                    elif part and part[0].isdigit() and fixed_parts[-1][-1].isdigit():
                        fixed_parts[-1] += "." + part
                    else:
                        fixed_parts.append(part)

                if len(fixed_parts) > 2:
                    fixed_parts = [" ".join(fixed_parts)]
                    # raise ValueError(f"Too many commas in line {i}: {line}")

                line = ",".join(first_parts + fixed_parts + end_parts)

            # Convert string back to list
            line = line.split(",")
            fixed_lines.append(line)

        return fixed_lines

    def read_csv(self, filepath: str, name: str) -> pd.DataFrame:
        """Read a csv file as dataframe."""
        if name == self.GYMBOOK_NAME:
            df = pd.read_csv(filepath, delimiter=";", decimal=",")
        else:
            df = pd.read_csv(filepath, delimiter=",", decimal=",")
        df.name = name
        return df

    # Cleanup the dataframes
    # Remove unused columns
    @staticmethod
    def remove_redundant_columns(df: pd.DataFrame, unneeded_columns: list = None) -> pd.DataFrame:
        """Remove columns which do not hold any valuable information."""
        constant_columns = [col for col in df.columns if df[col].nunique() <= 1]
        redundant_columns = constant_columns + unneeded_columns

        if "Set Duration (s)" in redundant_columns:
            # Before removing Set Duration, write the info in the repetitions columns, used for time-based exercises e.g. Plank
            df["Repetitions"] = df["Repetitions"].fillna(df["Set Duration (s)"])

        df_compact = df.drop(redundant_columns, axis=1, errors="ignore")
        # print(f"Removed columns {redundant_columns}")
        return df_compact

    @staticmethod
    def merge_date_time_columns(
        df: pd.DataFrame,
        format_string: str,
        date_col: str = "Date",
        time_col: str = "Set Timestamp",
    ):
        """Replace date and time column by one datetime column."""
        df["Time"] = pd.to_datetime(df[date_col] + " " + df[time_col], format=format_string)
        df_datetime = df.drop([date_col, time_col], axis=1)
        return df_datetime

    def remove_skipped_sets(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove sets from dataframe, which were not performed"""
        skipped_sets = df[df["Ausgelassen"] == "Ja"]
        df_no_skipped_sets = df.drop(skipped_sets.index, errors="ignore")
        return df_no_skipped_sets

    # Prepare the two dataframes for the merging into one
    # Map columns which hold the same information, only named differently
    @staticmethod
    def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Rename gymbook columns to match naming of progression app"""
        column_name_mapping = {
            "Datum": "Date",
            "Training": "Workout Name",
            "Zeit": "Set Timestamp",
            "Übung": "Exercise Name",
            "Wiederholungen / Zeit": "Repetitions",
            "Gewicht / Strecke": "Weight",
            "Notizen": "Set Comment",
        }
        df_renamed_cols = df.rename(columns=column_name_mapping)
        return df_renamed_cols

    @staticmethod
    def convert_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Convert number columns to int / float"""
        # Convert repetitions column from string to int
        df["Repetitions"] = df["Repetitions"].str.extract("(\d+)").astype(int)
        # Remove "kg" from weight column and convert from string to float
        df["Weight"] = df["Weight"].str.extract("(\d+,\d+)").replace(",", ".", regex=True).astype(float)
        return df

    def adapt_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename and convert gymbook columns to match progression columns"""
        df = self.rename_columns(df)
        df = self.convert_columns(df)
        return df

    # Check which columns are unique for each df
    @staticmethod
    def extend_gymbook_df(df: pd.DataFrame) -> pd.DataFrame:
        """Add Session Duration and Set Order column to gymbook df, to match progression df"""
        # Calculate workout time using time difference between first and last set for each day
        df["Session Duration (s)"] = (
            df.groupby(df["Time"].dt.date, observed=True)["Time"].transform(lambda x: x.max() - x.min()).dt.seconds
        )
        df["Set Order"] = df.groupby([df["Time"].dt.date, "Exercise Name"], observed=True).cumcount() + 1
        return df

    @staticmethod
    def singularize(exercises: set[str]) -> dict:
        """Convert from plural form to singular form"""
        singles = []
        for exercise in exercises:
            if exercise[-2:] == "es":
                if "Lunges" in exercise or "Raises" in exercise:
                    # Example: Barbell Lunges --> Barbell Lunge, Calf Raises...
                    singular_replacement = exercise[:-1]
                else:
                    # Example: Crunches -> Crunch, Arnold Presses...
                    singular_replacement = exercise[:-2]
                singles.append([exercise, singular_replacement])
            elif exercise[-1:] == "s" and not exercise[-2:] == "ss":
                # Example: Barbell Rows -> Barbell Row, Leg Extensions...
                singular_replacement = exercise[:-1]
                singles.append([exercise, singular_replacement])

        map_plural_to_singular = dict(singles)
        return map_plural_to_singular

    def match_exercise_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """"""
        map_gymbook_plural_to_singular = self.singularize(set(df["Exercise Name"]))

        # Convert some gymbook names to progression names
        map_gymbook_to_progression = {
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
        }

        # Convert some progression names to gymbook names
        map_progression_to_gymbook = {
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
        }

        # Convert some names to a value, which is in neither dataframe
        map_rename_in_both = {
            # Gymbook
            "Close-Grip Lat Pull-Down": "Close-Grip Machine Lat Pull-Down",
            "Parallel Bar Dip": "Dip",
            # Progression
            "Barbell Shrug (Behind the Back)": "Barbell Shrug",
            "Chest Dip": "Dip",
            "Deficit Deadlift": "Barbell Deficit Deadlift",
            "Machine Bench Press": "Seated Machine Bench Press",
        }

        df["Exercise Name"] = df["Exercise Name"].replace(map_gymbook_plural_to_singular)
        df["Exercise Name"] = df["Exercise Name"].replace(map_gymbook_to_progression)
        df["Exercise Name"] = df["Exercise Name"].replace(map_progression_to_gymbook)
        df["Exercise Name"] = df["Exercise Name"].replace(map_rename_in_both)

        # Capitalize all exercise names
        not_capitalized_exercise_names = [
            exercise
            for exercise in df["Exercise Name"].unique()
            if not all(word.istitle() for word in exercise.split())
            and not any(word in exercise for word in ["and", "in", "with"])
        ]
        capitalized_exercise_names = [exercise.title() for exercise in not_capitalized_exercise_names]
        map_capitalize = {key: value for key, value in zip(not_capitalized_exercise_names, capitalized_exercise_names)}
        df["Exercise Name"] = df["Exercise Name"].replace(map_capitalize)

        return df

    @staticmethod
    def add_muscle_category(df: pd.DataFrame) -> pd.DataFrame:
        # Convert from german to english
        map_muscle_category_ger_eng = {
            "Arme": "Arms",
            "Bauch": "Abs",
            "Beine": "Legs",
            "Brust": "Chest",
            "Gesäss": "Glute",
            "Rücken": "Back",
            "Schultern": "Shoulders",
        }
        df["Bereich"] = df["Bereich"].map(map_muscle_category_ger_eng).fillna("Undefined")

        exercises_without_category = set(df[df["Bereich"] == "Undefined"]["Exercise Name"])
        exercises_with_category = set(df[df["Bereich"] != "Undefined"]["Exercise Name"])
        # Exercises which where mapped from gymbook to progression naming and did loose their Bereich
        exercises_with_lost_category = exercises_with_category.intersection(exercises_without_category)

        for exercise in exercises_with_lost_category:
            # Get first (and only) element of set
            muscle_category = next(iter(set(df[df["Exercise Name"] == exercise]["Bereich"]) - {"Undefined"}))
            df.loc[
                (df["Exercise Name"] == exercise) & (df["Bereich"] == "Undefined"),
                "Bereich",
            ] = muscle_category

        map_exercise_to_muscle = {
            "Abs": {"Crunch"},
            "Arms": {"Push", "Curl", "Kickback", "Triceps"},
            "Back": {"Pull", "Row", "Deadlift"},
            "Chest": {"Bench", "Crossover", "Fly"},
            "Legs": {"Calf", "Leg", "Squat", "Lunge", "Thigh", "Clean"},
            "Shoulders": {"Shoulder", "Shrug", "Delt", "Arnold", "Raise"},
        }

        for exercise in exercises_without_category:
            muscle_categories = []
            for category, keywords in map_exercise_to_muscle.items():
                for keyword in keywords:
                    if keyword in exercise:
                        muscle_category = category
                        muscle_categories.append(category)
            if len(muscle_categories) == 1:
                # print(f"Mapping {exercise} to {muscle_category}")
                df.loc[df["Exercise Name"] == exercise, "Bereich"] = muscle_category
            elif len(muscle_categories) > 1:
                # Legs always wins
                if "Legs" in muscle_categories:
                    df.loc[df["Exercise Name"] == exercise, "Bereich"] = "Legs"
                else:
                    pass
                    # print(f"Problem with {exercise}. Found in {muscle_categories}. Skipping...")
            else:
                pass
                # print(f"No mapping for {exercise}")

        # Solving conflicts - have keywords in two muscle categories
        map_conflicts = {
            "Shoulders": {"Cable Rear Delt Fly"},
            "Back": {"Single-Arm Dumbbell Row on Bench"},
            "Chest": {"Barbell Bench Press (with Raised Feet)"},
        }

        # Map the rest manually
        manual_map = {
            "Abs": {
                "Ab Complex",
                "Burpee",
                "Plank",
                "Russian Twist",
                "Standing Cable Lift",
            },
            "Back": {"Weighted Chinup"},
            "Arms": {"Wrist Curl (Roller)"},
            "Shoulders": "Barbell Push Press",
        }

        for muscle_category, exercises in map_conflicts.items():
            for exercise in exercises:
                df.loc[df["Exercise Name"] == exercise, "Bereich"] = muscle_category

        for muscle_category, exercises in manual_map.items():
            for exercise in exercises:
                df.loc[df["Exercise Name"] == exercise, "Bereich"] = muscle_category

        df = df.rename(columns={"Bereich": "Muscle Category"})
        return df

    @staticmethod
    def add_exercise_category(df: pd.DataFrame) -> pd.DataFrame:
        map_exercise_to_type = {
            "Barbell": {
                "Bar",
                "Box Squat",
                "Clean",
                "Ez-Bar",
                "Hexbar Deadlift",
                "Barbell",
            },
            "Bodyweight": {
                "Ab",
                "Burpee",
                "Chinup",
                "Cossaq Squat",
                "Crunch",
                "Dip",
                "Glute Ham Raise",
                "Hanging Leg Raise",
                "Incline Sit-Up",
                "Pistol Squat",
                "Plank",
                "Pullup",
                "Pushup",
                "Razor Curl",
                "Russian Twist",
            },
            "Cable": {"Cable", "One-Arm Lat Pull-Down", "Push-Down"},
            "Dumbbell": {
                "Bulgarian Split Squat",
                "Dumbbell",
                "Goblet Squat",
                "Larsen Press",
                "Press Around",
                "Walking Lunge",
            },
            "Kettlebell": {"Kettlebell"},
            "Machine": {
                "Calf Press In Leg Press",
                "Glute Drive",
                "Machine",
                "Single-Leg Press",
                "Standing Calf Raisees",
            },
        }

        df["Exercise Type"] = "Other"
        for exercise_type, exercise in map_exercise_to_type.items():
            mask = df["Exercise Name"].str.contains("|".join(exercise))
            df.loc[mask, "Exercise Type"] = exercise_type
        return df

    @staticmethod
    def fix_dtypes(df: pd.DataFrame) -> pd.DataFrame:
        # Remove NaNs
        df["Weight"] = df["Weight"].fillna(0).astype(float)

        df["Repetitions"] = df["Repetitions"].astype(int)
        df["Muscle Category"] = df["Muscle Category"].astype("category")
        df["Exercise Type"] = df["Exercise Type"].astype("category")
        return df

    @staticmethod
    def add_other_stuff(df: pd.DataFrame) -> pd.DataFrame:
        """Add weekday and volume information as columns"""
        weekday_map = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }

        df["Weekday"] = df["Time"].dt.weekday.map(weekday_map).astype("category")
        df["Volume"] = df["Weight"].astype(float) * df["Repetitions"]
        return df

    @staticmethod
    def clean_up_data(df: pd.DataFrame) -> pd.DataFrame:
        """Remove and/or edit inplausible data"""
        # Limit gym session duration
        # Workout session of more than 3 hours must be a mistake
        session_time_limit_s = 3 * 60 * 60
        df_too_long = df[df["Session Duration (s)"] > session_time_limit_s]
        # Find entry which differs greatly from the other entries
        outlier = df_too_long[df_too_long["Time"].diff() > pd.Timedelta(hours=1)]
        # Get the entry before, because...
        outlier_id = outlier.index[0] - 1
        # Remove outlier from dataframe
        df = df.drop(outlier_id)
        # Recalculate session duration
        df_too_long = df[df["Session Duration (s)"] > session_time_limit_s]
        df.loc[df["Session Duration (s)"] > session_time_limit_s, "Session Duration (s)"] = (
            df_too_long.groupby(df["Time"].dt.date, observed=True)["Time"]
            .transform(lambda x: x.max() - x.min())
            .dt.seconds
        )

        # Replace NaNs of column Set Comment with empty string
        df["Set Comment"] = df["Set Comment"].fillna("None")
        return df

    def main(self):
        # Data file of Progression app (android)
        fixed_progression_csv = self.fix_progression_csv(self.progression_path)
        df_progression = self.read_csv(fixed_progression_csv, self.PROGRESSION_NAME)

        # Data file of GymBook app (iOS)
        # Note: sep=, has to be added as first line in the csv file
        # Also file has to be saved as utf-8 csv in Excel
        df_gymbook = self.read_csv(self.gymbook_path, self.GYMBOOK_NAME)

        df_gymbook = self.remove_skipped_sets(df_gymbook)

        df_gymbook = self.remove_redundant_columns(
            df_gymbook,
            [
                "Muskelgruppen (Primäre)",
                "Muskelgruppen (Sekundäre)",
                "Satz / Aufwärmsatz / Abkühlungssatz",
            ],
        )
        # Before removing Set Duration, write the info in the repetitions columns, used for time-based exercises e.g. Plank
        df_progression = self.remove_redundant_columns(df_progression, ["Time", "Set Duration (s)"])

        df_gymbook = self.adapt_columns(df_gymbook)

        # Convert and combine date / time columns into one datetime column
        df_progression = self.merge_date_time_columns(df_progression, "%Y-%m-%d %H:%M:%S")
        # Change progression set Order, such that it starts at 1 instead of 0
        df_progression["Set Order"] = df_progression["Set Order"] + 1
        df_gymbook = self.merge_date_time_columns(df_gymbook, "%d.%m.%Y %H:%M")

        df_gymbook = self.extend_gymbook_df(df_gymbook)

        df = pd.concat([df_progression, df_gymbook])
        df = df.sort_values("Time", ascending=False)

        df = self.match_exercise_names(df)
        df = self.add_muscle_category(df)
        df = self.add_exercise_category(df)
        df = self.fix_dtypes(df)
        df = self.add_other_stuff(df)

        df = df.sort_values("Time").reset_index(drop=True)
        df = self.clean_up_data(df)
        df.index = df["Time"]
        # Rename index to Time
        df.index.name = "Time"

        df_bodyweight = self.get_body_weight_dataframe()

        return df, df_bodyweight

    def get_body_weight_dataframe(self):
        # Old data export from myFitnessPal
        df_weight_old = pd.read_csv(self.weight_myfitnesspal_path, delimiter=";")
        # Add a time to the date
        df_weight_old["Time"] = df_weight_old["Date"] + " 09:00:00"
        df_weight_old = df_weight_old.drop("Date", axis=1)

        # New data export from Eufy Smart Scale
        df_weight_new = pd.read_csv(self.weight_eufy_path)
        df_weight_new = df_weight_new.rename(columns={"WEIGHT (kg)": "Weight"})

        df_weight = pd.concat([df_weight_old, df_weight_new])
        df_weight["Time"] = pd.to_datetime(df_weight["Time"], format="%Y-%m-%d %H:%M:%S")
        # Sort by time
        df_weight = df_weight.sort_values("Time")
        df_weight = df_weight.reset_index(drop=True)

        return df_weight
