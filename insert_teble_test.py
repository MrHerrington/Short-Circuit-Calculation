import sqlalchemy as sa
from tools import Session
from database.transformer import PowerNominal, VoltageNominal, Scheme, Transformer


with Session() as session:
    for i in [25, 40, 63, 100, 160, 250, 400, 630, 1000, 1600]:
        if i not in list(map(lambda x: x.power, session.query(PowerNominal))):
            session.execute(sa.insert(PowerNominal), [{'power': i}])
    session.commit()
