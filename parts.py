from sympy import poly
import utils

class Part:

    # Ordinal number of participant to distinguish properly
    ordinal = -1

    # Keys
    publicKey = -1 # pk -> h^sk
    privateKey = -1 # sk

    # Plain polynom
    polynom = poly()

    shares = []
    cypheredShares = []

    ldei = []

    # Initiate participant saving global variables and generating keys
    def __init__(self, ordinal: int, t: int, l: int, n: int, q: int, h: int):
        self.ordinal = ordinal
        self.publicKey, self.privateKey = utils.generateKeys(q, h)
        self.polynom = utils.generatePolynom(t, l, q)
        self.shares, self.cypheredShares = utils.computePolynom(self.polynom, self.publicKey, n, q)
        self.ldei = utils.generateLDEI(self.polynom, self.pk, n, q, t, l)

    # Return the ordinal number of the participant and his public key
    def sendPublicKey(self):
        return self.ordinal, self.publicKey

    # Return the ordinal number of the participant and his cyphered shares
    def sendCypheredShares(self):
        return self.ordinal, self.cypheredShares