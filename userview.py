from point import Point
from userclient import Client


import math
import pygame_textinput
import pygame

import count



#constants
BLACK = (  0,   0,   0)
GRAY  = (127, 127, 127)
WHITE = (255, 255, 255)
BLUE  = (  0,   0, 255)
GREEN = (  0, 255,   0)
RED   = (255,   0,   0)

fps = 30
tags = "1234567890qwertyuiop"

width, height = 960, 720
avatar_size = 100   #circle for player
shield_size = 60    #triangle for shielding action
loaded_size = 50    #rectangle for loading


class Avatar:
    """it is a circle"""

    def __init__(self, name, position):

        self.name = name
        self.name_surf = self.adjust_name(self.name)
        self.pos = position


    def set_position(self, position):
        """position is a tuple"""
        if isinstance(position, tuple):
            self.pos = position
        else:
            raise ValueError("set_position: not a tuple")


    def adjust_name(self, name):
        """finds right font size for name"""
        name_size = 32

        font = pygame.font.SysFont(None, name_size)
        w, h = font.size(name)
        while w > avatar_size and name_size > 5:
            name_size -= 1

            font = pygame.font.SysFont(None, name_size)
            w, h = font.size(title)

            font = pygame.font.SysFont(None, font_size)

        return font.render(name, 1, BLACK)


    def shield_symbol(self, pos = None, side = None):
        """draw triangle down"""
        if pos is None:
            pos = self.pos
        if side is None:
            side = shield_size

        perp = side / math.sqrt(3)
        side /= 2.

        #return list of tuples
        return [(int(pos[0] - side), int(pos[1] - perp / 2.)), 
                (int(pos[0] + side), int(pos[1] - perp / 2.)), 
                (int(pos[0]       ), int(pos[1] + perp     ))]


    def shield_symbol_up(self, pos = None, side = None):
        """draw triangle up"""
        if pos is None:
            pos = self.pos
        if side is None:
            side = shield_size

        perp = side / math.sqrt(3)
        side /= 2.

        #return list of tuples
        return [(int(pos[0] - side), int(pos[1] + perp / 2.)), 
                (int(pos[0] + side), int(pos[1] + perp / 2.)), 
                (int(pos[0]       ), int(pos[1] - perp     ))]


    def loaded_symbol(self, pos = None, side = None):
        """draw vertical stick
        it is a vertical rectangle 1:2 ratio"""
        if pos is None:
            pos = self.pos
        if side is None:
            side = loaded_size

        side /= 2.
        base = side / 2.

        #return list of tuples
        return [(int(pos[0] - base), int(pos[1] - side)),
                (int(pos[0] + base), int(pos[1] - side)),
                (int(pos[0] + base), int(pos[1] + side)),
                (int(pos[0] - base), int(pos[1] + side))]


    def avatar_name(self):
        """compute position of avatar name"""
        #if first time, adjust font size

        w = self.name_surf.get_width() / 2.
        h = self.name_surf.get_height()
        return (int(self.pos[0] - w),
                int(self.pos[1] - h - avatar_size/2. - 5))


    def blit_avatar(self, surf, col):
        """draw avatar symbol on surf and returns rect to be updated
        col is a colour tuple"""

        r = pygame.draw.circle(surf, col, self.pos, int(avatar_size/2.))
        t = surf.blit(self.name_surf,  self.avatar_name())

        #return list of rects
        return [r, t]


    def blit_fire(self, surf, end = None):
        """draw fire action, a line and a circle"""
        if end is not None:      #fire
            r = pygame.draw.line(surf, RED, self.pos, end, 10)
            c =  pygame.draw.circle(surf, RED, self.pos, int(avatar_size/5.))
            return [r.union(c)]


    def blit_shield(self, surf):
        """draw shield action, a triangle"""
        return [pygame.draw.polygon(surf, BLUE, self.shield_symbol())]
    

    def blit_load(self, surf):
        """draw load action, a rectangle"""
        return [pygame.draw.polygon(surf, GREEN, self.loaded_symbol())]




