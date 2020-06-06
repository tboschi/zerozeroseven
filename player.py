import random

class Player:
    """player class which can take actions"""

    def __init__(self):
        self.is_loaded = False     #bool
        self.is_shield = 3         #int
        self.is_fired  = None      #player


    #############
    #game actions

    def last_action(self):
        """list of possible actions
        
        ! means fire
        # means shield
        * means load
        """
        if self.is_fired is not None:
            return '!', self.is_fired
        elif self.is_shield:
            return '#', None
        else:
            return '*', None


    def fire(self, player):
        if self.can_fire() and player is not self:  #can fire only if loaded
            self.is_loaded = False     #used bullet
            self.is_shield = 3         #restore defend
            self.is_fired  = player    #shooting player
            return True
        else:
            return False


    def shield(self):
        if self.can_shield():
            #self.is_loaded = True     #shield does not change load status
            self.is_shield -= 1        #decrease defend
            self.is_fired  = None      #not shooting 
            return True
        else:
            return False


    def load(self):
        if self.can_load():
            self.is_loaded = True      #new bullet
            self.is_shield = 3         #restore defend
            self.is_fired  = None      #not shooting 
            return True
        else:                           #never here...
            return False



    def can_fire(self):
        return self.is_loaded


    def can_load(self):             #always true, but can change
        return True


    def can_shield(self):
        return self.is_shield   #can defend max 3 times in a row



    def random(self, uid, others):
        """random action but need list of other players"""
        act = '*'
        if self.can_fire():
            act += '!'
        if self.can_shield():
            act += '#'

        choice = random.choice(act)
        if choice == '!':
            oid, tgt = random.choice(list(others.items()))
            self.fire(tgt)
            return oid
        elif choice == '#':
            self.shield()
            return uid
        else:
            self.load()
            return None
