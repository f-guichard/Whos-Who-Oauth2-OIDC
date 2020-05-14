## Rapide projet pour expliciter un usage concret d'OIDC

## FAQ 
# Forward de port local pour utiliser son navigateur de bureau
ssh -fN -L 9998:127.0.0.1:5000 ip_de_ma_machine_distante

Il faut tapper ensuite https://127.0.0.1:9998 dans son navigateur

# Pour contourner le problème de certificat
Sur la machine qui exécute l'application Flask : 
```
mkdir .certs
openssl req -x509 -newkey rsa:4096 -nodes -out .certs/mon_certificat_serveur.pem -keyout .certs/ma_cle_privee.pem -days 7
```
=> Réponses : FR/IDF/PARIS/FAKE COMPANY/DEV DPT/whoswho.fr/support@whoswho.fr

sur la machine cliente : Editer C:\Windows\system32\drivers/etc/hosts ou /etc/hosts selon votre os
pour rajouter :
``` 
127.0.0.1   whoswho.fr
```

# Pour exporter automatiquement ses variables d'environnement
source .credentials.oauth2 .credentials.skey

# Si pb 401 lors de la création du client oauth2
Bien valider les valeurs de _CLIENT_ID, _CLIENT_SECRET dans la console.developers.google.com
Bien valider que app_redirect_uri correspond au domaine autorise dans console.developers.google.com

# Pour contourner le problème Insecure Transport Error
export OAUTHLIB_INSECURE_TRANSPORT=1