from datetime import datetime, timedelta, timezone
import random


raw_users = [{
  "email": "nkeeltagh0@sfgate.com",
  "password": "rH7|1Wb)ME/gT,\\"
}, {
  "email": "fcowie1@java.com",
  "password": "rR6&{Q#g59ll5G!"
}, {
  "email": "atruin2@senate.gov",
  "password": "wQ3\"@phxXm1$voG"
}, {
  "email": "djendas3@marketwatch.com",
  "password": "sD1>eK5U%/(2N+"
}, {
  "email": "probak4@phpbb.com",
  "password": "lI7$!>cwPJA<mg"
}, {
  "email": "fhansemann5@home.pl",
  "password": "wG7)tD&6%Y8"
}, {
  "email": "ldoidge6@nyu.edu",
  "password": "cX3=i*gR5"
}, {
  "email": "mharte7@toplist.cz",
  "password": "dP5_PT@dbY1s*|7"
}, {
  "email": "mfrancescotti8@multiply.com",
  "password": "rC6\"~iM2,"
}, {
  "email": "ckonert9@geocities.jp",
  "password": "nW6$cBD5??NwElw"
}]

start = datetime(2025, 10, 26, 10, 0, 0, tzinfo=timezone.utc)
end = datetime(2025, 10, 26, 22, 0, 0, tzinfo=timezone.utc)

raw_verifications = []

for _ in range(20):
    random_seconds = random.randint(0, int((end - start).total_seconds()))
    dt = start + timedelta(seconds=random_seconds)
    raw_verifications.append(dt)
