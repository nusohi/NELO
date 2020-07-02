'''
@Description: SLR 分析器
@Author: nuso
@LastEditors: nuso
@Date: 2020-06-29 17:10:02
@LastEditTime: 2020-07-02 16:40:56
'''
import queue
from collections import Iterable
import numpy as np


class Closure():
    def __init__(self):
        self.projSet = set()
        self.projList = []       # 正常顺序 存储项目序号
        self.Edges = []          # ['E', I2]

    def add(self, projs):   # 批量添加
        for p in projs:
            if p not in self.projSet:
                self.projSet.add(p)
                self.projList.append(p)

    def get(self, index):
        return self.projList[index]

    def len(self):
        return len(self.projList)

    def __eq__(self, other):
        return self.projSet == other.projSet


# 可随其他 NSet 扩充
class NSet():
    def __init__(self):
        self._set = set()
        self.listeners = []  # 自己有的 listeners 都要有

    def add(self, newItems):
        if not isinstance(newItems, Iterable):
            newItems = [newItems]

        hasNew = False
        for item in newItems:
            if item not in self._set:
                hasNew = True
                self._set.add(item)
        if hasNew:
            self.broadcast()

    def all(self):
        return self._set

    def addListener(self, other):
        if other == self:
            return
        if other not in self.listeners:
            self.listeners.append(other)
            other.add(self._set)

    def broadcast(self):
        for listener in self.listeners:
            listener.add(self._set)


