import rsa

PRIVATE_KEY = '-----BEGIN RSA PRIVATE KEY-----\nMIIB0QIBAAJiAPmIdDqtoCR39fLL64zVI/bIaXIAKhbf8C1qVb4XyYdTXLFEmcWE\n2coM2rdcaqPhODJNcOyCCjqFLrn3vHj7q82EvujH7OigPYZFwDH86xx0CHC5vLRE\nMy3ojflN/+E0UIECAwEAAQJhEsNv+fmUUSm0FM3AqJZeXfAz/Z6Fi7LLHJ8iU2j2\nfnaGQc4mwfN7bPYKfD82xG36v0M+nzpsNe10fJ2eIRRUUUkOmntZ60x+kg7XKDNJ\nm52UB39jRIBJYzYRZZ4HG/X8AQI0D69kZEbmwlzsoT06Y/a0itjKmNhi6lQvjwlj\nNv0FsClaIykLRpU1r5RarsnN7S5wusiItQIuD+itX22lrtRrvPg1sXwoRxPtNljV\nZdwyqS4R3Kjt8J1RnxmDiR9Xi1JuNzIEHQI0B7UcE9pzUlbvQFwh8TUtinz1MR5D\nnPo5VIQ8aKz0upfXXyewDsMLWngAB5vKwR3s7xvTcQIuCjRAIBmAUCdIA6lhJzpv\ny0dou5c3KWKXzBQUuOhR1ifSFq6Sw/0qdd6lexnFsQI0AO9EXgsS7HZ1xAFtB07+\nvgfGYSrj1tctAjBM37wz2ob3OcwWzG7U2Gazsv73VrJQFMbg5Q==\n-----END RSA PRIVATE KEY-----\n'
PUB_KEY = '-----BEGIN RSA PUBLIC KEY-----\nMGkCYgD5iHQ6raAkd/Xyy+uM1SP2yGlyACoW3/AtalW+F8mHU1yxRJnFhNnKDNq3\nXGqj4TgyTXDsggo6hS6597x4+6vNhL7ox+zooD2GRcAx/OscdAhwuby0RDMt6I35\nTf/hNFCBAgMBAAE=\n-----END RSA PUBLIC KEY-----\n'


def generate_key():
    (public_key, private_key) = rsa.newkeys(777)
    pub = public_key.save_pkcs1()
    # 将公钥保存到文件
    with open('public.pem', 'w+') as fp:
        fp.write(pub.decode('utf-8'))
        fp.close()
    pri = private_key.save_pkcs1()
    # 将私钥保存到文件
    with open('private.pem', 'w+') as fp:
        fp.write(pri.decode('utf-8'))
        fp.close()


if __name__ == '__main__':
    pubkey = rsa.PublicKey.load_pkcs1(PUB_KEY)
    prikey = rsa.PrivateKey.load_pkcs1(PRIVATE_KEY)
    string = 'lazzy'
    crypt = rsa.encrypt(string.encode('utf-8'), pubkey)
    de_crypt = rsa.decrypt(crypt, prikey)
    print(de_crypt == string.encode('utf-8'))


