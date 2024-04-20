from ShortCircuitCalc.database import *
import multiprocessing


if __name__ == '__main__':
    p1 = multiprocessing.Process(target=Cable.show_table)
    p2 = multiprocessing.Process(target=Transformer.show_table)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
