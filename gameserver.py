import zerozeroseven as zzs

import time
import socket
import select
import pickle

import count


READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR

class GameServer:
    """server for engine of 007 game

    contains a list of clients with uuid 
    in self.clients, which has a max length of 256 = #ff
    This allows the use of a single 8-bit char to represent a player
    """

    def __init__(self, hostport):
        self.connections = dict()   #fd, (sock, addr)

        self._uid = set()
        #dictionary of user connected to server
        self.clients = dict()       #uid, fd
        #dictionary of all named players (bot included)
        self.names = dict()         #uid, (name, status)    to meet clients
        self.staged = dict()        #uid, action
        self.players = dict()       #uid, Player()


        #server stuff
        host, _, port = hostport.partition(':')
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server.setblocking(False)  # non blocking socket
        self.server.bind((host, int(port)))  # bind host address and port together

        self.server.listen(256)         #ready for max 256 new connections

        self.poller  = select.poll()    #incoming data on socket
        self.poller.register(self.server, READ_ONLY)



    def set_bots(self, n):
        """a bot is a non-client player"""
        if isinstance(n, str):
            n = int(n)
        bots = [uid for uid in self.names if uid not in self.clients]

        if n < len(bots):  #add new bots
            for uid in bots[n:]:
                self.del_client(uid)
        else:
            for i in range(n - len(bots)):
                uid = zzs.new_uid()
                self.names[uid] = ("bot" + str(uid), True)


    def waiting_room(self):
        """wait here if there are no active connections or 
        not all connections are ready
        at least two players read to start and at least one client
        """
        ready = 0
        while not self.clients or (ready < 2 or ready != len(self.names)):
            print(f"waiting for clients at {self.server.getsockname()}...")
            #poll
            events = self.poller.poll(5000)  # every 2s checks for new clients
            for fd, flag in events:
                #print(f"event on {fd} with {flag}")
                #if polling on main socket it is accept request
                if flag & (select.POLLIN | select.POLLPRI):
                    if fd == self.server.fileno():
                        print("new connection")
                        (conn, addr) = self.server.accept()

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
                                    self.del_client(uid)
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
                            self.del_client(uid)
                            break

                else:
                    print("something else")

                self.connect_clients()

            is_ready = [uid for uid, (name, stat) in self.names.items() if stat]
            ready = len(is_ready)


    def del_client(self, i):
        """remove any trace of uid 'i'"""
        #remove from clients
        if i in self.clients:
            del self.clients[i]

        #remove from names
        if i in self.names:
            del self.names[i]

        zzs.del_uid(i)



    def greet_client(self, fd, name):
        """send uid to client"""
        uid = zzs.new_uid()
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
                        self.del_client(uid)
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

        self.engine = zzs.Engine(True)
        for uid in self.names:
            if uid in self.clients:
                self.engine.add_player(uid, 0)
            else:
                self.engine.add_player(uid, 1)

        self.ingame = ''.join(chr(uid) for uid in self.names.keys())

        print(f"Server: sending start")
        for uid, fd in self.clients.items():
            sock = self.connections[fd]
            msg = chr(uid) * 10
            try:  # send long and personalised message to client
                sock.send(msg.encode())
            except ConnectionError:
                print("broken connection with " + str(sock.getsockname()))

        #the game is about to start

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

        self.engine.newround()

        for uid, fd in self.clients.items():

            if not self.engine.gameover(uid):
                act = '*'
                if self.engine.can_shield(uid):
                    act += '#' * self.engine.can_shield(uid)
                if self.engine.can_fire(uid):
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

        start = time.time()
        end = start + 2     #1.0s wait    == 0 0 7
        while time.time() < end:
            events = self.poller.poll(50)  #polls at most 50ms
            for fd, flag in events:
                #if polling on main socket it is accept request
                if flag & (select.POLLIN | select.POLLPRI):
                    if fd != self.server.fileno():
                        sock = self.connections[fd]

                        for uid, fs in self.clients.items(): #find clients uid
                            if fs == fd:
                                break

                        data = sock.recv(1024)  #message is action
                        if data:
                            act = data.decode()
                            print(f"{uid} staging message {act}")
                            self.engine.stage(uid, ord(act[-1]))
                        else: #closing connection if empty message
                            self.poller.unregister(sock)
                            sock.close()
                            if fd in self.connections:
                                del self.connections[fd]

                                for uid, fs in self.clients.items():
                                    if fs == fd:
                                        self.del_client(uid)
                                        break




    ######################################


    def commit(self):
        self.engine.commit()

    ######################################


    def solve(self):
        """solve and send list of actions just occured"""

        rep, allp = self.engine.solve()

        self.print_report(rep, allp)

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


    def print_report(self, rep, allp):
        """print report rep, where allp is players in game"""
        print(f"\nRound {ord(rep[0])}")

        #a and t are consecutive characters
        loaders = [ord(p) for p in self.ingame]
        for a, t in zip(rep[1::2], rep[2::2]):
            a = ord(a)
            t = ord(t)
            if a == t:
                print(f"\t{a} is defending")
            else:
                print(f"\t{a} is shooting {t}")
            loaders.remove(a)

        for n in loaders:
            print(f"\t{n} is loading")

        print("\t-------In game----------")
        self.ingame = allp
        for p in self.ingame:
            print(f"\t{ord(p)}", end='')


    def finish(self):
        """game over"""
        if self.ingame:
            winner = chr(self.ingame[0])
            print("The winner is ", self.ingame[0])
        else:
            winner = ''
            print("There is no")

        for uid, fd in self.clients.items():
            sock = self.connections[fd]
            msg = chr(uid) * 10 + chr(winner)
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
        return self.engine.gameover()




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
            time.sleep(2)

        print("finish\n")
        self.finish()
        time.sleep(5)



if __name__ == "__main__":
    import sys

    #address = socket.gethostname() + ":5000"
    address = "192.168.1.6:5000"

    match = GameServer(address)
    if len(sys.argv) > 1:
        match.set_bots(sys.argv[1])

    #wait for clients to join and be ready
    match.waiting_room()

    match.newgame()
    match.execute()
    #match.again()
