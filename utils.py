from random import randint
from sympy import Poly
from sympy.abc import X

# Generate random key winthin order cyclic group
def generateKeys(q: int, h: int):
    privateKey = randint(1, q-1) #Range starts at 1 because 0 is not a valid public key
    publicKey = pow(h, privateKey) % q
    return publicKey, privateKey

# Finding a valid generator for a given cyclic group
# Used algorithm found in https://github.com/evapln/albatross/blob/master/CyclicGroup/src/func.cpp
# Generator should comply with gen**2 mod q != 1 and gen**q mod q != 1
def findGenerator(q : int):
    for i in range(2, 2*q + 1):
        temp = pow(i, 2) % q
        if temp == 1:
            continue
        temp = pow(i, q) % q
        if temp == 1:
            continue
        return i # Return i if previous conditions fulfilled
    return -1 # Return -1 if no generator found

# Generate random polynom using SymPy library of degree t + l following πPPVSS,
# inside cyclic group of order q
# TODO: Asegurar si el polinomio se "cifra" con el generador antes de computarlo y generar las partes de πPPVSS (fichas.pdf, pag 7)
def generatePolynom(t : int, l : int, q : int): 
    coefs = [randint(0, q) for _ in range((int)(t + l))]
    return Poly(coefs, X), coefs

# Compute polynom for all n participants inside cyclic group
# Return plain computed shares and cyphered ones with public key
def computePolynom(poly: Poly, pk, n, q):
    shares = [-1] * (n - 1)
    cypheredShares = [-1] * (n - 1)

    for i in range(1, n):
        shares[i-1] = poly.eval(X, i) % q
        cypheredShares[i-1] = pow(pk, shares[i-1]) % q

    return shares, cypheredShares

# Generate LDEI proof for a computed polynom
# TODO: consultar esto, no queda claro si se hace con todas las claves publicas o solo con la propia
def generateLDEI(poly : Poly, polyCoefs, pk, n, q, t, l):

    auxPolynom, auxPolynomCoefs = generatePolynom(t, l, q)
    auxComputedPoly = computePolynom(auxPolynom, pk, n, q)[0] 

    aux = [-1] * len(auxComputedPoly)
    for i in range(1, n):
        aux[i-1] = pow(pk, auxComputedPoly[i-1]) % q

    # Literature about this process calculates e as the hash of the auxiliar polynom
    # We use "custom" hash function because lists are not hashable    
    e = sum((aux[i-1] * i) for i in range(1, n)) % q

    coefficients = [e * c for c in polyCoefs]
    
    z = [(coefficients[i] + auxPolynomCoefs[i]) % q for i in range(len(coefficients))]

    return Poly(z, X)