class SLR():
    def __init__(self):
        self.dot_str = '◉'
        self.Keys = []       # ['if',    'else',     'S']
        self.Key2Index = {}  # {'if':0,  'else':1,   'S':2}
        self.expressions = []    # [0, [1,3,2]]  # [ 左部 [右部各项] ]
        self.NS, self.TS = [], []

        self.Projects = []   # 所有项目  [1, 0, 3]  [ 产生式ID, 圆点位置, maxpos ]
        self.Familys = []    # 项目集规范族    [Closure_1, Closure_2]
        self.Table = []
        self._table_ = []
        self.TableHead = []

        self.First = {}
        self.Follow = {}

        self.LeftCombs = {}  # 左结合的情况
        self.conflicts = []  # 产生的冲突

    # 分析主函数
    def Run(self, grammarPath, leftComb=[]):
        self.LoadGrammar(grammarPath)
        self.SetLeftCombs(leftComb)

        self.InitTSNS()
        # 手动添加 TS # sharp
        self.Keys.append('#')
        self.Key2Index['#'] = len(self.Keys) - 1
        self.TS.append(len(self.Keys) - 1)

        self.InitFirst()
        self.InitFollow()
        self.InitProjects()
        self.InitFamily()
        self.InitTable()
        self.CleanTable()

    # 从 txt 中读入文法
    def LoadGrammar(self, path):
        with open(path, encoding='utf-8') as f:
            for line in f.readlines():
                if line.startswith("EOF"):
                    break
                slr.ReadOneLine(line.strip('\n'))

    # 设置左结合
    def SetLeftCombs(self, combs):
        for comb in combs:
            if len(comb) == 2:      # ('*', 1)
                self.LeftCombs[comb] = True
            elif len(comb) == 3:    # ('+', 1, False)
                self.LeftCombs[(comb[0], comb[1])] = comb[2]

    # 初始化 所有项目
    def InitProjects(self):
        for e in range(len(self.expressions)):
            length = len(self.expressions[e][1])
            for i in range(0, length + 1):
                self.Projects.append([e, i, length])   # i 表示圆点的位置

    # 构造项目集
    def InitFamily(self):
        que = queue.Queue()     # 存放闭包在 Family 中的 ID

        closure = self.BuildClosure([0])
        index, _ = self.AddClosureToFamily(closure)
        que.put(index)

        while not que.empty():
            index = que.get()
            closure = self.Familys[index]

            # 构造 边 以及下一组闭包
            edge2Closure = {}           # 存放该闭包产生的下一组闭包
            for i in range(closure.len()):
                pro = self.Projects[closure.get(i)]  # [ 产生式ID, 圆点位置, maxpos ]
                if pro[1] == pro[2]:    # 规约的项目排除
                    continue

                # [0, [1,3,2]]  # [ 左部 [右部各项] ]
                exp = self.expressions[pro[0]]
                nextKey = exp[1][pro[1]]            # 边的符号
                nextProj = closure.get(i) + 1       # 圆点后移的下一个项目号

                if nextKey in edge2Closure:
                    edge2Closure[nextKey].append(nextProj)
                else:
                    edge2Closure[nextKey] = [nextProj]

            # 根据 edge2Closure 构造子闭包和边
            for edge in edge2Closure.keys():
                sub_closure = self.BuildClosure(edge2Closure[edge])
                index, isNew = self.AddClosureToFamily(sub_closure)
                closure.Edges.append([edge, index])
                if isNew:           # 新产生的闭包添加进队列
                    que.put(index)

    # 构造一个闭包，并添加到项目集，返回闭包在项目集中的下标
    def BuildClosure(self, init_closure):
        closure = Closure()
        closure.add(init_closure)

        # 构造闭包
        i = 0
        while i < closure.len():
            pro = self.Projects[closure.get(i)]  # [ 产生式ID, 圆点位置, maxpos ]
            # 跳过 可规约的项目 和 圆点后为终结符的项目
            if pro[1] >= pro[2] or self.expressions[pro[0]][1][pro[1]] in self.TS:
                i = i + 1
                continue
            ns = self.expressions[pro[0]][1][pro[1]]
            projs = self.GetProjsNSLeading(ns)
            closure.add(projs)
            i = i + 1

        return closure

    # 添加闭包到规范族 无重复 并返回项目集在 Familys 中下标
    def AddClosureToFamily(self, closure):
        for i, fam in enumerate(self.Familys):
            if closure == fam:
                return i, False             # isNew = False
        self.Familys.append(closure)
        return len(self.Familys) - 1, True  # isNew = True

    # 查找所有以 ns 为左部 & 圆点在最前面 的项目
    def GetProjsNSLeading(self, ns):
        projs = []      # p ->[ 产生式ID, 圆点位置, maxpos ]
        for i, p in enumerate(self.Projects):
            if self.expressions[p[0]][0] == ns and p[1] == 0:
                projs.append(i)
        return projs

    # 因左结合而需要移进的判定
    def LeftPrior(self, key_ts, expIndex):
        tup = (self.Keys[key_ts], expIndex)
        if tup in self.LeftCombs:
            return self.LeftCombs[tup]
        else:
            print(f"没有配置的冲突: {tup}")

    # 读入一条产生式
    def ReadOneLine(self, line):
        words = line.strip(' ').split(' ')
        words = [w for w in words if w != '']
        if len(words) <= 1:
            return

        self.AddKeys(words)
        self.AddNS(words[0])

        exp = []
        for i in range(1, len(words)):
            exp.append(self.Key2Index[words[i]])
        self.expressions.append([self.Key2Index[words[0]], exp])

    def AddKeys(self, _keys):
        for key in _keys:
            if key in self.Keys:
                continue
            self.Key2Index[key] = len(self.Keys)
            self.Keys.append(key)

    def AddNS(self, _ns):
        index = self.Key2Index[_ns]
        if index not in self.NS:
            self.NS.append(index)

    # 计算 TS NS 表
    def InitTSNS(self):
        self.NS.sort()
        for i in range(0, len(self.Keys)):
            if i not in self.NS:
                self.TS.append(i)

    # 计算 First 集
    def InitFirst(self):
        for ns in self.NS:
            self.First[ns] = NSet()
        for ns in self.NS:
            for exp in self.expressions:
                if exp[0] != ns:
                    continue
                if exp[1][0] in self.TS:
                    self.First[ns].add(exp[1][0])
                else:
                    self.First[exp[1][0]].addListener(self.First[ns])
        for ts in self.TS:
            self.First[ts] = NSet()
            self.First[ts].add(ts)

    # 计算 Follow 集
    def InitFollow(self):
        for ns in self.NS:
            self.Follow[ns] = NSet()

        # Step1 开始符号的 FOLLOW 集 加入 #
        self.Follow[0].add(self.Key2Index['#'])

        # Step2 产生式右部中 ns 之后符号的 First 加到 ns 的 Follow 中
        for exp in self.expressions:
            for i, key in enumerate(exp[1]):
                if key in self.NS and i+1 != len(exp[1]):
                    self.Follow[key].add(self.First[exp[1][i+1]].all())

        # Step3 左部 Follow 加到右部尾的 Follow
        for exp in self.expressions:
            if exp[1][-1] in self.NS:
                self.Follow[exp[0]].addListener(self.Follow[exp[1][-1]])

    # 计算最终的分析表 _table_ 存储备份
    def InitTable(self):
        self.TableHead = self.Keys

        for i, closure in enumerate(self.Familys):
            line = [' ' for i in range(0, len(self.Keys))]
            self.Table.append(line)

            # 移进 和 GOTO (通过 edges 判定)
            for edge in closure.Edges:  # ['E', I2] [1, 2]
                if edge[0] in self.TS:
                    line[edge[0]] = 's' + str(edge[1])     # shift
                else:
                    line[edge[0]] = str(edge[1])           # goto

            # 规约 (r0==ACC)
            for i in range(closure.len()):
                pro = self.Projects[closure.get(i)]   # [ 产生式ID, 圆点位置, maxpos ]
                if pro[1] != pro[2]:
                    continue
                # 遍历该产生式左部的 Follow 集
                ns = self.expressions[pro[0]][0]
                for key in self.Follow[ns].all():
                    if line[key] != ' ':            # 有冲突    shift/reduce
                        self.conflicts.append((     # 记录该冲突
                            self.Keys[key],
                            pro[0],
                            self.LeftPrior(key, pro[0])
                        ))
                        if not self.LeftPrior(key, pro[0]):
                            continue    # 保持之前的 shift
                    s = ('r' + str(pro[0])) if pro[0] != 0 else 'ACC'
                    line[key] = s       # 规约 reduce

        self._table_ = self.Table

    # 整理 Table: 去掉 `FINAL`, GOTO 表后置
    def CleanTable(self):
        self.TableHead = self.TS + self.NS
        self.TableHead.remove(0)    # 去掉 'FINAL'

        table = np.array(self._table_)
        table = table[:, self.TableHead]
        self.Table = table

    def ResetTableHead(self, head):
        if len(head) == 0:
            return
        head = [self.Key2Index[key] for key in head]
        self.TableHead = head

        table = np.array(self._table_)
        table = table[:, self.TableHead]
        self.Table = table

    def Strf_Project(self, proIndex):
        # [ 产生式ID, 圆点位置, maxpos ]
        index, dot, maxpos = self.Projects[proIndex]
        exp = self.expressions[index]               # [0, [1,3,2]]

        string = self.Keys[exp[0]] + ' -> '
        for i, k in enumerate(exp[1]):
            if i == dot:
                string += self.dot_str+' '
            string += self.Keys[k] + ' '
        if dot == maxpos:
            string += self.dot_str
        return string

    def Strf_Closure(self, closure):
        string = ''
        for i in range(0, closure.len()):
            string += self.Strf_Project(closure.get(i)) + '\n'
        return string

    def LogFamily(self):
        print(f'=== 项目集规约族 ======================================')
        for i, closure in enumerate(self.Familys):
            print(f'I_{i}:\n{self.Strf_Closure(closure)}\n')
        print()

    def LogFirstOrFollow(self, isFirst=True):
        nSetDict = self.First if isFirst else self.Follow
        info = 'FIRST' if isFirst else 'FOLLOW'

        print(f'=== {info} ======================================')
        for k in nSetDict:
            nset = nSetDict[k]
            string = self.Keys[k] + '\t' + str(len(nset.all())) + '\t{ '
            for i in nset.all():
                string += self.Keys[i]+'  '
            string += '}'
            print(string)
        print()

    def Strf_Table(self):
        heads = [self.Keys[k] for k in self.TableHead]
        lines = '状态\t' + '\t'.join(heads) + '\n'
        for i, tl in enumerate(self.Table):
            lines += str(i)+'\t' + '\t'.join(tl) + '\n'
        return lines

    def LogConflicts(self):
        print('>> Conflicts >>>>>>>>>>>>>>>>>>>>>>>>')
        for conflict in self.conflicts:
            print(conflict.__str__() + ',')
        print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')


