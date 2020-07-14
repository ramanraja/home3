from CryptoConfig import CryptoConfig

jmessage = {"name" : "Rajaram", "age":55, "city": "Coimbatore North"} 
print ("secret message:")
print (jmessage)
print()

crypto = CryptoConfig (debug=True)
encrypted = crypto.encrypt_json (jmessage)
decrypted = crypto.decrypt_json (encrypted)

print ("recovered message:")
print (decrypted)
print()    
if (jmessage == decrypted):
    print ("Message verified OK.")
else:
    print ("Message verification failed.")    