class Main(Avatar):
    """it is a bigger circle
    
    it is not actually, but just the naming position changes
    plus there is a status method"""

    def __init__(self, name, position):
        super().__init__(name, position)

        #for main
        self.defense = 0
        self.loaded  = 0


    def adjust_name(self, name):
        """64 pt name"""
        return pygame.font.SysFont(None, 64).render(name, 1, BLACK)


    def avatar_name(self):
        """name position is different for main"""
        w = self.name_surf.get_width() 
        h = self.name_surf.get_height() 
        return (int(self.pos[0] - avatar_size / 2. - w - 10),
                int(self.pos[1] - h / 2.))
                #int(self.pos[1] - avatar_size / 2. + h))


    def shield_status(self, surf):
        """status of shield"""
        pos = (int(self.pos[0] + avatar_size/2. + 5),
               int(self.pos[1] + avatar_size/2. - shield_size / math.sqrt(12)))

        rects = []
        #defense = self.actions.count('#')
        for i in range(3):
            sp = 0 if i < self.defense else 5    #define thickness

            if i % 2 == 0:
                pos = (int(pos[0] + shield_size / 2. + 10),
                       int(pos[1] - shield_size / math.sqrt(12)))

                r = pygame.draw.polygon(surf, BLUE, self.shield_symbol(pos), sp)
            else:
                pos = (int(pos[0] + shield_size / 2. + 10),
                       int(pos[1] + shield_size / math.sqrt(12)))

                r = pygame.draw.polygon(surf, BLUE, self.shield_symbol_up(pos), sp)

            rects.append(r)

        return rects


    def loaded_status(self, surf):
        """status of loaded"""
        sp = 0 if self.loaded else 5
        pos = (int(self.pos[0] + avatar_size / 2. + 2.5 * shield_size + 25),
               int(self.pos[1] + avatar_size / 2. - shield_size / 2.))

        return [pygame.draw.polygon(surf, GREEN, self.loaded_symbol(pos), sp)]


    def blit_status(self, surf, act):
        """collect rectangles to be updated
        and update the status from aavailable actions"""
        print("act", act)
        if act:
            self.defense = act.count('#')
            self.loaded = '!' in act

        r  = self.shield_status(surf)
        r += self.loaded_status(surf)

        return r


    def blit_actions(self, surf, actions, others):
        """only works if actions is defined
        others is a dictionary with uid and position of other avatars"""
        print("actions")

        #tag_font = pygame.font.SysFont(None, self.tag.size)
        #tag_text = tag_font.render(str(tag), 1, WHITE)
        #self.screen.blit(tag_text, avatar_tag(pos, tag_text))

        rects = []
        tag_uid = dict()

        font48 = pygame.font.SysFont(None, 48)
        font64 = pygame.font.SysFont(None, 64)

        can_fire   = '!' in actions
        can_shield = '#' in actions
        can_load   = '*' in actions

        text_centre = int(self.pos[0]), int(self.pos[1] - avatar_size / 2.)

        if can_load:
            key = font48.render("<  > :", 1, BLACK)
            act = font48.render(" load",  1, BLACK)

            kw, kh = key.get_width(), key.get_height()
            aw, ah = act.get_width(), act.get_height()

            text_centre = text_centre[0], text_centre[1] - max(kh, ah) - 10

            key_pos = int(text_centre[0] - kw), int(text_centre[1])
            act_pos = int(text_centre[0] - 5),  int(text_centre[1])

            rects.append(surf.blit(key, key_pos))
            rects.append(surf.blit(act, act_pos))

        if can_shield:
            key = font48.render("<space> :", 1, BLACK)
            act = font48.render(" shield",  1, BLACK)

            kw, kh = key.get_width(), key.get_height()
            aw, ah = act.get_width(), act.get_height()

            text_centre = text_centre[0], text_centre[1] - max(kh, ah) - 10

            key_pos = int(text_centre[0] - kw), int(text_centre[1])
            act_pos = int(text_centre[0] - 5),  int(text_centre[1])

            rects.append(surf.blit(key, key_pos))
            rects.append(surf.blit(act, act_pos))

        if can_fire:
            #place tags
            t = 0
            for uid, pos in others.items():

                tag_uid[tags[t]] = uid
                tag_text = font64.render(tags[t], 1, WHITE)

                pos = int(pos[0] - tag_text.get_width()/2.), \
                      int(pos[1] - tag_text.get_height()/2.)

                rects.append(surf.blit(tag_text, pos))

                t += 1


            #place text
            key = font48.render("<x> :", 1, BLACK)
            act = font48.render(" shoot x",  1, BLACK)

            kw, kh = key.get_width(), key.get_height()
            aw, ah = act.get_width(), act.get_height()

            text_centre = text_centre[0], text_centre[1] - max(kh, ah) - 10

            key_pos = int(text_centre[0] - kw), int(text_centre[1])
            act_pos = int(text_centre[0] - 5),  int(text_centre[1])

            rects.append(surf.blit(key, key_pos))
            rects.append(surf.blit(act, act_pos))


        return rects, tag_uid



