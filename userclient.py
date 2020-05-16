import socket
import select
import pickle
import os

import count


pstart = bytearray([128])   #pickle start

class Client:
    """ client class, to respond to server
    this class deals with connections only """


    def __init__(self, addr, port):
        """client needs a address and port to creates
        a select for incoming messages"""


        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((addr, port))  # bind host address and port together
        #self.sock.setblocking(0)

        self.names = None
        self.names_update = False

        self.tags = "1234567890qwertyuiop"
        self.tag_uid = dict()

        self.status = "REGISTER"
        self.play_status = ["PLAYING", "WATCHING", "GAMEOVER"]
        self.game_over = False

        self.take_action = False
        self.start_signal = False
        self.reset_count = False
        self.cdown = False

        self.main = None
        self.name = ""

        self.actions = ""
        self.report  = ""
        self.ingame  = ""
        #self.choice  = ""


#####incoming mail


    def waiting(self):
        """receive list of users and start message"""
        #print("Client: listening...")

        ready = select.select([self.sock], [], [], 1)
        if ready[0]:

            data = self.sock.recv(1024)
            if not data: #data is empty, broken connection!
                #print("Client: broken connection")
                self.sock.close()
                exit()
            while len(data) >= 1024:    #more data in buffer
                data += self.sock.recv(1024)

            #print(f"Client: received ", data)

            if self.main is not None:
                start = chr(self.main) * 10
                start = start.encode()
                if start in data:
                    self.start_signal = True

                    pos = data.find(pstart)  #check for last pickle
                    if pos >= 0:
                        try:
                            pickd = pickle.loads(data[pos:])
                        except pickle.UnpicklingError:  #not pickle
                            pass
                        else:
                            #print("pickle!")
                            if isinstance(pickd, dict):
                                self.names = pickd
                    return


            #grab names and uid
            allpos = []
            pos = data.find(pstart)
            while pos != -1:
                allpos.append(pos)  #list of possilbe pickle objects
                pos = data.find(pstart, pos+1)
            allpos.append(len(data))   #and very last pos

            while allpos:   #check pickle from last position
                pos = allpos.pop()
                if not self.names_update:
                    try:
                        pickd = pickle.loads(data[pos:])
                    except (pickle.UnpicklingError, EOFError):  #not pickle
                        pass
                    else:
                        #print("pickle!")
                        if isinstance(pickd, dict):
                            #this is the address of each player
                            #print("dictionary")
                            self.names = pickd
                            self.names_update = True

                if self.main is None:
                    #print("uid try at ", pos)
                    #check if there is a uid before pickle
                    try:    #for uid decode last four
                        uid = data[max(pos - 4, 0):pos].decode()
                    except UnicodeDecodeError:
                        #print("fail")
                        pass
                    else:
                        #print("maybe " + uid)
                        if len(uid) > 1 and uid[-2] == uid[-1]:
                            self.main = ord(uid[-1])
                            print("New uid: ", self.main)




    def playing(self):
        """receive list of users and start message"""
        #print("Client: playing...")

        #no blocking!
        ready, _, _ = select.select([self.sock], [], [], 0)
        if ready:
            data = self.sock.recv(1024)
            while len(data) >= 1024:    #more data in buffer
                data += self.sock.recv(1024)

            if not data: #data is empty, broken connection!
                print("Client: broken connection")
                self.sock.close()
                exit()

            #try first the start message
            #if there is an uncaught pickle object this is likely
            #at the beginning of data and the start msg at the end
            try:
                data = data.decode()
            except UnicodeDecodeError:  #not decodable
                return False
            else:
                #print("Client: report ", data)
                if chr(self.main) * 10 in data:   #this is the end message
                    self.game_over = True
                    self.winner = ord(data.replace(chr(self.main) * 10, ''))
                    return True
                elif chr(self.main) * 5 in data:   #this is the report
                    self.report, _, self.ingame = \
                            data.partition(chr(0) + chr(self.main)*5 + chr(0))
                    #print ("Client: report")
                    return True
                else:
                    self.actions = data
                    #print("Client: actions ", self.actions)
                    return True

        return False


