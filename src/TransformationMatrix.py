"""Graphiktransformationen im R2
"""
import math
import numpy


class TransformationMatrix():
    """T-Matrix Klasse die nach der Initialisierung mit einer der bereitgestellten Klassenmethoden
    zur Koordinatenumrechung im R2 benutzt werden kann.
    """

    @classmethod    
    def from_params_simple(cls, movex, movey, scalefact, rotateby):
        """Konstruktor mit Translationsort, Skalierungsfaktor (gleichf. in x und y) sowie einem Rotationswinkel
        """
        res = TransformationMatrix()
        tsmat = numpy.matrix([
            [scalefact, 0, movex],
            [0, scalefact, movey],
            [0, 0, 1]])

        rotmat = numpy.matrix([
            [math.cos(rotateby), -math.sin(rotateby), 0],
            [math.sin(rotateby), math.cos(rotateby), 0],
            [0, 0, 1]])
        
            
        res.transmat = tsmat * rotmat
        return res

    
    @classmethod
    def from_trans_mat(cls, other):
        """Konstruktor fuer eine T-Matrix als Kopie einer anderen T-Matrix
        """
        res = TransformationMatrix()
        res.transmat = other.transmat
        return res

    
    @classmethod
    def from_followed_trans(cls, firsttrans, nexttrans):
        """Konstruktor für eine T-Matrix aus der Abfolge zweier anderer T-Matrizen
        Dabei wird zuerst firstTrans und dann nextTrans angewendet
        """
        res = TransformationMatrix()
        res.transmat = nexttrans.transmat * firsttrans.transmat
        return res

    
    def transform(self, ptx, pty):
        """Liefert x,y eines transformierten 2D-Vektors mit dieser Transformationsmatrix
        ptx, pty sind dabei die x- und die y-Koordinate des zu transformierenden Verkrors
        """
        hvec = numpy.array([ptx, pty, 1.0])
        res = numpy.dot(self.transmat.A, hvec)
        return res[0], res[1]