class NameDialog:

    def __init__(self, centre):
        """init parameters"""
        self.textinput = pygame_textinput.TextInput()

        self.rect_size = 400, 200
        self.rect_pos  = int(centre[0] - 200), int(centre[1] - 100)
        self.rect = pygame.Rect(self.rect_pos[0],  self.rect_pos[1],
                                self.rect_size[0], self.rect_size[1])

        font32 = pygame.font.SysFont(None, 32)
        self.inst = font32.render("Insert your name:", 1, BLUE)

        self.inst_pos = int(centre[0] - 190), int(centre[1] - 90)
        self.name_pos = int(centre[0] - 190), int(centre[1] - 40)


    def update(self, surf, events):

        h  = self.inst.get_height()
        b0 = self.rect_pos[0],  self.rect_pos[1] + h + 20
        b1 = self.rect_pos[0] + self.rect_size[0], self.rect_pos[1] + h + 20

        pygame.draw.rect(surf, WHITE, self.rect)
        pygame.draw.rect(surf, BLACK, self.rect, 5)
        pygame.draw.line(surf, BLACK, b0, b1)

        surf.blit(self.inst, self.inst_pos)
        surf.blit(self.textinput.get_surface(), self.name_pos)

        #in case window is closed
        #events = pygame.event.get()
        #for event in events:
        #    if event.type == pygame.QUIT:
        #        exit()

        name = ""
        if self.textinput.update(events):
            name = self.textinput.get_text()

        return name, [self.rect]



class StartButton:

    def __init__(self, centre):
        """create dialog for start button"""
        rect_size = 200, 100
        rect_pos = centre[0] - 100, centre[1] - 50
        self.rect = pygame.Rect(rect_pos[0], rect_pos[1], rect_size[0], rect_size[1])

        font32 = pygame.font.SysFont(None, 32)
        self.click = font32.render("Click me if ready", 1, BLACK)
        self.ready = font32.render("READY", 1, BLACK)

        self.msg = self.click
        self.col = RED
        self.centre = centre


    def update(self, surf):
        pygame.draw.rect(surf, self.col, self.rect)
        pygame.draw.rect(surf, BLACK, self.rect, 5)

        ready_pos = (int(self.centre[0] - self.msg.get_width()/2),
                     int(self.centre[1] - self.msg.get_height()/2))
        surf.blit(self.msg, ready_pos)

        return [self.rect]


    def clear(self, surf):
        area = self.rect.inflate(50, 50)
        return [pygame.draw.rect(surf, WHITE, area)]


    def is_ready(self, events):
        ret = False

        for evt in events:
            if evt.type == pygame.MOUSEBUTTONUP:
                ret = self.rect.collidepoint(pygame.mouse.get_pos())
                break

        if ret:
            self.msg = self.ready
            self.col = GREEN

        return ret


