"""Plotter Printer Module, stellt im wesentlichen die gleichnamige Klasse bereit
"""
import math
import os
from tkinter import *
import svgwrite as svg
from transformationmatrix import *


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
        self.laengen_m = self.breiten_m * math.cos(self.breite / 180 * math.pi)
        self.related_30_scale = (30000 / self.mass)

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
