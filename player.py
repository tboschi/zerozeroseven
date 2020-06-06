import random


class Player:
    """player class which can take actions"""

    def __init__(self):
        self.is_loaded = False     #bool
        self.is_shield = 3         #int


    #############
    #game actions


    def fire(self):
        if self.can_fire():            #can fire only if loaded
            self.is_loaded = False     #used bullet
            self.is_shield = 3         #restore defend
            return True
        else:
            return False


    def shield(self):
        if self.can_shield():
            #self.is_loaded = True     #shield does not change load status
            self.is_shield -= 1        #decrease defend
            return True
        else:
            return False


    def load(self):
        if self.can_load():
            self.is_loaded = True      #new bullet
            self.is_shield = 3         #restore defend
            return True
        else:                           #never here...
            return False



    def can_fire(self):
        return self.is_loaded

    def can_load(self):             #always true, but can change
        return True

    def can_shield(self):
        return self.is_shield   #can defend max 3 times in a row


    def actions(self):
        act = []
        if self.can_load():
            act.append(self.load)
        if self.can_shield():
            act.append(self.shield)
        if self.can_fire():
            act.append(self.fire)

        return act


class Bot(Player):

    def take_action(self, uid, others):
        """random action but need list of other players"""
        choice = random.choice(self.actions())

        if choice == self.shield:
            return uid
        elif choice == self.fire:
            return random.choice(others)
        else:
            return None
