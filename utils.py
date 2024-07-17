from random import randint
from sympy import Poly
from sympy.abc import X
from ldei import LDEI
from dleq import DLEQ

# Generate random key winthin order cyclic group
def generateKeys(q: int, h: int):
    privateKey = randint(1, q-1) #Range starts at 1 because 0 is not a valid public key
    publicKey = pow(h, privateKey, q)
    return publicKey, privateKey

# Finding a valid generator for a given cyclic group, only works when q is prime, but in this program always will be
# TODO: Comprobar la utilidad de esto, si q es primo siempre va a devolver 2 porque todos los elementos son generadores
# Used algorithm found in https://github.com/evapln/albatross/blob/master/CyclicGroup/src/func.cpp
# Generator should comply with gen**2 mod q != 1 and gen**q mod q != 1
def findGenerator(q : int):
    for i in range(2, 2*q + 1):
        temp = pow(i, 2, q)
        if temp == 1:
            continue
        temp = pow(i, q, q)
        if temp == 1:
            continue
        return i # Return i if previous conditions fulfilled
    return -1 # Return -1 if no generator found

# Generate random polynom inside cyclic group of order q
# TODO: Asegurar si el polinomio se "cifra" con el generador antes de computarlo y generar las partes de πPPVSS (fichas.pdf, pag 7)
def generatePolynom(t : int, l : int, q : int): 
    coefs = [randint(0, q) for _ in range(int(t + l))]
    poly = Poly(coefs, X)
    poly.set_modulus(q)
    return poly

# Compute polynom for all n participants inside cyclic group
# Return plain computed shares and cyphered ones with public key
def computePolynom(poly, pk, l:int, n, q, h):

    #Implementacion de πPPVSS del documento (fichas.pdf, pag. 15) 

    # Check https://docs.sympy.org/latest/modules/polys/internals.html#manipulation-of-dense-univariate-polynomials-with-finite-field-coefficients

    secrets = [-1] * int(l)
    encryptedSecrets = [-1] * int(l)

    for i in range(0, int(l)):
        secrets[i] = poly.eval(X, -i) % q
        encryptedSecrets[i] = pow(h, secrets[i]) % q

    shares = [-1] * int(n)
    encryptedShares = [-1] * int(n)
    for i in range(1, n+1):
        shares[i-1] = poly.eval(X,i) % q
        encryptedShares[i-1] = int(pow(pk, shares[i-1]) % q)

    return secrets, encryptedSecrets, shares, encryptedShares



# Generate LDEI proof for a computed polynom using a list of his coefficients in case coef[i] = 0
# TODO: consultar esto, no queda claro si se hace con todas las claves publicas o solo con la propia
def generateLDEI(poly, encryptedShares, pk, n, q, t, l) -> LDEI:

    auxPolynom = generatePolynom(t+1, l, q) # Generating random polynom of degree t+l+1
    auxComputedPoly = [-1] * n
    for i in range(1, n+1):
        auxComputedPoly[i-1] = auxPolynom.eval(X, i) % q

    a = [-1] * len(auxComputedPoly)
    for i in range(0, n):
        a[i] = pow(pk, auxComputedPoly[i]) % q

    # Literature about this process calculates e as the hash of the auxiliar polynom
    # We use "custom" hash function because lists are not hashable    
    e = (sum((a[i-1] * i * encryptedShares[i-1]) for i in range(1, n+1))) % q

    temp = poly.mul_ground(e).set_modulus(q)
    
    z = temp.add(auxPolynom).set_modulus(q)

    return LDEI(a, e, z)


def verifyLDEI(ldei: LDEI, publicKey, shares, n, q):

    auxE = (sum((ldei.a[i-1] * i * shares[i-1]) for i in range(1, n+1))) % q

    auxZeval = [-1] * n

    for i in range(1, n+1):
        auxZeval[i-1] = ldei.z.eval(X, i) % q

    for i in range(n):
        temp1 = pow(publicKey, auxZeval[i]) % q
        temp2 = pow(shares[i], auxE) % q
        temp3 = (temp2 * ldei.a[i]) % q
        if(temp3 != temp1):
            print("LDEI no valido", i)
            break


def verifyDLEQ(dleq : DLEQ, encryptedShares, dleqShares, q):

    auxE = (sum((dleq.a[i] * dleqShares[i] * encryptedShares[i]) for i in range(0, len(dleq.a)))) % q

    if auxE != dleq.e:
        return False
    
    for i in range(len(dleq.a)):
        temp1 = (pow(encryptedShares[i], dleq.z)) % q
        temp2 = (pow(dleqShares[i], dleq.e)) % q
        temp3 = (temp1 * temp2) % q
        if dleq.a[i] != temp3:
            return False
        
    return True
