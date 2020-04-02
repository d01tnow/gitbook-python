# Python3 基础

## 类型

1. int 的最大值. sys.maxsize. 不同于 c/c++, java 语言中的 int.
2. ord(ch) 获取字符的整数表示, chr(i) 把编码转换为对应的字符
3. bytes.decode('utf-8') 后得到 str, str.encode('utf-8') 后得到 bytes.  len(str) 得到字符数. len(bytes) 得到字节数. 请统一使用 'utf-8' 进行编解码.
4. 一个元素的 tuple 定义方法: t = (1, ) . 不要忘记 ',', 否则, t = 1
5. 可变对象: list, dict, set, bytearray, 自定义的对象. 不可变对象: bool, int, float, string, tuple, function, range, frozenset, bytes. 用户定义的对象如果重写了 \_\_slots\_\_ 和 \_\_setattr\_\_ , 可以定义不可变对象. _\_slots\_\_ 使 \_\_dict\_\_ 对象失效, 不能添加新属性(仅对当前类有效, 对子类无效), 可以节省内存 . 通过修改 \_\_getattribute\_\_(self, item) 函数, 控制属性访问行为. 不变对象不变的是对象本身, 而不是其内部元素.

``` python
t = (1, 2, [3, 4])
t[2].append(5) #(1,2, [3,4,5])
# 注意
t[2] += [6, 7] # t 被修改为 (1,2, [3,4,5,6,7]), 也会抛出异常 TypeError: 'tuple' object does not support item assignment . 这说明增量赋值不是原子操作.
```



### list

#### 列表推导

1. python 会忽略代码里 [], {}, () 中的换行符.
2. 推导表达式内部有局部作用域

#### 生成器表达式

1. 如果生成器表达式是函数**唯一**的参数, 那么不需要用额外的括号把它括起来.
2. 生成器是惰性求值, 占用内存更少.

#### 成员函数

##### list.sort

原型: list.sort(key=None, reverse=False). 默认升序排列. 它的排序是稳定的.

* key -- 原型为 func(element) -> obj 的函数. element 是原 list 的元素, obj 是实现了小于运算符(\_\_lt\_\_)的对象. operator 模块有很多函数可以用作 key 参数.
* reverse -- False, 表示升序排列. True, 表示降序排列.

list.sort 是 in place 的. 故, 返回值为 None. 而内置函数 sorted, 会创建新 list 排序后返回. 所以, sorted 可以接受任何形式的可迭代对象作为参数, 包括不可变对象或生成器.

### tuple

1. 元组的位置信息很重要. 
2. 元组和其他 iterable 对象一样可以被拆包. 用 *var 捕获不确定的参数, *var 可以在任意位置.
3. *var 作为函数参数, 可以将 var 变量拆开作为函数参数.
4. 元组可以作为函数的返回值, 以支持多返回值得情况.
5. '_' 作为占位符, 以忽略拆包后不感兴趣的数据

### 具名元组

collections.namedtuple 是一个工厂函数, 可以构建带字段名的, 有名字的元组. 可以用来构建简单对象. 它的实例比普通对象要小一些, 因为 python 不用 \_\_dict\_\_ 存放这些属性 .

1. 构建方法例子: Card = collections.nametuple('Card', ['rank', 'suit']) , 第一个参数是元组名称, 第二个参数是其字段. 第二个字段也可以是由**空格**分隔的多个字段字符串.
2. 具名元组有几个特殊属性和方法. _fields 类属性-- 以元组类型返回具名元组的字段名. 类方法 _make(iterable) -- 接受一个可迭代的对象, 生成具名元组类的实例, 和类名(*it) 效果一样. 实例方法 _asdict() -- 以 collections.OrderedDict 的形式返回元组信息.

``` python
from collections import namedtuple
Point = namedtuple('Point', 'x y')
p1 = Point(1, 2)
t1 = (3, 4)
p2 = Point._make(t1) # 等同于 p2 = Point(*t1)
Point._fields # ('x', 'y')
p2._asdict() # OrderDict([('x', 3), ('y', 4)])
```

### slice

基本形式: seq[start:stop:step]. step 默认为 1. 可以用 slice(start, stop, step) 构造切片对象, 为其命名, 使其更具可读性. 

1. 切片和区间不包含最后一个元素. 即是[start, stop) 左闭右开区间. 这样做的好处是.
   * 当只有最后一个位置信息时, 切片和区间里的元素个数等于最后一个位置信息的值: range(5) 和 l[:5] 一样都返回 5 个元素.
   * 当起止位置信息都存在时, 可以使用 end - start 快速计算出切片和区间的长度.
   * 可以简单的使用一个下标, 把序列分割成**不重叠**的两个部分. lt[:x] 和 lt[x:] .

``` python
# 假设一系列字符串的 [0:4] 是年, [5:7] 是月
SL_YEAR = slice(0, 6)
SL_MONTH = slice(5, 7)
l1 = "2001-03"
l1[SL_YEAR] # '2001'
l1[SL_MONTH] # '03'
```



### 序列的 + 和 * 操作

1. \+ 和 \* 操作不修改原有的操作对象, 而是构建一个新对象. + 对应的是 \_\_add\_\_(), * 对应的是 \_\_mul\_\_() 
2. 如果 seq * n 中 seq 的元素是对其他**可变对象**的引用的话, 那么其结果是产生 n 个引用且都指向同一个可变对象的序列.

``` python
l1 = [1,2]
l2 = l1*2 # [1, 2, 1, 2]
l3 = [l1] * 2 # [[1,2], [1,2]]
l4 = [[*l1]] * 2 #[[1,2],[1,2]]
l1[0] = 2
l2 # [1,2, 1,2]
l3 # [[2,2], [2,2]]
l4 # [[1,2], [1,2]]

```

序列的 += 和 *= 操作

1. += 对应的是 \_\_iadd\_\_(), 即 inplace add, 就像调用 seq.extend(seq1) 一样. 但是, 当类型没有实现时, 退化为 \_\_add\_\_(). 同样的, *= 对应的是 \_\_imul\_\_().
2. 可变序列都实现了 += 和 *= ,