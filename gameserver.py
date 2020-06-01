from player import Player
from client import Client

import time
import socket
import select
import pickle

import count


READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR

class GameServer:
    """engine of 007 game

    contains a list of clients with uuid 
    in self.clients, which has a max length of 256 = #ff
    This allows the use of a single 8-bit char to represent a player
    """

    def __init__(self):
        self.connections = dict()   #fd, (sock, addr)

        self._uid = set()
        #dictionary of user connected to server
        self.clients = dict()       #uid, fd
        #dictionary of all named players (bot included)
        self.names = dict()         #uid, (name, status)
        self.staged = dict()        #uid, action
        self.players = dict()       #uid, Player()


        #server stuff
        host = socket.gethostname()
        port = 5000
        self.engine = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.engine.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.engine.setblocking(False)  # non blocking socket
        self.engine.bind((host, port))  # bind host address and port together

        self.engine.listen(256)         #ready for max 256 new connections

        self.poller  = select.poll()    #incoming data on socket
        self.poller.register(self.engine, READ_ONLY)


    def new_uid(self):
        """return unique id, but max of id are 256"""
        for i in range(256):
            if i not in self._uid:
                self._uid.add(i)
                return i
        else:
            return None


    def del_uid(self, i):
        """remove any trace of uid 'i'"""
        #remove from clients
        if i in self.clients:
            del self.clients[i]

        #remove from names
        if i in self.names:
            del self.names[i]

        #finally remove from set
        if i in self._uid:
            self._uid.remove(i)



    def set_bots(self, n):
        """a bot is a non-client player"""
        if isinstance(n, str):
            n = int(n)
        bots = [uid for uid in self.names if uid not in self.clients]

        if n < len(bots):  #add new bots
            for uid in bots[n:]:
                self.del_uid(uid)
        else:
            for i in range(n - len(bots)):
                uid = self.new_uid()
                self.names[uid] = ("bot" + str(uid), True)



    def waiting_room(self):
        """wait here if there are no active connections or 
        not all connections are ready
        at least two players read to start and at least one client
        """
        ready = 0
        while not self.clients or (ready < 2 or ready != len(self.names)):
            print(f"waiting for clients at {self.engine.getsockname()}...")
            #poll
            events = self.poller.poll(5000)  # every 2s checks for new clients
            for fd, flag in events:
                #print(f"event on {fd} with {flag}")
                #if polling on main socket it is accept request
                if flag & (select.POLLIN | select.POLLPRI):
                    if fd == self.engine.fileno():
                        print("new connection")
                        (conn, addr) = self.engine.accept()

                        #register new socket
                        conn.setblocking(False)
                        self.poller.register(conn, READ_ONLY)
                        self.connections[conn.fileno()] = conn

                    #message from other socket, which is name of client
                    else:
                        sock = self.connections[fd]
                        data = sock.recv(1024).decode()
                        if data: #replace data with uid string
                            print(f"message incoming: {str(data)}.")
                            #client sent a known id, so ready to play
                            if len(data) == 1 and ord(data) in self.clients:
                                uid = ord(data)
                                self.ready_client(uid)
                            else: #it is name of client and want to play
                                uid = self.greet_client(fd, data)
                                #send client its uid
                                msg = chr(uid) * 2
                                print(f"Server: sending {str(msg)}.")
                                sock.send(msg.encode())

                            #tell all clients about other clients

                        #closing connection if empty message
                        #either because connection lost or rejected
                        else:
                            print("broken connection with "
                                  + str(sock.getsockname()))
                            self.poller.unregister(sock)
                            sock.close()
                            del self.connections[fd]

                            for uid, fs in self.clients.items():
                                if fs == fd:
                                    self.del_uid(uid)
                                    break

                elif flag & (select.POLLHUP | select.POLLERR):
                    print("broken connection with ", end='')
                    sock = self.connections[fd]
                    print(str(sock.getsockname()))
                    self.poller.unregister(sock)
                    sock.close()
                    del self.connections[fd]

                    for uid, fs in self.clients.items():
                        if fs == fd:
                            self.del_uid(uid)
                            break

                else:
                    print("something else")

                self.connect_clients()

            is_ready = [uid for uid, (name, stat) in self.names.items() if stat]
            ready = len(is_ready)



    def greet_client(self, fd, name):
        """send uid to client"""
        uid = self.new_uid()
        print(f"Server: uid for {name} is {uid}")
        if uid is not None:
            self.clients[uid] = fd
            self.names[uid] = (name, False)

            return uid     #send client uid 
        else:   #refuse connection
            return ''


    def ready_client(self, uid):
        """set client uid to ready state"""
        name, _ = self.names[uid]
        self.names[uid] = (name, True)
        print (name + " is ready")


    def connect_clients(self):
        """this makes connections know each other"""
        print("connecting")
        names_pick = pickle.dumps(self.names, -1)
        for fd in list(self.connections):
            sock = self.connections[fd]
            try:
                sock.send(names_pick)  # send data to the client
            except ConnectionError:
                print("broken connection with " + str(sock.getsockname()))
                self.poller.unregister(sock)
                sock.close()
                del self.connections[fd]

                for uid, fs in self.clients.items():
                    if fs == fd:
                        self.del_uid(uid)
                        break


    """various stages of the game, once it has started

    begin   creates a new round and players are warned
            players are given their available actions
    commit  the next action chosen by each player
            is commited to this engine
    solve   the engine resolves the actions states
            deciding if any players has lost
    end     end round by telling players they have lost
    """


    def newgame(self):
        """players is a list of players objects"""
        #self.connect_clients()
        time.sleep(1)       #wait one second
        print(f"Server: sending start")
        for uid, fd in self.clients.items():
            sock = self.connections[fd]
            msg = chr(uid) * 10
            try:  # send long and personalised message to client
                sock.send(msg.encode())
            except ConnectionError:
                print("broken connection with " + str(sock.getsockname()))

        #the game is about to start

        if self.players:
            self.players.clear()

        for uid in self.names:
            self.players[uid] = Player()

        self.rounds = 0

        #sleep 3.5 s here
        #time.sleep(0.5)


        cdown = count.down(3)
        while True:
            try:
                tt, dt = next(cdown)
            except StopIteration:
                break
            else:
                if tt is not None:
                    print(tt)


    ######################################


    def begin(self):
        """return a string of available actions for player uid
        only players in game get it
        
        # means shield
        ! means fire
        * means load : can always load, so no need to specify
        """
        for uid, fd in self.clients.items():

            if uid in self.players:
                act = '*'
                if self.players[uid].can_shield():
                    act += '#' * self.players[uid].can_shield()
                if self.players[uid].can_fire():
                    act += '!'
            else:
                act = 'xxx'

            sock = self.connections[fd]
            try:
                sock.send(act.encode())  # send data to the client
            except ConnectionError:
                print("broken connection with " + str(sock.getsockname()))


    ######################################


    def stage(self):
        """collect stage messages from players, only last one gets commited"""

        self.staged.clear()

        start = time.time()
        end = start + 2     #1.0s wait    == 0 0 7
        while time.time() < end:
            events = self.poller.poll(50)  #polls at most 50ms
            for fd, flag in events:
                #if polling on main socket it is accept request
                if flag & (select.POLLIN | select.POLLPRI):
                    if fd != self.engine.fileno():
                        sock = self.connections[fd]

                        for uid, fs in self.clients.items(): #find clients uid
                            if fs == fd:
                                break

                        data = sock.recv(1024)  #message is action
                        if data:
                            act = data.decode()
                            print(f"{uid} staging message {act}")
                            self.staged[uid] = ord(act[-1])
                        else: #closing connection if empty message
                            self.poller.unregister(sock)
                            sock.close()
                            if fd in self.connections:
                                del self.connections[fd]

                                for uid, fs in self.clients.items():
                                    if fs == fd:
                                        self.del_uid(uid)
                                        break



    ######################################


    def commit(self):
        """execute action act of player uid
        
        action is a string and can be any of
        empty   player not responded or loading, deault loading
        AA      player A is defending
        AB      player A is shooting player B
        """

        to_remove = set()  #staged messages to be removed because faulty
        print(self.staged)
        for uid, p in self.players.items():
            if uid not in self.clients:     #this is a bot
                others = dict(self.players)
                del others[uid]
                act = p.random(uid, others)
                if act is not None:
                    self.staged[uid] = act

            #real client has sent non empty message
            elif uid in self.staged: # and self.staged[uid] is not None:
                if uid == self.staged[uid]:
                    if not p.shield():  #commit did not work, wrong message
                        to_remove.add(uid)
                else:
                    t = self.players[self.staged[uid]]
                    if not p.fire(t):
                        to_remove.add(uid)
            else:   #empty staged message
                if not p.load():
                    to_remove.add(uid)

        for uid in to_remove:
            del self.staged[uid]


    ######################################


    def solve(self):
        """solve commited actions"""
        to_remove = set()  #players to be removed because dead
        report = chr(self.rounds)
        num_rep = str(self.rounds)

        print(f"Round {self.rounds}")
        for uid, p in self.players.items():
            if uid in self.staged: #has shot or defended
                oid = self.staged[uid]  #other
                if uid != oid:          #p is shooting t
                    print(f"\t{uid} is shooting {oid}")
                    report  += chr(uid) + chr(oid)
                    num_rep += str(uid) + str(oid)
                    t = self.players[oid]

                    #target is dead if loading or is shooting someone else
                    if oid not in self.staged or \
                            self.staged[oid] not in [uid, oid]:
                        to_remove.add(oid)   #remove it from game
                else:
                    print(f"\t{uid} is defending")
                    report  += chr(uid) * 2          # AA -> A is defending
                    num_rep += str(uid) * 2
            else:
                print(f"\t{uid} is loading")

        for uid in to_remove:
            print(f"\t{uid} is dead")
            del self.players[uid]

        num_rep += ';'
        num_rep += ''.join(str(uid) for uid in self.players)
        print("->", num_rep)
        print()

        self.send_report(report)

        self.rounds += 1
        time.sleep(2)



    def send_report(self, rep):
        """send list of actions just occured"""
        allp = ''.join(chr(uid) for uid in self.players.keys())

        rep  = rep.encode()
        allp = allp.encode()

        for uid, fd in self.clients.items():
            sock = self.connections[fd]

            sep = chr(0) + chr(uid) * 5 + chr(0)
            msg = rep + sep.encode() + allp
            try:
                sock.send(msg)     #report
            except ConnectionError:
                print("broken connection with " + str(sock.getsockname()))



    def finish(self):
        """game over"""
        if self.players:
            winner = chr(next(iter(self.players)))
        else:
            winner = ''

        for uid, fd in self.clients.items():
            sock = self.connections[fd]
            msg = chr(uid) * 10 + winner
            try:
                sock.send(msg.encode())
            except ConnectionError:
                print("broken connection with " + str(sock.getsockname()))



    ############################################


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
            self.begin()

            #in these two seconds server listens from clients
            print("stage")
            self.stage()

            #in commit phase messages are stored and exectued
            print("commit")
            self.commit()

            #right after the engine resolves the actions
            #and send a report to each client
            print("solve\n")
            self.solve()

        print("finish\n")
        self.finish()
        time.sleep(5)



if __name__ == "__main__":
    import sys

    match = GameServer()
    if len(sys.argv) > 1:
        match.set_bots(sys.argv[1])

    #wait for clients to join and be ready
    match.waiting_room()

    match.newgame()
    match.execute()
    #match.again()
