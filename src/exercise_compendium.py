from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Force(Enum):
    PUSH = "push"
    PULL = "pull"
    HOLD = "hold"

    def __str__(self):
        return self.value


class Mechanic(Enum):
    ISOLATION = "Isolation"
    MIXED = "Mixed"
    COMPOUND = "Compound"
    STRENGTH = "Strength"

    def __str__(self):
        return self.value


class Equipment(Enum):
    BARBELL = "Barbell"
    BODY_WEIGHT = "Bodyweight"
    DUMBBELL = "Dumbbell"
    MACHINE = "Machine"
    OTHER = "Other"

    def __str__(self):
        return self.value


class Muscle(Enum):
    CALVES = "Calves"
    HAMSTRINGS = "Hamstrings"
    QUADS = "Quads"
    GLUTES = "Glutes"
    LOWER_BACK = "Lower back"
    ABS = "Abdominals"
    OBLIQUES = "Obliques"
    LATS = "Lats"
    CHEST = "Chest"
    TRAPS = "Traps"
    SHOULDERS = "Shoulders"
    TRICEPS = "Triceps"
    BICEPS = "Biceps"
    FOREARMS = "Forearms"

    def __str__(self):
        return self.value


@dataclass
class ExerciseData:
    """Different information about an exercise."""

    name: str
    force: Force
    mechanic: Mechanic
    equipment: Equipment
    prime_muscles: list[Muscle]
    secondary_muscles: list[Muscle] = field(default_factory=list)
    teritary_muscles: list[Muscle] = field(default_factory=list)
    is_variation_of: Optional[str] = None

    def join_muscles(self, muscles) -> str:
        return ", ".join([str(muscle) for muscle in muscles])

    def get_similar_exercise(self, exercise_compendium) -> set[str]:
        """Return a set of exercise names that are similar to the current exercise."""
        if self.is_variation_of is None:
            # Check if this is a main exercise and there are variations of it
            variations = {
                exercise.name for exercise in exercise_compendium.values() if exercise.is_variation_of == self.name
            }
            variations.add(self.name)
        else:
            parent_exercise = self.is_variation_of
            variations = {
                exercise.name
                for exercise in exercise_compendium.values()
                if exercise.is_variation_of == parent_exercise
            }
            variations.add(parent_exercise)
            variations.add(self.name)

        return variations


# Type alias for ExerciseData
Exercise = ExerciseData


exercise_compendium = {
    "Ab Complex": ExerciseData(
        name="Ab Complex",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.ABS],
    ),
    "Ab Roller": ExerciseData(
        name="Ab Roller",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.ABS],
    ),
    "Alternating Dumbbell Curl": ExerciseData(
        name="Alternating Dumbbell Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.BICEPS],
        is_variation_of="Dumbbell Curl",
    ),
    "Alternating Dumbbell Hammer Curl": ExerciseData(
        name="Alternating Dumbbell Hammer Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.BICEPS],
        is_variation_of="Dumbbell Curl",
    ),
    "Arnold Dumbbell Press (Seated)": ExerciseData(
        name="Arnold Dumbbell Press (Seated)",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        teritary_muscles=[Muscle.CHEST],
        is_variation_of="Dumbbell Shoulder Press",
    ),
    "Arnold Dumbbell Press (Standing)": ExerciseData(
        name="Arnold Dumbbell Press (Standing)",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        teritary_muscles=[Muscle.CHEST],
        is_variation_of="Dumbbell Shoulder Press",
    ),
    "Barbell Bench Press": ExerciseData(
        name="Barbell Bench Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.TRICEPS],
        teritary_muscles=[Muscle.SHOULDERS],
    ),
    "Barbell Bench Press (with Raised Feet)": ExerciseData(
        name="Barbell Bench Press (with Raised Feet)",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.TRICEPS],
        teritary_muscles=[Muscle.SHOULDERS],
        is_variation_of="Barbell Bench Press",
    ),
    "Barbell Clean": ExerciseData(
        name="Barbell Clean",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.TRAPS],
        secondary_muscles=[Muscle.HAMSTRINGS, Muscle.GLUTES],
        teritary_muscles=[Muscle.CALVES],
    ),
    "Barbell Deadlift": ExerciseData(
        name="Barbell Deadlift",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.LOWER_BACK, Muscle.TRAPS],
        secondary_muscles=[Muscle.GLUTES],
        teritary_muscles=[Muscle.HAMSTRINGS],
    ),
    "Barbell Deficit Deadlift": ExerciseData(
        name="Barbell Deficit Deadlift",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.LOWER_BACK, Muscle.TRAPS],
        secondary_muscles=[Muscle.GLUTES],
        teritary_muscles=[Muscle.HAMSTRINGS],
        is_variation_of="Barbell Deadlift",
    ),
    "Barbell Front Squat": ExerciseData(
        name="Barbell Front Squat",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES, Muscle.ABS],
        teritary_muscles=[Muscle.LOWER_BACK],
    ),
    "Barbell Lunge": ExerciseData(
        name="Barbell Lunge",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.QUADS, Muscle.GLUTES],
    ),
    "Barbell Power Clean": ExerciseData(
        name="Barbell Power Clean",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.TRAPS],
        secondary_muscles=[Muscle.HAMSTRINGS, Muscle.GLUTES],
        teritary_muscles=[Muscle.CALVES],
        is_variation_of="Barbell Clean",
    ),
    "Barbell Push Press": ExerciseData(
        name="Barbell Push Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        teritary_muscles=[Muscle.QUADS, Muscle.ABS],
        is_variation_of="Barbell Shoulder Press",
    ),
    "Barbell Romanian Deadlift": ExerciseData(
        name="Barbell Romanian Deadlift",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.GLUTES, Muscle.HAMSTRINGS],
        secondary_muscles=[Muscle.LOWER_BACK],
        is_variation_of="Barbell Deadlift",
    ),
    "Barbell Row": ExerciseData(
        name="Barbell Row",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS],
        teritary_muscles=[Muscle.FOREARMS, Muscle.LOWER_BACK],
    ),
    "Barbell Shoulder Press": ExerciseData(
        name="Barbell Shoulder Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        teritary_muscles=[Muscle.CHEST],
    ),
    "Barbell Shoulder Press (Seated)": ExerciseData(
        name="Barbell Shoulder Press (Seated)",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        teritary_muscles=[Muscle.CHEST],
        is_variation_of="Barbell Shoulder Press",
    ),
    "Barbell Shrug": ExerciseData(
        name="Barbell Shrug",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.TRAPS],
    ),
    "Barbell Squat": ExerciseData(
        name="Barbell Squat",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES],
        teritary_muscles=[Muscle.LOWER_BACK],
    ),
    "Barbell Sumo Deadlift": ExerciseData(
        name="Barbell Sumo Deadlift",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.GLUTES],
        secondary_muscles=[Muscle.HAMSTRINGS, Muscle.QUADS],
        teritary_muscles=[Muscle.LOWER_BACK],
        is_variation_of="Barbell Deadlift",
    ),
    "Barbell Triceps Extension (Seated)": ExerciseData(
        name="Barbell Triceps Extension (Seated)",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.TRICEPS],
    ),
    "Dumbbell Curl": ExerciseData(
        name="Dumbbell Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.BICEPS],
    ),
}
