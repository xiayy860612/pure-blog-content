# Java Collection的使用

Java的Collection类库将接口和实现进行了分离.

集合类有两个基本接口

- Collection
- Map

## 迭代器Iterator

Iterator接口的主要方法:

  - hasNext
  - next

Collection接口继承自Iterable, 它提供了生成iterator的方法:

  - iterator

foreach可以和任何实现了Iterable接口的对象一起工作,
通过iterator来遍历所有元素, **元素被访问的顺序取决于集合类型**.

使用Iterator访问时, 必须顺序的访问元素.

随机访问可以按任意顺序访问元素.

可以使用Java 1.4引入的**RandomAccess**来测试集合是否支持随机访问.

## 队列Queue

先进先出

通常的实现方式:

- 循环数组, ArrayDeque
  - 有界集合, 即容量有限
- 链表, LinkedList
  - 容量没有上限



