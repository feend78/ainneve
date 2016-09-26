"""
Combat commands


"""

from evennia import default_cmds, CmdSet, create_script
from evennia.contrib.rpsystem import CmdEmote, CmdPose
from evennia.utils.evtable import EvTable
from commands.equip import CmdInventory

# cmdsets


class InitCombatCmdSet(CmdSet):
    """Command set containing combat starting commands"""
    key = 'combat_init_cmdset'
    priority = 1
    mergetype = 'Union'

    def at_cmdset_creation(self):
        self.add(CmdInitiateAttack())


class CombatBaseCmdSet(CmdSet):
    """Command set containing always-available commands"""
    key = 'combat_base_cmdset'
    priority = 10
    mergetype = 'Replace'
    no_exits = True

    def at_cmdset_creation(self):
        look = default_cmds.CmdLook()
        look.help_category = 'free instant actions'
        self.add(look)

        say = default_cmds.CmdSay()
        say.help_category = 'free instant actions'
        self.add(say)

        inv = CmdInventory()
        inv.help_category = 'free instant actions'
        self.add(inv)

        self.add(CmdEmote())
        self.add(CmdPose())


class CombatCmdSet(CmdSet):
    """Command set containing combat commands"""
    key = "combat_cmdset"
    priority = 15
    mergetype = "Union"

    def at_cmdset_creation(self):
        """Populate CmdSet"""
        self.add(CmdDropItem())
        self.add(CmdGetItem())
        self.add(CmdEquip())
        self.add(CmdKick())
        self.add(CmdStrike())
        self.add(CmdDodge())
        self.add(CmdAdvance())
        self.add(CmdRetreat())
        self.add(CmdFlee())
        #self.add(CmdWrestle())
        #self.add(CmdTackle())


class MeleeWeaponCmdSet(CmdSet):
    """Command set containing melee weapon commands"""
    key = "melee_cmdset"
    priority = 15
    mergetype = "Union"

    def at_cmdset_creation(self):
        self.add(CmdAttackMelee())


class RangedWeaponCmdSet(CmdSet):
    """Command set containing ranged weapon commands"""
    key = "ranged_cmdset"
    priority = 15
    mergetype = "Union"

    def at_cmdset_creation(self):
        self.add(CmdAttackRanged())

# commands


class CmdInitiateAttack(default_cmds.MuxCommand):
    """
    initiate combat against an enemy

    Usage:
      attack <target>

    Begins or joins turn-based combat against the given enemy.
    """
    key = 'attack'
    aliases = ['att', 'battle', 'batt']
    locks = 'cmd:not in_combat()'
    help_category = 'combat'

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: attack <target>")
            return

        target = caller.search(self.args)
        if not target:
            return

        # set up combat
        if target.ndb.combat_handler:
            # target is already in combat - join it
            target.ndb.combat_handler.add_character(caller)
            target.ndb.combat_handler.msg_all("{} joins combat!".format(
                caller.get_display_name(target)))
        else:
            # create a new combat handler
            chandler = create_script("typeclasses.combat_handler.CombatHandler")
            chandler.add_character(caller)
            chandler.add_character(target)
            caller.msg("You attack {}! You are in combat.".format(
                target.get_display_name(caller)))
            target.msg("{} attacks you! You are in combat.".format(
                caller.get_display_name(target)))
            chandler.msg_all("Next turn begins. Declare your actions!")


