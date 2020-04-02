# Python3 内置模块

## bisect

它是基于二分查找算法实现的针对有序序列进行查找和插入的模块. 通常, 用 bisect 管理已排序的序列. 

**注意**: 前提条件 -- 一定要**升序**排列的序列.

bisect, bisect_right, bisect_left 用于搜索 x 在 序列 a 中合适的插入点, 但不插入. insort, insort_right, insort_left 查找 x 在序列 a 中合适的插入点, 并插入 x , 并且保持 a 的有序性. 

_left, _right 主要用于 a 中已存在 x 等值元素时, 插入位置是该元素位置的左侧还是右侧.

| 函数                               | 含义                                               | 插入? | 返回值     |
| ---------------------------------- | -------------------------------------------------- | ----- | ---------- |
| bisect(a,x, lo=0, hi=len(a))       | 同 bisect_right.                                   | 否    | 插入点索引 |
| bisect_right(a,x, lo=0, hi=len(a)) | 返回: (x 右侧索引) if x in a else (x 可插入的位置) | 否    |            |
| bisect_left(a,x, lo=0, hi=len(a))  | 返回: (x 左侧索引) if x in a else (x 可插入的位置) | 否    |            |
| insort_left(a,x, lo=0, hi=len(a))  | 按顺序插入 x, x 已存在时插入左侧                   | 是    | None       |
| insort_right(a,x, lo=0, hi=len(a)) | 按顺序插入 x, x 已存在时插入右侧                   | 是    | None       |
| insort(a,x, lo=0, hi=len(a))       | 同 insort_right.                                   |       |            |



