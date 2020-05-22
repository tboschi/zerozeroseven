
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