class CmdDropItem(default_cmds.MuxCommand):
    """
    drop an item onto the floor during combat

    Usage:
      drop <item>

    Drops the given item.

    This is a free combat action.
    """
    key = 'drop'
    aliases = []
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'free actions'

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: drop <item>")
            return
        target = caller.search(self.args,
                               candidates=self.caller.contents)
        if not target:
            return

        caller.ndb.combat_handler.add_action(
            action="drop",
            character=self.caller,
            target=target,
            duration=0)

        caller.msg(
            "You add 'drop {}' to the combat queue".format(
                target.get_display_name(caller)))

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdAttack(default_cmds.MuxCommand):
    """implementation melee and ranged attack shared functionality"""
    key = 'attack'
    aliases = ['att']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'half turn actions'

    def func(self):
        caller = self.caller

        attack_type = self.attack_type if hasattr(self, 'attack_type') \
                        else 'attack'
        duration = self.duration if hasattr(self, 'duration') else 1

        if not self.args:
            caller.msg("Usage: {}[/s] <target>".format(attack_type))
            return

        if len(self.switches) > 0:
            switch = '/{}'.format(self.switches[0])
        else:
            switch = ''

        combat_chars = caller.ndb.combat_handler.db.characters.values()

        target = caller.search(
                    self.args,
                    candidates=combat_chars)

        if not target:
            return

        ok = caller.ndb.combat_handler.add_action(
                action="{}{}".format(attack_type, switch),
                character=caller,
                target=target,
                duration=duration)

        if ok:
            caller.msg(
                "You add '{attack}{switch} {target}' to the combat queue".format(
                    attack=attack_type,
                    switch=switch,
                    target=target.get_display_name(caller)))
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdAttackMelee(CmdAttack):
    """
    attack an enemy with melee weapons

    Usage:
      attack[/s[ubdue]] <target>

    Switches:
      subdue, s - Inflict damage to SP instead of HP
                  for a non-fatal attack.

    Strikes the given enemy with your current weapon.

    This is a half-turn combat action.
    """

    aliases = ['att', 'stab', 'slice', 'chop', 'slash', 'bash']

    def func(self):
        super(CmdAttackMelee, self).func()


class CmdAttackRanged(CmdAttack):
    """
    attack an enemy with ranged weapons

    Usage:
      attack[/s[ubdue]] <target>

    Switches:
      subdue, s - Inflict damage to SP instead of HP
                  for a non-fatal attack.

    Strikes the given enemy with your current weapon.

    This is a half-turn combat action.
    """

    aliases = ['att', 'fire at', 'shoot']

    def func(self):
        super(CmdAttackRanged, self).func()


class CmdKick(CmdAttack):
    """
    attack an enemy by kicking

    Usage:
      kick[/s[ubdue]] <target>

    Switches:
      subdue, s - Inflict damage to SP instead of HP
                  for a non-fatal attack.

    Kicks give a +2 bonus to your attack, but if you miss,
    you suffer a -1 penalty to your defense for one turn.

    This is a full-turn combat action.
    """
    key = 'kick'
    aliases = ['boot', 'stomp']
    help_category = 'full turn actions'

    def func(self):
        self.attack_type = 'kick'
        self.duration = 2
        super(CmdKick, self).func()


class CmdStrike(CmdAttack):
    """
    attack an enemy with quick strikes

    Usage:
      strike[/s[ubdue]] <target>

    Switches:
      subdue, s - Inflict damage to SP instead of HP
                  for a non-fatal attack.

    Strikes are fast and accurate punches using your fists
    and arms.

    This is a half-turn combat action, but if both
    hands are available, two strikes will be performed
    during that half-turn, allowing up to four attacks
    per turn.
    """
    key = 'strike'
    aliases = ['punch', 'hit']
    help_category = 'half turn actions'

    def func(self):
        self.attack_type = 'strike'
        super(CmdStrike, self).func()