class Counter:

    def __init__(self, centre):
        self.centre = centre
        self.font64 = pygame.font.SysFont(None, 64)      #large font

        self.area = None        #used to clear countdown


    def reset(self, messages, dt=1):
        """reset countdown and create new one
        the length of time is given by messages and dt"""
        if isinstance(messages, list):
            self.words = messages
        elif isinstance(messages, str):
            self.words = messages.split()

        self.dt = dt
        self.text = ""
        self.cdown = count.down(len(self.words), dt)


    def countdown(self):
        """return text from words and proprtion in dt of time
        since it is count.down, now is decreasing"""
        try:
            tt, now = next(self.cdown)
        except StopIteration:   #stop iteration, don't call this anymore
            return "", 0
        else:
            if tt is not None:
                self.text = self.words.pop(0)
            return self.text, now / self.dt



    def blit_countdown(self, surf):
        """print countdown with changing alpha at centre"""
        text, sec = self.countdown()     #text and time

        if not text and not sec:
            return [None]

        ready_wh = self.font64.size(text)
        ready_pos = (int(self.centre[0] - ready_wh[0] / 2.),
                     int(self.centre[1] - ready_wh[1] / 2.))

        self.area = pygame.Rect(ready_pos[0], ready_pos[1],
                           ready_wh[0],  ready_wh[1])
        self.area.inflate_ip(10, 10)

        alpha = int(255 * sec)

        ready = self.font64.render(text, 1, BLACK, WHITE)
        ready.set_alpha(alpha)

        pygame.draw.rect(surf, WHITE, self.area)
        surf.blit(ready, ready_pos)

        return [self.area]



    def clear(self, surf, text):
        msg     = self.font64.render(text, 1, BLACK, WHITE)
        msg_pos = int(self.centre[0] - msg.get_width()/2.), \
                  int(self.centre[1] - msg.get_height()/2.)

        pygame.draw.rect(surf, WHITE, self.area)
        r = surf.blit(msg, msg_pos)

        return [r.union(self.area)]





#### main class

class MatchView:
    """build GUI for one single client and handles communication
    synchronsied with GUI"""

    def __init__(self, cli):
        """client is a Client object"""

        self.client = cli

        pygame.init()
        pygame.font.init()

        #initialize the screen
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("zerozeroseven")

        #initialize pygame clock
        self.clock = pygame.time.Clock()

        #initialize graphics
        #surface


        #self.status_shield_size = 80
        #self.status_loaded_size = 70

        self.board_pos  = (0, 0)
        self.board_size = (height, height)
        self.board_surf = pygame.Surface(self.board_size)
        self.board_surf.fill(WHITE)


        self.side_bar = abs(width - height)
        self.side_start = width - self.side_bar, 0
        self.side_end   = width - self.side_bar, height
        
        self.report_pos  = (height, 0)
        self.report_size = (self.side_bar, height)
        self.report_surf = pygame.Surface(self.report_size)
        self.report_surf.fill(WHITE)


        #now define margins
        self.bmargin = 5  + avatar_size/2.
        self.tmargin = 32 + avatar_size/2.
        self.lmargin = 10 + avatar_size/2.
        self.rmargin = 10 + avatar_size/2.

        self.radius = 0.5 * min(width - self.side_bar
                                - self.lmargin - self.rmargin,
                                height - self.tmargin - self.bmargin)
        self.centre = int(.5 * (width - self.side_bar - self.lmargin
                                + self.rmargin)), \
                      int(.5 * (height + self.tmargin - self.bmargin))

        #useful objects
        #ready button, name dialog, counter
        self.startbutt = StartButton(self.centre)
        self.name_dial = NameDialog(self.centre)
        self.counter   = Counter(self.centre)


        #dict of avatars, including position -> {tag : Avatar}
        self.avatars = dict()
        self.tag_uid = dict()



        #first blitting
        #draw play game for the first time
        self.screen.blit(self.board_surf, self.board_pos)
        self.screen.blit(self.report_surf, self.report_pos)
        pygame.draw.line(self.screen, BLACK, self.side_start, self.side_end, 5)
        pygame.display.flip()



