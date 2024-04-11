import utils
import ledger
import parts
# TODO: Instantiate participants and ledger and simulate an use of the protocol
n, q = 9, 11
h = utils.findGenerator(q)

auxLedger = ledger.Ledger(n, q, h)
t, l = auxLedger.getT(), auxLedger.getL()

part1 = parts.Part(1, t, l, n, q, h)

print(part1.publicKey, part1.polynom, part1.ldei)