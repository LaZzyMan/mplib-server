import rsa
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto import Random
import base64

RANDOM_GENERATOR = Random.new().read
PUB_KEY = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCMRWy62srQJhljxzaxbSjbl6R3
bA4dXTEdVhcSB7ZDM54axZFmikmOdiAZ7kD4xdRysdp1P+vRjBIWMFJeyYN8v/p+
NqJT8o2Y8nJdmBTX7e0JkwIiEgSORlXai+eR3e8eBOtBQ8EUwSSi0bgkLOkOTQ7/
CPDsDJ7vp7Q2+WLvlQIDAQAB
-----END PUBLIC KEY-----'''

PRIVATE_KEY = '''-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQCMRWy62srQJhljxzaxbSjbl6R3bA4dXTEdVhcSB7ZDM54axZFm
ikmOdiAZ7kD4xdRysdp1P+vRjBIWMFJeyYN8v/p+NqJT8o2Y8nJdmBTX7e0JkwIi
EgSORlXai+eR3e8eBOtBQ8EUwSSi0bgkLOkOTQ7/CPDsDJ7vp7Q2+WLvlQIDAQAB
AoGBAIo/onpHSbz8z+lXXsBgJfTH8IEDLqYiQ1X2k6Zhk3GIXjtknXnCsdyG7/ye
pcqKsGiaggUtiu5sbycPWR+y3LORtNcJnyjuulKej4YMTyJMlqKh60CKwRqEwX1A
hL4+n0nyOzsSY1TSxfSxrIXSwpacjHrjl5IaXLOlXrD+gGvBAkEAu5qUjMz4IJoV
ErVO0pHSCYEV1clNtrCIn2Ye57yld5mFon+QLhSGef7dEYQBAQkuC2ZufGnq4m2S
g6OBOhQR4wJBAL9pMyppSsUxNgfOqxol8AgWiY0ZflgmqRvSvr2WqvGZmpkQAbFM
Aw+udlOyzsVddfqfh8wvR/1tfNbhwkA40icCQCZV4CUlfU6sLcI06nZ89b6bcirN
h+PdDw4DgC06j1VxOa2LA5tm9lPXkLUTlGDxz0blF4601hqO6XGc57tGfqECQQCT
CBZbj8H1s5WTbbeVQGsfa2CB2IFq6VehncMTEzeAmsNcrCUAsijv1M3kAUg/50kH
GaBQwkkEbSQmVAjJGFylAkBDibHDD1cms1DHyqFMxqkPG0Y50N0eu1hU7brZfQPB
kNRpW9f/TE97QOb8ux867n2i0/q0YpjWSTY6XsZncKkI
-----END RSA PRIVATE KEY-----'''


def generate_key():
    rsa_key = RSA.generate(1024)
    pri = rsa_key.exportKey()
    with open('private.pem', 'w+') as f:
        f.write(pri.decode())
        f.close()
    pub = rsa_key.publickey().exportKey()
    with open('public.pem', 'w+') as f:
        f.write(pub.decode())
        f.close()


if __name__ == '__main__':
    # generate_key()
    rsa_key = RSA.importKey(PUB_KEY)
    x = PKCS1_v1_5.new(rsa_key).encrypt('lazzy'.encode())
    x = base64.b64encode(x).decode()
    # x = 'f1lQLhP19w6p1Q0jgA2i3EIFWtnA/wj5aTp8mJn8PLEeIJ2GxLohPDMUr1GNbngIjVEmAuIFbLLku3BL8NEsll+xlovWOXV/cA5W/INPpJlUz8kBtIOn9Yj9zTqUAy2LnHHrZm0v3TapY9J/TSBYR/DjV7dV2PxZH4WMLNPyRgc='
    rsa_privkey = RSA.importKey(PRIVATE_KEY)
    y = PKCS1_v1_5.new(rsa_privkey).decrypt(base64.b64decode(x), None)
    print(y == 'lazzy'.encode('utf-8'))


