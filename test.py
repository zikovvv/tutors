from dataclasses import dataclass

@dataclass
class Dota :
    asd : str
    asd1 : str

clip = lambda x, mi, ma : ((x if x > mi else mi) if x < ma else ma) if ma > mi else ma

if __name__ == '__main__':
    print(clip(-1123, -1000, 4))
