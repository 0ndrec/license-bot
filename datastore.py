import urllib3
import json
from pydantic import BaseModel

urllib3.disable_warnings()


source = 'https://data.gov.il/api/3/action/datastore_search?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3&q={}'


class Car(BaseModel):
    mispar_rechev: str
    tozeret_nm: str
    kinuy_mishari: str
    ramat_gimur: str
    shnat_yitzur: str
    mivchan_acharon_dt: str
    tokef_dt: str
    tzeva_cd: str
    sug_degem: str
    rank: str
    tzeva_rechev: str


def get(license_number):
    url = source.format(license_number)
    try:

        http = urllib3.PoolManager(cert_reqs='CERT_NONE')
        r = http.request('GET', url)
        data = json.loads(r.data.decode('utf-8'))

        if data['success'] == True:
            if len(data['result']['records']) == 0:
                return None
            else:
                return Car(**data['result']['records'][0])
        else:
            return None

    except:
        return None