class CmdDodge(default_cmds.MuxCommand):
    """
    dodge any incoming attack

    Usage:
      dodge

    Any incoming attackers make two attack rolls and
    keep the lower of the two, reducing your damage.

    This is a half-turn combat action.
    """
    key = 'dodge'
    aliases = ['duck']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'half turn actions'

    def func(self):
        caller = self.caller

        ok = caller.ndb.combat_handler.add_action(
                action="dodge",
                character=self.caller,
                target=self.caller,
                duration=1)
        if ok:
            caller.msg("You add 'dodge' to the combat queue")
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdAdvance(default_cmds.MuxCommand):
    """
    move toward an opponent

    Usage:
      advance[/reach] [<target>]

    Switches:
      reach: advances only as far as 'reach' range,
             rather than 'melee'

    Moves your character from 'ranged' range to
    'melee' range with the specified opponent.

    This is a half-turn combat action.
    """
    key = 'advance'
    aliases = ['approach', 'adv', 'appr']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'half turn actions'

    def func(self):
        caller = self.caller
        combat_chars = caller.ndb.combat_handler.db.characters.values()
        target = None
        if not self.args:
            if len(combat_chars) == 2:
                target = [x for x in combat_chars if x.id != caller.id][0]
            else:
                caller.msg("Usage: advance <target>")
                return

        target = target or caller.search(
                                self.args,
                                candidates=combat_chars)

        if not target:
            return

        ok = caller.ndb.combat_handler.add_action(
                action="advance",
                character=caller,
                target=target,
                duration=1)
        if ok:
            caller.msg("You add 'advance on {target}' to the combat queue".format(
                target=target.get_display_name(caller)
            ))
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
            caller.ndb.combat_handler.check_end_turn()


class CmdRetreat(default_cmds.MuxCommand):
    """
    move away from all opponents

    Usage:
      retreat[/reach]

    Switches:
      reach: retreats only as far as 'reach' range,
             rather than 'ranged'

    Attempts to moves your character away from all
    other combatants. If spaces is not specified, uses
    all available MV points.

    This is a half-turn combat action.
    """
    key = 'retreat'
    aliases = ['ret']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'half turn actions'

    def func(self):
        caller = self.caller

        ok = caller.ndb.combat_handler.add_action(
                action="retreat",
                character=self.caller,
                target=self.caller,
                duration=1)
        if ok:
            caller.msg("You add 'retreat' to the combat queue")
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdGetItem(default_cmds.CmdGet):
    """
    get an item during combat

    Usage:
      get <obj>

    Switches:
      equip - Equips the object

    Picks up an object from your location and
    puts it in your inventory.

    This is a half-turn combat action.
    """
    key = 'get'
    aliases = ['grab', 'pick up']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'half turn actions'

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: get <obj>")
            return

        target = caller.search(self.args)

        if not target:
            return

        ok = caller.ndb.combat_handler.add_action(
                action="get",
                character=self.caller,
                target=target,
                duration=1)
        if ok:
            caller.msg("You add 'get {}' to the combat queue".format(
                target.get_display_name(self.caller)))
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdEquip(default_cmds.MuxCommand):
    """
    equip a weapon or piece of armor

    Usage:
      equip
      equip <item>

    If no item is specified, displays your current equipment
    as a free action.

    Equips an item to its required slot(s), replacing any
    currently equipped item.

    This is a half-turn combat action.
    """
    key = 'equip'
    aliases = ['wear', 'wield']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'half turn actions'

    def func(self):
        caller = self.caller
        if self.args:

            target = caller.search(self.args)

            if not target:
                return

            ok = caller.ndb.combat_handler.add_action(
                    action="equip",
                    character=self.caller,
                    target=target,
                    duration=1)

            if ok:
                caller.msg("You add 'equip {}' to the combat queue".format(
                    target.get_display_name(caller)))
            else:
                caller.msg("You have already entered all actions for your turn.")

            # tell the handler to check if turn is over
            caller.ndb.combat_handler.check_end_turn()
        else:
            # no arguments; display current equip
            data = []
            s_width = max(len(s) for s in caller.equip.slots)
            for slot, item in caller.equip:
                if not item or not item.access(caller, 'view'):
                    continue
                stat = " "
                if item.attributes.has('damage'):
                    stat += "(|rDamage: {:>2d}|n) ".format(item.db.damage)
                if item.attributes.has('toughness'):
                    stat += "(|yToughness: {:>2d}|n)".format(item.db.toughness)
                if item.attributes.has('range'):
                    stat += "(|G{}|n) ".format(
                        ", ".join([r.capitalize() for r in item.db.range]))

                data.append(
                    "  |b{slot:>{swidth}.{swidth}}|n: {item:<20.20} {stat}".format(
                        slot=slot.capitalize(),
                        swidth=s_width,
                        item=item.name,
                        stat=stat,
                    )
                )
            if len(data) <= 0:
                output = "You have nothing in your equipment."
            else:
                table = EvTable(header=False, border=None, table=[data])
                output = "|YYour equipment:|n\n{}".format(table)

            caller.msg(output)


