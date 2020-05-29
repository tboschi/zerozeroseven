from point import Point
from userclient import Client


import math
import pygame_textinput
import pygame



#constants
BLACK = (  0,   0,   0)
GRAY  = (127, 127, 127)
WHITE = (255, 255, 255)
BLUE  = (  0,   0, 255)
GREEN = (  0, 255,   0)
RED   = (255,   0,   0)

fps = 30

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
        return (int(self.pos[0] - w), int(self.pos[1] - h - avatar_size/2. - 5))



    def blit_avatar(self, surf, col):
        """draw avatar symbol on surf and returns rect to be updated
        col is a colour tuple"""

        r = pygame.draw.circle(surf, col, self.pos, int(avatar_size/2.))
        t = surf.blit(self.name_surf,  self.avatar_name())

        #return list of rects
        return [r, t]


    def blit_action(self, surf, act):
        """draw action taken on top of avatar, where act is action"""
        if act == '!':      #fire
            return pygame.draw.circle(surf, RED, self.pos, int(avatar_size/5.))
        elif act == '#':    #shield
            return pygame.draw.polygon(surf, BLUE, self.shield_symbol())
        elif act == '*':    #loaded
            return pygame.draw.polygon(surf, GREEN, self.loaded_symbol())
        else:
            return None




class Main(Avatar):
    """it is a bigger circle
    
    it is not actually, but just the naming position changes
    plus there is a status method"""


    def adjust_name(self, name):
        """64 pt name"""
        return pygame.font.SysFont(None, 64).render(name, 1, BLACK)


    def avatar_name(self):
        """name position is different for main"""
        w = surf.get_width() 
        h = surf.get_height() 
        return (int(self.pos[0] - avatar_size / 2. - w - 10),
                int(self.pos[1] - avatar_size / 2. + h))


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
        pot = (int(pos[0] + self.avatar_size / 2. + 2.5 * shield_size + 25),
               int(pos[1] + self.avatar_size / 2. - shield_size / 2.))

        return [pygame.draw.polygon(surf, GREEN, self.loaded_symbol(pos), sp)]


    def update_status(self, act):
        """update the status from aavailable actions"""
        if act:
            self.defense = act.count('#')
            self.loaded = '!' in act


    def blit_status(self, surf):
        """collect rectangles to be updated"""

        r  = self.shield_status(surf)
        r += self.loaded_status(surf)

        return r



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
            return False
        else:
            if tt is not None:
                self.text = self.words.pop(0)
            return self.text, now / self.dt


    def blit_countdown(self, surf):
        """print countdown with changing alpha at centre"""
        text, sec = self.countdown()     #text and time

        ready_wh = self.font64.size(text)
        ready_pos = (int(self.centre[0] - ready_wh[0] / 2.),
                     int(self.centre[1] - ready_wh[1] / 2.))

        area = pygame.Rect(ready_pos[0], ready_pos[1],
                           ready_wh[0],  ready_wh[1])
        area.inflate_ip(10, 10)

        alpha = int(255 * sec)

        ready = self.font64.render(text, 1, BLACK, WHITE)
        ready.set_alpha(alpha)

        pygame.draw.rect(surf, WHITE, area)
        surf.blit(ready, ready_pos)

        return [area]



