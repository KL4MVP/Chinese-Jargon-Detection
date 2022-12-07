from bs4 import BeautifulSoup
import re

lengMap = {
  986: ['I', 'l'],
  998: ['1'],
  1068: ['I', 'l'],
  1081: ['1'],
  1082: ['v'],
  1130: ['Y'],
  1134: ['Y'],
  1172: ['v'],
  1224: ['Y'],
  1274: ['L', 'y'],
  1298: ['V'],
  1311: ['V'],
  1360: ['i'],
  1380: ['L', 'y'],
  1406: ['V'],
  1473: ['i'],
  1478: ['T'],
  1491: ['r'],
  1598: ['N', 'X'],
  1601: ['T'],
  1604: ['X'],
  1610: ['J', 'x'],
  1613: ['x'],
  1614: ['N'],
  1615: ['r', 'N'],
  1616: ['N'],
  1617: ['N'],
  1618: ['N'],
  1634: ['k'],
  1637: ['k'],
  1694: ['z', 't'],
  1706: ['K'],
  1709: ['K'],
  1731: ['X', 'N'],
  1744: ['x', 'J'],
  1754: ['F'],
  1770: ['k'],
  1835: ['z', 't'],
  1838: ['u'],
  1840: ['A'],
  1844: ['A'],
  1848: ['K'],
  1850: ['Z'],
  1853: ['Z'],
  1886: ['h'],
  1900: ['F'],
  1922: ['H'],
  1928: ['H'],
  1960: ['P'],
  1991: ['u'],
  1993: ['A'],
  1996: ['D'],
  2004: ['Z'],
  2018: ['w'],
  2035: ['w'],
  2042: ['7'],
  2043: ['h'],
  2080: ['j'],
  2082: ['H'],
  2104: ['R'],
  2107: ['R'],
  2123: ['P'],
  2140: ['4'],
  2162: ['D'],
  2164: ['O'],
  2183: ['w'],
  2198: ['n', 'C'],
  2199: ['C'],
  2200: ['C'],
  2201: ['C'],
  2202: ['C'],
  2210: ['f'],
  2212: ['7'],
  2246: ['E'],
  2253: ['j'],
  2260: ['o'],
  2272: ['d'],
  2279: ['R', 'M'],
  2282: ['M'],
  2294: ['U'],
  2301: ['U'],
  2310: ['W'],
  2318: ['4', 'W'],
  2321: ['M'],
  2332: ['a'],
  2344: ['O'],
  2345: ['W'],
  2346: ['W'],
  2366: ['s'],
  2380: ['b'],
  2381: ['n', 'C'],
  2382: ['0'],
  2394: ['f'],
  2433: ['E'],
  2448: ['o'],
  2461: ['d'],
  2464: ['p'],
  2466: ['M'],
  2485: ['U'],
  2498: ['c'],
  2501: ['e'],
  2503: ['W'],
  2512: ['q'],
  2526: ['a'],
  2546: ['2'],
  2563: ['s'],
  2578: ['b'],
  2580: ['0'],
  2606: ['5'],
  2632: ['6'],
  2669: ['p'],
  2706: ['c'],
  2709: ['e'],
  2721: ['q'],
  2758: ['2'],
  2800: ['9'],
  2823: ['5'],
  2851: ['6'],
  3033: ['9'],
  3038: ['S'],
  3054: ['B'],
  3160: ['g'],
  3244: ['Q'],
  3254: ['Q'],
  3266: ['G'],
  3291: ['S'],
  3308: ['B'],
  3414: ['8'],
  3423: ['g'],
  3514: ['Q'],
  3538: ['G'],
  3663: ['m'],
  3667: ['m'],
  3698: ['8'],
  3878: ['3'],
  3968: ['m'],
  4201: ['3']
}

def getFirst(d):
    # print(d)
    first = re.search(re.compile("\d+(\.\d*)?"),d)
    # print(first.group())
    return float(first.group())

def svgCrack(svg):
    # svg = BeautifulSoup(open(path),"lxml")
    svg = BeautifulSoup(svg,"lxml")
    # print(svg.prettify())

    # 查找path指令
    paths = svg.select("path")
    # print(paths,len(path))
    d = []
    # 获取d属性值并去除噪点横线
    for path in paths:
        length = len(path["d"])
        if length>500:
            d.append(path["d"])

    # 根据d值第一位来排序
    d.sort(key=getFirst)

    result = ""
    for n in d:
        r = lengMap[len(n)]
        result += r[0]
    # print(result)
    return result