########## draw players

    def update_players(self):
        """this routine adds player to the dictionary and updates positions
        add player only if client received uid or update player's status"""

        names = self.client.names
        main = self.client.main

        if main:
            angle  = 2. * math.pi / len(names)
        else:   #keep space for main player
            angle  = 2. * math.pi / (len(names) + 1)

        t = 1
        for uid, (name, _) in names.items():
            if uid == main:
                k = 0
            else:
                k = t
                t += 1

            #k is 0 for main player
            pos = int(self.centre[0]
                      + self.radius * math.cos(math.pi/2. + k*angle)), \
                  int(self.centre[1]
                      + self.radius * math.sin(math.pi/2. + k*angle))

            if uid in self.avatars:
                self.avatars[uid].set_position(pos)
            elif uid == main:
                self.avatars[uid] = Main(name, pos)
            else:
                self.avatars[uid] = Avatar(name, pos)



    def blit_players(self, game):
        """game is game status, true is on, false is not on"""
        print("print players")

        names = self.client.names
        main = self.client.main
        act  = self.client.actions

        if game:
            colON, colOFF = BLACK, GRAY
        else:
            colON, colOFF = GREEN, RED

        rects = []
        for uid, (name, stat) in names.items():

            if stat:
                col = colON     #player is ready/alive
            else:
                col = colOFF    #player is not ready/dead

            rects += self.avatars[uid].blit_avatar(self.screen, col)

            if game and uid == main:
                rects += self.avatars[uid].blit_status(self.screen, act)
            
        return rects    #list of rects to be updated



    def blit_name_dialog(self, evts):
        """name dialog stays on until name is given"""
        #print("name dialog")

        name, rects = self.name_dial.update(self.screen, evts)

        if name:
            self.client.name_register(name)

        return rects




    def blit_start_button(self, evts):
        """print a start button in the centre"""
        #print("start button")

        if self.startbutt.is_ready(evts):
            self.client.ready_register()
        return self.startbutt.update(self.screen)


    def blit_no_button(self):
        """print a start button in the centre"""
        #print("start button")

        return self.startbutt.clear(self.screen)


    def blit_countdown(self):
        """blit game countdown"""

        return self.counter.blit_countdown(self.screen)


    def blit_end_count(self, text):
        """blit game countdown"""
        print("seven!")

        return self.counter.clear(self.screen, text)


    def blit_available_actions(self):
        """blit available actions"""

        main = self.client.main
        act  = self.client.actions
        others = {uid : avt.pos for uid, avt in self.avatars.items()
                                    if uid != main}

        rects, self.tag_uid = self.avatars[main].blit_actions(self.screen,
                                                              act, others)

        #clear previous choice
        self.choice = None
        self.choice_rect = None


        return rects


    def blit_current_choice(self):
        """blit current choice"""

        if self.choice == self.client.main and '#' in self.client.actions:
            act = "DEFEND"
        elif self.choice in self.client.names and '!' in self.client.actions:
            act = "SHOOTING " + self.client.names[self.choice][0]
        elif '*' in self.client.actions:
            act = "LOADING"

        font48 = pygame.font.SysFont(None, 48)
        text = font48.render(act, 1, BLUE)
        pos  = int(self.centre[0] - text.get_width() / 2.), \
               int(self.centre[1] - text.get_height() - 100)

        if self.choice_rect:
            #clear old choice
            pygame.draw.rect(self.screen, WHITE, self.choice_rect)
            self.choice_rect.union_ip(self.screen.blit(text, pos))
        else:
            self.choice_rect = self.screen.blit(text, pos)

        return [self.choice_rect]



    def blit_result(self):
        """report result on board"""

        report = self.client.report
        print("result", report)

        if not report:
            return []

        rects = []

        names = self.client.names
        main = self.client.main

        #a and t are consecutive characters
        fires   = []
        shields = []
        loads   = [uid for uid, (_, stat) in names.items() if stat]
        for a, t in zip(report[1::2], report[2::2]):
            a = ord(a)
            t = ord(t)
            if a == t:
                #print(f"\t{self.names[a][0]} is defending")
                shields.append(a)
            else:
                #print(f"\t{self.names[a][0]} is shooting {self.names[t][0]}")
                fires.append((a, t))
            loads.remove(a)

        #for n in loaders:
        #rn = ord(report[0])  #round number
        #print(f"\nRound {r}")

        #for a in self.report:
        #    print(ord(a), end='')
        #print()

        #    if self.names[n][1]:
        #        print(f"\t{self.names[n][0]} is loading")

        #print("\t--------------------------")
        #for name, stat in self.names.values():
        #    if not stat:
        #        print(f"\t{name} is dead")
            #if chr(uid) not in self.ingame:
            #self.names[uid] = (name, False)
        
        #if not self.names[self.main][1]:     #main status
        #    print("You are dead!")
        #    self.status = "WATCHING"


        #update list of players
        self.client.update_players(self.client.ingame)

        #rects += self.avatars[uid].blit_avatar(self.screen, col)

        #shooting lines
        for id0, id1 in fires:
            rects += self.avatars[id0].blit_fire(self.screen,
                                                 self.avatars[id1].pos)

        #defending
        for id0 in shields:
            rects += self.avatars[id0].blit_shield(self.screen)

        #loading
        for id0 in loads:
            rects += self.avatars[id0].blit_load(self.screen)

        return rects


    def blit_winner(self):
        """print name of winner"""
        winner = self.client.names[self.client.winner][0]
        print("the winner is:", winner)

        font32 = pygame.font.SysFont(None, 32)
        font64 = pygame.font.SysFont(None, 64)

        winn = font32.render("The winner is:", 1, BLACK)
        name = font32.render(winner, 1, BLACK)

        winn_pos = int(self.centre[0] - winn.get_width()/2.), \
                   int(self.centre[1] - winn.get_height()/2.)
        name_pos = int(self.centre[0] - name.get_width()/2.), \
                   int(self.centre[1] - 2 * name.get_width() - winn.get_height()/2.)

        rects = []
        rects.append(self.screen.blit(winn, winn_pos))
        rects.append(self.screen.blit(name, name_pos))

        return rects


    def catch_action(self, events):
        """keyboard input for decision"""

        if events:
            print("there are", len(events))

        for evt in events:
            if evt.type == pygame.KEYDOWN:

                if evt.key == pygame.K_SPACE:
                    self.choice = self.client.main

                elif evt.unicode in self.tag_uid:
                    self.choice = self.tag_uid[evt.unicode]

        if self.choice is not None:
            self.client.stage_action(chr(self.choice))




    def clear_board(self):
        print("clear board")
        return [self.screen.blit(self.board_surf, self.board_pos)]

        
    def clear_report(self):
        return [pygame.draw.line(self.screen, BLACK,
                                 self.side_start, self.side_end, 5),
                self.screen.blit(self.report_surf, self.report_pos)]


    def update(self):
        """main function to run in an infinite loop"""

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

        rects = []
        cli = self.client

        #if self.status != "PLAYING" and self.status != "GAMEOVER":
        if cli.status not in cli.play_status:
            cli.waiting(0)
            if cli.names_update:
                self.update_players()
                rects += self.clear_board()
                rects += self.blit_players(False)
                cli.names_update = False
                #cli.print_players()

        if cli.status == "REGISTER":
            rects += self.blit_name_dialog(events)  #catch name

        elif cli.status == "WAITING" or cli.status == "READY":
            if cli.start_signal:                #received start from server
                cli.status = "PLAYING"
                rects += self.blit_no_button()  #no button
                self.counter.reset("3 2 1")
            else:
                rects += self.blit_start_button(events)   #click start or ready

        #last state, but order is weird because need to use final 'else'
        elif cli.status == "GAMEOVER":
            if not self.has_printed:
                self.blit_winner()
                cli.sock.close()

        else:   #cli.status == "PLAYING" or cli.status == "WATCHING"

            if cli.playing():  #message, so new state
                rects += self.clear_board()
                rects += self.blit_players(True)
                #cli.print_players()

                #define game status, if actions or countdown
                cli.start_signal = False                #no more countdown
                cli.take_action = not cli.take_action   #change state
                self.counter.reset("zero zero")

                self.has_printed = False                #print once

                if cli.game_over:
                    cli.status = "GAMEOVER"    #skip
                    return

            if cli.start_signal:    #this is initial countdown (3, 2, 1)
                rects += self.blit_countdown()
            elif cli.take_action:
                if cli.status == "PLAYING":
                    if not self.has_printed:  #only update once
                        rects += self.blit_available_actions()
                        self.has_printed = True
                    self.catch_action(events)         #catch action
                    rects += self.blit_current_choice()

                #else just watching
                rects += self.blit_countdown()
            else:
                if not self.has_printed:
                    rects += self.blit_end_count("seven")
                    rects += self.blit_result()
                    self.has_printed = True

                if cli.is_gameover():
                    cli.status = "WATCHING"  #only if main dead


        if rects:   #update screen
            pygame.display.update(rects)
            self.clock.tick(fps)







