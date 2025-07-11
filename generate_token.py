import jwt
import datetime

JWT_SECRET = 'seu-segredo-super-secreto'

payload = {
    'sub': 'test-user', 
    'iat': datetime.datetime.now(datetime.timezone.utc),
    'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
}

token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

print("Seu token de teste (copie e use no header 'Authorization: Bearer <token>'):")
print(f"\n{token}\n")