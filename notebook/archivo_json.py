import requests

url = "https://datos.cdmx.gob.mx/api/3/action/package_show"
params = {"id": "afluencia-diaria-del-metro-cdmx"}

respond = requests.get(url, params)
package_data = respond.json()

#print(package_data)

for recurso in package_data["result"]["resources"]:
    print(recurso["name"], "->", recurso["id"])