if __name__ == '__main__':
    config = {
        'GrammarFile': './SLR/exp.txt',       # 文法需为拓广文法，有起始符(FINAL, S')
        'OutputFile': './SLR/SLR_table.txt',
        'PrintTable': False,
        'PrintConflicts': True,
        'TableHead': [],  # ['ci', 'i', '+', '*', '(', ')', '#', 'E'],  # 为空不改
        'LeftCombs': [
            (';', 9, True),
            ('and', 13, True),
            ('or', 13, True),
            ('and', 14, False),
            ('or', 14, True),
            ('and', 15, True),
            ('or', 15, True),
            ('+', 21, True),
            ('*', 21, False),
            ('+', 22, True),
            ('*', 22, True),
        ],
    }

    slr = SLR()
    slr.Run(config['GrammarFile'], config['LeftCombs']) # 构造分析表的主函数

    slr.LogFamily()
    slr.LogFirstOrFollow()
    slr.LogFirstOrFollow(False)

    slr.ResetTableHead(config['TableHead'])
    table = slr.Strf_Table()

    with open(config['OutputFile'], 'w+', encoding='utf-8') as f:
        f.write(table)

    if config['PrintTable']:
        print('================================>')
        print(table)
        print('<================================')

    if config['PrintConflicts']:
        slr.LogConflicts()

    print('#################################nuso')