######## old stuff

    


    #def blit_waiting_ready(self, rect):
    #    """print a ready message in the centre"""
    #    print("waiting ready")
 
    #    #self.blit_waiting_room()

    #    rect_pos = self.centre - Point(100, 50)
    #    rect_size = Point(200, 100)

    #    rect_list = [rect_pos.xy()[0], rect_pos.xy()[1], 
    #                 rect_size.xy()[0], rect_size.xy()[1]]
    #    r1 = pygame.draw.rect(self.screen, GREEN  , rect_list)
    #    r2 = pygame.draw.rect(self.screen, BLACK, rect_list, 5)

    #    ready = self.font32.render("READY", 1, BLACK)
    #    ready_pos = self.centre - Point(ready.get_width()/2, ready.get_height()/2)
    #    self.screen.blit(ready, ready_pos.xy())

    #    pygame.display.update(r1)
    #    self.clock.tick(fps)


    #def blit_countdown(self, rect):
    #    """game is about to start, show count down"""
    #    print("ready")

    #    self.blit_players(rect)

    #    count = 3
    #    secs = 3000
    #    ready_wh = self.font64.size(str(count))
    #    ready_pos = self.centre - Point(ready_wh[0]/2, ready_wh[1]/2)

    #    area = pygame.Rect(ready_pos.xy()[0], ready_pos.xy()[1],
    #                       ready_wh[0], ready_wh[1])
    #    area.inflate_ip(10, 10)

    #    start = pygame.time.get_ticks()
    #    while secs > 0:
    #        #sec goes from 0 to 1000
    #        sec = (pygame.time.get_ticks() - start) % 1000
    #        alpha = int(255 * (1 - sec / 1000.))

    #        #print(count, sec, alpha)

    #        ready = self.font64.render(str(count), 1, BLACK, WHITE)
    #        #ready = ready.convert()
    #        ready.set_alpha(alpha)

    #        pygame.draw.rect(self.screen, WHITE, area)
    #        self.screen.blit(ready, ready_pos.xy())

    #        pygame.display.update(area)
    #        self.clock.tick(fps)

    #        if pygame.time.get_ticks() - start > 1000:
    #            start = pygame.time.get_ticks()
    #            secs -= 1000
    #            count -= 1


