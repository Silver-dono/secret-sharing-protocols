from flask import Flask, request, jsonify, session
from sympy import Poly, Integer
import json
import utils


ordinal = -1



def create_app(nOrdinal):
    global ordinal
    ordinal = nOrdinal
    app = Flask("Participant " + str(ordinal))

    import secrets as sessionSecret
    app.secret_key = sessionSecret.token_hex()

    @app.route('/setup_variables', methods = ["POST"])
    def setupVariables():
        bodyContent = request.json
        print(bodyContent)
        session['n'] = bodyContent['n']
        session['t'] = bodyContent['t']
        session['q'] = bodyContent['q']
        session['h'] = bodyContent['h']
        session['l'] = bodyContent['l']
        return "Variables saved"


    @app.get("/get_public_key")
    def sendPublickKey():
        if(validateContext()):
            q : int = session.get('q')
            h : int = session.get('h')
            if('publicKey' not in session):
                pk, sk = utils.generateKeys(q, h)
                session['publicKey'] = pk
                session['secretKey'] = sk
                return jsonify({'pk' : pk})
            else:
                return jsonify({'pk' : session.get('publicKey')})
        else:
            return "Non valid context"    

    @app.get("/get_encrypted_shares")
    def sendEncryptedShares():
        if(validateContext() or 'publicKey' not in session):
            t = session.get('t')
            l = session.get('l')
            q = session.get('q')
            publicKey = session.get('publicKey')
            n = session.get('n')
            h = session.get('h')
            if('polynom' not in session):
                session['polynom'] = utils.generatePolynom(t, l, q)
            if('secrets' not in session):
                secrets, encryptedSecrets, shares, encryptedShares = utils.computePolynom(session.get('polynom'), publicKey, l, n, q, h)
                session['secrets'] = secrets
                session['encryptedSecrets'] = encryptedSecrets
                session['shares'] = shares
                session['encryptedShares'] = encryptedShares
                
                return jsonify({'eS' : encryptedShares})
            else:
                return jsonify({'eS' : session.get('encryptedShares')})
        else:
            return "Non valid context"        


    @app.get("/get_ldei")
    def sendLDEI():
        if(validateContext() 
           or 'publicKey' not in session 
           or 'polynom' not in session
           or 'encryptedShares' not in session):
            t = session.get('t')
            l = session.get('l')
            q = session.get('q')
            publicKey = session.get('publicKey')
            n = session.get('n')
            polynom = session.get('polynom')
            encryptedShares = session.get('encryptedShares')
            if('computedLDEI' not in session):
                computedLDEI = utils.generateLDEI(polynom, encryptedShares, publicKey, n, q, t, l)
                session['computedLDEI'] = computedLDEI
                return jsonify({'ldei' : computedLDEI})
            else:
                return jsonify({'ldei' : session.get('computedLDEI')})
        else:
            return "Non valid context"        

    def validateContext():
        if(session.get('n') == -1 
        or session.get('t') == -1
        or session.get('q') == -1
        or session.get('h') == -1
        or session.get('l') == -1
        ):
            return False
        else:
            return True

    def convert(o):
        if isinstance(o, Integer):
            return int(o)  
        raise TypeError

    return app