class CmdWrestle(default_cmds.MuxCommand):
    """
    wrestle an opponent

    Usage:
      wrestle[/break] <target>

    Perform an unarmed attack against the target character
    that if successful, lowers the target's wrestling position
    one level. Wrestling positions go from

    Free standing -> clinching -> take down -> pinned

    Any combatant whose wrestling position is clinching or
    below can only defend and use the /break switch to
    attempt to raise their wrestling position.

    This is a full-turn combat action.
    """
    key = 'wrestle'
    aliases = ['grapple']
    locks = 'cmd:in_combat()'
    help_category = 'full turn actions'

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: wrestle[/break] <target>")
            return

        if len(self.switches) > 0:
            switch = '/{}'.format(self.switches[0])
        else:
            switch = ''

        combat_chars = caller.ndb.combat_handler.db.characters.values()

        target = caller.search(
                    self.args,
                    candidates=combat_chars)

        if not target:
            return

        ok = caller.ndb.combat_handler.add_action(
                action="wrestle{}".format(switch),
                character=self.caller,
                target=target,
                duration=2)

        if ok:
            caller.msg(
                "You add 'wrestle{switch} {target}' to the combat queue".format(
                    switch=switch,
                    target=target.get_display_name(caller)))
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdTackle(default_cmds.MuxCommand):
    """
    tackle an opponent

    Usage:
      tackle <target>

    Attempt to rush an opponent to try and tackle them to the
    ground. A tackle must be started with at least 4 spaces
    distance between you and your target. If successful, lowers
    the target's wrestling position immediately to 'take down',

    This combat action takes a turn and a half to complete.
    """
    key = 'tackle'
    aliases = []
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'multi turn actions'

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: tackle <target>")
            return

        combat_chars = caller.ndb.combat_handler.db.characters.values()

        target = caller.search(
                    self.args,
                    candidates=combat_chars)

        if not target:
            return


        ok1 = caller.ndb.combat_handler.add_action(
                action="charge",
                character=caller,
                target=target,
                duration=1)

        ok2 = caller.ndb.combat_handler.add_action(
                action="tackle",
                character=caller,
                target=target,
                duration=2,
                longturn=True)

        if ok1 and ok2:
            caller.msg(
                "You add 'tackle {target}' to the combat queue".format(
                    target=target.get_display_name(self.caller)))
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()


class CmdFlee(default_cmds.MuxCommand):
    """
    escape from combat

    Usage:
      flee

    Attempt to disengage combat and leave the area. Success
    is governed by the escape skill as well as the distance from
    other combatants.

    This is a half-turn combat action.
    """
    key = 'flee'
    aliases = ['escape']
    locks = 'cmd:in_combat() and attr(position, STANDING)'
    help_category = 'full turn actions'

    def func(self):
        caller = self.caller

        ok = caller.ndb.combat_handler.add_action(
                action="flee",
                character=caller,
                target=caller,
                duration=2)
        if ok:
            caller.msg("You add 'flee' to the combat queue")
        else:
            caller.msg("You have already entered all actions for your turn.")

        # tell the handler to check if turn is over
        caller.ndb.combat_handler.check_end_turn()