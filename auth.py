import base64

def httpbasicauth(username, password):
        authinfo = base64.b64encode("{}:{}".format(username,password).encode('utf-8'))
        authinfo = "Basic {}".format(authinfo.decode('utf-8'))
        return authinfo