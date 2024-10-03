from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower().replace("_", " ")


class Force(AutoName):
    PUSH = auto()
    PULL = auto()
    ISOMETRIC = auto()
    ENDURANCE = auto()


class Mechanic(AutoName):
    ISOLATION = auto()
    MIXED = auto()
    COMPOUND = auto()
    STRENGTH = auto()
    AEROBIC = auto()


class Equipment(AutoName):
    BARBELL = auto()
    BODY_WEIGHT = auto()
    DUMBBELL = auto()
    MACHINE = auto()
    KETTLEBELL = auto()
    HEX_BAR = auto()
    OTHER = auto()


class Muscle(AutoName):
    ABS = auto()
    BICEPS = auto()
    CALVES = auto()
    CHEST = auto()
    FOREARMS = auto()
    GLUTES = auto()
    HAMSTRINGS = auto()
    HIP_ABDUCTORS = auto()
    HIP_ADDUCTORS = auto()
    HIP_FLEXORS = auto()
    LATS = auto()
    LOWER_BACK = auto()
    MIDDLE_BACK = auto()
    OBLIQUES = auto()
    QUADS = auto()
    REAR_DELTS = auto()
    SHOULDERS = auto()
    TIBIALIS = auto()
    TRAPS = auto()
    TRICEPS = auto()
    UPPER_BACK = auto()


@dataclass
class ExerciseData:
    """Different information about an exercise."""

    name: str
    force: Force
    mechanic: Mechanic
    equipment: Equipment
    prime_muscles: List[Muscle]
    secondary_muscles: List[Muscle] = field(default_factory=list)
    tertiary_muscles: List[Muscle] = field(default_factory=list)
    description: Optional[str] = None
    is_variation_of: Optional[str] = None

    @staticmethod
    def join_muscles(muscles: List[Muscle]) -> str:
        return ", ".join(str(muscle.value) for muscle in muscles)

    def get_similar_exercises(self, exercise_compendium: Dict[str, "ExerciseData"]) -> Set[str]:
        """Return a set of exercise names that are similar to the current exercise."""
        if self.is_variation_of is None:
            # Exercise could be a parent exercise --> look for children
            variations = {
                exercise.name for exercise in exercise_compendium.values() if exercise.is_variation_of == self.name
            }
            variations.add(self.name)
        else:
            # Exercise is a variation and has parent --> get parent and other children
            parent_exercise = self.is_variation_of
            variations = {
                exercise.name
                for exercise in exercise_compendium.values()
                if exercise.is_variation_of == parent_exercise
            }
            variations.add(parent_exercise)
            variations.add(self.name)

        return variations


def map_to_enum(data, enum_class):
    try:
        return enum_class[data.upper()]
    except KeyError:
        raise ValueError(f"Invalid value '{data}' for enum {enum_class.__name__}")


# Type alias for ExerciseData
Exercise = ExerciseData