class Logger:
    def __init__(self):
        pass



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

        self.font32 = pygame.font.SysFont(None, 32)
        self.font48 = pygame.font.SysFont(None, 48)
        self.font64 = pygame.font.SysFont(None, 64)      #large font

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

        #ready button, name dialog, counter
        self.startbutt = StartButton(self.centre)
        self.name_dial = NameDialog(self.centre)
        self.counter   = Counter(self.centre)


        #dict of avatars, including position -> {tag : Avatar}
        self.avatars = dict()


        self.name = ""
        self.client_ready = False
        self.game_started = False
        self.game_starting = False
        self.take_action = False

        self.action = ""
        self.report = ""
        self.shield = 3
        self.loaded = False

        self.tags = "1234567890qwertyuiop"
        self.tag_uid = dict()


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

        print ("there are ", len(names))

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
            pos = int(self.radius * math.cos(math.pi/2. + k*angle)), \
                  int(self.radius * math.sin(math.pi/2. + k*angle))

            if uid in self.avatars:
                self.avatars[uid].set_position(pos)
            else:
                if uid == main:
                    self.avatars[uid] = Main(name, pos)
                else:
                    self.avatars[uid] = Avatar(name, pos)



    def blit_players(self, game):
        """game is game status, true is on, false is not on"""
        print("waiting room")

        names = self.client.names
        main = self.client.main

        if game:
            colON, colOFF = GREEN, RED
        else:
            colON, colOFF = BLACK, GRAY

        rects = []
        for uid, (name, stat) in names.items():

            if stat:
                col = colON     #player is ready/alive
            else:
                col = colOFF    #player is not ready/dead

            rects += self.avatars[uid].blit_avatar(self.screen, col)

            if uid == main:
                rects += self.avatars[uid].blit_status(self.screen)
            
        return rects    #list of rects to be updated



    def blit_name_dialog(self, evts):
        """name dialog stays on until name is given"""
        print("name dialog")

        name, rects = self.name_dial.update(self.screen, evts)

        if name:
            self.client.name_register(name)

        return rects




    def blit_start_button(self, evts):
        """print a start button in the centre"""
        #print("start button")

        self.startbutt.is_ready(evts)
        return self.startbutt.update(self.screen)


    def blit_countdown(self):
        """blit game countdown"""

        return self.counter.blit_countdown(self.screen)


    def clear_board(self):
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
                #cli.print_players()

        if cli.status == "REGISTER":
            rects += self.blit_name_dialog(events)  #catch name
        elif cli.status == "WAITING" or cli.status == "READY":
            rects += self.blit_start_button(events)   #click start or ready
            if cli.start_signal:
                cli.status = "PLAYING"
                cli.reset_count = True

        elif cli.status == "PLAYING" or cli.status == "WATCHING":

            if cli.playing():  #message, so new state
                rects += self.clear_board()
                rects += self.blit_players(True)
                #cli.print_players()

                cli.start_signal = False      #no more countdown
                cli.reset_count  = True       #reset counter
                #change state
                cli.take_action = not cli.take_action
                cli.has_printed = False                #print once

                if cli.game_over:
                    cli.status = "GAMEOVER"    #skip
                    return

            if cli.start_signal:
                rects += self.blit_countdown()
            elif cli.take_action:
                if cli.status == "PLAYING":
                    if not cli.has_printed:
                        os.system('cls' if os.name == 'nt' else 'clear')
                        self.blit_actions()
                        #cli.has_printed = True
                    #cli.catch_action()         #catch action
                self.blit_zerozero()     #timer done
            else:
                if not cli.has_printed:
                    self.blit_result()
                    #cli.has_printed = True

        elif cli.status == "GAMEOVER":
            self.blit_winner()
            cli.sock.close()
            return

        if rects:
            pygame.display.update(rects)
            self.clock.tick(fps)









######## old stuff

    


    def blit_waiting_ready(self, rect):
        """print a ready message in the centre"""
        print("waiting ready")
 
        #self.blit_waiting_room()

        rect_pos = self.centre - Point(100, 50)
        rect_size = Point(200, 100)

        rect_list = [rect_pos.xy()[0], rect_pos.xy()[1], 
                     rect_size.xy()[0], rect_size.xy()[1]]
        r1 = pygame.draw.rect(self.screen, GREEN  , rect_list)
        r2 = pygame.draw.rect(self.screen, BLACK, rect_list, 5)

        ready = self.font32.render("READY", 1, BLACK)
        ready_pos = self.centre - Point(ready.get_width()/2, ready.get_height()/2)
        self.screen.blit(ready, ready_pos.xy())

        pygame.display.update(r1)
        self.clock.tick(fps)


    def blit_countdown(self, rect):
        """game is about to start, show count down"""
        print("ready")

        self.blit_players(rect)

        count = 3
        secs = 3000
        ready_wh = self.font64.size(str(count))
        ready_pos = self.centre - Point(ready_wh[0]/2, ready_wh[1]/2)

        area = pygame.Rect(ready_pos.xy()[0], ready_pos.xy()[1],
                           ready_wh[0], ready_wh[1])
        area.inflate_ip(10, 10)

        start = pygame.time.get_ticks()
        while secs > 0:
            #sec goes from 0 to 1000
            sec = (pygame.time.get_ticks() - start) % 1000
            alpha = int(255 * (1 - sec / 1000.))

            #print(count, sec, alpha)

            ready = self.font64.render(str(count), 1, BLACK, WHITE)
            #ready = ready.convert()
            ready.set_alpha(alpha)

            pygame.draw.rect(self.screen, WHITE, area)
            self.screen.blit(ready, ready_pos.xy())

            pygame.display.update(area)
            self.clock.tick(fps)

            if pygame.time.get_ticks() - start > 1000:
                start = pygame.time.get_ticks()
                secs -= 1000
                count -= 1


