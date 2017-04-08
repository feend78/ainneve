"""
Magic commands.
"""

from evennia import default_cmds, CmdSet

# cmdsets


class Tier0BlackCombatSpellsCmdSet(CmdSet):
    """Command set containing tier 0 black spells for combat."""
    key = 'black_t0com_cmdset'

    def at_cmdset_creation(self):
        self.add(CmdArcaneBolt())
        self.add(CmdItchify())


class Tier0WhiteCombatSpellsCmdSet(CmdSet):
    """Command set containing tier 0 white spells for combat."""
    key = 'white_t0com_cmdset'

    def at_cmdset_creation(self):
        self.add(CmdHeal())
        self.add(CmdStoneSkin())


class ItchingCmdSet(CmdSet):
    """Command set containing the "scratch" command."""
    key = 'itching_cmdset'

    def at_cmdset_creation(self):
        self.add(CmdScratch())


# commands


class CombatMagicCommand(default_cmds.MuxCommand):
    """Base command class for combat spells."""
    locks = 'cmd:in_combat()'


# black magic


class CmdArcaneBolt(CombatMagicCommand):
    """
    fire a bolt of arcane energy at an enemy

    Usage:
      arcane bolt <target>
      abolt <target>
      ab <target>

    Duration:
      instantaneous

    Attacks a target with concentrated arcane energy.

    Casting Arcane Bolt is a half-turn combat action.
    """
    key = 'arcane bolt'
    aliases = ['abolt', 'ab']
    help_category = 'half turn actions'

    def func(self):
        pass


class CmdItchify(CombatMagicCommand):
    """
    cause an enemy to become very itchy

    Usage:
      itchify <target>

    Duration:
      4 turns

    Target can spend a full-turn action scratching to
    cancel the effect of Itch.

    Casting Itchify is a full-turn combat action.
    """
    key = 'itchify'
    aliases = ['itch']
    help_category = 'full turn actions'

    def func(self):
        pass


class CmdScratch(CombatMagicCommand):
    """
    scratch that crazy-making itch

    Usage:
      scratch

    Scratch all the itchy places, restoring your concentration.

    This is a full-turn combat action.
    """
    key = 'scratch'
    aliases = ['scr']
    help_category = 'full turn actions'

    def func(self):
        pass


# white magic


class CmdHeal(CombatMagicCommand):
    """
    heal your self or another

    Usage:
      heal [<target>]

    Duration:
      instantaneous

    Heals a small amount of HP for caster or target.

    Casting Heal is a full-turn combat action
    """
    key = 'heal'
    aliases = ['he']
    help_category = 'full turn actions'

    def func(self):
        pass


class CmdStoneSkin(CombatMagicCommand):
    """
    harden your skin against attacks

    Usage:
      stone skin
      sskin
      ss

    Duration:
      3 turns

    Boosts your defenses for a short time.

    Casting Stone Skin is a full-turn combat action.
    """
    key = 'stone skin'
    aliases = ['sskin', 'ss']
    help_category = 'full turn actions'

    def func(self):
        pass
