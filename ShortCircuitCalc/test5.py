from ShortCircuitCalc.tools import *


print(T(160, 'Д/Ун-11'))
print(repr(T(160, 'Д/Ун-11')))

print(W('ВВГ', 5, 1, 1000))
print(repr(W('ВВГ', 5, 1, 1000)))

print(Q(160))
print(repr(Q(160, 'Пускатель')))

print(QF(40))
print(repr(QF(40)))

print(QS(63))
print(repr(QS(63)))

print(R())
print(repr(R()))

print(Line())
print(repr(Line()))

print(Arc())
print(repr(Arc()))


chain1 = ElemChain(
    [
        T(160, 'Д/Ун-11'),
        W('ВВГ', 5, 120, 1000),
        QS(100),
        QF(40)
    ]
)

chain2 = ElemChain(
    {
        'TCH': T(160, 'Д/Ун-11'),
        'w1': W('ВВГ', 5, 120, 1000),
        'QS1': QS(100),
        'QF1': QF(40)
    }
)
# print(chain1.one_phase_current_short_circuit)
# print(repr(chain1))
# print(*(f'{k}: {v}' for k, v in chain2[1].items()))
# print(chain2[1])
# print(repr(chain2))