#############################



    def blit_actions(self):
        """only works if self.actions is defined"""
        print("actions")

        #tag_font = pygame.font.SysFont(None, self.tag.size)
        #tag_text = tag_font.render(str(tag), 1, WHITE)
        #self.screen.blit(tag_text, avatar_tag(pos, tag_text))

        rects = []

        can_fire   = '!' in self.actions
        can_shield = '#' in self.actions
        can_load   = '*' in self.actions

        text_centre = self.pl_point[self.main] - Point(0, self.avatar_size / 2)

        if can_load:
            key = self.font48.render("<  > :", 1, BLACK)
            act = self.font48.render(" load",  1, BLACK)
            kw, kh = key.get_width(), key.get_height()
            aw, ah = act.get_width(), act.get_height()
            text_centre -= Point(0, max(kh, ah) + 10)
            key_pos = text_centre - Point(kw, 0)
            act_pos = text_centre - Point(5, 0)
            rects.append(self.screen.blit(key, key_pos.xy()))
            rects.append(self.screen.blit(act, act_pos.xy()))

        if can_shield:
            key = self.font48.render("<space> :", 1, BLACK)
            act = self.font48.render(" shield",  1, BLACK)
            kw, kh = key.get_width(), key.get_height()
            aw, ah = act.get_width(), act.get_height()
            text_centre -= Point(0, max(kh, ah) + 10)
            key_pos = text_centre - Point(kw, 0)
            act_pos = text_centre - Point(5, 0)
            rects.append(self.screen.blit(key, key_pos.xy()))
            rects.append(self.screen.blit(act, act_pos.xy()))

        if can_fire:
            #place tags
            tt = 0
            self.tag_uid.clear()
            for uid, pos in self.pl_point.items():
                if uid != self.main and self.pl_names[uid][1]:     #if still in game
                    tag = self.tags[tt]
                    self.tag_uid[tag] = uid
                    tt += 1

                    tag_text = self.font64.render(tag, 1, WHITE)
                    pos -= Point(tag_text.get_width()/2, tag_text.get_height()/2)
                    rects.append(self.screen.blit(tag_text, pos.xy()))


            #place text
            key = self.font48.render("<x> :", 1, BLACK)
            act = self.font48.render(" shoot x",  1, BLACK)
            kw, kh = key.get_width(), key.get_height()
            aw, ah = act.get_width(), act.get_height()
            text_centre -= Point(0, max(kh, ah) + 10)
            key_pos = text_centre - Point(kw, 0)
            act_pos = text_centre - Point(5, 0)
            rects.append(self.screen.blit(key, key_pos.xy()))
            rects.append(self.screen.blit(act, act_pos.xy()))


        return rects

        #pygame.display.update(rect)
        #self.clock.tick(fps)


########## zero zero seven countdown

    def blit_zerozero(self, text):
        """draw zero zero seven countdown and print 'text' """
        print("countdown")

        ready_wh = self.font64.size("zero")
        ready_pos = self.centre - Point(ready_wh[0]/2, ready_wh[1]/2)

        area = pygame.Rect(ready_pos.xy()[0], ready_pos.xy()[1],
                           ready_wh[0], ready_wh[1])
        area.inflate_ip(10, 10)

        #count = 2
        #while count > 0:
        speed = 750
        start = pygame.time.get_ticks()
        #sec goes from 0 to 1000
        sec = (pygame.time.get_ticks() - start) % speed
        alpha = int(255 * (1 - sec / speed))

        ready = self.font64.render(text, 1, BLACK, WHITE)
        #ready = ready.convert()
        ready.set_alpha(alpha)

        pygame.draw.rect(self.screen, WHITE, area)
        self.screen.blit(ready, ready_pos.xy())

        pygame.display.update(area)
        self.clock.tick(fps)

        #if pygame.time.get_ticks() - start > speed:
        #    start = pygame.time.get_ticks()
        #    count -= 1

        return [area]



