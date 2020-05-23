
    def vertical_rect(pos, side, ratio):
        """keep rect vertical (hight >= width), so ratio is inverted if positive"""
        if not isinstance(pos, Point):
            pos = Point(pos)

        if ratio < 1:   #vertical
            base = side * ratio
        else:
            base = side / ratio

        rect = [Point(-base/2., -side/2.),
                Point( base/2., -side/2.),
                Point( base/2.,  side/2.),
                Point(-base/2.,  side/2.)]

        return [(pos + p).xy() for p in rect]

    def horizontal_rect(pos, base, ratio):
        """keep rect horizontal (hight <= width), so ratio is inverted if positive"""
        if not isinstance(pos, Point):
            pos = Point(pos)

        if ratio < 1:   #vertical
            side = base * ratio
        else:
            side = base / ratio

        rect = [Point(-base/2., -side/2.), Point(base, side)]

        return [(pos + p).xy() for p in rect]


    def triangle_down(pos, side):
        if not isinstance(pos, Point):
            pos = Point(pos)

        tri = [Point(-side / 2., -side / math.sqrt(12)), 
               Point( side / 2., -side / math.sqrt(12)), 
               Point(        0.,  side / math.sqrt( 3))]

        return [(pos + p).xy() for p in tri]  #return list of tuple,
                                            #ready to be used with pygame

    def triangle_up(pos, side):
        if not isinstance(pos, Point):
            pos = Point(pos)

        tri = [Point(-side / 2.,  side / 12**0.5), 
               Point( side / 2.,  side / 12**0.5), 
               Point(        0., -side /  3**0.5)]

        return [(pos + p).xy() for p in tri]  #return list of tuple,
                                            #ready to be used with pygame


    def adjust_font(self, width, title):
        tx_size = 32

        font = pygame.font.SysFont(None, tx_size)
        w, h = font.size(title)

        while w > width and tx_size > 1:
            tx_size -= 1
            font = pygame.font.SysFont(None, tx_size)
            w, h = font.size(title)

        return tx_size

############## old one

    def blit_players(self):
        print("players")

        #tag_font = pygame.font.SysFont(None, self.tag.size)
        #tag_text = tag_font.render(str(tag), 1, WHITE)
        #self.screen.blit(tag_text, avatar_tag(pos, tag_text))


        rect = []
        for uid, pos in self.pl_point.items():

            name, stat = self.pl_names[uid]
            if stat:
                col = BLACK     #player is in game
            else:
                col = GRAY      #player is dead

            r = pygame.draw.circle(self.screen, col,
                               pos.xy(), int(self.avatar_size/2.))
            rect.append(r)

            if uid == self.main:
                #print text
                name_text = self.font64.render(name, 1, BLACK)
                r = self.screen.blit(name_text,
                                     avatar_name_main(pos,
                                                  self.avatar_size,
                                                  name_text))
                rects.append(r)

                if stat:
                    #print shields
                    _pos = pos \
                         + Point(self.avatar_size/2.
                                 + shield_size/2 + 15,
                                   self.avatar_size/2.
                                 - shield_size / math.sqrt(3))

                    if self.actions:
                        self.defense = self.actions.count('#')
                    #defense = self.actions.count('#')
                    for i in range(3):
                        sp = 0 if i < self.defense else 5
                        if i % 2 == 0:
                            r = pygame.draw.polygon(self.screen, BLUE,
                                    triangle_down(_pos, shield_size), sp)
                        else:
                            _pos += Point(shield_size/2 + 10,
                                         shield_size * math.sqrt(3) / 6)
                            r = pygame.draw.polygon(self.screen, BLUE,
                                            triangle_up(_pos, shield_size),
                                            sp)
                            _pos += Point(shield_size/2 + 10,
                                         -shield_size * math.sqrt(3) / 6)
                        rects.append(r)

                    #print load status
                    if self.actions: loaded = '!' in self.actions
                    sp = 0 if loaded else 5
                    _pos = pos + Point(self.avatar_size/2.
                                       + 2 * shield_size
                                       + self.avatar_size/2. + 25,
                                       self.avatar_size/2.
                                       - shield_size / 2.)
                    r = pygame.draw.polygon(self.screen, GREEN,
                                            vertical_rect(_pos,
                                            self.loaded_size, 0.5), sp)
                    rects.append(r)

            else:
                font_size = self.adjust_font(self.avatar_size, name)
                name_font = pygame.font.SysFont(None, font_size)
                name_text = name_font.render(name, 1, BLACK)
                r = self.screen.blit(name_text, avatar_name(pos, self.avatar_size, name_text))
                rects.append(r)

        pygame.display.update(rects)
        #self.clock.tick(fps)

###########################