#############################



    #def blit_actions(self):
    #    """only works if self.actions is defined"""
    #    print("actions")

    #    #tag_font = pygame.font.SysFont(None, self.tag.size)
    #    #tag_text = tag_font.render(str(tag), 1, WHITE)
    #    #self.screen.blit(tag_text, avatar_tag(pos, tag_text))

    #    rects = []

    #    can_fire   = '!' in self.actions
    #    can_shield = '#' in self.actions
    #    can_load   = '*' in self.actions

    #    text_centre = self.pl_point[self.main] - Point(0, self.avatar_size / 2)

    #    if can_load:
    #        key = self.font48.render("<  > :", 1, BLACK)
    #        act = self.font48.render(" load",  1, BLACK)
    #        kw, kh = key.get_width(), key.get_height()
    #        aw, ah = act.get_width(), act.get_height()
    #        text_centre -= Point(0, max(kh, ah) + 10)
    #        key_pos = text_centre - Point(kw, 0)
    #        act_pos = text_centre - Point(5, 0)
    #        rects.append(self.screen.blit(key, key_pos.xy()))
    #        rects.append(self.screen.blit(act, act_pos.xy()))

    #    if can_shield:
    #        key = self.font48.render("<space> :", 1, BLACK)
    #        act = self.font48.render(" shield",  1, BLACK)
    #        kw, kh = key.get_width(), key.get_height()
    #        aw, ah = act.get_width(), act.get_height()
    #        text_centre -= Point(0, max(kh, ah) + 10)
    #        key_pos = text_centre - Point(kw, 0)
    #        act_pos = text_centre - Point(5, 0)
    #        rects.append(self.screen.blit(key, key_pos.xy()))
    #        rects.append(self.screen.blit(act, act_pos.xy()))

    #    if can_fire:
    #        #place tags
    #        tt = 0
    #        self.tag_uid.clear()
    #        for uid, pos in self.pl_point.items():
    #            if uid != self.main and self.pl_names[uid][1]:     #if still in game
    #                tag = self.tags[tt]
    #                self.tag_uid[tag] = uid
    #                tt += 1

    #                tag_text = self.font64.render(tag, 1, WHITE)
    #                pos -= Point(tag_text.get_width()/2, tag_text.get_height()/2)
    #                rects.append(self.screen.blit(tag_text, pos.xy()))


    #        #place text
    #        key = self.font48.render("<x> :", 1, BLACK)
    #        act = self.font48.render(" shoot x",  1, BLACK)
    #        kw, kh = key.get_width(), key.get_height()
    #        aw, ah = act.get_width(), act.get_height()
    #        text_centre -= Point(0, max(kh, ah) + 10)
    #        key_pos = text_centre - Point(kw, 0)
    #        act_pos = text_centre - Point(5, 0)
    #        rects.append(self.screen.blit(key, key_pos.xy()))
    #        rects.append(self.screen.blit(act, act_pos.xy()))


    #    return rects

        #pygame.display.update(rect)
        #self.clock.tick(fps)