############## results

    def blit_result(self, rect):
        """show seven and report result on board"""
        print("result")

        start = pygame.time.get_ticks()

        ready = self.font64.render("seven", 1, BLACK, WHITE)
        ready_pos = self.centre - Point(ready.get_width()/2, ready.get_height()/2)
        pygame.draw.rect(self.screen, WHITE, ready.get_rect())
        self.screen.blit(ready, ready_pos.xy())

        fires = []
        shields = []
        loads = list(self.pl_names.keys())
        for p0, p1 in zip(self.report[1::2], self.report[2::2]):
            p0 = ord(p0)
            p1 = ord(p1)
            if p0 == p1:
                shields.append(p0)
            else:
                fires.append((p0, p1))
            loads.remove(p0)

        #shooting lines
        for id0, id1 in fires:
            pygame.draw.line(self.screen, RED, self.pl_point[id0].xy(),
                                               self.pl_point[id1].xy(), 10)


        self.blit_players(rect)


        #shooting
        for id0, _ in fires:
            pygame.draw.circle(self.screen, RED, self.pl_point[id0].xy(),
                                               int(self.avatar_size/5.))


        #defending
        for id0 in shields:
            pygame.draw.polygon(self.screen, BLUE,
                                triangle_down(self.pl_point[id0], shield_size))

        #loading
        for id0 in loads:
            pygame.draw.polygon(self.screen, GREEN,
                                vertical_rect(self.pl_point[id0], self.loaded_size, 0.5))


        pygame.display.update(rect)
        #pygame.display.flip()
        self.clock.tick(fps)

        #wait for a round second
        pygame.time.wait(start + 1000 - pygame.time.get_ticks())



########################## update main board


    def blit_board(self):
        """refresh is done in individual blocks"""
        #draw basic stuff

        #self.screen.fill(WHITE)
        #rect is the rectangle to be updated
        rect = self.screen.blit(self.board_surf, self.board_pos)

        if not self.game_started:

            #waiting room but name not set

            self.blit_waiting_room(rect)
            if not self.name:
                self.blit_name_dialog(rect) #pop up dialog for name input
            #elif not self.name_sent:
            #    self.send_name()  #client send name to server
            #    self.name_sent = True
            elif not self.client_ready:
                self.blit_start_button(rect)
            elif not self.game_starting:
                self.blit_waiting_ready(rect)
            else:
                self.blit_ready(rect)

        else:

            if self.actions:
                self.blit_players(rect)
                self.blit_actions(rect)
                self.blit_countdown(rect)
            else:
                self.blit_players(rect)
                self.blit_result(rect)

            #self.report = ''    #clear report as need to get this
            #self.actions = ''   #clear actions


########################## update sidebar


    def blit_report(self):
        """draw on the report side bar"""
        rect = self.screen.blit(self.report_surf, self.report_pos)
        pygame.draw.line(self.screen, BLACK, self.side_start, self.side_end, 5)

        pygame.display.update(rect)



########################## handle user events for mouse or keyboard


    def handle_events(self):
        
        action = ''
        
        allevents = pygame.event.get()
        print(f"there are {len(allevents)} events")
        print(allevents)
        for event in allevents:
            #quit if the quit button was pressed
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.MOUSEBUTTONUP:

                mouse = pygame.mouse.get_pos()
                if self.ready_butt and self.ready_butt.collidepoint(mouse):
                    self.client_ready = True
                    #name, _ = self.pl_names[self.main]
                    self.add_player(self.main, status=True)
                    self.ready_butt = None
                    self.client.send_ready()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    action = chr(self.main)
                    print("actions will be defend")
                elif event.unicode in self.tag_uid:
                    action = chr(self.tag_uid[event.unicode])
                    print(f"actions will be {event.unicode}")

        if not action:
            print(f"actions will be load")
        self.client.stage_action(action)




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
