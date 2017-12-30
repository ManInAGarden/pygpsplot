"""Plotter Printer Module, stellt im wesentlichen die gleichnamige Klasse bereit
"""
import math
import os
from tkinter import *
import svgwrite as svg
from TransformationMatrix import *

MM_FACT = 3.543307

class PlotterPrinter:
    """Klasse mit der ein Plotter auf der Bildschirm dargestellt aber auch als svg-File exportiert
    kann
    """
    def __init__(self, breitengrad, massstab, missweisung, minuten):
        self.mass = massstab
        self.breite = breitengrad
        self.miss = missweisung
        self.min = minuten
        self.breiten_m = (1852.216 * 1000) / self.mass
        self.laengen_m = self.breiten_m * math.cos(self.breite/180*math.pi)
        self.printed = False

    def print_on_canvas(self, canv):
        """Den Plotter auf einem TK-Canvas Widget darstellen
        *canv - das Canvas Widget
        """
        #Grundeinstellungen
        pad = 10
        hscale = canv.winfo_width()/(2 * pad + self.min*self.laengen_m)
        vscale = canv.winfo_height()/(2 * pad + self.min*self.breiten_m)

        if vscale < hscale:
            c = vscale
        else:
            c = hscale

        #meine Transformationsmatrix
        tm = TransformationMatrix.from_params_simple(pad, pad, c, 0)

        #Der Rahmen
        olx, oly = tm.transform(0.0, 0.0)
        urx, ury = tm.transform(self.min*self.laengen_m, self.min * self.breiten_m)
        canv.create_rectangle(olx, oly,
             urx, ury)

        #Laengenskala
        for i in range(0, self.min):
            self.__print_canc_minute(canv, tm, self.laengen_m * i,
                                     0.0, self.laengen_m, 0.0) #oben
            self.__print_canc_minute(canv, tm, self.laengen_m * (i+1),
                                     self.breiten_m * self.min, self.laengen_m, math.pi) #unten

        #Breitenskala
        for i in range(0, self.min):
            self.__print_canc_minute(canv, tm, self.min * self.laengen_m, i * self.breiten_m,
                                     self.breiten_m, math.pi/2) #links
            self.__print_canc_minute(canv, tm, 0.0, self.breiten_m * (i + 1),
                                     self.breiten_m, 3/2*math.pi) #rechts

        #die langen waagerechten Striche auf den vollen Breitengraden
        for i in range(1, self.min):
            self.__plotline(canv, tm, 0.0, self.breiten_m * i,
                            self.laengen_m * self.min, self.breiten_m * i)
            
        #die langen senkrechten Striche auf den vollen Längengraden
        for i in range(1, self.min):
            self.__plotline(canv, tm, self.laengen_m * i, 0.0,
                            self.laengen_m * i, self.breiten_m * self.min)

        #Die Kompassrose
        self.__printrose(canv, tm)

        cx = olx + (urx-olx)/2
        cy = oly + (ury-oly)/2
        self.__print_hole(canv, cx, cy) #ein Loch in die Mitte
        #und ein Loch in jede Ecke
        self.__print_hole(canv, olx, oly)
        self.__print_hole(canv, olx, ury)
        self.__print_hole(canv, urx, oly)
        self.__print_hole(canv, urx, ury)

        self.__print_scale(canv, tm, pad + (urx-olx)/2, ury + 20)
        self.__print_logo_and_else(canv, tm, self.min * self.laengen_m/2, self.min * self.breiten_m * 0.85)

    def __print_hole(self, canv, xc, yc):
        """Ein Loch mit Zentrum an der übergebenen Stelle auf einen canvas malen
        """
        rad = 3.0
        canv.create_oval(xc-rad, yc-rad, xc+rad, yc+rad)

    def __printrose(self, canv, tm):
        """Die Kompassrose darstellen auf einem canvas-Objekt
        * canv  -das Canvas-Widget auf dem gezeichnet werden soll
        * tm die Transformationsmatrix
        """
        radius = self.laengen_m * self.min * 0.7 / 2
        xc = self.min / 2 * self.laengen_m
        yc = self.min / 2 * self.breiten_m
        tx1, ty1 = tm.transform(xc-radius, yc-radius)
        tx2, ty2 = tm.transform(xc+radius, yc+radius)
        canv.create_oval(tx1, ty1, tx2, ty2)

        for i in range(0, 360, 5):
            tl = 0.05
            doit = False
            if i % 10 == 0:
                tl = 0.1
                doit = True
            
            if doit:
                self.__printtick(canv, tm, xc, yc, radius, i + self.miss, tl, i)

        self.__print_rose_cross(canv, tm, xc, yc, radius)

    def __print_rose_cross(self, canv, tm, xc, yc, radius):
        """Das Kreuz in der Mitte der Kompassrose zeichnen
        Das Kreuz besteht aus je einer Linie zwischen 0 und 180 sowie
        einer zwischen 90 und 270 Grad
        """
        bogwink = (2 * math.pi * self.miss) / 360.0
        parttm = TransformationMatrix.from_params_simple(xc, yc, 0.9*radius, bogwink)
        myTm = TransformationMatrix.from_followed_trans(parttm, tm)
        x1, y1 = myTm.transform(0.0, -1.0)
        x2, y2 = myTm.transform(0.0, 1.0)
        canv.create_line(x1, y1, x2, y2)
        x1, y1 = myTm.transform(-1.0, 0.0)
        x2, y2 = myTm.transform(1.0, 0.0)
        canv.create_line(x1, y1, x2, y2)

        x1, x2 = myTm.transform(0.0, -1.4)
        canv.create_text(x1, x2, text="N", angle=-self.miss, font=("Helvetika", "8", "bold"))
    
    def __printtick(self, canv, tm, xc, yc, radius, angle, tl, pangle):
        """Einen Strich der Kompassrose mit angeschriebenr Gradzahl darstellen
        """
        bogwink = (2 * math.pi * angle) / 360.0
        part_tm = TransformationMatrix.from_params_simple(xc, yc, radius, bogwink)
        my_tm = TransformationMatrix.from_followed_trans(part_tm, tm)
        x1, y1 = my_tm.transform(0.0, -1.0)
        x2, y2 = my_tm.transform(0.0, -1.0-tl)
        xt, yt = my_tm.transform(0.0, -1.0 - 1.8 * tl)
        canv.create_line(x1, y1, x2, y2)
        atxt = "{0:03.0f}".format(pangle)
        canv.create_text(xt, yt, text=atxt, angle = -angle, font=("Helvetika", "7", "bold"))

    def __plotline(self, canv, tm, xs, ys, xe, ye):
        """Eine Strecke zwischen zwei Punkten zeichnen
        * canv - Das Canvas Widget
        * tm - Die Transformationsmatrix
        * xs, ys - Der Startpunkt der Strecke
        * xe, ye - Der Endpunkt der Strecke
        """
        x1, y1 = tm.transform(xs, ys)
        x2, y2 = tm.transform(xe, ye)
        canv.create_line(x1, y1, x2, y2)

    
    def __print_canc_minute(self, canv, tm, movx, movy, scale, angle):
        """Die Unterteilung für eine einzelne Bogenmitnute drucken
        canv - Der Canvas
        tm - die Grundskalierung
        movx, movy - der Startpunkt
        scale - die Skalierung
        angle - der Drehwinkel (die gehen ja schließlich einmal rund um den ganzen Rand)
        """
        longl = 0.2
        shortl = 0.1
        midl = 0.15
        
        #Der lange Strich am Anfang
        x = 0.0
        y = longl

        parttrans = TransformationMatrix.from_params_simple(movx, movy, scale, angle)      
        my_tm = tm.from_followed_trans(parttrans, tm)

        for i in range(0, 11):
            if i == 0:
                y = longl
            elif i == 5:
                y = midl
            elif i == 10:
                y = longl
            else:
                y = shortl

            x = 0.1 * i
            sx, sy = my_tm.transform(x, 0.0)
            ex, ey = my_tm.transform(x, y)
            canv.create_line(sx, sy, ex, ey)
    
    def get_mm(self, fval):
        """Liefert eine Zahl oder einen Tupel mit zwei Zahlen als string bzw. als
        Tupel von 2 strings
        mit angehaengter Einheit "mm" zurück.
        """
        if isinstance(fval, tuple):
            fst, sec = fval
            answ = (self.get_mm(fst), self.get_mm(sec))
        else:
            answ = '{0}mm'.format(fval)

        return answ

    def get_deg(self, angle):
        """Liefert eine Zahl als string zurück und stellt die Einheit deg dahinter
        für die Nutzung mit svg Bogenmasswinkeln"""
        return '{0}deg'.format(angle)

    def produce_svg(self):
        """Gibt einen string zurück der den Plotter mit den eingestellten Parametern im svg-Format
        enthält.
        """
        pad = 10 #1cm Rand an allen Seiten        
       
        #meine Transformationsmatrix
        tm = TransformationMatrix.from_params_simple(pad, pad, MM_FACT, 0)
        wh = (self.min * self.laengen_m + 2*pad, self.min * self.breiten_m + 2*pad)
        dwg = svg.Drawing('plotter.svg', size=self.get_mm(wh))
        #Der Rahmen
        olx, oly = tm.transform(0.0, 0.0)
        urx, ury = tm.transform(self.min * self.laengen_m, self.min * self.breiten_m)
        dwg.add(dwg.rect((olx, oly),
                         (urx-olx, ury-oly),
                         fill='white',
                         stroke='black'))

         #Laengenskala
        for i in range(0, self.min):
            self.__svg_canc_minute(dwg, tm, self.laengen_m * i,
                                   0.0, self.laengen_m, 0.0) #oben
            self.__svg_canc_minute(dwg, tm, self.laengen_m * (i+1),
                                   self.breiten_m * self.min, self.laengen_m, math.pi) #unten

        #Breitenskala
        for i in range(0, self.min):
            self.__svg_canc_minute(dwg, tm, self.min * self.laengen_m, i * self.breiten_m,
                                   self.breiten_m, math.pi/2) #links
            self.__svg_canc_minute(dwg, tm, 0.0, self.breiten_m * (i + 1),
                                   self.breiten_m, 3/2*math.pi) #rechts

        #die langen waagerechten Striche auf den vollen Breitengraden
        for i in range(1, self.min):
            self.__svg_plotline(dwg, tm, 
                                0.0, self.breiten_m * i,
                                self.laengen_m * self.min, self.breiten_m * i)
            
        #die langen senkrechten Striche auf den vollen Längengraden
        for i in range(1, self.min):
            self.__svg_plotline(dwg, tm, self.laengen_m * i, 0.0,
                                self.laengen_m * i, self.breiten_m * self.min)

        #Die Kompassrose
        self.__svg_printrose(dwg, tm)

        cx = olx + (urx-olx)/2
        cy = oly + (ury-oly)/2
        self.__svg_print_hole(dwg, cx, cy) #ein Loch in die Mitte
        #und ein Loch in jede Ecke
        self.__svg_print_hole(dwg, olx, oly)
        self.__svg_print_hole(dwg, olx, ury)
        self.__svg_print_hole(dwg, urx, oly)
        self.__svg_print_hole(dwg, urx, ury)

        self.__svg_print_scale(dwg)
        self.__svg_print_logo_and_else(dwg)
        dwg.save()

    def __svg_canc_minute(self, dwg, tm, movx, movy, scale, angle):
        """Die Unterteilung für eine einzelne Bogenmitnute drucken
        canv - Der Canvas
        tm - die Grundskalierung
        movx, movy - der Startpunkt
        scale - die Skalierung
        angle - der Drehwinkel (die gehen ja schließlich einmal rund um den ganzen Rand)
        """
        longl = 0.2
        shortl = 0.1
        midl = 0.15
        
        #Der lange Strich am Anfang
        x = 0.0
        y = longl

        parttrans = TransformationMatrix.from_params_simple(movx, movy, scale, angle)      
        my_tm = tm.from_followed_trans(parttrans, tm)

        for i in range(0, 11):
            if i == 0:
                y = longl
            elif i == 5:
                y = midl
            elif i == 10:
                y = longl
            else:
                y = shortl

            x = 0.1 * i
            sx, sy = my_tm.transform(x, 0.0)
            ex, ey = my_tm.transform(x, y)
            dwg.add(dwg.line((sx, sy),
                             (ex, ey),
                             stroke='black'))

    def __svg_plotline(self, dwg, tm, xs, ys, xe, ye):
        """Eine Strecke zwischen zwei Punkten zeichnen
        * dwg - Das Drawing Objekt für die zu zeichnenden Linie
        * tm - Die Transformationsmatrix
        * xs, ys - Der Startpunkt der Strecke
        * xe, ye - Der Endpunkt der Strecke
        """
        x1, y1 = tm.transform(xs, ys)
        x2, y2 = tm.transform(xe, ye)
        dwg.add(dwg.line((x1, y1),
                         (x2, y2),
                         stroke='black'))
        return

    def __svg_printrose(self, dwg, tm):
        """Die Kompassrose darstellen auf einem canvas-Objekt
        * dwg  -das Drawing-Objekt auf dem gezeichnet werden soll
        * tm die Transformationsmatrix
        """
        radius = self.laengen_m * self.min * 0.7 / 2
        xc = self.min / 2 * self.laengen_m
        yc = self.min / 2 * self.breiten_m
        tx1, ty1 = tm.transform(xc, yc)
        dwg.add(dwg.circle((tx1, ty1), 
                           radius * MM_FACT,
                           fill='none',
                           stroke='black'))

        for i in range(0, 360, 5):
            tl = 0.05
            doit = False
            if i % 10 == 0:
                tl = 0.1
                doit = True

            if doit:
                self.__svg_printtick(dwg, tm, xc, yc, radius, i + self.miss, tl, i)

        self.__svg_print_rose_cross(dwg, tm, xc, yc, radius)

    def __svg_print_rose_cross(self, dwg, tm, xc, yc, radius):
        """Das Kreuz in der Mitte der Kompassrose zeichnen
        Das Kreuz besteht aus je einer Linie zwischen 0 und 180 sowie
        einer zwischen 90 und 270 Grad
        """
        bogwink = (2 * math.pi * self.miss) / 360.0
        parttm = TransformationMatrix.from_params_simple(xc, yc, 0.9*radius, bogwink)
        myTm = TransformationMatrix.from_followed_trans(parttm, tm)
        x1, y1 = myTm.transform(0.0, -1.0)
        x2, y2 = myTm.transform(0.0, 1.0)
        dwg.add(dwg.line((x1, y1),
                         (x2, y2),
                         stroke='black'))
        x1, y1 = myTm.transform(-1.0, 0.0)
        x2, y2 = myTm.transform(1.0, 0.0)
        dwg.add(dwg.line((x1, y1),
                         (x2,y2),
                         stroke='black'))

        dwg.add(dwg.text("N",
                         insert=(0.0, -1.4),
                         font_size="0.09",
                         text_anchor="middle",
                         font_weight="bold",
                         transform=myTm.get_svg_str()))
    
    def __svg_printtick(self, dwg, tm, xc, yc, radius, angle, tl, pangle):
        """Einen Strich der Kompassrose mit angeschriebener Gradzahl darstellen
        """
        bogwink = (2 * math.pi * angle) / 360.0
        part_tm = TransformationMatrix.from_params_simple(xc, yc, radius, bogwink)
        my_tm = TransformationMatrix.from_followed_trans(part_tm, tm)
        x1, y1 = my_tm.transform(0.0, -1.0)
        x2, y2 = my_tm.transform(0.0, -1.0 - tl)
        dwg.add(dwg.line((x1, y1),
                         (x2, y2),
                         stroke='black'))
        self.__svg_print_rot_angletxt(dwg, my_tm, angle, 0.0, -1.0 -1.2*tl, pangle)
        
    def __svg_print_rot_angletxt(self, paro, tm, angle, xt, yt, pangle):
        atxt = "{0:03.0f}".format(pangle)
        dtxt = paro.text(atxt,
                         insert=(xt, yt),
                         font_size="0.08",
                         text_anchor="middle",
                         transform=tm.get_svg_str())
        paro.add(dtxt)

    def __svg_print_hole(self, dwg, xc, yc):
        """Ein Loch mit Zentrum an der übergebenen Stelle in ein svg
        objekt malen
        """
        rad = 2.0 * MM_FACT
        dwg.add(dwg.circle((xc, yc), rad, fill="none", stroke="black"))

    def __svg_print_scale(self, dwg):
        """Die Skala zur Kontrolle der Druckgroesse hinzufuegen
        """
        uy = self.min * self.breiten_m + 8
        xc = (self.min * self.laengen_m + 10) / 2.0
        x1, y1 = xc - 25, uy + 2
        x2, y2 = xc + 25, uy + 2
        dwg.add(dwg.line(self.get_mm((x1, y1)), self.get_mm((x2, y2)), stroke="black"))
        dwg.add(dwg.line(self.get_mm((x1, y1-2)),self.get_mm((x1, y1+2)), stroke="black"))
        dwg.add(dwg.line(self.get_mm((x2, y1-2)),self.get_mm((x2, y1+2)), stroke="black"))
        dwg.add(dwg.text("5cm",
                         insert=(xc*MM_FACT, uy*MM_FACT),
                         font_size="9",
                         text_anchor="middle"
                ))

    def __svg_print_logo_and_else(self, dwg):
        lw = 4 * (30000 / self.mass)
        th = 3.8 * (30000 / self.mass)
        y = (self.min * self.breiten_m) * 0.8
        x = (self.min * self.laengen_m) / 2.0
        dwg.add(dwg.text("Maßstab: 1:{}".format(self.mass), 
                         insert=self.get_mm((x, y+lw)), 
                         font_size=self.get_mm(th),
                         text_anchor="middle"))
        dwg.add(dwg.text("{:0.0f}°N".format(self.breite),
                         insert=self.get_mm((x, y+2*lw)),
                         font_size=self.get_mm(th),
                         text_anchor="middle"))
        dwg.add(dwg.text("Missweisung: {:0.1f}°".format(self.miss),
                         insert=self.get_mm((x, y+3*lw)),
                         font_size=self.get_mm(th),
                         text_anchor="middle"))
        picscale = 0.333 * (30000 / self.mass) / MM_FACT
        picwidth = 248 * picscale
        picheight = 150 * picscale
        y = self.min * self.breiten_m * 0.15 - picheight/2
        self.__svg_add_image(dwg, "Wimpelh150.jpg",
                             x -  picwidth/2, y,
                             "{}mm".format(picwidth), "{}mm".format(picheight))
        dwg.add(dwg.text("Essener-Faltboot-Fahrer e.V.",
                         insert=self.get_mm((x, y + picheight + lw )),
                         font_size=self.get_mm(th),
                         text_anchor="middle"))

    def __svg_add_image(self, dwg, filename, x, y, width, height):
        absp = os.path.abspath(filename)
        imgurl="file:///{}".format(absp)
        img = dwg.image(href=imgurl, insert=self.get_mm((x, y)), size=(width, height))
        img.fit()
        dwg.add(img)

    def __print_scale(self, canv, tm, x, y):
        x1, y1 = x-25, y
        x2, y2 = x+25, y
        canv.create_line(x1, y1, x2, y2)
        canv.create_line(x1, y1-5, x1, y1+5)
        canv.create_line(x2, y1-5, x2, y1+5)
        canv.create_text(x, y-6, text="5cm", font=("Helvetika", "8", "bold"))

    def __print_logo_and_else(self, canv, tm, x, y):
        lw = 5 * 30000 / self.mass
        #halfwidth = 14 * 30000 / self.mass
        x1, y1 = tm.transform(x, y)
        #bdx1, bdy1 = tm.transform(x - halfwidth, y - 5)
        #bdx2, bdy2 = tm.transform(x + halfwidth, y + 3*lw)
        #canv.create_rectangle(bdx1, bdy1, bdx2, bdy2, fill="white", outline='white')
        canv.create_text(x1, y1, text="Maßstab: 1:{}".format(self.mass), font=("Helvetika", "7", "bold"))
        x1, y1 = tm.transform(x, y+lw)
        canv.create_text(x1, y1, text="{:0.0f}°N".format(self.breite), font=("Helvetika", "7", "bold"))
        x1, y1 = tm.transform(x, y+2*lw)
        canv.create_text(x1, y1, text="Missweisung: {:0.1f}°".format(self.miss), font=("Helvetika", "7", "bold"))        
        
        