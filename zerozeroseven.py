import player


_uid = set()

def new_uid():
    """return unique id, but max of id are 256"""
    for i in range(256):
        if i not in _uid:
            _uid.add(i)
            return i
    else:
        return None

def del_uid(i):
    """remove any trace of uid 'i'"""
    if i in _uid:
        _uid.remove(i)



class Engine:
    """engine of zerozeroseven game

    contains a list of players with uuid given by server
    in self.players, which has a max length of 256 = #ff
    This allows the use of a single 4-byte char to represent a player

    To start a new game, simply create an instance of this class
    and add players
    """

    def __init__(self, verbose):
        self.players = dict()
        self.staged  = dict()

        self.round = 0

        self.verb = verbose


    def add_player(self, uid, lvl = 1):
        """add player to engine and return uid
        lvl indicates difficulty
        0 for human, 1, 2, 3, ... for bot"""
        if uid is None:
            print("Cannot have more than 256 players, skipping.")
            return None
            
        if not lvl:
            print("-> ", uid, "player")
            self.players[uid] = player.Player()
        else:
            print("-> ", uid, "bot")
            self.players[uid] = player.Bot()



    """various stages of the game, once it has started

    begin   creates a new round and players are warned
            players are given their available actions
    stage   store actions to be taken that can change 
            until commit is called
    commit  the next action chosen by each player
            is commited to this engine
    solve   the engine resolves the actions states
            deciding if any players has lost
    end     end round by telling players they have lost
    """


    def can_load(self, uid):
        return self.players[uid].can_load()

    def can_shield(self, uid):
        return self.players[uid].can_shield()

    def can_fire(self, uid):
        return self.players[uid].can_fire()


    ######################################


    def newround(self):
        self.round += 1
        self.staged.clear()


    def stage(self, uid, action = None):
        """actions for human players are staged here"""
        if uid in self.staged and action is None:
            del self.staged[uid]
        elif action is not None:
            self.staged[uid] = action


    def commit(self):
        """execute action act of player uid
        first stage actions of not human players 
        action is stored in actions"""
        
        for uid, p in self.players.items():
            print("commit", uid)

            if isinstance(p, player.Bot):          #this is a bot
                others = list(self.players.keys())  #other players
                others.remove(uid)
                #return a random action and add to stage
                self.staged[uid] = p.take_action(uid, others)

            if uid not in self.staged:      #no bot but no message
                self.staged[uid] = None

            if self.staged[uid] == uid:
                if not p.shield():      #failed shield
                    self.staged[uid] = None
            elif self.staged[uid] is not None:
                if not p.fire():        #failed fire
                    self.staged[uid] = None

            if self.staged[uid] is None:    #failed and missing actions
                p.load()        #default action



    def solve(self):
        """solve commited actions"""
        remove = set()  #players to be removed because dead
        rep = chr(self.round)

        if self.verb:
            numrep = str(self.round)
            print(f"Round {self.round}")

        for uid, p in self.players.items():

            if uid in self.staged:       #has shot or defended
                oid = self.staged[uid]  #other

                if oid is None and self.verb:
                    print(f"\t{uid} is loading")

                elif uid != oid:          #p is shooting t
                    rep += chr(uid) + chr(oid)
                    if self.verb:
                        numrep += str(uid) + str(oid)

                    #target is dead if loading or is shooting someone else
                    if oid not in self.staged or \
                            self.staged[oid] not in [uid, oid]:
                        remove.add(oid)   #remove it from game
                else:
                    if self.verb:
                        print(f"\t{uid} is defending")
                    rep += chr(uid) * 2          # AA -> A is defending
                    if self.verb:
                        numrep += str(uid) * 2


        for uid in remove:
            if self.verb:
                print(f"\t{uid} is dead")
            del self.players[uid]

        allp = ''.join(chr(uid) for uid in self.players.keys())

        if self.verb:
            numrep += ';'
            numrep += ''.join(str(uid) for uid in self.players.keys())
            print("->", numrep)
            print()

        return rep, allp


    def gameover(self, uid = None):
        """return true if uid is not anymore in players meaning the playes has
        lost; if no value is passed, return true if there is more than one
        player in game
        """
        if uid is None:
            return len(self.players) < 2
        else:
            return not uid in self.players


    def execute(self):
        """run in loop emulating server client response"""

        while not self.gameover():

            #start new round by sending a message to each client
            #with the available actions they can do
            print("begin")
            self.begin(uid)

            self.stage()

            self.commit()
            self.solve()




if __name__ == "__main__":
    import sys

    player_names = []
    while True:
        name = input("Enter player name: ")
        if name == '':
            break
        else:
            player_names.append(name)


    match = Game()

    for n in player_names:
        uid = match.add_client(n)
        print (f"added client with uid {hex(uid)}")

    match.connect_clients()

    match.newgame()
    while True:
        match.execute()
