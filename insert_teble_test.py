import sqlalchemy as sa
import sqlalchemy.orm
from create_electrical_product_catalog import engine, PowerNominal, VoltageNominal, Scheme, Transformer

Session = sa.orm.sessionmaker(engine)

with Session() as session:
    for i in [25, 40, 63, 100, 160, 250, 400, 630, 1000, 1600, 2000]:
        if i not in list(map(lambda x: x.power, session.query(PowerNominal))):
            session.execute(sa.insert(PowerNominal), [{'power': i}])
    session.commit()