########## zero zero seven countdown

    #def blit_zerozero(self, text):
    #    """draw zero zero seven countdown and print 'text' """
    #    print("countdown")

    #    ready_wh = self.font64.size("zero")
    #    ready_pos = self.centre - Point(ready_wh[0]/2, ready_wh[1]/2)

    #    area = pygame.Rect(ready_pos.xy()[0], ready_pos.xy()[1],
    #                       ready_wh[0], ready_wh[1])
    #    area.inflate_ip(10, 10)

    #    #count = 2
    #    #while count > 0:
    #    speed = 750
    #    start = pygame.time.get_ticks()
    #    #sec goes from 0 to 1000
    #    sec = (pygame.time.get_ticks() - start) % speed
    #    alpha = int(255 * (1 - sec / speed))

    #    ready = self.font64.render(text, 1, BLACK, WHITE)
    #    #ready = ready.convert()
    #    ready.set_alpha(alpha)

    #    pygame.draw.rect(self.screen, WHITE, area)
    #    self.screen.blit(ready, ready_pos.xy())

    #    pygame.display.update(area)
    #    self.clock.tick(fps)

    #    #if pygame.time.get_ticks() - start > speed:
    #    #    start = pygame.time.get_ticks()
    #    #    count -= 1

    #    return [area]



############## results




########################## update main board


#    def blit_board(self):
#        """refresh is done in individual blocks"""
#        #draw basic stuff
#
#        #self.screen.fill(WHITE)
#        #rect is the rectangle to be updated
#        rect = self.screen.blit(self.board_surf, self.board_pos)
#
#        if not self.game_started:
#
#            #waiting room but name not set
#
#            self.blit_waiting_room(rect)
#            if not self.name:
#                self.blit_name_dialog(rect) #pop up dialog for name input
#            #elif not self.name_sent:
#            #    self.send_name()  #client send name to server
#            #    self.name_sent = True
#            elif not self.client_ready:
#                self.blit_start_button(rect)
#            elif not self.game_starting:
#                self.blit_waiting_ready(rect)
#            else:
#                self.blit_ready(rect)
#
#        else:
#
#            if self.actions:
#                self.blit_players(rect)
#                self.blit_actions(rect)
#                self.blit_countdown(rect)
#            else:
#                self.blit_players(rect)
#                self.blit_result(rect)
#
            #self.report = ''    #clear report as need to get this
            #self.actions = ''   #clear actions


########################## update sidebar


    #def blit_report(self):
    #    """draw on the report side bar"""
    #    rect = self.screen.blit(self.report_surf, self.report_pos)
    #    pygame.draw.line(self.screen, BLACK, self.side_start, self.side_end, 5)

    #    pygame.display.update(rect)



########################## handle user events for mouse or keyboard




#    def update(self):
#        """main function to run in an infinite loop"""
#
#        #receive messages from server
#        if not self.game_starting:
#            if self.client.waiting():    #true means there is a message
#            #check first if game starting
#                self.game_starting = self.client.is_game_starting()
#                self.update_players(self.client.get_book())
#
#        else:   #game is starting! actions will declare new game
#            if self.client.playing():
#                print("act: " + self.actions + ", rep: " + self.report)
#                if not self.actions:
#                    print("h0")
#                    if not self.game_started:   #start game now!
#                        self.game_started = True
#                    self.actions = self.client.get_actions()
#                else:
#                    print("h1")
#                    self.report, ingame = self.client.get_report()
#                    print("report " + self.report)
#                    self.update_players(ingame)
#                    self.actions = ''    #empty action
#                print("act: " + self.actions + ", rep: " + self.report)
#
#
#        #update GUI
#        self.blit_report()  #first blit side bar
#        self.blit_board()   #then main board
#        self.handle_events()


        

if __name__ == "__main__":
    import socket

    #address = sys.argv[1]
    #host, _, port = address.partition(':')
    host = socket.gethostname()
    port = 5000
    cli = Client(host, port)

    view = MatchView(cli)

    while True:
        view.update()