# Exercise compendium definition (abbreviated for brevity)
exercise_compendium: Dict[str, ExerciseData] = {
    "Ab Complex": ExerciseData(
        name="Ab Complex",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.ABS],
        description="""
        The ab complex is a challenging bodyweight exercise that targets the entire abdominal region, engaging both upper and lower abs, as well as obliques.
        It promotes core strength, stability, and endurance, essential for functional movement and injury prevention.""",
    ),
    "Ab Roller": ExerciseData(
        name="Ab Roller",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.ABS],
        description="""
        The ab roller exercise primarily targets the rectus abdominis, with secondary activation of the obliques, hip flexors, and lower back.
        This movement builds core strength, enhances stability, and improves balance by challenging the muscles through dynamic range of motion.""",
    ),
    "Alternating Dumbbell Curl": ExerciseData(
        name="Alternating Dumbbell Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.BICEPS],
        is_variation_of="Dumbbell Curl",
        description="""
    The alternating dumbbell curl is an isolation exercise that primarily targets the biceps, with secondary engagement of the forearms.
    In contrast to the standard dumbbell curl, this variation alternates between arms, allowing for better focus on each bicep individually and improving muscular balance and control.""",
    ),
    "Alternating Dumbbell Hammer Curl": ExerciseData(
        name="Alternating Dumbbell Hammer Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.BICEPS],
        is_variation_of="Dumbbell Curl",
        description="""
    The alternating dumbbell hammer curl is an isolation exercise that targets the brachialis and biceps, with secondary involvement of the forearms.
    Unlike the standard dumbbell curl, this variation uses a neutral grip, which shifts more focus to the brachialis and forearms, promoting arm strength and grip endurance.""",
    ),
    "Arnold Dumbbell Press (Seated)": ExerciseData(
        name="Arnold Dumbbell Press (Seated)",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        tertiary_muscles=[Muscle.CHEST],
        is_variation_of="Dumbbell Shoulder Press",
        description="""
    The seated Arnold dumbbell press is a compound exercise targeting the shoulders, triceps, and chest.
    It enhances shoulder mobility, builds upper body strength, and engages multiple muscle groups to improve overall stability and balance.
    Unlike the standard dumbbell shoulder press, this variation includes a rotation at the wrists, activating more of the deltoids and enhancing shoulder flexibility.""",
    ),
    "Arnold Dumbbell Press (Standing)": ExerciseData(
        name="Arnold Dumbbell Press (Standing)",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        tertiary_muscles=[Muscle.CHEST],
        is_variation_of="Dumbbell Shoulder Press",
        description="""
    The standing Arnold dumbbell press targets the shoulders, triceps, and chest while also engaging the core for stability.
    This compound movement promotes strength, flexibility, and coordination across the upper body, improving functional fitness.
    Compared to the seated version, this standing variation increases core engagement and balance, making it more challenging for the lower body and core stability.""",
    ),
    "Assisted Pullup": ExerciseData(
        name="Assisted Pullup",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS, Muscle.REAR_DELTS],
        description="""
    The assisted pullup allows for performing pullups with assistance, targeting the lats, biceps, and rear delts, and helping users develop upper body pulling strength.""",
    ),
    "Barbell Bench Press": ExerciseData(
        name="Barbell Bench Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.TRICEPS],
        tertiary_muscles=[Muscle.SHOULDERS],
        description="""
    The barbell bench press is a foundational compound exercise that primarily targets the chest, with secondary activation of the triceps and shoulders.
    It enhances upper body strength, muscle mass, and improves pushing power, making it essential for strength training.""",
    ),
    "Barbell Bench Press (with Raised Feet)": ExerciseData(
        name="Barbell Bench Press (with Raised Feet)",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.TRICEPS],
        tertiary_muscles=[Muscle.SHOULDERS],
        is_variation_of="Barbell Bench Press",
        description="""
    The barbell bench press with raised feet variation emphasizes chest activation while reducing lower body involvement.
    Unlike the standard barbell bench press, raising the feet minimizes leg drive, placing more emphasis on upper body control and chest engagement for improved strength and stability.""",
    ),
    "Barbell Clean": ExerciseData(
        name="Barbell Clean",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.TRAPS],
        secondary_muscles=[Muscle.HAMSTRINGS, Muscle.GLUTES],
        tertiary_muscles=[Muscle.CALVES],
        description="""
    The barbell clean is a dynamic compound exercise that targets the traps, hamstrings, and glutes while also engaging the calves.
    This explosive movement develops power, coordination, and strength, making it beneficial for athletes across various sports.""",
    ),
    "Barbell Deadlift": ExerciseData(
        name="Barbell Deadlift",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.LOWER_BACK, Muscle.TRAPS],
        secondary_muscles=[Muscle.GLUTES],
        tertiary_muscles=[Muscle.HAMSTRINGS],
        description="""
    The barbell deadlift is a fundamental compound exercise primarily targeting the lower back and traps, with secondary emphasis on the glutes.
    This exercise enhances overall strength, stability, and muscle development in the posterior chain, making it essential for functional fitness.""",
    ),
    "Barbell Deficit Deadlift": ExerciseData(
        name="Barbell Deficit Deadlift",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.LOWER_BACK, Muscle.TRAPS],
        secondary_muscles=[Muscle.GLUTES],
        tertiary_muscles=[Muscle.HAMSTRINGS],
        is_variation_of="Barbell Deadlift",
        description="""
    The barbell deficit deadlift is a compound exercise that targets the lower back and traps, while also engaging the glutes.
    This variation differs from the standard deadlift by increasing the range of motion, which enhances muscle activation and strength in the lower back and hamstrings, providing a greater challenge for lifters.""",
    ),
    "Barbell Front Squat": ExerciseData(
        name="Barbell Front Squat",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES, Muscle.ABS],
        tertiary_muscles=[Muscle.LOWER_BACK],
        description="""
    The barbell front squat is a compound exercise that primarily targets the quadriceps, with secondary emphasis on the glutes and abs.
    This variation encourages proper posture and core stability, enhancing overall strength and muscle development in the lower body.""",
    ),
    "Barbell Lunge": ExerciseData(
        name="Barbell Lunge",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.QUADS, Muscle.GLUTES],
        description="""
    The barbell lunge is a compound exercise that targets the quadriceps and glutes effectively.
    It promotes lower body strength, balance, and coordination while engaging the core for stability during movement.""",
    ),
    "Barbell Power Clean": ExerciseData(
        name="Barbell Power Clean",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.TRAPS],
        secondary_muscles=[Muscle.HAMSTRINGS, Muscle.GLUTES],
        tertiary_muscles=[Muscle.CALVES],
        is_variation_of="Barbell Clean",
        description="""
    The barbell power clean is a dynamic compound exercise that primarily targets the traps, with secondary involvement of the hamstrings and glutes.
    This variation focuses on explosiveness and speed, enhancing power generation and overall athletic performance, while requiring less range of motion than the traditional clean.""",
    ),
    "Barbell Power Squat": ExerciseData(
        name="Barbell Power Squat",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES, Muscle.HAMSTRINGS],
        is_variation_of="Barbell Squat",
        description="""
    The barbell power squat is a full-body compound exercise that primarily targets the quads while engaging the glutes and hamstrings, promoting lower body strength and power.""",
    ),
    "Barbell Push Press": ExerciseData(
        name="Barbell Push Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        tertiary_muscles=[Muscle.QUADS, Muscle.ABS],
        is_variation_of="Barbell Shoulder Press",
        description="""
    The barbell push press is a compound movement that targets the shoulders while also engaging the triceps and core.
    This variation incorporates a slight dip in the knees to generate momentum, allowing for heavier weights to be lifted compared to the strict shoulder press, enhancing upper body strength and power.""",
    ),
    "Barbell Romanian Deadlift": ExerciseData(
        name="Barbell Romanian Deadlift",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.GLUTES, Muscle.HAMSTRINGS],
        secondary_muscles=[Muscle.LOWER_BACK],
        is_variation_of="Barbell Deadlift",
        description="""
    The barbell Romanian deadlift focuses on the glutes and hamstrings, providing a powerful posterior chain workout.
    Unlike the standard deadlift, this variation emphasizes hip hinge mechanics and limits knee flexion, promoting better hamstring activation and strength development.""",
    ),
    "Barbell Row": ExerciseData(
        name="Barbell Row",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS],
        tertiary_muscles=[Muscle.FOREARMS, Muscle.LOWER_BACK],
        description="""
    The barbell row is a compound exercise that primarily targets the lats, with secondary engagement of the biceps and forearms.
    This movement enhances upper body strength, improves posture, and promotes muscle growth in the back and arms, crucial for overall upper body development.""",
    ),
    "Barbell Shoulder Press": ExerciseData(
        name="Barbell Shoulder Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        tertiary_muscles=[Muscle.CHEST],
        description="""
    The barbell shoulder press is a fundamental compound exercise that primarily targets the shoulders and triceps, with secondary emphasis on the chest.
    This movement builds upper body strength, stability, and muscle definition, essential for various athletic activities and daily tasks.""",
    ),
    "Barbell Shoulder Press (Seated)": ExerciseData(
        name="Barbell Shoulder Press (Seated)",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        tertiary_muscles=[Muscle.CHEST],
        is_variation_of="Barbell Shoulder Press",
        description="""
    The seated barbell shoulder press is a compound exercise that primarily targets the shoulders, triceps, and chest.
    This variation provides additional support to the back, allowing for better stability and focus on shoulder strength, which enhances overall upper body development.""",
    ),
    "Barbell Shrug": ExerciseData(
        name="Barbell Shrug",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.TRAPS],
        description="""
    The barbell shrug is an isolation exercise that targets the trapezius muscles in the upper back.
    This movement enhances upper back strength, muscle definition, and is essential for developing a strong and muscular neck and upper body posture.""",
    ),
    "Barbell Squat": ExerciseData(
        name="Barbell Squat",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES],
        tertiary_muscles=[Muscle.LOWER_BACK],
        description="""
The barbell squat is a fundamental strength training exercise that targets multiple muscle groups, including the quadriceps, hamstrings, glutes, and lower back.
This full-body workout provides numerous benefits, such as increased power, endurance, and stability.""",
    ),
    "Barbell Sumo Deadlift": ExerciseData(
        name="Barbell Sumo Deadlift",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.GLUTES],
        secondary_muscles=[Muscle.HAMSTRINGS, Muscle.QUADS],
        tertiary_muscles=[Muscle.LOWER_BACK],
        is_variation_of="Barbell Deadlift",
        description="""
    The barbell sumo deadlift is a compound exercise that emphasizes the glutes while also engaging the hamstrings and quads.
    This variation allows for a wider stance, which reduces strain on the lower back and enhances hip mobility, making it an effective choice for lower body strength development.""",
    ),
    "Barbell Triceps Extension (Seated)": ExerciseData(
        name="Barbell Triceps Extension (Seated)",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    The seated barbell triceps extension is an isolation exercise focusing on the triceps muscles.
    This movement is effective for building upper arm strength and definition, helping to improve performance in pressing movements and overall arm aesthetics.""",
    ),
    "Bent-Over Dumbbell Row": ExerciseData(
        name="Bent-Over Dumbbell Row",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.MIDDLE_BACK, Muscle.BICEPS],
        description="""
    This exercise targets the lats and middle back, while also engaging the biceps for a complete upper body workout.""",
    ),
    "Bent-Over Machine T-Bar Row": ExerciseData(
        name="Bent-Over Machine T-Bar Row",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.MIDDLE_BACK, Muscle.BICEPS],
        description="""
    This machine variation of the T-Bar row engages the lats and upper back, while providing stability and control during the movement.""",
    ),
    "Bent-Over T-Bar Row": ExerciseData(
        name="Bent-Over T-Bar Row",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.MIDDLE_BACK, Muscle.BICEPS],
        description="""
    The bent-over T-Bar row focuses on the lats and upper back, providing a challenging row movement with additional core engagement.""",
    ),
    "Bicycle Crunch": ExerciseData(
        name="Bicycle Crunch",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.ABS],
        secondary_muscles=[Muscle.OBLIQUES],
        description="""
    The bicycle crunch is a dynamic bodyweight exercise that targets the abs and obliques, promoting core strength and endurance.""",
    ),
    "Box Squat": ExerciseData(
        name="Box Squat",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES, Muscle.HAMSTRINGS],
        description="""
    The box squat focuses on the quads, glutes, and hamstrings, providing a stable base to enhance form and depth during the squat.""",
    ),
    "Bulgarian Split Squat": ExerciseData(
        name="Bulgarian Split Squat",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES, Muscle.HAMSTRINGS],
        description="""
    This unilateral exercise targets the quads and glutes, with an added focus on balance and stability for improved leg strength.""",
    ),
    "Burpee": ExerciseData(
        name="Burpee",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.CHEST, Muscle.TRICEPS],
        description="""
    The burpee is a full-body exercise that combines strength and cardio, engaging the core, chest, legs, and arms for a challenging workout.""",
    ),
    "Cable Back Fly": ExerciseData(
        name="Cable Back Fly",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.REAR_DELTS],
        secondary_muscles=[Muscle.UPPER_BACK],
        description="""
    This isolation exercise targets the rear delts and upper back, providing controlled resistance through a cable machine.""",
    ),
    "Cable Crossover (with High Angle)": ExerciseData(
        name="Cable Crossover (with High Angle)",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.SHOULDERS],
        description="""
    This high-angle variation of the cable crossover emphasizes the upper chest, while also engaging the shoulders.""",
    ),
    "Cable Crossover (with Low Angle)": ExerciseData(
        name="Cable Crossover (with Low Angle)",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.SHOULDERS],
        description="""
    This low-angle variation of the cable crossover focuses on the lower chest, providing a different range of motion for complete chest development.""",
    ),
    "Cable Crossover (with Straight Angle)": ExerciseData(
        name="Cable Crossover (with Straight Angle)",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.SHOULDERS],
        description="""
    This variation of the cable crossover targets the chest in a straight horizontal plane, promoting balanced chest development.""",
    ),
    "Cable Crunch": ExerciseData(
        name="Cable Crunch",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.ABS],
        description="""
    The cable crunch is an isolation exercise that targets the abs, providing controlled resistance to strengthen the core.""",
    ),
    "Cable Curl": ExerciseData(
        name="Cable Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.BICEPS],
        description="""
    This exercise isolates the biceps, providing controlled resistance through a cable machine for consistent tension throughout the movement.""",
    ),
    "Cable Face Pull": ExerciseData(
        name="Cable Face Pull",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.REAR_DELTS],
        secondary_muscles=[Muscle.UPPER_BACK],
        description="""
    The cable face pull targets the rear delts and upper back, improving posture and shoulder stability.""",
    ),
    "Cable Kickback": ExerciseData(
        name="Cable Kickback",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.GLUTES],
        secondary_muscles=[Muscle.HAMSTRINGS],
        description="""
    This isolation exercise focuses on the glutes, helping to develop strength and muscle in the posterior chain.""",
    ),
    "Cable Overhead Pushdown": ExerciseData(
        name="Cable Overhead Pushdown",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    The cable overhead pushdown isolates the triceps, allowing for a full range of motion and consistent tension through a cable machine.""",
    ),
    "Cable Pull Through": ExerciseData(
        name="Cable Pull Through",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.GLUTES],
        secondary_muscles=[Muscle.HAMSTRINGS],
        description="""
    This exercise targets the glutes and hamstrings, helping to improve posterior chain strength and stability.""",
    ),
    "Cable Pullover": ExerciseData(
        name="Cable Pullover",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.CHEST],
        description="""
    The cable pullover is an isolation movement that targets the lats while also engaging the chest, improving upper body strength and control.""",
    ),
    "Cable Pushdown (with Bar Handle)": ExerciseData(
        name="Cable Pushdown (with Bar Handle)",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    The cable pushdown with a bar handle isolates the triceps, helping to build arm strength and definition.""",
    ),
    "Cable Pushdown (with Rope Handle)": ExerciseData(
        name="Cable Pushdown (with Rope Handle)",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    The cable pushdown with a rope handle targets the triceps, promoting upper arm strength and muscle growth.""",
    ),
    "Cable Rear Delt Fly": ExerciseData(
        name="Cable Rear Delt Fly",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.REAR_DELTS],
        secondary_muscles=[Muscle.TRAPS],
        description="""
    The cable rear delt fly isolates the rear delts and traps, improving shoulder stability and upper back strength.""",
    ),
    "Cable Shrug": ExerciseData(
        name="Cable Shrug",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.TRAPS],
        description="""
    The cable shrug focuses on strengthening the traps, improving upper back and neck stability.""",
    ),
    "Cable Side Raise": ExerciseData(
        name="Cable Side Raise",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.SHOULDERS],
        description="""
    The cable side raise isolates the lateral deltoids, enhancing shoulder width and strength.""",
    ),
    "Cable Woodchop": ExerciseData(
        name="Cable Woodchop",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.OBLIQUES],
        secondary_muscles=[Muscle.ABS],
        description="""
    The cable woodchop is a rotational compound movement targeting the obliques and abs, promoting core strength and stability.""",
    ),
    "Cable Wrist Curl": ExerciseData(
        name="Cable Wrist Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.FOREARMS],
        description="""
    The cable wrist curl isolates the forearms, improving grip strength and wrist flexibility.""",
    ),
    "Calf Press In Leg Press": ExerciseData(
        name="Calf Press In Leg Press",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.CALVES],
        description="""
    The calf press in the leg press machine isolates the calves, promoting strength and endurance in the lower legs.""",
    ),
    "Chinup": ExerciseData(
        name="Chinup",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS],
        description="""
    The chinup is a bodyweight compound movement that primarily targets the lats, with secondary engagement of the biceps.""",
    ),
    "Clean and Jerk": ExerciseData(
        name="Clean and Jerk",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES, Muscle.SHOULDERS, Muscle.TRAPS],
        description="""
    The clean and jerk is a complex full-body movement that primarily targets the quads, while engaging the glutes, shoulders, and traps for power and stability.""",
    ),
    "Close-Grip Barbell Bench Press": ExerciseData(
        name="Close-Grip Barbell Bench Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.TRICEPS],
        secondary_muscles=[Muscle.CHEST],
        description="""
    The close-grip barbell bench press focuses on the triceps, with secondary engagement of the chest, promoting upper body strength.""",
    ),
    "Close-Grip Machine Lat Pull-Down": ExerciseData(
        name="Close-Grip Machine Lat Pull-Down",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS],
        description="""
    The close-grip machine lat pull-down targets the lats with a close grip, helping to improve upper body pulling strength and muscle development.""",
    ),
    "Close-Grip Pushup": ExerciseData(
        name="Close-Grip Pushup",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.TRICEPS],
        secondary_muscles=[Muscle.CHEST],
        description="""
    The close-grip pushup emphasizes the triceps while also engaging the chest, offering a bodyweight option for upper body strength development.""",
    ),
    "Cossack Squat": ExerciseData(
        name="Cossack Squat",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES],
        description="""
    The Cossack squat is a unilateral exercise that targets the quads and glutes, improving balance, flexibility, and lower body strength.""",
    ),
    "Cross-Body Lat Pull-Around": ExerciseData(
        name="Cross-Body Lat Pull-Around",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        description="""
    The cross-body lat pull-around is an isolation movement that focuses on the lats, improving strength and definition.""",
    ),
    "Decline Pushup": ExerciseData(
        name="Decline Pushup",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.SHOULDERS, Muscle.TRICEPS],
        description="""
    The decline pushup targets the upper chest and shoulders while also engaging the triceps, offering a challenging variation of the pushup.""",
    ),
    "Diamond Pushup": ExerciseData(
        name="Diamond Pushup",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.TRICEPS],
        secondary_muscles=[Muscle.CHEST],
        description="""
    The diamond pushup primarily targets the triceps while also activating the chest, offering an advanced variation of the traditional pushup.""",
    ),
    "Dip": ExerciseData(
        name="Dip",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.TRICEPS],
        secondary_muscles=[Muscle.CHEST, Muscle.SHOULDERS],
        description="""
    The dip is a bodyweight exercise that focuses on the triceps, chest, and shoulders, improving upper body pushing strength.""",
    ),
    "Dumbbell Bench Press": ExerciseData(
        name="Dumbbell Bench Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.SHOULDERS, Muscle.TRICEPS],
        description="""
    The dumbbell bench press targets the chest, shoulders, and triceps, promoting upper body strength and stability through a full range of motion.""",
    ),
    "Dumbbell Calf Raise": ExerciseData(
        name="Dumbbell Calf Raise",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.CALVES],
        description="""
    The dumbbell calf raise is an isolation exercise that strengthens the calves, enhancing lower leg endurance and stability.""",
    ),
    "Dumbbell Concentration Curl": ExerciseData(
        name="Dumbbell Concentration Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.BICEPS],
        description="""
    The dumbbell concentration curl isolates the biceps, improving arm strength and muscle definition with focused movement.""",
    ),
    "Dumbbell Curl": ExerciseData(
        name="Dumbbell Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.BICEPS],
        description="""
    The dumbbell curl is an isolation exercise that primarily targets the biceps, with secondary engagement of the forearms.
    This movement helps improve arm strength, muscle definition, and symmetry between both arms.""",
    ),
    "Dumbbell Fly": ExerciseData(
        name="Dumbbell Fly",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.CHEST],
        description="""
    The dumbbell fly is an isolation exercise that primarily targets the chest muscles, with secondary engagement of the shoulders.
    This movement enhances muscle definition and flexibility while promoting a greater range of motion in the chest during pressing movements.""",
    ),
    "Dumbbell Front Raise": ExerciseData(
        name="Dumbbell Front Raise",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.SHOULDERS],
        description="""
    The dumbbell front raise is an isolation exercise focusing on the anterior deltoids, with secondary involvement of the upper chest.
    This movement helps improve shoulder strength, stability, and muscle definition in the front of the shoulders.""",
    ),
    "Dumbbell Hammer Curl": ExerciseData(
        name="Dumbbell Hammer Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.BICEPS],
        description="""
    The dumbbell hammer curl is an isolation exercise that targets the brachialis and biceps, with secondary involvement of the forearms.
    This movement builds arm strength and enhances grip endurance while promoting balanced muscle development in both arms.""",
    ),
    "Dumbbell Kickback": ExerciseData(
        name="Dumbbell Kickback",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    The dumbbell kickback is an isolation exercise that primarily targets the triceps, with secondary engagement of the shoulders.
    This movement is effective for developing upper arm strength and definition, contributing to overall arm aesthetics.""",
    ),
    "Dumbbell Lat Pullover": ExerciseData(
        name="Dumbbell Lat Pullover",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.CHEST],
        description="""
    The dumbbell lat pullover is a compound exercise that primarily targets the latissimus dorsi, with secondary involvement of the chest and triceps.
    This movement enhances upper body strength and flexibility, promoting better posture and shoulder stability.""",
    ),
    "Dumbbell Lunge": ExerciseData(
        name="Dumbbell Lunge",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.QUADS, Muscle.GLUTES],
        description="""
    The dumbbell lunge is a compound exercise that targets the quads and glutes, with secondary engagement of the hamstrings and calves.
    This movement improves lower body strength, balance, and coordination while also enhancing functional fitness for everyday activities.""",
    ),
    "Dumbbell Preacher Curl": ExerciseData(
        name="Dumbbell Preacher Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.BICEPS],
        description="""
    The dumbbell preacher curl is an isolation exercise that primarily targets the biceps, effectively preventing cheating during the movement.
    This exercise promotes maximum muscle engagement for building arm strength and definition.""",
    ),
    "Dumbbell Preacher Curl (with Hammer Grip)": ExerciseData(
        name="Dumbbell Preacher Curl (with Hammer Grip)",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.BICEPS],
        is_variation_of="Dumbbell Preacher Curl",
        description="""
    The dumbbell preacher curl with hammer grip targets the biceps and brachialis while reducing wrist strain.
    This variation helps improve arm strength and muscle definition with an emphasis on balanced development in the arms.""",
    ),
    "Dumbbell Romanian Deadlift": ExerciseData(
        name="Dumbbell Romanian Deadlift",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.GLUTES, Muscle.HAMSTRINGS],
        description="""
    The dumbbell Romanian deadlift is a compound exercise that primarily targets the glutes and hamstrings, with secondary involvement of the lower back.
    This movement enhances posterior chain strength, improves flexibility, and supports overall athletic performance.""",
    ),
    "Dumbbell Shoulder Press": ExerciseData(
        name="Dumbbell Shoulder Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        description="""
    The dumbbell shoulder press is a compound exercise that targets the shoulders and triceps, with secondary engagement of the upper chest.
    This movement builds upper body strength, stability, and muscle coordination, contributing to improved performance in various pressing activities.""",
    ),
    "Dumbbell Shoulder Press (Seated)": ExerciseData(
        name="Dumbbell Shoulder Press (Seated)",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        is_variation_of="Dumbbell Shoulder Press",
        description="""
    The seated dumbbell shoulder press focuses on the shoulders and triceps while providing greater stability during the movement.
    This variation enhances muscle activation in the shoulders, allowing for improved strength development and upper body control.""",
    ),
    "Dumbbell Shrug": ExerciseData(
        name="Dumbbell Shrug",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.TRAPS],
        description="""
    The dumbbell shrug is an isolation exercise that primarily targets the trapezius muscles.
    This movement strengthens the upper traps, improving posture and enhancing the aesthetic appearance of the upper back and neck.""",
    ),
    "Dumbbell Side Bend": ExerciseData(
        name="Dumbbell Side Bend",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.OBLIQUES],
        description="""
    The dumbbell side bend is an isolation exercise that primarily targets the oblique muscles along the sides of the abdomen.
    This movement helps improve core stability, lateral strength, and muscle definition in the waist area.""",
    ),
    "Dumbbell Side Raise": ExerciseData(
        name="Dumbbell Side Raise",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.SHOULDERS],
        description="""
    The dumbbell side raise is an isolation exercise that targets the lateral deltoids, contributing to shoulder width and definition.
    This movement enhances shoulder strength, stability, and overall upper body aesthetics.""",
    ),
    "Dumbbell Triceps Extension": ExerciseData(
        name="Dumbbell Triceps Extension",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    The dumbbell triceps extension is an isolation exercise focusing on the triceps muscles.
    This movement helps improve arm strength and definition, enhancing performance in pressing movements and overall upper arm aesthetics.""",
    ),
    "Dumbbell Wrist Curl": ExerciseData(
        name="Dumbbell Wrist Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.FOREARMS],
        description="""
    The dumbbell wrist curl is an isolation exercise that primarily targets the forearm muscles, particularly the flexors.
    This movement enhances grip strength and wrist stability, supporting better performance in various upper body exercises.""",
    ),
    "Ez-Bar Curl": ExerciseData(
        name="Ez-Bar Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.BICEPS],
        description="""
    The Ez-bar curl is an isolation exercise that primarily targets the biceps. The curved bar allows for a more natural grip, reducing strain on the wrists.""",
    ),
    "Ez-Bar Preacher Curl": ExerciseData(
        name="Ez-Bar Preacher Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.BICEPS],
        is_variation_of="Ez-Bar Curl",
        description="""
    The Ez-bar preacher curl is a variation of the Ez-bar curl performed on a preacher bench, which helps to isolate the biceps by eliminating momentum and increasing the range of motion.""",
    ),
    "Farmers Walk": ExerciseData(
        name="Farmers Walk",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,  # or any weight that can be carried
        prime_muscles=[Muscle.FOREARMS],
        secondary_muscles=[Muscle.TRAPS, Muscle.ABS],
        description="""
    The farmer's walk is a full-body exercise that enhances grip strength and core stability. It involves carrying heavy weights in each hand for a set distance.""",
    ),
    "Glute Drive": ExerciseData(
        name="Glute Drive",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.GLUTES],
        secondary_muscles=[Muscle.HAMSTRINGS],
        description="""
    The glute drive is an isolation exercise that targets the glutes with minimal involvement from the lower back or other muscles, improving hip strength and power.""",
    ),
    "Glute Ham Raise": ExerciseData(
        name="Glute Ham Raise",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.HAMSTRINGS],
        secondary_muscles=[Muscle.GLUTES],
        description="""
    The glute ham raise strengthens the hamstrings and glutes through a full range of motion, improving posterior chain strength and stability.""",
    ),
    "Goblet Squat": ExerciseData(
        name="Goblet Squat",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES, Muscle.ABS],
        description="""
    The goblet squat is a squat variation where the weight is held in front of the chest, emphasizing core stability and leg strength while reducing lower back strain.""",
    ),
    "Hanging Leg Raise": ExerciseData(
        name="Hanging Leg Raise",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.ABS],
        secondary_muscles=[Muscle.HIP_FLEXORS],
        description="""
    The hanging leg raise is an effective core exercise that targets the lower abdominal muscles and hip flexors. It also improves grip strength and overall stability.""",
    ),
    "Hexbar Deadlift": ExerciseData(
        name="Hexbar Deadlift",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.HEX_BAR,
        prime_muscles=[Muscle.GLUTES, Muscle.QUADS],
        secondary_muscles=[Muscle.HAMSTRINGS, Muscle.LOWER_BACK],
        is_variation_of="Barbell Deadlift",
        description="""
    The hexbar deadlift is a variation of the barbell deadlift that allows for a more upright posture and reduced stress on the lower back, while still targeting the glutes, quads, and hamstrings.""",
    ),
    "Incline Barbell Bench Press": ExerciseData(
        name="Incline Barbell Bench Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.TRICEPS],
        tertiary_muscles=[Muscle.SHOULDERS],
        is_variation_of="Barbell Bench Press",
        description="""
    The incline barbell bench press is a variation of the traditional bench press that emphasizes the upper chest, with additional involvement from the shoulders and triceps.""",
    ),
    "Incline Cable Triceps Extension": ExerciseData(
        name="Incline Cable Triceps Extension",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    The incline cable triceps extension targets the triceps with the cable set at an incline. This variation increases the range of motion and engages the triceps throughout the movement.""",
    ),
    "Incline Dumbbell Bench Press": ExerciseData(
        name="Incline Dumbbell Bench Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.SHOULDERS, Muscle.TRICEPS],
        is_variation_of="Dumbbell Bench Press",
        description="""
    The incline dumbbell bench press is a variation of the dumbbell bench press that emphasizes the upper chest and shoulders by positioning the bench at an incline.""",
    ),
    "Incline Dumbbell Curl": ExerciseData(
        name="Incline Dumbbell Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.BICEPS],
        is_variation_of="Dumbbell Curl",
        description="""
    The incline dumbbell curl is a variation of the dumbbell curl performed on an incline bench, which helps to isolate the biceps by increasing the stretch and range of motion.""",
    ),
    "Incline Dumbbell Fly": ExerciseData(
        name="Incline Dumbbell Fly",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.CHEST],
        is_variation_of="Dumbbell Fly",
        description="""
    The incline dumbbell fly is a variation of the dumbbell fly that targets the upper chest, placing more emphasis on the upper pectoral muscles due to the inclined bench position.""",
    ),
    "Incline Sit-Up": ExerciseData(
        name="Incline Sit-Up",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.ABS],
        is_variation_of="Sit-Up",
        description="""
    The incline sit-up is a variation of the traditional sit-up performed on an inclined bench, which increases the intensity by adding resistance due to gravity.""",
    ),
    "Kettlebell Squat": ExerciseData(
        name="Kettlebell Squat",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.KETTLEBELL,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES, Muscle.ABS],
        description="""
    The kettlebell squat is a compound lower body exercise that targets the quadriceps, glutes, and core while enhancing balance and coordination.""",
    ),
    "Larsen Press": ExerciseData(
        name="Larsen Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.TRICEPS, Muscle.SHOULDERS],
        description="""
    The Larsen press is a variation of the bench press that eliminates leg drive by keeping the feet off the ground, increasing chest activation and upper body control.""",
    ),
    "Lying Barbell Row": ExerciseData(
        name="Lying Barbell Row",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS, Muscle.FOREARMS],
        is_variation_of="Barbell Row",
        description="""
    The lying barbell row is a variation of the barbell row performed while lying flat on a bench, which isolates the back muscles by removing any leg involvement.""",
    ),
    "Lying Barbell Skull Crusher": ExerciseData(
        name="Lying Barbell Skull Crusher",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    The lying barbell skull crusher is an isolation exercise that targets the triceps by extending the arms while lying on a bench, providing an intense contraction of the triceps muscles.""",
    ),
    "Lying Dumbbell Skull Crusher": ExerciseData(
        name="Lying Dumbbell Skull Crusher",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    The lying dumbbell skull crusher is an isolation exercise that targets the triceps, similar to the barbell version but allowing for more freedom of movement and wrist rotation.""",
    ),
    "Machine Ab Crunch": ExerciseData(
        name="Machine Ab Crunch",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.ABS],
        description="""
    The machine ab crunch isolates the abdominal muscles by providing controlled resistance, promoting core strength and muscle definition.""",
    ),
    "Machine Biceps Curl": ExerciseData(
        name="Machine Biceps Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.BICEPS],
        description="""
    The machine biceps curl is an isolation exercise that targets the biceps by providing consistent resistance throughout the movement, enhancing strength and muscle growth.""",
    ),
    "Machine Calf Raise": ExerciseData(
        name="Machine Calf Raise",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.CALVES],
        description="""
    The machine calf raise isolates the calf muscles, providing resistance for strength and endurance, ideal for improving lower leg muscle definition and mobility.""",
    ),
    "Machine Crunch": ExerciseData(
        name="Machine Crunch",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.ABS],
        description="""
    The machine crunch isolates the abdominal muscles, allowing for controlled movement to strengthen and build core stability.""",
    ),
    "Machine Dip": ExerciseData(
        name="Machine Dip",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.TRICEPS],
        secondary_muscles=[Muscle.CHEST, Muscle.SHOULDERS],
        description="""
    The machine dip is a compound exercise that primarily targets the triceps, with secondary activation of the chest and shoulders, providing guided movement for controlled muscle engagement.""",
    ),
    "Machine Fly": ExerciseData(
        name="Machine Fly",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.SHOULDERS],
        description="""
    The machine fly isolates the chest muscles, allowing for a controlled movement that builds pectoral strength and muscle definition.""",
    ),
    "Machine Hack Squat": ExerciseData(
        name="Machine Hack Squat",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES],
        description="""
    The machine hack squat is a compound leg exercise that primarily targets the quads, providing controlled resistance for safe and effective lower body development.""",
    ),
    "Machine Hyperextension": ExerciseData(
        name="Machine Hyperextension",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LOWER_BACK],
        secondary_muscles=[Muscle.GLUTES, Muscle.HAMSTRINGS],
        description="""
    The machine hyperextension targets the lower back while engaging the glutes and hamstrings, enhancing back strength and stability.""",
    ),
    "Machine Lat Pulldown": ExerciseData(
        name="Machine Lat Pulldown",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS, Muscle.SHOULDERS],
        description="""
    The machine lat pulldown is a compound exercise that targets the lats while also engaging the biceps and shoulders for upper body strength.""",
    ),
    "Machine Lateral Raise": ExerciseData(
        name="Machine Lateral Raise",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.SHOULDERS],
        description="""
    The machine lateral raise isolates the shoulders, specifically targeting the deltoids, helping to build shoulder strength and definition.""",
    ),
    "Machine Leg Curl": ExerciseData(
        name="Machine Leg Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.HAMSTRINGS],
        description="""
    The machine leg curl isolates the hamstrings, providing resistance to enhance leg strength and muscle tone.""",
    ),
    "Machine Leg Extension": ExerciseData(
        name="Machine Leg Extension",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.QUADS],
        description="""
    The machine leg extension isolates the quadriceps, providing controlled resistance to build leg strength and muscle definition.""",
    ),
    "Machine Leg Press": ExerciseData(
        name="Machine Leg Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES, Muscle.HAMSTRINGS],
        description="""
    The machine leg press is a compound exercise that primarily targets the quads, with secondary activation of the glutes and hamstrings, promoting lower body strength.""",
    ),
    "Machine Lying Leg Curl": ExerciseData(
        name="Machine Lying Leg Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.HAMSTRINGS],
        description="""
    The machine lying leg curl isolates the hamstrings, promoting strength and muscle growth in the back of the legs.""",
    ),
    "Machine Pullover": ExerciseData(
        name="Machine Pullover",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.CHEST, Muscle.SHOULDERS],
        description="""
    The machine pullover is a compound movement that primarily targets the lats while engaging the chest and shoulders for upper body development.""",
    ),
    "Machine Push-Down": ExerciseData(
        name="Machine Push-Down",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    The machine push-down isolates the triceps, providing controlled resistance to strengthen and build arm muscle definition.""",
    ),
    "Machine Row": ExerciseData(
        name="Machine Row",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS, Muscle.REAR_DELTS],
        description="""
    The machine row is a compound exercise that targets the lats, while also engaging the biceps and rear deltoids, promoting back strength and muscle growth.""",
    ),
    "Machine Shoulder Press": ExerciseData(
        name="Machine Shoulder Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        description="""
    The machine shoulder press is a compound exercise that targets the shoulders and triceps, offering guided resistance for building upper body strength.""",
    ),
    "Machine Single-Leg Extension": ExerciseData(
        name="Machine Single-Leg Extension",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.QUADS],
        description="""
    The machine single-leg extension isolates one quadricep at a time, allowing for better focus on strength and muscle balance.""",
    ),
    "Machine Thigh Abduction (Out)": ExerciseData(
        name="Machine Thigh Abduction (Out)",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.HIP_ABDUCTORS],
        description="""
    The machine thigh abduction targets the hip abductors, improving strength and mobility in the outer thigh and hip area.""",
    ),
    "Machine Thigh Adduction (In)": ExerciseData(
        name="Machine Thigh Adduction (In)",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.HIP_ADDUCTORS],
        description="""
    The machine thigh adduction targets the inner thigh muscles, helping to strengthen the hip adductors for improved leg stability and coordination.""",
    ),
    "Machine V-Bar Lat Pulldown": ExerciseData(
        name="Machine V-Bar Lat Pulldown",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS],
        is_variation_of="Machine Lat Pulldown",
        description="""
    The machine V-bar lat pulldown is a variation of the lat pulldown that uses a V-bar to emphasize the lower lats and biceps by altering the hand positioning.""",
    ),
    "One-Arm Lat Pull-Down": ExerciseData(
        name="One-Arm Lat Pull-Down",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS],
        description="""
    The one-arm lat pull-down isolates one lat muscle at a time, promoting strength and muscle balance while enhancing upper body development.""",
    ),
    "Paused Barbell Squat": ExerciseData(
        name="Paused Barbell Squat",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES, Muscle.HAMSTRINGS],
        is_variation_of="Barbell Squat",
        description="""
    The paused barbell squat is a variation of the traditional squat where the lifter pauses at the bottom position, increasing time under tension and enhancing muscle activation.""",
    ),
    "Pistol Squat": ExerciseData(
        name="Pistol Squat",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES, Muscle.HAMSTRINGS],
        description="""
    The pistol squat is a unilateral bodyweight exercise that challenges balance, strength, and flexibility, primarily targeting the quads while engaging other lower body muscles.""",
    ),
    "Plank": ExerciseData(
        name="Plank",
        force=Force.ISOMETRIC,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.ABS],
        secondary_muscles=[Muscle.LOWER_BACK, Muscle.SHOULDERS],
        description="""
    The plank is an isometric exercise that engages the core and stabilizes the entire body, promoting strength, endurance, and balance.""",
    ),
    "Press Around": ExerciseData(
        name="Press Around",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRICEPS],
        description="""
    The press around is a compound exercise that targets the shoulders while engaging the triceps, providing functional strength and stability for overhead movements.""",
    ),
    "Pullup": ExerciseData(
        name="Pullup",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS, Muscle.REAR_DELTS],
        description="""
    The pull-up is a compound bodyweight exercise that primarily targets the lats while also engaging the biceps and rear deltoids, enhancing upper body strength and muscle definition.""",
    ),
    "Push-Down": ExerciseData(
        name="Push-Down",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    The push-down is an isolation exercise that targets the triceps, providing controlled resistance to build strength and muscle definition in the arms.""",
    ),
    "Pushup": ExerciseData(
        name="Pushup",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.TRICEPS, Muscle.SHOULDERS],
        description="""
    The push-up is a compound bodyweight exercise that primarily targets the chest, while also engaging the triceps and shoulders, promoting upper body strength and endurance.""",
    ),
    "Razor Curl": ExerciseData(
        name="Razor Curl",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.BICEPS],
        description="""
    The razor curl is an isolation exercise focusing on the biceps, providing a unique angle for muscle engagement and promoting strength and growth.""",
    ),
    "Reverse Machine Fly": ExerciseData(
        name="Reverse Machine Fly",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.REAR_DELTS],
        secondary_muscles=[Muscle.TRAPS],
        description="""
    The reverse machine fly isolates the rear deltoids and upper back muscles, enhancing strength and definition in the posterior shoulder region.""",
    ),
    "Rowing Concept 2": ExerciseData(
        name="Rowing Concept 2",
        force=Force.PULL,
        mechanic=Mechanic.AEROBIC,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.HAMSTRINGS, Muscle.GLUTES, Muscle.BICEPS],
        description="""
    The Rowing Concept 2 is a full-body compound exercise that engages multiple muscle groups, primarily targeting the back and legs, providing cardiovascular and strength training benefits.""",
    ),
    "Running on Treadmill": ExerciseData(
        name="Running on Treadmill",
        force=Force.ENDURANCE,
        mechanic=Mechanic.AEROBIC,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.CALVES],
        secondary_muscles=[Muscle.QUADS, Muscle.GLUTES, Muscle.HAMSTRINGS],
        description="""
    Running on a treadmill is a cardiovascular exercise that primarily targets the leg muscles while also engaging the core for stability and balance, promoting overall fitness and endurance.""",
    ),
    "Russian Twist": ExerciseData(
        name="Russian Twist",
        force=Force.ISOMETRIC,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.ABS],
        secondary_muscles=[Muscle.OBLIQUES],
        description="""
    The Russian twist is an isolation exercise that targets the core and obliques, enhancing rotational strength and stability for improved athletic performance.""",
    ),
    "Seated Cable Row": ExerciseData(
        name="Seated Cable Row",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS, Muscle.MIDDLE_BACK],
        description="""
    The seated cable row is a compound exercise that targets the lats and mid-back, while also engaging the biceps for a full upper-body workout.""",
    ),
    "Seated Dumbbell One-Arm Triceps Extension": ExerciseData(
        name="Seated Dumbbell One-Arm Triceps Extension",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    This triceps extension variation allows for unilateral training, isolating each arm to promote balance and strength in the triceps.""",
    ),
    "Seated Machine Bench Press": ExerciseData(
        name="Seated Machine Bench Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.SHOULDERS, Muscle.TRICEPS],
        description="""
    The seated machine bench press focuses on the chest muscles while providing stability and control, making it a great option for strength training in a seated position.""",
    ),
    "Side Plank": ExerciseData(
        name="Side Plank",
        force=Force.ISOMETRIC,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.OBLIQUES],
        secondary_muscles=[Muscle.ABS, Muscle.SHOULDERS],
        is_variation_of="Plank",
        description="""
    The side plank is an isometric exercise that strengthens the obliques and core, while also engaging the shoulders and promoting balance and stability.""",
    ),
    "Single-Arm Cable Pushdown": ExerciseData(
        name="Single-Arm Cable Pushdown",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    This isolation exercise targets the triceps by allowing one arm to work independently, helping to build muscle symmetry and strength.""",
    ),
    "Single-Arm Cable Row": ExerciseData(
        name="Single-Arm Cable Row",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS, Muscle.MIDDLE_BACK],
        description="""
    The single-arm cable row isolates each side of the back and lats, promoting muscular balance and unilateral strength development.""",
    ),
    "Single-Arm Dumbbell Row on Bench": ExerciseData(
        name="Single-Arm Dumbbell Row on Bench",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS, Muscle.REAR_DELTS],
        description="""
    This exercise focuses on the lats and upper back while also engaging the biceps and rear deltoids, making it ideal for developing back strength with isolated control.""",
    ),
    "Single-Arm Dumbbell Triceps Extension": ExerciseData(
        name="Single-Arm Dumbbell Triceps Extension",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    This unilateral exercise isolates the triceps to promote muscle balance and strength in each arm individually.""",
    ),
    "Single-Arm Kettlebell Clean and Jerk": ExerciseData(
        name="Single-Arm Kettlebell Clean and Jerk",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.KETTLEBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.GLUTES, Muscle.ABS],
        description="""
    The single-arm kettlebell clean and jerk is a dynamic, full-body exercise that strengthens the shoulders and engages the core and glutes for explosive power.""",
    ),
    "Single-Arm Machine Lat Pulldown": ExerciseData(
        name="Single-Arm Machine Lat Pulldown",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS],
        description="""
    This variation of the lat pulldown targets one lat at a time, ensuring balanced development of the upper back and biceps.""",
    ),
    "Single-Arm Machine Row": ExerciseData(
        name="Single-Arm Machine Row",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.MIDDLE_BACK, Muscle.BICEPS],
        description="""
    The single-arm machine row targets the lats and mid-back while allowing each side to work independently, helping to correct muscle imbalances.""",
    ),
    "Single-Leg Curl in Machine": ExerciseData(
        name="Single-Leg Curl in Machine",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.HAMSTRINGS],
        description="""
    This exercise isolates the hamstrings, working one leg at a time to build muscle symmetry and strength.""",
    ),
    "Single-Leg Machine Calf Press": ExerciseData(
        name="Single-Leg Machine Calf Press",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.CALVES],
        description="""
    The single-leg machine calf press targets the calf muscles, promoting unilateral strength and balance in the lower legs.""",
    ),
    "Single-Leg Press": ExerciseData(
        name="Single-Leg Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES, Muscle.HAMSTRINGS],
        description="""
    The single-leg press focuses on developing strength in the quadriceps and glutes while working one leg at a time, helping to address muscle imbalances.""",
    ),
    "Situp": ExerciseData(
        name="Situp",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.ABS],
        description="""
    The situp is a classic bodyweight exercise that targets the abdominal muscles, promoting core strength and endurance.""",
    ),
    "Smith Machine Calf Raise": ExerciseData(
        name="Smith Machine Calf Raise",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.CALVES],
        description="""
    This exercise isolates the calf muscles, allowing for controlled movement using the Smith Machine for stability and safety.""",
    ),
    "Smith Machine Incline Bench Press": ExerciseData(
        name="Smith Machine Incline Bench Press",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.CHEST],
        secondary_muscles=[Muscle.SHOULDERS, Muscle.TRICEPS],
        is_variation_of="Bench Press",
        description="""
    This incline bench press variation performed on the Smith Machine targets the upper chest while providing additional stability.""",
    ),
    "Smith Machine Shrug": ExerciseData(
        name="Smith Machine Shrug",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.TRAPS],
        description="""
    The Smith Machine shrug isolates the traps, helping to build strength and muscle mass in the upper back.""",
    ),
    "Standing Cable Lift": ExerciseData(
        name="Standing Cable Lift",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.ABS],
        secondary_muscles=[Muscle.OBLIQUES],
        description="""
    This exercise engages the core and obliques, providing rotational strength and stability through a controlled cable movement.""",
    ),
    "Standing Dumbbell One-Arm Triceps Extension": ExerciseData(
        name="Standing Dumbbell One-Arm Triceps Extension",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    This unilateral exercise isolates the triceps, helping to build strength and muscle symmetry between the arms.""",
    ),
    "Standing Dumbbell One-Leg Calf Raise": ExerciseData(
        name="Standing Dumbbell One-Leg Calf Raise",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.DUMBBELL,
        prime_muscles=[Muscle.CALVES],
        description="""
    The standing one-leg calf raise focuses on the calves, promoting balance and strength in the lower legs with added dumbbell resistance.""",
    ),
    "Standing High Cable One-Arm Triceps Extension": ExerciseData(
        name="Standing High Cable One-Arm Triceps Extension",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    This exercise isolates the triceps, allowing for a full range of motion and controlled resistance using a high cable setup.""",
    ),
    "Standing Low Cable Triceps Extension": ExerciseData(
        name="Standing Low Cable Triceps Extension",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    The standing low cable triceps extension provides targeted triceps training with the use of a low pulley cable for controlled resistance.""",
    ),
    "Straight-Leg Barbell Deadlift": ExerciseData(
        name="Straight-Leg Barbell Deadlift",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.HAMSTRINGS],
        secondary_muscles=[Muscle.GLUTES, Muscle.LOWER_BACK],
        is_variation_of="Barbell Deadlift",
        description="""
    The straight-leg deadlift variation places more emphasis on the hamstrings and lower back, while still engaging the glutes.""",
    ),
    "T-Bar Row": ExerciseData(
        name="T-Bar Row",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.MIDDLE_BACK, Muscle.BICEPS],
        description="""
    The T-Bar row is a compound movement that strengthens the lats, middle back, and biceps, providing a complete upper-body workout.""",
    ),
    "Tibialis Raise": ExerciseData(
        name="Tibialis Raise",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.OTHER,
        prime_muscles=[Muscle.TIBIALIS],
        description="""
    The tibialis raise isolates the front of the lower leg, helping to strengthen the tibialis muscles and improve overall leg stability.""",
    ),
    "Torso Rotation Machine": ExerciseData(
        name="Torso Rotation Machine",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.OBLIQUES],
        secondary_muscles=[Muscle.ABS],
        description="""
    This exercise engages the obliques and core through controlled rotational movement, helping to improve core strength and flexibility.""",
    ),
    "Trap Bar Shrug": ExerciseData(
        name="Trap Bar Shrug",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.TRAPS],
        description="""
    The trap bar shrug isolates the trapezius muscles, providing a great way to develop upper back strength and size.""",
    ),
    "Triceps Machine": ExerciseData(
        name="Triceps Machine",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.TRICEPS],
        description="""
    The triceps machine allows for targeted triceps training with controlled resistance, promoting muscle growth and strength.""",
    ),
    "Upright Barbell Row": ExerciseData(
        name="Upright Barbell Row",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BARBELL,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRAPS],
        is_variation_of="Barbell Row",
        description="""
    The upright barbell row emphasizes the shoulders and traps while providing a variation of the traditional barbell row.""",
    ),
    "Upright Cable Row": ExerciseData(
        name="Upright Cable Row",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.SHOULDERS],
        secondary_muscles=[Muscle.TRAPS],
        is_variation_of="Cable Row",
        description="""
    This exercise targets the shoulders and traps while using a cable for controlled tension throughout the movement.""",
    ),
    "Walking Lunge": ExerciseData(
        name="Walking Lunge",
        force=Force.PUSH,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.QUADS],
        secondary_muscles=[Muscle.GLUTES, Muscle.HAMSTRINGS],
        description="""
    The walking lunge works the quads, glutes, and hamstrings, making it a dynamic lower-body exercise that also engages balance and coordination.""",
    ),
    "Weighted Chinup": ExerciseData(
        name="Weighted Chinup",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS, Muscle.FOREARMS],
        is_variation_of="Chinup",
        description="""
    The weighted chinup adds resistance to the traditional chinup, intensifying the workout for the lats, biceps, and forearms.""",
    ),
    "Weighted Crunch": ExerciseData(
        name="Weighted Crunch",
        force=Force.PUSH,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.ABS],
        is_variation_of="Crunch",
        description="""
    This variation of the crunch incorporates additional weight to increase resistance and further target the abdominal muscles.""",
    ),
    "Weighted Pullup": ExerciseData(
        name="Weighted Pullup",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.BODY_WEIGHT,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS, Muscle.FOREARMS],
        is_variation_of="Pullup",
        description="""
    The weighted pullup increases the difficulty of the traditional pullup by adding resistance, further targeting the lats, biceps, and forearms.""",
    ),
    "Wide-Grip Machine Lat Pulldown": ExerciseData(
        name="Wide-Grip Machine Lat Pulldown",
        force=Force.PULL,
        mechanic=Mechanic.COMPOUND,
        equipment=Equipment.MACHINE,
        prime_muscles=[Muscle.LATS],
        secondary_muscles=[Muscle.BICEPS, Muscle.REAR_DELTS],
        description="""
    This wide-grip variation of the lat pulldown targets the lats, with an increased focus on the upper back and rear deltoids.""",
    ),
    "Wrist Curl (Roller)": ExerciseData(
        name="Wrist Curl (Roller)",
        force=Force.PULL,
        mechanic=Mechanic.ISOLATION,
        equipment=Equipment.OTHER,
        prime_muscles=[Muscle.FOREARMS],
        description="""
    The wrist curl roller strengthens the forearms, specifically targeting the wrist flexors with controlled rolling movements.""",
    ),
}


def get_exercise(name: str) -> Optional[ExerciseData]:
    """Retrieve an exercise by name from the compendium."""
    return exercise_compendium.get(name)


def get_exercises_by_muscle(muscle: Muscle) -> List[ExerciseData]:
    """Retrieve all exercises that target a specific muscle."""
    return [
        exercise
        for exercise in exercise_compendium.values()
        if muscle in exercise.prime_muscles
        or muscle in exercise.secondary_muscles
        or muscle in exercise.tertiary_muscles
    ]


def get_exercises_by_equipment(equipment: Equipment) -> List[ExerciseData]:
    """Retrieve all exercises that use a specific equipment."""
    return [exercise for exercise in exercise_compendium.values() if exercise.equipment == equipment]
