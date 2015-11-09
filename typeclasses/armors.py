"""
Armor typeclasses
"""

from typeclasses.items import Equippable

class Armor(Equippable):
    """
    Typeclass for armor objects.

    Attributes:
        toughness (int): primary defensive stat
    """
    toughness = 0

    def at_object_creation(self):
        super(Armor, self).at_object_creation()
        self.db.toughness = self.toughness


# typeclasses for prototyping


class Headwear(Armor):
    """Typeclass for armor prototypes worn on the head."""
    slots = ['head']


class Breastplate(Armor):
    """Typeclass for sleeveless armor prototypes."""
    slots = ['torso']


class SleevedShirt(Armor):
    """Typeclass for full upper body armor prototypes."""
    slots = ['torso', 'arms']
    multi_slot = True


class Armband(Armor):
    """Typeclass for arm band/bracelet prototypes."""
    slots = ['left wrist', 'right wrist']
    multi_slot = False


class Gloves(Armor):
    """Typeclass for armor prototypes for the hands."""
    slots = ['hands']


class Gauntlets(Gloves):
    """Typeclass for long glove armor prototypes."""
    slots = ['hands', 'left wrist', 'right wrist']
    multi_slot = True


class Belt(Armor):
    """Typeclass for armor prototypes worn in belt slots."""
    slots = ['belt1', 'belt2']
    multi_slot = False


class Legwear(Armor):
    """Typeclass for armor prototypes worn on the legs."""
    slots = ['legs']


class Footwear(Armor):
    """Typeclass for armor prototypes worn on the feet."""
    slots = ['feet']


class Robes(Armor):
    """Typeclass for arcanist shroud prototypes."""
    slots = ['torso', 'arms', 'legs']
    multi_slot = True


class Shield(Armor):
    """Typeclass for shield prototypes."""
    slots = ['wield2', 'back']
    multi_slot = False