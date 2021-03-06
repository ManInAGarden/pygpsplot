from plotterprinter import *
from transformationmatrix import *

class TkiPlotterPrinter(PlotterPrinter):
    """Plotter Printer, der auf ein Canvas Widget plottet
    """

    def print(self, canv):
        """Den Plotter auf einem TK-Canvas Widget darstellen
        * canv - das Canvas Widget
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

    def __print_scale(self, canv, tm, x, y):
        x1, y1 = x-25, y
        x2, y2 = x+25, y
        canv.create_line(x1, y1, x2, y2)
        canv.create_line(x1, y1-5, x1, y1+5)
        canv.create_line(x2, y1-5, x2, y1+5)
        canv.create_text(x, y-6, text="5cm", font=("Helvetika", "8", "bold"))

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

    def __print_logo_and_else(self, canv, tm, x, y):
        """Das Logo und die Angaben zum Massstab, Missweisung usw. auf dem Plotter zeichnen
        """
        scale = tm.get_scale() / 2.9431599
        lw = 3 * scale * self.related_30_scale       
        fontsize = "{0:0.0f}".format(8 * scale  * self.related_30_scale)
        x1, y1 = tm.transform(x, y)
        canv.create_text(x1, y1, text="Maßstab: 1:{}".format(self.mass), font=("Helvetika", fontsize, "bold"))
        x1, y1 = tm.transform(x, y+lw)
        canv.create_text(x1, y1, text="{:0.0f}°N".format(self.breite), font=("Helvetika", fontsize, "bold"))
        x1, y1 = tm.transform(x, y+2*lw)
        canv.create_text(x1, y1, text="Missweisung: {:0.1f}°".format(self.miss), font=("Helvetika", fontsize, "bold"))        