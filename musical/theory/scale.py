from .note import Note
import itertools

# TODO: Non-rooted scales? (just hold intervals and apply root later on)
# TODO: Probable scale identification (from a set of notes)

NAMED_SCALES = {
    "major": (2, 2, 1, 2, 2, 2, 1),
    "minor": (2, 1, 2, 2, 1, 2, 2),
    "melodicminor": (2, 1, 2, 2, 2, 2, 1),
    "harmonicminor": (2, 1, 2, 2, 1, 3, 1),
    "pentatonicmajor": (2, 2, 3, 2, 3),
    "bluesmajor": (3, 2, 1, 1, 2, 3),
    "pentatonicminor": (3, 2, 2, 3, 2),
    "bluesminor": (3, 2, 1, 1, 3, 2),
    "augmented": (3, 1, 3, 1, 3, 1),
    "diminished": (2, 1, 2, 1, 2, 1, 2, 1),
    "chromatic": (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
    "wholehalf": (2, 1, 2, 1, 2, 1, 2, 1),
    "halfwhole": (1, 2, 1, 2, 1, 2, 1, 2),
    "wholetone": (2, 2, 2, 2, 2, 2),
    "augmentedfifth": (2, 2, 1, 2, 1, 1, 2, 1),
    "japanese": (1, 4, 2, 1, 4),
    "oriental": (1, 3, 1, 1, 3, 1, 2),
    "ionian": (2, 2, 1, 2, 2, 2, 1),
    "dorian": (2, 1, 2, 2, 2, 1, 2),
    "phrygian": (1, 2, 2, 2, 1, 2, 2),
    "lydian": (2, 2, 2, 1, 2, 2, 1),
    "mixolydian": (2, 2, 1, 2, 2, 1, 2),
    "aeolian": (2, 1, 2, 2, 1, 2, 2),
    "locrian": (1, 2, 2, 1, 2, 2, 2),
}

# INVERTED_NAMED_SCALES = {v: k for k, v in NAMED_SCALES.items()}

INVERTED_NAMED_SCALES = {}

for k, v in NAMED_SCALES.items():
    if v in INVERTED_NAMED_SCALES:
        INVERTED_NAMED_SCALES[v].append(k)
    else:
        INVERTED_NAMED_SCALES[v] = [k]


class Scale:

    """Scale class manages rooted scales. Can be constructed by passing a root
    and either a list of intervals or a scale name (which is used to look up
    the intervals from NAMED_SCALES dict
    """

    def __init__(self, root, scale):
        self.root = root.at_octave(0)
        if isinstance(scale, str):
            intervals = Scale.intervals_from_name(scale)
        elif isinstance(scale, Scale):
            intervals = scale.intervals

        self.intervals = tuple(intervals)

    def __repr__(self):
        return "Scale(%s, %s)" % (self.root, self.intervals)

    def __str__(self):
        return " - ".join(self.get(x).note for x in range(len(self.intervals)))

    def __len__(self):
        return len(self.intervals)

    def __iter__(self):
        return iter(self.get(i) for i in range(len(self)))

    def __eq__(self, other):
        return all(
            (
                self.root.note == other.root.note,
                self.intervals == other.intervals,
            )
        )

    @property
    def scale_name(self):
        return INVERTED_NAMED_SCALES[self.intervals]

    def relative_scale(self):
        if self.scale_name[0] == "major":
            return Scale(self.root.transpose(-3), "minor")
        if self.scale_name[0] == "minor":
            return Scale(self.root.transpose(3), "major")

    @classmethod
    def intervals_from_name(self, name):
        """Return intervals for named scale"""
        global NAMED_SCALES
        name = name.lower()
        for text in ["scale", "mode", "-", " ", "_"]:
            name = name.replace(text, "")
        return NAMED_SCALES[name]

    def get(self, index):
        """Get note from scale, 0 is the root at octave 0"""
        intervals = self.intervals
        if index < 0:
            index, intervals = abs(index), reversed(self.intervals)
        intervals = itertools.cycle(self.intervals)
        note = self.root
        for i in range(index):
            note = note.transpose(next(intervals))
        return note

    def index(self, note):
        """Return index for note, if it exists in the scale"""
        intervals = itertools.cycle(self.intervals)
        index = 0
        x = self.root
        while x < note:
            x = x.transpose(next(intervals))
            index += 1
        if x == note:
            return index
        raise ValueError("%s not in %s" % (note, self))

    def transpose(self, note, interval):
        """Transpose note with scale by intervals, 1 = second, 2 = third..."""
        return self.get(self.index(note) + interval)
