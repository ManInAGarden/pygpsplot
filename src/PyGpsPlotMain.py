"""Hauptmodul des GPS-Plotters
"""
#! /usr/bin/python3
#main prog with tcl gui
import tkinter as tki
#from tkinter.filedialog import askdirectory
from TclWinBase import *
from PlotterPrinter import *

class PyGpsPlotMain(TclWinBase):
    """Main Window für PyGpsPlotter
    """

    def make_gui(self, title):
        """Die GUI im Haupt-Frame aufbauen
        """
        self.setwintitle(title)

        row = 0
        self.set_defaults()
        self.breite = self.makeentry(erow=row, lrow=row,
                                     caption="Breitengrad",
                                     width=2,
                                     textvariable=self.breitengrad_tv)
        row += 1
        self.minuten = self.makeentry(erow=row, lrow=row,
                                      caption="Anzahl Minuten",
                                      textvariable=self.minuten_tv,
                                      width=2)
        row += 1
        self.minuten = self.makeentry(erow=row, lrow=row,
                                      caption="Maßstab",
                                      textvariable=self.massstab_tv,
                                      width=6)
        row += 1
        self.missweisung = self.makeentry(erow=row, lrow=row,
                                          caption="Missweisung /°",
                                          textvariable=self.missweisung_tv,
                                          width=3)
        row += 1
        self.create_plotter_bu = self.makebutton(erow=row,
                                                 caption="Anzeigen",
                                                 sticky=tki.W+tki.S,
                                                 cmd=self.view_plotter)
        self.create_svg_bu = self.makebutton(erow=row, ecol=1,
                                             caption='SVG erzeugen',
                                             sticky=tki.W+tki.S,
                                             cmd=self.create_svg)
        self.canvas = self.makecanvas(ecol=2, rspan=row+1,
                                      width=400, height=600,
                                      bg="white")
        self.canvas.bind("<Configure>", self.resize_canvas)

        for i in range(0, row):
            self.rowconfigure(i, weight=0, pad=5)

        self.rowconfigure(row, weight=1, pad=5)

        self.columnconfigure(0, weight=0, pad=5)
        self.columnconfigure(1, weight=0, pad=5)
        self.columnconfigure(2, weight=1, pad=5)

        #end in the end pack ...
        self.pack(fill=tki.BOTH, expand=tki.YES)

    def resize_canvas(self, event):
        """event callback fuer die Groessenaenderung des cnvas
        """
        self.view_plotter()

    def set_defaults(self):
        """Die defaults für die Eingabefelder in deren Bind-Variablen setzen
        """
        self.breitengrad_tv = self.getvar(54.0)
        self.missweisung_tv = self.getvar(0.0)
        self.minuten_tv = self.getvar(3)
        self.massstab_tv = self.getvar(30000)

    def loaded(self):
        """Das Window wurde aufgebaut
        """
        self.isloaded = True

    def view_plotter(self):
        """cmd um den Plotter auf dem Canvas darzustellen
        """
        self.canvas.delete("all")
        missweisung = self.missweisung_tv.get()
        massstab = self.massstab_tv.get()
        minuten = self.minuten_tv.get()
        breit = self.breitengrad_tv.get()
        plotter = PlotterPrinter(breit, massstab, missweisung, minuten)
        plotter.print_on_canvas(self.canvas)

    def create_svg(self):
        """cmd um den Plotter im svg-format zu produzieren
        """
        missw = self.missweisung_tv.get()
        mass = self.massstab_tv.get()
        bmi = self.minuten_tv.get()
        brg = self.breitengrad_tv.get()
        plotter = PlotterPrinter(brg, mass, missw, bmi)
        svg = plotter.produce_svg()

if __name__ == '__main__':
    MW = PyGpsPlotMain("PyGpsPlot")
    MW.mainloop()