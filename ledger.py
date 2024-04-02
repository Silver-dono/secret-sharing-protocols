
class ledger:

    # Defining global variable for the ledger
    nParticipants = -1  # n
    tolerance = -1      # t
    sizeDomain = -1     # q
    generator = -1      # h
    l = -1              # l

    publicKeys = []

    def __init__(self, n: int, q: int, h: int):
        self.nParticipants = n
        self.sizeDomain = q
        self.generator = h

        self.tolerance = n/3 # A bit arbitrary this value
        self.l = n - 2 * self.tolerance


    def addPublicKey(self, ordinal:int, pk: int):
        if self.publicKeys[ordinal]:
            self.publicKeys[ordinal] = pk
        else:
            if len(self.publicKeys) == ordinal:
                self.publicKeys.append(pk)
            else: 
                for i in range(len(self.publicKeys)-1, ordinal-1):
                    self.publicKeys.append(None)
                self.publicKeys.append(pk)