#####outgoing mail


    
    #def send_name(self):
    #    """send name to server and receive uid and names of other players"""
    #    self.sock.send(self.name.encode())   #send name to server

    #    uid = self.sock.recv(1024)
    #    #if len(uid) > 1:
    #    #uid = uid[-1:].decode()
    #    print("new uid is ", ord(uid))
    #    self.add_player(ord(uid), self.name, main=True)

    #    #print(f"Client: obtained uid {self.main}")

    #    #return self.uid


    def send_ready(self):
        """send name to server and receive uid and names of other players"""
        if self.main is not None:
            msg = chr(self.main)
            print("sending ", self.main)
            self.sock.send(msg.encode())   #send name to server


    def add_player(self, uid, name='', status=False, main=False):
        """add player only if client received uid or update player's status"""

        if main:    #save main uid
            self.main = uid
            #print("main ", self.main)

        if uid in self.names and not name:
            name, _ = self.pl_names[uid]
        self.names[uid] = (name, status)


    def update_players(self, book):
        """this is done only during the game action"""
        if isinstance(book, str):
            for uid, (name, stat) in self.names.items():
                if chr(uid) in book:
                    self.names[uid] = (name, True)
                else:
                    self.names[uid] = (name, False)



    def name_dialog(self):
        """get name input"""
        self.name = input("Enter your name: ")
        if self.name:
            print("Welcome " + self.name)
            self.status = "WAITING"
            #self.send_name()
            self.sock.send(self.name.encode())   #send name to server


    def print_players(self):
        """loop through characters of self.actions"""
        print("Players:")
        for name, status in self.names.values():
            st = "ready" if status else "wait"
            print(f"{name} ({st})", end='\t')
        print()
        self.names_update = False


    def catch_is_ready(self):
        print("Press ENTER when ready")
        ready, _, _ = select.select([sys.stdin], [], [], 1)
        if ready and '\n' in sys.stdin.readline():
            self.status = "READY"
            self.send_ready()
            print("Waiting game to start")


    def print_actions(self):
        """loop through characters of self.actions"""
        self.tag_uid.clear()
        #self.choice = ''

        print("New round, available actions (press ENTER after):")

        if '!' in self.actions:
            t = 0
            for uid, (name, stat) in self.names.items():
                if stat and uid != self.main:
                    c = self.tags[t]
                    self.tag_uid[c] = uid
                    print(f"\t<  {c}  > : fire {name}")
                    t += 1

        if '#' in self.actions:
            ns = self.actions.count('#')
            print (f"\t<space> : defend ({ns})")

        if '*' in self.actions:
            print ("\t<     > : load")


    def catch_action(self):
        #print("catching ", end='')
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        if ready:
            seq = sys.stdin.readline().strip('\n')  #remove carriage return
            #for s in seq:
                #print(ord(s), end=',')
            #print(".")

            if not seq:
                return
            if seq[-1] == chr(32):      #space bar = shield
                choice = chr(self.main)
                self.stage_action(choice)
            elif seq[-1] in self.tag_uid:   #known key = shoot
                choice = chr(self.tag_uid[seq[-1]])
                self.stage_action(choice)
            else:                       #other = load
                pass
                #self.choice = ''



    def stage_action(self, choice):
        """send action choice to server
        if it is sent multiple times, the server will keep only the last one"""
        if choice:
            #print(f"Client: staging {ord(choice)}")
            self.sock.send(choice.encode())   #send name to server




    def print_result(self):
        #print("rep " + self.report + ".")
        print("seven!")
        if not self.report:
            return
        r = ord(self.report[0])
        print(f"\nRound {r}")
        #for a in self.report:
        #    print(ord(a), end='')
        #print()

        #a and t are consecutive characters
        loaders = list(self.names.keys())
        for a, t in zip(self.report[1::2], self.report[2::2]):
            a = ord(a)
            t = ord(t)
            if a == t:
                print(f"\t{self.names[a][0]} is defending")
            else:
                print(f"\t{self.names[a][0]} is shooting {self.names[t][0]}")
            loaders.remove(a)

        for n in loaders:
            if self.names[n][1]:
                print(f"\t{self.names[n][0]} is loading")

        print("\t--------------------------")
        self.update_players(self.ingame)
        for name, stat in self.names.values():
            if not stat:
                print(f"\t{name} is dead")
            #if chr(uid) not in self.ingame:
            #self.names[uid] = (name, False)
        
        if not self.names[self.main][1]:     #main status
            print("You are dead!")
            self.status = "WATCHING"

        print()


    def print_winner(self):
        """show winner"""
        print("The game is over and ", end='')
        if self.winner:
            name = self.names[self.winner][0]
            print(f"the winner is {name}")
        else:
            print("no one has won")



    def update(self):
        """main function to run in an infinite loop"""

        #if self.status != "PLAYING" and self.status != "GAMEOVER":
        if self.status not in self.play_status:
            self.waiting()
            if self.names_update:
                self.print_players()

        if self.status == "REGISTER":
            self.name_dialog()  #catch name
        elif self.status == "WAITING":
            #self.print_players()
            self.catch_is_ready()   #press enter
        elif self.status == "READY":
            if self.start_signal:
                self.status = "PLAYING"
                self.reset_count = True

        elif self.status == "PLAYING" or self.status == "WATCHING":

            if self.playing():  #message, so new state
                #self.print_players()

                self.start_signal = False      #no more countdown
                self.reset_count  = True       #reset counter

                self.take_action = not self.take_action #change state
                self.has_printed = False                #print once

                if self.game_over:
                    self.status = "GAMEOVER"    #skip
                    return

            if self.start_signal:
                self.countdown()
            elif self.take_action:
                if self.status == "PLAYING":
                    if not self.has_printed:
                        os.system('cls' if os.name == 'nt' else 'clear')
                        self.print_actions()
                        self.has_printed = True
                    self.catch_action()         #catch action
                self.zerozero()     #timer done
            else:
                if not self.has_printed:
                    self.print_result()
                    self.has_printed = True

        elif self.status == "GAMEOVER":
            self.print_winner()
            self.sock.close()
            exit()




    def countdown(self):
        """3 2 1 countdown"""
        if self.reset_count:
            self.cdown = count.down(3)
            self.reset_count = False

        try:
            tt = next(self.cdown)
        except StopIteration:   #stop iteration, don't call this anymore
            return False
        else:
            if tt is not None:
                print(tt)
            return True


    def zerozero(self):
        """3 2 1 countdown"""
        if self.reset_count:
            self.cdown = count.down(2, dt=1.0)
            self.reset_count = False

        try:
            tt = next(self.cdown)
        except StopIteration:   #stop iteration, don't call this anymore
            #print("seven!")
            return False
        else:
            if tt is not None:
                print("zero")
            return True     #timer active


if __name__ == "__main__":
    import sys
    
    #address = sys.argv[1]
    #host, _, port = address.partition(':')
    host = socket.gethostname()
    port = 5000
    cli = Client(host, port)

    while True:
        cli.update()

