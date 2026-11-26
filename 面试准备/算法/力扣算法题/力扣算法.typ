
#set document(title: "力扣复习笔记")
#let accent = rgb("#B45A14")
#let ink = rgb("#20252b")
#set page(paper: "a4", margin: (x: 19mm, top: 16mm, bottom: 17mm), numbering: "1")
#set text(font: ("Times New Roman", "Kaiti SC"), size: 11pt, fill: ink, lang: "zh")
#set par(justify: true, leading: .55em, spacing: .8em)
#set heading(numbering: none)
#show table: set par(justify: false)
#show heading.where(level: 1): it => block(width: 100%, sticky: true, above: 12pt, below: 8pt)[
  #text(size: 15pt, weight: "bold", fill: accent, it.body)
  #v(3pt)
  #line(length: 100%, stroke: .65pt + accent)
]
#show heading.where(level: 2): it => block(sticky: true, above: 11pt, below: 6pt,
  text(size: 12.5pt, weight: "bold", it.body))
#show raw: set text(font: ("Menlo", "Kaiti SC"), size: 9.2pt)
#show raw.where(block: true): it => block(width: 100%, inset: (x: 8pt, y: 6pt),
  fill: rgb("#F6F6F4"), radius: 2pt, breakable: true, it)
#let toc-title(body) = block(sticky: true, above: 8pt, below: 3pt,
  text(fill: accent, weight: "bold", body))
#let jump(target, title) = link(label(target), text(fill: accent, title))

#align(center, text(size: 21pt, weight: "bold", "力扣复习笔记｜按题型归类"))
#text("按 Hot 100 官方分类和题序编排，其余题目归入对应章节。共收录 67 道题。")

= 目录 <toc>

#toc-title[#text("哈希")]
- #jump("lc1", "LeetCode 1｜两数之和")#text(" — 哈希表")
- #jump("lc49", "LeetCode 49｜字母异位词分组")#text(" — 哈希表 + 排序")
- #jump("lc128", "LeetCode 128｜最长连续序列")#text(" — 集合")

#toc-title[#text("双指针")]
- #jump("lc283", "LeetCode 283｜移动零")#text(" — 双指针")
- #jump("lc11", "LeetCode 11｜盛最多水的容器")#text(" — 双指针 + 贪心")
- #jump("lc15", "LeetCode 15｜三数之和")#text(" — 排序 + 双指针")
- #jump("lc88", "LeetCode 88｜合并两个有序数组")#text(" — 逆向双指针")
- #jump("lc415", "LeetCode 415｜字符串相加")#text(" — 双指针 + 模拟竖式加法")

#toc-title[#text("滑动窗口")]
- #jump("lc3", "LeetCode 3｜无重复字符的最长子串")#text(" — 滑动窗口 + 集合")
- #jump("lc438", "LeetCode 438｜找到字符串中所有字母异位词")#text(" — 固定窗口 + Counter")

#toc-title[#text("子串")]
- #jump("lc560", "LeetCode 560｜和为 K 的子数组")#text(" — 前缀和 + 哈希表")
- #jump("lc239", "LeetCode 239｜滑动窗口最大值")#text(" — 单调队列")

#toc-title[#text("普通数组")]
- #jump("lc53", "LeetCode 53｜最大子数组和")#text(" — 动态规划 / Kadane 算法")
- #jump("lc56", "LeetCode 56｜合并区间")#text(" — 排序 + 区间合并")
- #jump("lc189", "LeetCode 189｜轮转数组")#text(" — 三次反转 + 双指针")
- #jump("lc238", "LeetCode 238｜除了自身以外数组的乘积")#text(" — 前缀积 + 后缀积")

#toc-title[#text("矩阵")]
- #jump("lc54", "LeetCode 54｜螺旋矩阵")#text(" — 四边界模拟")

#toc-title[#text("链表")]
- #jump("lc160", "LeetCode 160｜相交链表")#text(" — 双指针 + 交换起点")
- #jump("lc206", "LeetCode 206｜反转链表")#text(" — 迭代 + 三指针")
- #jump("lc234", "LeetCode 234｜回文链表")#text(" — 链表遍历 + 反转")
- #jump("lc141", "LeetCode 141｜环形链表")#text(" — 快慢指针")
- #jump("lc142", "LeetCode 142｜环形链表 II")#text(" — 快慢指针 + 环入口定位")
- #jump("lc21", "LeetCode 21｜合并两个有序链表")#text(" — 双指针 + 虚拟头节点")
- #jump("lc2", "LeetCode 2｜两数相加")#text(" — 模拟竖式加法")
- #jump("lc19", "LeetCode 19｜删除链表的倒数第 N 个节点")#text(" — 虚拟头节点 + 快慢指针")
- #jump("lc24", "LeetCode 24｜两两交换链表中的节点")#text(" — 指针重连")
- #jump("lc25", "LeetCode 25｜K 个一组翻转链表")#text(" — 分组反转 + 指针调整")
- #jump("lc138", "LeetCode 138｜随机链表的复制")#text(" — 节点穿插法")
- #jump("lc148", "LeetCode 148｜排序链表")#text(" — 归并排序")
- #jump("lc23", "LeetCode 23｜合并 K 个升序链表")#text(" — 分治归并")
- #jump("lc146", "LeetCode 146｜LRU 缓存")#text(" — 哈希表 + 手写双向链表")
- #jump("lc82", "LeetCode 82｜删除排序链表中的重复元素 II")#text(" — 虚拟头节点 + 双指针")
- #jump("lc92", "LeetCode 92｜反转链表 II")#text(" — 虚拟头节点 + 头插法")
- #jump("lc143", "LeetCode 143｜重排链表")#text(" — 快慢指针 + 反转 + 交替合并")

#toc-title[#text("二叉树")]
- #jump("lc94", "LeetCode 94｜二叉树的中序遍历")#text(" — DFS 递归")
- #jump("lc104", "LeetCode 104｜二叉树的最大深度")#text(" — DFS + 深度")
- #jump("lc226", "LeetCode 226｜翻转二叉树")#text(" — DFS + 交换左右子树")
- #jump("lc101", "LeetCode 101｜对称二叉树")#text(" — 镜像递归")
- #jump("lc543", "LeetCode 543｜二叉树的直径")#text(" — DFS + 最大深度")
- #jump("lc102", "LeetCode 102｜二叉树的层序遍历")#text(" — BFS + 队列")
- #jump("lc108", "LeetCode 108｜将有序数组转换为二叉搜索树")#text(" — 二分 + 递归建树")
- #jump("lc98", "LeetCode 98｜验证二叉搜索树")#text(" — BST + 上下界递归")
- #jump("lc230", "LeetCode 230｜二叉搜索树中第 K 小的元素")#text(" — 中序遍历")
- #jump("lc199", "LeetCode 199｜二叉树的右视图")#text(" — BFS + 每层最后一个节点")
- #jump("lc114", "LeetCode 114｜二叉树展开为链表")#text(" — 先序遍历 + 栈")
- #jump("lc105", "LeetCode 105｜从前序与中序遍历序列构造二叉树")#text(" — 前序定位根 + 中序划分")
- #jump("lc437", "LeetCode 437｜路径总和 III")#text(" — 前缀和 + DFS 回溯")
- #jump("lc236", "LeetCode 236｜二叉树的最近公共祖先")#text(" — DFS 自底向上")
- #jump("lc103", "LeetCode 103｜二叉树的锯齿形层序遍历")#text(" — BFS 分层 + 隔层反转")

#toc-title[#text("图论")]
- #jump("lc200", "LeetCode 200｜岛屿数量")#text(" — DFS + 栈")

#toc-title[#text("回溯")]
- #jump("lc46", "LeetCode 46｜全排列")#text(" — 回溯 + used 数组")

#toc-title[#text("二分查找")]
- #jump("lc35", "LeetCode 35｜搜索插入位置")#text(" — 左闭右开二分")
- #jump("lc74", "LeetCode 74｜搜索二维矩阵")#text(" — 矩阵虚拟展开 + 二分")
- #jump("lc34", "LeetCode 34｜在排序数组中查找元素的第一个和最后一个位置")#text(" — 两次二分 + 左右边界")
- #jump("lc33", "LeetCode 33｜搜索旋转排序数组")#text(" — 判断有序半区")
- #jump("lc153", "LeetCode 153｜寻找旋转排序数组中的最小值")#text(" — 二分 + 旋转断点")
- #jump("lc704", "LeetCode 704｜二分查找")#text(" — 左闭右开二分")

#toc-title[#text("栈")]
- #jump("lc20", "LeetCode 20｜有效的括号")#text(" — 栈 + 括号配对")
- #jump("lc155", "LeetCode 155｜最小栈")#text(" — 双栈 + 同步维护最小值")
- #jump("lc232", "LeetCode 232｜用栈实现队列")#text(" — 双栈")

#toc-title[#text("堆")]
- #jump("lc215", "LeetCode 215｜数组中的第 K 个最大元素")#text(" — 随机快速选择 + 三路分组")
- #jump("lc912", "LeetCode 912｜排序数组")#text(" — 大顶堆排序")

#toc-title[#text("贪心算法")]
- #jump("lc121", "LeetCode 121｜买卖股票的最佳时机")#text(" — 贪心 + 维护历史最低价")

#toc-title[#text("动态规划")]
- #jump("lc300", "LeetCode 300｜最长递增子序列")#text(" — 动态规划 / 贪心 + 二分")

#toc-title[#text("多维动态规划")]
- #jump("lc5", "LeetCode 5｜最长回文子串")#text(" — 中心扩展法")
- #jump("lc1143", "LeetCode 1143｜最长公共子序列")#text(" — 二维前缀动态规划")
- #jump("lc72", "LeetCode 72｜编辑距离")#text(" — 二维前缀动态规划")

#pagebreak()
= #text("哈希")

== #text("1. 两数之和（LeetCode 1）") <lc1>

#strong[#text("方法：")]#text(" 哈希表")

#strong[#text("题目要求：")]#text(" 给定整数数组 nums 和目标值 target，找到两个不同位置的数字，使它们的和等于 target，返回这两个数字的下标。")

#strong[#text("具体例子：")]#text(" nums = [2, 7, 11, 15]，target = 9。因为 2 + 7 = 9，返回 [0, 1]。")

#strong[#text("核心原理：")]#text(" 遍历数组时，当前数字是 num，另一个数字必须等于 target - num。用字典 seen 存储已经遍历过的“数字 → 下标”，先查询差值是否出现，再记录当前数字。这样既避免重复使用同一位置，也不用对每一对数字逐个比较。")

#strong[#text("完整代码：")]

```python
class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        seen = {}
        for i, num in enumerate(nums):
            need = target - num
            if need in seen:
                return [seen[need], i]
            seen[num] = i
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，空间 O(n)。")

#strong[#text("记忆骨架：")]#text(" 遍历数字 → 计算差值 → 查询字典 → 找到则返回，否则记录当前位置。")

#jump("toc", "↑ 返回目录")

== #text("49. 字母异位词分组（LeetCode 49）") <lc49>

#strong[#text("方法：")]#text(" 哈希表 + 排序")

#strong[#text("题目要求：")]#text(" 把由相同字母组成、排列顺序不同的字符串分为同一组，返回全部分组。")

#strong[#text("具体例子：")]#text(" [\"eat\", \"tea\", \"tan\", \"ate\", \"nat\", \"bat\"] 可以分为 [[\"eat\", \"tea\", \"ate\"], [\"tan\", \"nat\"], [\"bat\"]]；分组顺序不限。")

#strong[#text("核心原理：")]#text(" 异位词拥有相同的字母及出现次数，因此排序后的字符串必然相同。例如 eat、tea 和 ate 的排序结果都是 aet。以排序结果为字典 key，把原字符串依次加入对应列表，最后返回所有分组。")

#strong[#text("完整代码：")]

```python
class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        groups = {}
        for s in strs:
            key = "".join(sorted(s))
            if key not in groups:
                groups[key] = []
            groups[key].append(s)
        return list(groups.values())
```

#strong[#text("复杂度：")]#text(" 设字符串个数为 n，平均长度为 k。时间 O(nk log k)，空间 O(nk)。")

#strong[#text("记忆骨架：")]#text(" 遍历字符串 → 排序得到 key → 创建或找到分组 → 加入原字符串 → 返回所有 value。")

#jump("toc", "↑ 返回目录")

== #text("128. 最长连续序列（LeetCode 128）") <lc128>

#strong[#text("方法：")]#text(" 集合")

#strong[#text("题目要求：")]#text(" 给定无序整数数组，找到最长的连续整数序列，返回序列长度。序列中的数字无需在原数组里相邻。")

#strong[#text("具体例子：")]#text(" nums = [100, 4, 200, 1, 3, 2]，最长连续序列是 [1, 2, 3, 4]，答案为 4。")

#strong[#text("核心原理：")]#text(" 先转为集合，查找一个数字是否存在的平均时间为 O(1)。仅在 num - 1 不存在时，才把 num 视为连续序列的起点，然后用 while 检查后继数字。每段序列只从起点计算一次，避免重复计数。")

#strong[#text("完整代码：")]

```python
class Solution:
    def longestConsecutive(self, nums: list[int]) -> int:
        num_set = set(nums)
        longest = 0
        for num in num_set:
            if num - 1 not in num_set:
                current_num = num
                current_length = 1
                while current_num + 1 in num_set:
                    current_num += 1
                    current_length += 1
                longest = max(longest, current_length)
        return longest
```

#strong[#text("复杂度：")]#text(" 平均时间 O(n)，空间 O(n)。")

#strong[#text("记忆骨架：")]#text(" 转集合 → 判断是不是起点 → while 向后寻找连续数字 → 更新最大长度。")

#jump("toc", "↑ 返回目录")

= #text("双指针")

== #text("283. 移动零（LeetCode 283）") <lc283>

#strong[#text("方法：")]#text(" 双指针")

#strong[#text("题目要求：")]#text(" 把数组中的所有 0 移动到末尾，保持非零数字的相对顺序，直接修改原数组。")

#strong[#text("具体例子：")]#text(" [0, 1, 0, 3, 12] 处理后变为 [1, 3, 12, 0, 0]。")

#strong[#text("核心原理：")]#text(" right 从左到右寻找非零数字；left 指向下一个应该存放非零数字的位置。遇到非零数字时，将 nums[right] 与 nums[left] 交换，再将 left 加一。这样非零数字保持原有顺序，零会逐渐移动到后面。")

#strong[#text("完整代码：")]

```python
class Solution:
    def moveZeroes(self, nums: list[int]) -> None:
        left = 0
        for right in range(len(nums)):
            if nums[right] != 0:
                nums[left], nums[right] = nums[right], nums[left]
                left += 1
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" 右指针寻找非零 → 与左指针位置交换 → 左指针右移。")

#jump("toc", "↑ 返回目录")

== #text("11. 盛最多水的容器（LeetCode 11）") <lc11>

#strong[#text("方法：")]#text(" 双指针 + 贪心")

#strong[#text("题目要求：")]#text(" 给定数组 ")#raw("height")#text("，每个元素表示一条竖线的高度。选择两条线与 x 轴构成容器，求可容纳的最大水量。")

#strong[#text("具体例子：")]#text(" ")#raw("height = [1,8,6,2,5,4,8,3,7]")#text("，选择下标 1 和 8 两条竖线，宽度 7，较矮高度 7，最大面积为 ")#raw("7 × 7 = 49")#text("。")

#strong[#text("核心原理：")]#text(" 左右指针从数组两端出发。当前容器面积为 ")#raw("(right - left) * min(height[left], height[right])")#text("，每轮计算并更新最大面积，再移动较矮的一侧。因为指针向内移动后宽度变小，若保留较矮高度，则新面积不可能超过当前面积；移动较矮侧才有机会找到更高的竖线。")

#table(columns: (1fr, 1.4fr, 1.4fr, 1.4fr, 2fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("轮次")], [#text("两端下标")], [#text("两端高度")], [#text("当前面积")], [#text("移动方向")]),
  table.hline(stroke: .4pt),
  [#text("1")], [#text("0、8")], [#text("1、7")], [#text("8")], [#text("左指针右移")],
  [#text("2")], [#text("1、8")], [#text("8、7")], [#text("49")], [#text("右指针左移")],
  [#text("3")], [#text("1、7")], [#text("8、3")], [#text("18")], [#text("右指针左移")],
  [#text("4")], [#text("1、6")], [#text("8、8")], [#text("40")], [#text("右指针左移")],
  [#text("5")], [#text("1、5")], [#text("8、4")], [#text("16")], [#text("右指针左移")],
  [#text("6")], [#text("1、4")], [#text("8、5")], [#text("15")], [#text("右指针左移")],
  [#text("7")], [#text("1、3")], [#text("8、2")], [#text("4")], [#text("右指针左移")],
  [#text("8")], [#text("1、2")], [#text("8、6")], [#text("6")], [#text("右指针左移")],
  table.hline(stroke: .7pt))

#strong[#text("完整代码：")]

```python
class Solution:
    def maxArea(self, height: list[int]) -> int:
        left = 0
        right = len(height) - 1
        max_area = 0

        while left < right:
            width = right - left
            h = min(height[left], height[right])
            max_area = max(max_area, width * h)

            if height[left] < height[right]:
                left += 1
            else:
                right -= 1

        return max_area
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" 左右指针从两端出发 → 面积等于宽度乘较矮高度 → 更新最大值 → 移动较矮一侧 → 两指针相遇时结束。")

#jump("toc", "↑ 返回目录")

== #text("15. 三数之和（LeetCode 15）") <lc15>

#strong[#text("方法：")]#text(" 排序 + 双指针")

#strong[#text("题目要求：")]#text(" 在整数数组中找出所有和为 0 的不重复三元组。")

#strong[#text("具体例子：")]#text(" nums = [-1, 0, 1, 2, -1, -4]，结果为 [[-1, -1, 2], [-1, 0, 1]]。")

#strong[#text("核心原理：")]#text(" 先排序，逐个固定第一个数字 nums[i]，然后用 left 和 right 寻找其余两个数。若三数之和小于 0，左指针右移以增大和；大于 0，右指针左移以减小和；等于 0，则记录并跳过重复值。固定数字本身也要去重，保证结果不重复。")

#strong[#text("完整代码：")]

```python
class Solution:
    def threeSum(self, nums: list[int]) -> list[list[int]]:
        result = []
        nums.sort()
        for i in range(len(nums) - 2):
            if i > 0 and nums[i] == nums[i - 1]:
                continue
            left, right = i + 1, len(nums) - 1
            while left < right:
                total = nums[i] + nums[left] + nums[right]
                if total < 0:
                    left += 1
                elif total > 0:
                    right -= 1
                else:
                    result.append([nums[i], nums[left], nums[right]])
                    left += 1
                    right -= 1
                    while left < right and nums[left] == nums[left - 1]:
                        left += 1
                    while left < right and nums[right] == nums[right + 1]:
                        right -= 1
        return result
```

#strong[#text("复杂度：")]#text(" 时间 O(n²)；排序的额外空间依实现而定，结果列表空间另计。")

#strong[#text("记忆骨架：")]#text(" 先排序 → 固定第一个数 → 左右指针调整和 → 找到三元组 → 两层去重。")

#jump("toc", "↑ 返回目录")

== #text("88. 合并两个有序数组（LeetCode 88）") <lc88>

#strong[#text("方法：")]#text(" 逆向双指针")

#strong[#text("题目要求：")]#text(" 两个非递减数组 ")#raw("nums1")#text(" 和 ")#raw("nums2")#text(" 分别有 ")#raw("m")#text(" 和 ")#raw("n")#text(" 个有效元素。")#raw("nums1")#text(" 尾部预留了 ")#raw("n")#text(" 个位置，直接在其中完成合并。")

#strong[#text("具体例子：")]#text(" ")#raw("nums1 = [1,2,3,0,0,0]")#text("，")#raw("nums2 = [2,5,6]")#text("。从右向左依次填入 ")#raw("6、5、3、2")#text("，此时 ")#raw("nums2")#text(" 已用完，结果为 ")#raw("[1,2,2,3,5,6]")#text("。")

#strong[#text("核心原理：")]#text(" ")#raw("p1")#text(" 和 ")#raw("p2")#text(" 指向两个数组尚未处理的末尾，")#raw("p")#text(" 指向下一个写入位置。较大的末尾元素就是剩余元素中的最大值，将它写到 ")#raw("p")#text("，再左移对应指针和 ")#raw("p")#text("。从右向左写可避免覆盖 ")#raw("nums1")#text(" 未处理的元素。")#raw("p1")#text(" 越过左端后继续写入 ")#raw("nums2")#text("，")#raw("p2")#text(" 越过左端即可结束。")

#strong[#text("完整代码：")]

```python

class Solution:
    def merge(
        self,
        nums1: list[int],
        m: int,
        nums2: list[int],
        n: int
    ) -> None:
        # 三个指针分别指向两个数组的有效末尾和写入位置
        p1 = m - 1
        p2 = n - 1
        p = m + n - 1

        # 只要 nums2 还有元素，就继续合并
        while p2 >= 0:
            # nums1 还有有效元素，且当前元素更大
            if p1 >= 0 and nums1[p1] > nums2[p2]:
                nums1[p] = nums1[p1]
                p1 -= 1
            else:
                # nums2 当前元素更大，或者 nums1 已处理完
                nums1[p] = nums2[p2]
                p2 -= 1

            # 写入位置向左移动
            p -= 1
```

#strong[#text("复杂度：")]#text(" 时间 O(m+n)，额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" 定位三个末尾 → 较大值写入末尾 → 左移指针 → nums2 用完即结束。")

#jump("toc", "↑ 返回目录")

== #text("415. 字符串相加（LeetCode 415）") <lc415>

#strong[方法：] 双指针 + 模拟竖式加法

#strong[题目要求：] 给定两个表示非负整数的字符串，返回它们相加后的字符串。每次只处理一个数字字符。

#strong[变量定义：] `i`、`j` 分别指向两个字符串当前要处理的字符，初始都在个位。越过左端的一侧按 0 计算。`carry` 是上一位传来的进位，初始为 0。`res` 按个位到高位的顺序保存结果字符。`x`、`y` 是这一位取出的数字，`total` 是两数加上进位的和。

#strong[为什么逐位计算就够了：] 十进制下，`total % 10` 是当前位写下的数字，`total // 10` 是传到左边一位的进位。比如 6 + 7 = 13，个位写 3，十位进 1。每轮向左移一位，只要任一字符串还有数字，或者仍有进位，就继续算。

#strong[逐位推演：] 用 `"456" + "77"` 演示。两个下标从各自的个位开始，第三轮短串已用完，所以按 0 对齐。

#table(
  columns: (auto, 1fr, 1fr, 1fr, 1.3fr),
  table.header([位置], [本轮计算], [写下数字], [传出进位], [当前 res]),
  [个位], [6 + 7 + 0 = 13], [3], [1], [`["3"]`],
  [十位], [5 + 7 + 1 = 13], [3], [1], [`["3", "3"]`],
  [百位], [4 + 0 + 1 = 5], [5], [0], [`["3", "3", "5"]`],
)

结果列表从低位往高位存，倒序拼接后得到 `"533"`。如果计算 `"99" + "1"`，两串用完后还有进位 1，循环会再执行一次，补上最高位。

```python
class Solution:
    def addStrings(self, num1: str, num2: str) -> str:
        i, j = len(num1) - 1, len(num2) - 1
        carry = 0
        res = []

        while i >= 0 or j >= 0 or carry:
            x = ord(num1[i]) - ord("0") if i >= 0 else 0
            y = ord(num2[j]) - ord("0") if j >= 0 else 0
            total = x + y + carry

            res.append(str(total % 10))
            carry = total // 10
            i -= 1
            j -= 1

        return "".join(reversed(res))
```

`ord("6") - ord("0")` 得到 6，因为数字字符的编码是连续的。先判断下标再取字符，避免 Python 把负下标当成从末尾取值。

#strong[复杂度：] 两个字符串长度分别为 m、n，时间和额外空间均为 O(max(m, n))，额外空间主要用于结果字符列表。

#strong[记忆骨架：] 从个位开始 → 缺位补 0 → 取余写当前位 → 整除留进位 → 倒序拼接。

#jump("toc", "↑ 返回目录")

= #text("滑动窗口")

== #text("3. 无重复字符的最长子串（LeetCode 3）") <lc3>

#strong[#text("方法：")]#text(" 滑动窗口 + 集合")

#strong[#text("题目要求：")]#text(" 给定字符串，找到不含重复字符的最长连续子串，返回它的长度。")

#strong[#text("具体例子：")]#text(" s = \"abcabcbb\"，最长无重复子串可以是 \"abc\"，答案为 3。")

#strong[#text("核心原理：")]#text(" 用区间 [left, right] 表示当前窗口，用 seen 记录窗口中出现的字符。每当 right 扩展到新字符，若该字符已在窗口中，就不断删除左端字符并右移 left，直到不再重复；随后更新窗口的最大长度。")

#strong[#text("完整代码：")]

```python
class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        seen = set()
        left = 0
        longest = 0
        for right in range(len(s)):
            while s[right] in seen:
                seen.remove(s[left])
                left += 1
            seen.add(s[right])
            longest = max(longest, right - left + 1)
        return longest
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，空间 O(min(n, k))，其中 k 为字符集大小。")

#strong[#text("记忆骨架：")]#text(" 右指针扩展 → 遇到重复时移动左指针 → 去除重复 → 更新最长长度。")

#jump("toc", "↑ 返回目录")

== #text("438. 找到字符串中所有字母异位词（LeetCode 438）") <lc438>

#strong[#text("方法：")]#text(" 固定滑动窗口 + Counter")

#strong[#text("题目要求：")]#text(" 给定字符串 s 和 p，找出 s 中所有 p 的字母异位词，返回这些子串的起始下标。")

#strong[#text("具体例子：")]#text(" s = \"cbaebabacd\"，p = \"abc\"，结果是 [0, 6]，对应 \"cba\" 和 \"bac\"。")

#strong[#text("核心原理：")]#text(" 异位词的字符出现次数完全相同。用 Counter(p) 统计目标词频，并在 s 中维护长度为 len(p) 的固定窗口。右边进入一个字符，超出长度时移除左边字符；窗口和目标 Counter 相同时记录左边界。")

#strong[#text("完整代码：")]

```python
from collections import Counter

class Solution:
    def findAnagrams(self, s: str, p: str) -> list[int]:
        need = Counter(p)
        window = Counter()
        left = 0
        result = []
        for right, ch in enumerate(s):
            window[ch] += 1
            if right - left + 1 > len(p):
                window[s[left]] -= 1
                if window[s[left]] == 0:
                    del window[s[left]]
                left += 1
            if right - left + 1 == len(p) and window == need:
                result.append(left)
        return result
```

#strong[#text("复杂度：")]#text(" 本题字符仅有 26 个小写英文字母，时间 O(n + m)，辅助空间 O(1)，n、m 分别为 s 和 p 的长度。")

#strong[#text("记忆骨架：")]#text(" 统计目标词频 → 窗口右移 → 加入新字符、移除旧字符 → 比较词频并记录下标。")

#jump("toc", "↑ 返回目录")

= #text("子串")

== #text("560. 和为 K 的子数组（LeetCode 560）") <lc560>

#strong[#text("方法：")]#text(" 前缀和 + 哈希表")

#strong[#text("题目要求：")]#text(" 统计数组中和恰好等于 k 的连续子数组有多少个。")

#strong[#text("具体例子：")]#text(" nums = [1, 1, 1]，k = 2，两个符合条件的子数组分别位于下标 [0, 1] 和 [1, 2]，答案为 2。")

#strong[#text("核心原理：")]#text(" 设当前前缀和为 S，某个历史位置的前缀和为 P，则两位置之间子数组的和为 S - P。若要求和为 k，就有 P = S - k。因此维护“历史前缀和 → 出现次数”的字典，每一步先查询 S - k 累加答案，再记录当前 S。初始化 {0: 1}，使从数组第一个元素开始的子数组也能被统计。")

#strong[#text("关键关系：")]#text(" ")#raw("S - P = k  ⇒  P = S - k")

#strong[#text("完整代码：")]

```python
class Solution:
    def subarraySum(self, nums: list[int], k: int) -> int:
        count = {0: 1}
        prefix_sum = 0
        result = 0
        for num in nums:
            prefix_sum += num
            need = prefix_sum - k
            if need in count:
                result += count[need]
            if prefix_sum in count:
                count[prefix_sum] += 1
            else:
                count[prefix_sum] = 1
        return result
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，空间 O(n)。")

#strong[#text("记忆骨架：")]#text(" 计算当前前缀和 → 查找 S - k → 累加出现次数 → 记录当前前缀和。")

#jump("toc", "↑ 返回目录")

== #text("239. 滑动窗口最大值（LeetCode 239）") <lc239>

#strong[方法：] 固定滑动窗口 + 单调队列

#strong[题目要求：] 给定整数数组 `nums` 和窗口大小 `k`，从左到右返回每个长度为 `k` 的连续窗口的最大值。例如 `nums = [1, 3, -1, -3, 5, 3, 6, 7]`、`k = 3`，结果是 `[3, 3, 5, 5, 6, 7]`。逐个扫描每个窗口需要 O(nk) 时间，其中 n 是数组长度。

#strong[变量定义：] `i` 是本轮加入窗口的元素下标。`q` 是双端队列，保存仍有资格成为最大值的元素下标，从队首到队尾下标递增、对应数值严格递减。`q[0]` 和 `q[-1]` 分别是队首和队尾下标。`ans` 保存各窗口的最大值。比如下标队列 `[1, 2]` 对应数值 `[3, -1]`。保存下标后，既可以检查元素是否过期，也可以通过 `nums` 取回数值。

#strong[队首删除过期下标：] 当前窗口的左边界是 `i - k + 1`，比它更小的下标都过期。比如 `i = 4`、`k = 3` 时，窗口包含下标 2、3、4，队首如果是 1，就用 `popleft()` 删除。下标按入队先后排列，所以最早过期的候选总在队首。代码里的 `q[0] <= i - k` 与 `q[0] < i - k + 1` 等价。

#strong[队尾删除被新值超过的候选：] 当新值大于或等于队尾的值时，可以用 `pop()` 删掉队尾。旧值比新值更早入窗，也会更早出窗。从本轮起，只要旧值仍在窗口，新值也一定在窗口，且至少和它一样大。一个新值可能连续淘汰多个候选，因此要循环检查队尾。新下标入队后，队首对应最大的有效候选。

#strong[完整推演：] 表中 `下标:值` 用于核对位置与数值，队列实际只保存下标。每轮先清理队首，再从队尾淘汰候选，最后加入当前下标。前两轮窗口未满，从 `i = k - 1` 开始记录最大值。

#table(
  columns: (auto, auto, 1fr, 1fr, 2fr, auto),
  table.header([下标], [新值], [队首删除], [队尾删除], [入队后：队首 → 队尾], [最大值]),
  [0], [1], [无], [无], [`0:1`], [未满],
  [1], [3], [无], [`0:1`], [`1:3`], [未满],
  [2], [-1], [无], [无], [`1:3, 2:-1`], [3],
  [3], [-3], [无], [无], [`1:3, 2:-1, 3:-3`], [3],
  [4], [5], [`1:3`], [`3:-3, 2:-1`], [`4:5`], [5],
  [5], [3], [无], [无], [`4:5, 5:3`], [5],
  [6], [6], [无], [`5:3, 4:5`], [`6:6`], [6],
  [7], [7], [无], [`6:6`], [`7:7`], [7],
)

第 5 轮（`i = 4`）同时发生两种删除。先从队首删掉离开窗口的 `1:3`，再用新值 5 从队尾依次淘汰仍在窗口内的 `3:-3`、`2:-1`。入队后只剩 `4:5`，因此最大值为 5。

#strong[完整代码：]

```python
from collections import deque
from typing import List

class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        q = deque()
        ans = []

        for i in range(len(nums)):
            # 队首删掉过期下标
            while q and q[0] <= i - k:
                q.popleft()

            # 队尾删掉被新值超过或追平的候选
            while q and nums[q[-1]] <= nums[i]:
                q.pop()

            q.append(i)
            if i >= k - 1:
                ans.append(nums[q[0]])

        return ans
```

`q[0]` 是下标，所以写入答案的是 `nums[q[0]]`。旧最大值过期后，仍留在队列里的下一个候选会自然成为队首。

#strong[复杂度：] 每个下标最多入队一次、出队一次，所有轮次的删除次数合计至多 n，时间 O(n)。队列最多保存 k 个有效下标，额外空间 O(k)，不计返回结果。

#strong[记忆骨架：] 队首删过期下标 → 队尾淘汰小于等于新值的候选 → 新下标入队 → 窗口满了就查队首下标对应的值。

#jump("toc", "↑ 返回目录")

= #text("普通数组")

== #text("53. 最大子数组和（LeetCode 53）") <lc53>

#strong[#text("方法：")]#text(" 动态规划 / Kadane 算法")

#strong[#text("题目要求：")]#text(" 给定数组，找出和最大的连续非空子数组，返回它的和。")

#strong[#text("具体例子：")]#text(" nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]，最大和来自 [4, -1, 2, 1]，答案为 6。")

#strong[#text("核心原理：")]#text(" 令 current 表示“必须以当前数字结尾”的最大子数组和。遍历到 num 时，比较从 num 重新开始与接在上一段后面的收益：current = max(num, current + num)。再用 max_sum 记录遍历过程中出现的最大值。")

#strong[#text("关键关系：")]#text(" ")#raw("current = max(num, current + num)；max_sum = max(max_sum, current)")

#strong[#text("完整代码：")]

```python
class Solution:
    def maxSubArray(self, nums: list[int]) -> int:
        current = nums[0]
        max_sum = nums[0]
        for num in nums[1:]:
            current = max(num, current + num)
            max_sum = max(max_sum, current)
        return max_sum
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" 选择继续累加或从当前位置重新开始 → 更新历史最大和。")

#jump("toc", "↑ 返回目录")

== #text("56. 合并区间（LeetCode 56）") <lc56>

#strong[#text("方法：")]#text(" 排序 + 区间合并")

#strong[#text("题目要求：")]#text(" 把给定的重叠区间合并，输出互不重叠的区间列表。")

#strong[#text("具体例子：")]#text(" [[1, 3], [2, 6], [8, 10], [15, 18]] 合并后为 [[1, 6], [8, 10], [15, 18]]。")

#strong[#text("核心原理：")]#text(" 先按区间左端点升序排序。维护 merged 作为当前已经合并的区间；对于下一个 [start, end]，如果 start 不超过 merged 最后一个区间的右端点，二者重叠，更新右端点为两个 end 的最大值，否则把当前区间作为新的一段加入结果。")

#strong[#text("关键关系：")]#text(" ")#raw("start ≤ merged[-1][1] 时合并，新的右端点 = max(merged[-1][1], end)")

#strong[#text("完整代码：")]

```python
class Solution:
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        intervals.sort()
        merged = [intervals[0]]
        for start, end in intervals[1:]:
            if start <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], end)
            else:
                merged.append([start, end])
        return merged
```

#strong[#text("复杂度：")]#text(" 时间 O(n log n)，主要来自排序；辅助空间取决于排序实现，输出空间另计。")

#strong[#text("记忆骨架：")]#text(" 按起点排序 → 保存首段 → 判断是否重叠 → 合并终点或加入新段。")

#jump("toc", "↑ 返回目录")

== #text("189. 轮转数组（LeetCode 189）") <lc189>

#strong[#text("方法：")]#text(" 三次反转 + 双指针")

#strong[#text("题目要求：")]#text(" 给定整数数组 nums，将元素向右轮转 k 个位置；需要直接修改原数组，并尽量使用 O(1) 的额外空间。")

#strong[#text("具体例子：")]#text(" nums = [1,2,3,4,5,6,7]，k = 3。最后三个元素 [5,6,7] 移动到最前面，得到 [5,6,7,1,2,3,4]。")

#strong[#text("核心原理：")]#text(" 把原数组看作 A+B，其中 B 是最后 k 个元素，目标顺序为 B+A。先整体反转，使两段各自逆序且交换前后位置；再分别反转前 k 个和其余元素，就能恢复 B、A 内部的正确顺序。每次反转用左右指针交换，不额外创建数组。由于 k 可能超过数组长度，开始时要令 k %= n。")

#table(columns: (1fr, 2.5fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("操作")], [#text("数组状态")]),
  table.hline(stroke: .4pt),
  [#text("初始")], [#text("[1,2,3,4,5,6,7]")],
  [#text("整体反转")], [#text("[7,6,5,4,3,2,1]")],
  [#text("反转前 3 个")], [#text("[5,6,7,4,3,2,1]")],
  [#text("反转后 4 个")], [#text("[5,6,7,1,2,3,4]")],
  table.hline(stroke: .7pt))

#text("每次反转只需要从两端向中间交换元素；三个区间依次是 [0,n-1]、[0,k-1] 和 [k,n-1]。")

#strong[#text("完整代码：")]

```python
class Solution:
    def rotate(self, nums: list[int], k: int) -> None:
        n = len(nums)
        k %= n

        def reverse(left, right):
            while left < right:
                nums[left], nums[right] = nums[right], nums[left]
                left += 1
                right -= 1

        reverse(0, n - 1)
        reverse(0, k - 1)
        reverse(k, n - 1)
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" k %= n → 整体反转 → 反转前 k 个元素 → 反转剩余元素。")

#jump("toc", "↑ 返回目录")

== #text("238. 除了自身以外数组的乘积（LeetCode 238）") <lc238>

#strong[#text("方法：")]#text(" 前缀积 + 后缀积")

#strong[#text("题目要求：")]#text(" 给定整数数组 nums，返回 answer，其中 answer[i] 是除 nums[i] 外所有元素的乘积。不能使用除法，要求时间 O(n)。")

#strong[#text("具体例子：")]#text(" nums = [1,2,3,4]，对于 3，左侧乘积为 1×2=2，右侧乘积为 4，因此答案为 8。最终输出 [24,12,8,6]。")

#strong[#text("核心原理：")]#text(" 每个位置的结果可以分为“左边所有数字的乘积 × 右边所有数字的乘积”。第一次从左往右，用 prefix 累乘并写入 answer；第二次从右往左，用 suffix 补上右侧乘积。两个方向都要先使用已有的乘积，再把当前数字乘进去，这样计算时才不会包含 nums[i] 自身。")

#table(columns: (1fr, 1fr, 1fr, 1fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("当前数字")], [#text("左侧乘积")], [#text("右侧乘积")], [#text("答案")]),
  table.hline(stroke: .4pt),
  [#text("1")], [#text("1")], [#text("2×3×4=24")], [#text("24")],
  [#text("2")], [#text("1")], [#text("3×4=12")], [#text("12")],
  [#text("3")], [#text("1×2=2")], [#text("4")], [#text("8")],
  [#text("4")], [#text("1×2×3=6")], [#text("1")], [#text("6")],
  table.hline(stroke: .7pt))

#text("第一次遍历结束时，answer = [1,1,2,6]；第二次补上右侧乘积 [24,12,4,1]，得到 [24,12,8,6]。prefix *= nums[i] 和 suffix *= nums[i] 必须放在记录当前结果之后。")

#strong[#text("完整代码：")]

```python
class Solution:
    def productExceptSelf(self, nums: list[int]) -> list[int]:
        n = len(nums)
        answer = [1] * n
        prefix = 1
        for i in range(n):
            answer[i] = prefix
            prefix *= nums[i]

        suffix = 1
        for i in range(n - 1, -1, -1):
            answer[i] *= suffix
            suffix *= nums[i]
        return answer
```

#strong[#text("复杂度：")]#text(" 时间 O(n)；不计返回的 answer，额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" 创建 answer → 从左向右记录前缀积 → 从右向左补后缀积 → 返回。关键是先记录，再更新累计积。")

#jump("toc", "↑ 返回目录")

= #text("矩阵")

== #text("54. 螺旋矩阵（LeetCode 54）") <lc54>

#strong[方法：] 四边界模拟

#strong[题目要求：] 给定一个矩阵，从左上角开始顺时针访问每个元素，返回访问顺序。

#strong[变量定义：] `m`、`n` 是行数和列数。`top`、`bottom` 是尚未访问区域的上下行下标，初始为 0 和 `m - 1`。`left`、`right` 是左右列下标，初始为 0 和 `n - 1`。四个边界都包含在剩余区域内。`i`、`j` 分别是行、列下标，`res` 保存访问结果。

#strong[为什么不会重复访问：] 每走完一条边，立即把对应边界往里挪一格。比如走完上边就执行 `top += 1`，下一条右边从新的 `top` 开始，右上角便只会走一次。每走完一圈，留下的仍是一个矩形。遍历下边之前检查是否还有行，遍历左边之前检查是否还有列。只剩一行时，上边走完后就没有下边可走了。只剩一列时，右边走完后就没有左边可走了。

#strong[逐步推演：] 对矩阵 `[[1,2,3],[4,5,6],[7,8,9]]`，先取上边 1、2、3，`top` 变成 1。再取右边 6、9，`right` 变成 1。接着取下边 8、7，`bottom` 变成 1。最后取左边 4，`left` 变成 1。此时四个边界都是 1，第二轮取走中心的 5 后结束。结果为 `[1,2,3,6,9,8,7,4,5]`。

#strong[循环范围：] Python 的 `range` 不包含终点。从左到右用 `range(left, right + 1)` 才能包含右边界。从右到左用 `range(right, left - 1, -1)` 才能包含左边界，行下标同理。

```python
class Solution:
    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        if not matrix:
            return []

        m, n = len(matrix), len(matrix[0])
        top, bottom = 0, m - 1
        left, right = 0, n - 1
        res = []

        while top <= bottom and left <= right:
            for j in range(left, right + 1):
                res.append(matrix[top][j])
            top += 1

            for i in range(top, bottom + 1):
                res.append(matrix[i][right])
            right -= 1

            if top <= bottom:
                for j in range(right, left - 1, -1):
                    res.append(matrix[bottom][j])
                bottom -= 1

            if left <= right:
                for i in range(bottom, top - 1, -1):
                    res.append(matrix[i][left])
                left += 1

        return res
```

#strong[复杂度：] 时间 O(mn)，每个元素访问一次。不计结果列表，额外空间 O(1)。

#strong[记忆骨架：] 未访问区域是矩形 → 上、右、下、左依次取边 → 取完马上缩边 → 下边和左边先检查边界。

#jump("toc", "↑ 返回目录")

= #text("链表")

== #text("160. 相交链表（LeetCode 160）") <lc160>

#strong[#text("方法：")]#text(" 双指针 + 交换起点")

#strong[#text("题目要求：")]#text(" 给定两个单链表的头节点 headA、headB，返回它们真正相交的起始节点；没有交点则返回 None，且不得修改链表。")

#strong[#text("具体例子：")]#text(" A：4 → 1 → 8 → 4 → 5；B：5 → 6 → 1 → 8 → 4 → 5。两条链表从节点 8 开始共用节点，答案是该共同节点。相同的 val 不代表同一节点，因此用 is 比较对象身份。")

#strong[#text("核心原理：")]#text(" 令两个指针 pA、pB 分别从 A、B 的头节点出发，每次移动一格；pA 走完 A 后从 B 头部继续走，pB 走完 B 后从 A 头部继续走。设两条链表独有部分长度分别为 a、b，共同部分为 c。两指针在切换后都走过 a+b 个独有节点，所以会同时到达交点；若不相交，最终会同时成为 None。")

#table(columns: (1fr, 1fr, 1fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("移动次数")], [#text("pA 指向")], [#text("pB 指向")]),
  table.hline(stroke: .4pt),
  [#text("初始")], [#text("A 的 4")], [#text("B 的 5")],
  [#text("1")], [#text("A 的 1")], [#text("B 的 6")],
  [#text("2")], [#text("共同的 8")], [#text("B 的 1")],
  [#text("3")], [#text("共同的 4")], [#text("共同的 8")],
  [#text("4")], [#text("共同的 5")], [#text("共同的 4")],
  [#text("5")], [#text("None")], [#text("共同的 5")],
  [#text("6")], [#text("B 的 5")], [#text("None")],
  [#text("7")], [#text("B 的 6")], [#text("A 的 4")],
  [#text("8")], [#text("B 的 1")], [#text("A 的 1")],
  [#text("9")], [#text("共同的 8")], [#text("共同的 8")],
  table.hline(stroke: .7pt))

#text("这里 pA is pB 才表示指向同一个节点对象；仅靠 pA.val == pB.val 可能误判。走到 None 才切换到另一条链表的头节点。")

#strong[#text("完整代码：")]

```python
class Solution:
    def getIntersectionNode(
        self,
        headA: ListNode,
        headB: ListNode
    ) -> Optional[ListNode]:
        pA = headA
        pB = headB
        while pA is not pB:
            if pA is None:
                pA = headB
            else:
                pA = pA.next
            if pB is None:
                pB = headA
            else:
                pB = pB.next
        return pA
```

#strong[#text("复杂度：")]#text(" 时间 O(m+n)，额外空间 O(1)，其中 m、n 为两条链表长度。")

#strong[#text("记忆骨架：")]#text(" 两个指针分别出发 → 同步向后移动 → 到 None 就切换另一条链表 → 相遇时返回节点。")

#jump("toc", "↑ 返回目录")

== #text("206. 反转链表（LeetCode 206）") <lc206>

#strong[#text("方法：")]#text(" 迭代 + 三指针")

#strong[#text("题目要求：")]#text(" 给定单链表头节点 head，原地反转整个链表，并返回反转后的新头节点。")

#strong[#text("具体例子：")]#text(" 1 → 2 → 3 → 4 → 5 → None 反转后得到 5 → 4 → 3 → 2 → 1 → None。")

#strong[#text("核心原理：")]#text(" 每次需要把当前节点 curr 的 next 指向已反转部分的头节点 prev。为避免丢失后面尚未处理的链表，必须先把原本的 curr.next 暂存到 next_node。改变箭头后，再更新 prev = curr、curr = next_node。直到 curr 变为 None，此时 prev 就是新头节点。")

#table(columns: (1fr, 1fr, 1fr, 1.7fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("状态")], [#text("prev 指向")], [#text("curr 指向")], [#text("已反转部分")]),
  table.hline(stroke: .4pt),
  [#text("初始")], [#text("None")], [#text("1")], [#text("空")],
  [#text("第一轮后")], [#text("1")], [#text("2")], [#text("1 → None")],
  [#text("第二轮后")], [#text("2")], [#text("3")], [#text("2 → 1 → None")],
  [#text("第三轮后")], [#text("3")], [#text("None")], [#text("3 → 2 → 1 → None")],
  table.hline(stroke: .7pt))

#text("四行核心操作分别是：先保存 next_node = curr.next；再用 curr.next = prev 真正改变箭头；随后 prev = curr 更新新头节点；最后 curr = next_node 处理下一节点。")

#strong[#text("完整代码：")]

```python
class Solution:
    def reverseList(
        self,
        head: Optional[ListNode]
    ) -> Optional[ListNode]:
        prev = None
        curr = head
        while curr is not None:
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node
        return prev
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" prev = None、curr = head → 保存下一节点 → 反转 curr.next → 更新 prev 和 curr → 返回 prev。")

#jump("toc", "↑ 返回目录")

== #text("234. 回文链表（LeetCode 234）") <lc234>

#strong[#text("方法：")]#text(" 链表遍历 + 列表反转")

#strong[#text("题目要求：")]#text(" 给定单链表头节点 ")#raw("head")#text("，判断是否为回文链表。从前向后和从后向前读取的节点值完全相同则返回 ")#raw("True")#text("，否则返回 ")#raw("False")#text("。")

#strong[#text("具体例子：")]#text(" ")#raw("head = [1,2,2,1]")#text("，正序和逆序均为 ")#raw("[1,2,2,1]")#text("，返回 ")#raw("True")#text("；")#raw("head = [1,2]")#text("，返回 ")#raw("False")#text("。")

#strong[#text("核心原理：")]#text(" 单链表只允许通过 ")#raw("next")#text(" 向后遍历。因此先让 ")#raw("curr")#text(" 从头到尾读取每个节点的 ")#raw("val")#text("，将它们依次存入列表 ")#raw("nums")#text("。再用 Python 切片 ")#raw("nums[::-1]")#text(" 生成逆序列表，比较正序和逆序是否相同。")#raw("curr = curr.next")#text(" 仅让指针移动，不会修改链表连接关系。")

#strong[#text("完整代码：")]

```python
class Solution:
    def isPalindrome(self, head: Optional[ListNode]) -> bool:
        nums = []
        curr = head
        while curr is not None:
            nums.append(curr.val)
            curr = curr.next
        return nums == nums[::-1]
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，额外空间 O(n)，主要用于保存各节点的值。")

#strong[#text("记忆骨架：")]#text(" 创建空列表 → 遍历链表收集 ")#raw("val")#text(" → 使用 ")#raw("[::-1]")#text(" 反转列表 → 比较正序和逆序。")

#jump("toc", "↑ 返回目录")

== #text("141. 环形链表（LeetCode 141）") <lc141>

#strong[#text("方法：")]#text(" 快慢指针（Floyd 判圈算法）")

#strong[#text("题目要求：")]#text(" 给定单链表头节点 ")#raw("head")#text("，判断链表中是否存在环。如果沿着 ")#raw("next")#text(" 指针能够再次访问以前经过的同一个节点，返回 ")#raw("True")#text("，否则返回 ")#raw("False")#text("。")

#strong[#text("具体例子：")]#text(" ")#raw("head = [3,2,0,-4]")#text("，")#raw("pos = 1")#text(" 表示尾节点 ")#raw("-4")#text(" 指回下标为 1 的节点 ")#raw("2")#text("，构成 ")#raw("2 → 0 → -4 → 2")#text(" 的环，答案为 ")#raw("True")#text("。")

#strong[#text("核心原理：")]#text(" ")#raw("slow")#text(" 和 ")#raw("fast")#text(" 初始均指向头节点，每轮让慢指针走一步，快指针走两步。如果链表有环，进入环后快指针每轮比慢指针多走一步，最终必然追上慢指针；如果没有环，快指针会走到 ")#raw("None")#text("。本例两指针的移动如下：")

#table(columns: (1fr, 1fr, 1fr, 1.6fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("轮次")], [#text("slow")], [#text("fast")], [#text("判断")]),
  table.hline(stroke: .4pt),
  [#text("初始")], [#text("3")], [#text("3")], [#text("尚未移动")],
  [#text("第 1 轮")], [#text("2")], [#text("0")], [#text("未相遇")],
  [#text("第 2 轮")], [#text("0")], [#text("2")], [#text("未相遇")],
  [#text("第 3 轮")], [#text("-4")], [#text("-4")], [#text("相遇，存在环")],
  table.hline(stroke: .7pt))

#text("判断是否为同一节点应使用 ")#raw("is")#text("，两个不同节点可能存有相同的 ")#raw("val")#text("。循环条件 ")#raw("fast and fast.next")#text(" 用于保证快指针可以安全地移动两步。")

#strong[#text("完整代码：")]

```python
class Solution:
    def hasCycle(self, head: Optional[ListNode]) -> bool:
        slow = head
        fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                return True
        return False
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，额外空间 O(1)，只需要两个指针。")

#strong[#text("记忆骨架：")]#text(" 初始化快慢指针 → 慢一快二 → 相遇返回 ")#raw("True")#text(" → 快指针到末尾返回 ")#raw("False")#text("。")

#jump("toc", "↑ 返回目录")

== #text("142. 环形链表 II（LeetCode 142）") <lc142>

#strong[#text("方法：")]#text(" 快慢指针 + 环入口定位")

#strong[#text("题目要求：")]#text(" 给定单链表的头节点 ")#raw("head")#text("，若存在环，返回环开始的第一个节点；没有环则返回 ")#raw("None")#text("。不能修改链表结构。")

#strong[#text("具体例子：")]#text(" ")#raw("head = [3,2,0,-4]")#text("，")#raw("pos = 1")#text("。尾节点 ")#raw("-4")#text(" 指向节点 ")#raw("2")#text("，因此入口是原链表中值为 ")#raw("2")#text(" 的节点。")

#strong[#text("核心原理：")]#text(" 先用快慢指针找到它们在环内第一次相遇的位置。随后令新指针 ")#raw("p = head")#text("，保留 ")#raw("slow")#text(" 在相遇点，再让 ")#raw("p")#text(" 和 ")#raw("slow")#text(" 每次各前进一步；第二次相遇的位置就是环入口。")

#text("设头节点到入口距离为 ")#raw("a")#text("，入口到第一次相遇点距离为 ")#raw("b")#text("，环的长度为 ")#raw("L")#text("。第一次相遇时，快指针走过的距离为慢指针的两倍，因此 ")#raw("a + b = kL")#text("（")#raw("k")#text(" 为正整数），即 ")#raw("a = (k-1)L + (L-b)")#text("。从头节点走 ")#raw("a")#text(" 步到入口，等价于从相遇点沿环继续走 ")#raw("a")#text(" 步后到入口；两个指针因此在入口相遇。")

#table(columns: (1fr, 2.3fr, 1.3fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("阶段")], [#text("指针位置变化")], [#text("结果")]),
  table.hline(stroke: .4pt),
  [#text("第一次相遇")], [#raw("slow")#text(" 和 ")#raw("fast")#text(" 同在 ")#raw("-4")], [#text("确认存在环")],
  [#text("设置新指针")], [#raw("p")#text(" 在 ")#raw("3")#text("，")#raw("slow")#text(" 在 ")#raw("-4")], [#text("准备寻找入口")],
  [#text("同步移动")], [#raw("p")#text(" 和 ")#raw("slow")#text(" 各走一步")], [#text("两者都到 ")#raw("2")],
  [#text("第二次相遇")], [#raw("p is slow")], [#text("返回环入口")],
  table.hline(stroke: .7pt))

#strong[#text("完整代码：")]

```python
class Solution:
    def detectCycle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        slow = head
        fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                p = head
                while p is not slow:
                    p = p.next
                    slow = slow.next
                return p
        return None
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，额外空间 O(1)，没有创建额外的数据结构。")

#strong[#text("记忆骨架：")]#text(" 快慢指针检测环 → 第一次相遇 → 新指针从头出发 → 两指针同速前进 → 第二次相遇就是环入口。")

#jump("toc", "↑ 返回目录")

== #text("21. 合并两个有序链表（LeetCode 21）") <lc21>

#strong[#text("方法：")]#text(" 双指针 + 虚拟头节点")

#strong[#text("题目要求：")]#text(" 给定两条按升序排列的链表 ")#raw("list1")#text(" 和 ")#raw("list2")#text("，把原有节点合并为一条升序链表，并返回合并后的头节点。")

#strong[#text("具体例子：")]#text(" ")#raw("list1 = [1,2,4]")#text("，")#raw("list2 = [1,3,4]")#text("，合并结果为 ")#raw("[1,1,2,3,4,4]")#text("。")

#strong[#text("核心原理：")]#text(" 由于两条链表均已排序，每次比较两个当前节点的 ")#raw("val")#text("，把较小的节点接到结果链表的尾部，并向后移动对应链表的指针。创建虚拟头节点 ")#raw("dummy = ListNode(0)")#text("，用 ")#raw("tail = dummy")#text(" 记录当前已合并部分的末尾。")#raw("dummy")#text(" 始终留在链表开头，")#raw("tail")#text(" 负责不断接入新节点。合并结束后返回 ")#raw("dummy.next")#text("，跳过用于连接的虚拟节点。")

#text("下面三句分别完成接入节点、移动原链表指针、移动结果尾指针：")

```python
tail.next = list1
list1 = list1.next
tail = tail.next
```

#table(columns: (1fr, 1.4fr, 1.3fr, 1.8fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("轮次")], [#text("当前比较")], [#text("选择节点")], [#text("已合并部分")]),
  table.hline(stroke: .4pt),
  [#text("初始")], [#text("1 和 1")], [#text("—")], [#text("空")],
  [#text("第 1 轮")], [#text("1 和 1")], [#raw("list1")#text(" 的 1")], [#text("1")],
  [#text("第 2 轮")], [#text("2 和 1")], [#raw("list2")#text(" 的 1")], [#text("1 → 1")],
  [#text("第 3 轮")], [#text("2 和 3")], [#raw("list1")#text(" 的 2")], [#text("1 → 1 → 2")],
  [#text("第 4 轮")], [#text("4 和 3")], [#raw("list2")#text(" 的 3")], [#text("1 → 1 → 2 → 3")],
  [#text("第 5 轮")], [#text("4 和 4")], [#raw("list1")#text(" 的 4")], [#text("1 → 1 → 2 → 3 → 4")],
  [#text("结束")], [#raw("list1")#text(" 已为空")], [#text("接上 ")#raw("list2")#text(" 的剩余节点")], [#text("1 → 1 → 2 → 3 → 4 → 4")],
  table.hline(stroke: .7pt))

#strong[#text("完整代码：")]

```python
class Solution:
    def mergeTwoLists(
        self,
        list1: Optional[ListNode],
        list2: Optional[ListNode]
    ) -> Optional[ListNode]:
        dummy = ListNode(0)
        tail = dummy
        while list1 is not None and list2 is not None:
            if list1.val <= list2.val:
                tail.next = list1
                list1 = list1.next
            else:
                tail.next = list2
                list2 = list2.next
            tail = tail.next
        if list1 is not None:
            tail.next = list1
        else:
            tail.next = list2
        return dummy.next
```

#strong[#text("复杂度：")]#text(" 时间 O(m+n)，额外空间 O(1)，其中 m、n 为两条链表长度，直接复用已有节点。")

#strong[#text("记忆骨架：")]#text(" 创建 ")#raw("dummy")#text(" 和 ")#raw("tail")#text(" → 比较两节点 → 接入较小节点 → 移动指针和 ")#raw("tail")#text(" → 接上剩余链表 → 返回 ")#raw("dummy.next")#text("。")

#jump("toc", "↑ 返回目录")

== #text("2. 两数相加（LeetCode 2）") <lc2>

#strong[#text("方法：")]#text(" 模拟竖式加法 + 虚拟头节点")

#strong[#text("题目要求：")]#text(" 两条非空链表 ")#raw("l1")#text(" 和 ")#raw("l2")#text(" 分别以逆序存储一个非负整数的各位数字，每个节点保存一位数字。计算两数之和，返回同样逆序存储的新链表。")

#strong[#text("具体例子：")]#text(" ")#raw("l1 = [2,4,3]")#text(" 表示 342，")#raw("l2 = [5,6,4]")#text(" 表示 465，因此 ")#raw("342 + 465 = 807")#text("，返回 ")#raw("[7,0,8]")#text("，即 ")#raw("7 → 0 → 8")#text("。")

#strong[#text("核心原理：")]#text(" 模拟小学竖式加法，同时遍历两个链表，并用 ")#raw("carry")#text(" 保存上一位的进位。某一条链表走到末尾后，该位置按 0 处理。每一位的和为 ")#raw("total = x + y + carry")#text("，利用 ")#raw("total % 10")#text(" 得到本位数字，利用 ")#raw("total // 10")#text(" 得到下一位进位。结果链表使用 ")#raw("dummy")#text(" 保存起点，")#raw("current")#text(" 指向最后一个已创建的节点。")

#text("以示例为例，每轮的计算过程如下：")

#table(columns: (0.8fr, 1.6fr, 1.4fr, 1.6fr, 1.8fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("轮次")], [#text("当前计算")], [#text("新节点 ")#raw("digit")], [#text("下一轮进位 ")#raw("carry")], [#text("结果链表")]),
  table.hline(stroke: .4pt),
  [#text("个位")], [#text("2 + 5 + 0 = 7")], [#text("7")], [#text("0")], [#text("7")],
  [#text("十位")], [#text("4 + 6 + 0 = 10")], [#text("0")], [#text("1")], [#text("7 → 0")],
  [#text("百位")], [#text("3 + 4 + 1 = 8")], [#text("8")], [#text("0")], [#text("7 → 0 → 8")],
  table.hline(stroke: .7pt))

#strong[#text("关键代码解释：")]#text(" ")#raw("current.next = ListNode(digit)")#text(" 创建并接入新节点；")#raw("current = current.next")#text(" 将尾指针移到新节点。")#raw("dummy")#text(" 始终位于起点，返回时使用 ")#raw("dummy.next")#text("。循环条件必须包含 ")#raw("carry")#text("，例如 ")#raw("99 + 1 = 100")#text(" 时，两条链表遍历结束后还要增加一个存放 1 的节点。")

#strong[#text("完整代码：")]

```python
class Solution:
    def addTwoNumbers(
        self,
        l1: Optional[ListNode],
        l2: Optional[ListNode]
    ) -> Optional[ListNode]:
        dummy = ListNode(0)
        current = dummy
        carry = 0

        while l1 or l2 or carry:
            x = l1.val if l1 else 0
            y = l2.val if l2 else 0
            total = x + y + carry
            digit = total % 10
            carry = total // 10

            current.next = ListNode(digit)
            current = current.next

            if l1:
                l1 = l1.next
            if l2:
                l2 = l2.next

        return dummy.next
```

#strong[#text("复杂度：")]#text(" 时间 O(max(m, n))；新链表占用 O(max(m, n)) 空间，其中 m、n 为输入链表长度。")

#strong[#text("记忆骨架：")]#text(" 创建 ")#raw("dummy")#text(" 和 ")#raw("current")#text(" → 取两位与进位求和 → ")#raw("% 10")#text(" 求本位、")#raw("// 10")#text(" 求进位 → 创建并连接节点 → 移动链表指针 → 返回 ")#raw("dummy.next")#text("。")

#jump("toc", "↑ 返回目录")

== #text("19. 删除链表的倒数第 N 个节点（LeetCode 19）") <lc19>

#strong[#text("方法：")]#text(" 虚拟头节点 + 快慢双指针")

#strong[#text("题目要求：")]#text(" 删除单链表中倒数第 ")#raw("n")#text(" 个节点，返回删除后的头节点；假设 ")#raw("n")#text(" 合法且不超过链表长度。")

#strong[#text("具体例子：")]#text(" ")#raw("head = [1,2,3,4,5]")#text("、")#raw("n = 2")#text("，删除节点 4 后得到 ")#raw("[1,2,3,5]")#text("。")

#strong[#text("核心原理：")]#text(" 创建 ")#raw("dummy = ListNode(0, head)")#text("，让 ")#raw("fast")#text("、")#raw("slow")#text(" 都从 ")#raw("dummy")#text(" 出发。先让 ")#raw("fast")#text(" 向后走 ")#raw("n + 1")#text(" 步，使两指针间隔为 ")#raw("n + 1")#text(" 个位置。然后两指针同步后移，直到 ")#raw("fast")#text(" 为 ")#raw("None")#text("，此时 ")#raw("slow")#text(" 恰好在待删除节点的前一个节点。于是用 ")#raw("slow.next = slow.next.next")#text(" 跳过待删除节点。")

#table(columns: (1fr, 1.3fr, 1.3fr, 2fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("阶段")], [#raw("fast")#text(" 所在位置")], [#raw("slow")#text(" 所在位置")], [#text("说明")]),
  table.hline(stroke: .4pt),
  [#text("初始")], [#text("dummy")], [#text("dummy")], [#text("两指针同起点")],
  [#raw("fast")#text(" 先走 3 步")], [#text("3")], [#text("dummy")], [#text("因 ")#raw("n = 2")#text("，先移动 ")#raw("n + 1")#text(" 步")],
  [#text("同步移动结束")], [#text("None")], [#text("3")], [#raw("slow.next")#text(" 是待删除节点 4")],
  [#text("执行删除")], [#text("None")], [#text("3")], [#text("让 3 直接连接 5")],
  table.hline(stroke: .7pt))

#strong[#text("关键代码解释：")]#text(" ")#raw("for _ in range(n + 1)")#text(" 用于拉开两指针距离。")#raw("slow.next = slow.next.next")#text(" 改变真实的节点连接，跳过下一个节点。使用 ")#raw("dummy")#text(" 能统一处理删除头节点的情况，例如 ")#raw("[1,2,3]")#text("、")#raw("n = 3")#text("，最终返回的 ")#raw("dummy.next")#text(" 就是节点 2。")

#strong[#text("完整代码：")]

```python
class Solution:
    def removeNthFromEnd(
        self,
        head: Optional[ListNode],
        n: int
    ) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        fast = dummy
        slow = dummy

        for _ in range(n + 1):
            fast = fast.next

        while fast:
            fast = fast.next
            slow = slow.next

        slow.next = slow.next.next
        return dummy.next
```

#strong[#text("复杂度：")]#text(" 时间 O(L)，额外空间 O(1)，其中 L 为链表长度。")

#strong[#text("记忆骨架：")]#text(" 添加 ")#raw("dummy")#text(" → 两指针从 ")#raw("dummy")#text(" 出发 → ")#raw("fast")#text(" 先走 ")#raw("n + 1")#text(" 步 → 两指针同步走到 ")#raw("fast")#text(" 为 ")#raw("None")#text(" → 跳过 ")#raw("slow.next")#text(" → 返回 ")#raw("dummy.next")#text("。")

#jump("toc", "↑ 返回目录")

== #text("24. 两两交换链表中的节点（LeetCode 24）") <lc24>

#strong[#text("方法：")]#text(" 虚拟头节点 + 三指针重连")

#strong[#text("题目要求：")]#text(" 将链表中每两个相邻节点交换位置，必须改变节点之间的 ")#raw("next")#text(" 连接，不直接修改节点的 ")#raw("val")#text("。")

#strong[#text("具体例子：")]#text(" ")#raw("1 → 2 → 3 → 4")#text(" 交换后变为 ")#raw("2 → 1 → 4 → 3")#text("；如果链表节点数为奇数，最后一个节点保持原位置。")

#strong[#text("核心原理：")]#text(" ")#raw("prev")#text(" 指向当前待交换的两个节点之前的节点，")#raw("first = prev.next")#text(" 是第一节点，")#raw("second = first.next")#text(" 是第二节点。交换一组需要修改三个 ")#raw("next")#text("：先让 ")#raw("first")#text(" 指向下一组的开头，再让 ")#raw("second")#text(" 指向 ")#raw("first")#text("，最后让 ")#raw("prev")#text(" 指向 ")#raw("second")#text("。完成后，")#raw("first")#text(" 成为本组尾节点，所以令 ")#raw("prev = first")#text("，继续处理下一组。")

#table(columns: (1fr, 1.5fr, 2fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("操作")], [#text("节点关系")], [#text("作用")]),
  table.hline(stroke: .4pt),
  [#text("初始")], [#text("dummy → 1 → 2 → 3")], [#text("当前要交换 1、2")],
  [#raw("first.next = second.next")], [#text("1 → 3")], [#text("保住后续链表")],
  [#raw("second.next = first")], [#text("2 → 1 → 3")], [#text("第二节点移到第一节点前")],
  [#raw("prev.next = second")], [#text("dummy → 2 → 1 → 3")], [#text("前一部分连接到新组头")],
  [#raw("prev = first")], [#raw("prev")#text(" 在节点 1")], [#text("准备下一组")],
  table.hline(stroke: .7pt))

#strong[#text("关键代码解释：")]#text(" 循环条件 ")#raw("while prev.next and prev.next.next")#text(" 确保后面至少有两个节点。")#raw("first.next = second.next")#text(" 必须先执行，以免断开后面未处理的节点。")#raw("prev = first")#text(" 将基准指针移到刚交换完的一组末尾。借助 ")#raw("dummy")#text("，原头节点被交换时也能返回正确的新头节点。")

#strong[#text("完整代码：")]

```python
class Solution:
    def swapPairs(
        self,
        head: Optional[ListNode]
    ) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        prev = dummy

        while prev.next and prev.next.next:
            first = prev.next
            second = first.next

            first.next = second.next
            second.next = first
            prev.next = second

            prev = first

        return dummy.next
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，额外空间 O(1)；仅使用固定数量的指针变量。")

#strong[#text("记忆骨架：")]#text(" 创建 ")#raw("dummy")#text(" 和 ")#raw("prev")#text(" → 找到 ")#raw("first")#text("、")#raw("second")#text(" → 修改三个 ")#raw("next")#text(" → 让 ")#raw("prev = first")#text(" → 继续下一组 → 返回 ")#raw("dummy.next")#text("。")

#jump("toc", "↑ 返回目录")


#strong[#text("链表指针操作对照")]

#text("这三题都使用 ")#raw("dummy")#text(" 处理链表起点，但对应三类不同的节点操作：第 2 题创建新节点，第 19 题跳过旧节点，第 24 题调整旧节点顺序。写代码前先明确指针指向哪个节点，再判断需要修改的 ")#raw("next")#text("。")

#table(columns: (0.9fr, 1.25fr, 1.5fr, 1.4fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("对比维度")], [#text("2. 两数相加")], [#text("19. 删除倒数第 N 个")], [#text("24. 两两交换")]),
  table.hline(stroke: .4pt),
  [#text("核心方法")], [#text("竖式加法 + 建链表")], [#text("快慢双指针")], [#text("三次重连")],
  [#raw("dummy")#text(" 的作用")], [#text("保存新链表起点")], [#text("统一删除头节点")], [#text("处理头节点换位")],
  [#text("关键指针")], [#raw("current")], [#raw("fast")#text("、")#raw("slow")], [#raw("prev")#text("、")#raw("first")#text("、")#raw("second")],
  [#text("核心操作")], [#raw("current.next = ListNode(digit)")], [#raw("slow.next = slow.next.next")], [#text("修改三个 ")#raw("next")],
  [#text("是否创建业务节点")], [#text("是")], [#text("否")], [#text("否")],
  table.hline(stroke: .7pt))

== #text("25. K 个一组翻转链表（LeetCode 25）") <lc25>

#strong[#text("方法：")]#text(" 虚拟头节点 + 分组反转 + 指针调整")

#strong[#text("题目要求：")]#text(" 给定链表头节点 ")#raw("head")#text(" 和整数 ")#raw("k")#text("，每 ")#raw("k")#text(" 个节点翻转一次。剩余节点不足 ")#raw("k")#text(" 个时保持原顺序。必须实际交换节点的连接关系，不能只交换节点的值。")

#strong[#text("具体例子：")]#text(" ")#raw("1 → 2 → 3 → 4 → 5")#text("，")#raw("k = 2")#text("，输出 ")#raw("2 → 1 → 4 → 3 → 5")#text("。")

#strong[#text("核心原理：")]#text(" 每次处理一组节点。先找到这一组的第 ")#raw("k")#text(" 个节点 ")#raw("kth")#text("，确定下一组的起点 ")#raw("group_next")#text("。然后把当前组的指针逐个反转，最后把前一组重新连接到反转后的组头，并移动到下一组。如果当前剩余节点不足 ")#raw("k")#text(" 个，就直接返回，不再反转。")

#strong[#text("完整代码：")]

```python
class Solution:
    def reverseKGroup(self, head: ListNode | None, k: int) -> ListNode | None:
        dummy = ListNode(0, head)
        group_prev = dummy  # 当前组前面的节点

        while True:
            kth = group_prev
            # 找当前组第 k 个节点，不足 k 个就结束
            for _ in range(k):
                kth = kth.next
                if kth is None:
                    return dummy.next

            group_next = kth.next  # 下一组的第一个节点
            # 反转当前组，prev 一开始指向下一组
            prev = group_next
            curr = group_prev.next
            while curr is not group_next:
                next_node = curr.next  # 先保存下一个节点
                curr.next = prev       # 反转当前节点的指针
                prev = curr
                curr = next_node

            # 当前组原来的头节点，反转后变成组尾
            group_tail = group_prev.next
            group_prev.next = kth    # 前一组连接到反转后的组头
            group_prev = group_tail  # 从新组尾继续处理下一组
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，每个节点只处理常数次；额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" 找第 ")#raw("k")#text(" 个节点 → 确定下一组起点 → 反转当前组 → 前一组连接新组头 → 从新组尾继续。")

#jump("toc", "↑ 返回目录")

== #text("138. 随机链表的复制（LeetCode 138）") <lc138>

#strong[#text("方法：")]#text(" 节点穿插法 + 三次遍历")

#strong[#text("题目要求：")]#text(" 给定一条链表，每个节点有 ")#raw("val")#text("、")#raw("next")#text(" 和 ")#raw("random")#text("。")#raw("random")#text(" 可以指向链表中的任意节点或 ")#raw("None")#text("。要求深拷贝所有节点，并正确复制 ")#raw("next")#text(" 和 ")#raw("random")#text(" 的指向，复制链表中不能引用原链表节点。")

#strong[#text("具体例子：")]#text(" 原链表 ")#raw("A(7) → B(13) → C(11)")#text("，其中 ")#raw("A.random → C")#text("、")#raw("B.random → A")#text("、")#raw("C.random → B")#text("。复制后得到 ")#raw("A' → B' → C'")#text("，三个新节点的 ")#raw("random")#text(" 分别指向 ")#raw("C'")#text("、")#raw("A'")#text("、")#raw("B'")#text("。")

#strong[#text("核心原理：")]#text(" 把新节点插在对应原节点后面，形成 ")#raw("A → A' → B → B' → C → C'")#text("。此时，对于任意原节点 ")#raw("curr")#text("，")#raw("curr.next")#text(" 就是它的复制节点。若原节点的 ")#raw("random")#text(" 指向另一个原节点，那个目标节点的 ")#raw("next")#text(" 就是对应的新节点，因此可用 ")#raw("curr.random.next")#text(" 设置复制节点的 ")#raw("random")#text("。")

#text("整个过程分三次遍历：先穿插创建新节点；再复制 ")#raw("random")#text("；最后分离两个链表并恢复原链表。拆分时要先利用原有连接找到下一组节点，再修改 ")#raw("next")#text("。")

#table(columns: (1fr, 3fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("阶段")], [#text("链表状态 / 关键操作")]),
  table.hline(stroke: .4pt),
  [#text("原始链表")], [#raw("A → B → C")],
  [#text("穿插复制")], [#raw("A → A' → B → B' → C → C'")],
  [#text("设置随机指针")], [#raw("A'.random → C'")#text("，依次处理所有原节点")],
  [#text("分离与恢复")], [#text("原链表 ")#raw("A → B → C")#text("；复制链表 ")#raw("A' → B' → C'")],
  table.hline(stroke: .7pt))

#strong[#text("完整代码：")]

```python
class Solution:
    def copyRandomList(self, head: 'Optional[Node]') -> 'Optional[Node]':
        if head is None:
            return None

        # 第一次：在每个原节点后插入对应的复制节点
        curr = head
        while curr is not None:
            copy = Node(curr.val)
            copy.next = curr.next
            curr.next = copy
            curr = copy.next

        # 第二次：通过原节点的 random 找到复制节点的 random
        curr = head
        while curr is not None:
            copy = curr.next
            if curr.random is not None:
                copy.random = curr.random.next
            curr = copy.next

        # 第三次：恢复原链表，并拆出复制链表
        curr = head
        new_head = head.next
        while curr is not None:
            copy = curr.next
            curr.next = copy.next
            if copy.next is not None:
                copy.next = copy.next.next
            curr = curr.next

        return new_head
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，额外辅助空间 O(1)，不计必须创建的 n 个复制节点；操作过程中会临时修改原链表，最后恢复。")

#strong[#text("记忆骨架：")]#text(" 每个原节点后插入新节点 → 利用 ")#raw("curr.random.next")#text(" 设置复制节点的 ")#raw("random")#text(" → 拆分新旧链表 → 恢复原链表 → 返回 ")#raw("new_head")#text("。")

#jump("toc", "↑ 返回目录")

== #text("148. 排序链表（LeetCode 148）") <lc148>

#strong[#text("方法：")]#text(" 归并排序 + 快慢指针 + 递归")

#strong[#text("题目要求：")]#text(" 将单链表中的节点按照升序排列，返回排序后的头节点。")

#strong[#text("具体例子：")]#text(" ")#raw("head = [4,2,1,3]")#text("，排序后为 ")#raw("[1,2,3,4]")#text("。")

#strong[#text("核心原理：")]#text(" 使用归并排序：先通过快慢指针找到中点，将链表断开成左右两部分；分别递归排序；最后按第 21 题的思路，用虚拟头节点和 ")#raw("tail")#text(" 合并两条已排序链表。")

#text("这里 ")#raw("fast = head.next")#text("、")#raw("slow = head")#text("，循环结束后 ")#raw("slow")#text(" 停在左半部分末尾。先保存 ")#raw("right_head = slow.next")#text("，再执行 ")#raw("slow.next = None")#text("，将左右两半真正断开；否则递归会反复处理未缩短的链表。")

```text
            [4,2,1,3]
             /     \
          [4,2]   [1,3]
          /  \     /  \
        [4]  [2] [1]  [3]
          \  /     \  /
          [2,4]   [1,3]
             \     /
            [1,2,3,4]
```

#strong[#text("完整代码：")]

```python
class Solution:
    def sortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # 空链表或单节点链表已经有序
        if head is None or head.next is None:
            return head

        # 找到左半部分的尾节点
        slow = head
        fast = head.next
        while fast is not None and fast.next is not None:
            slow = slow.next
            fast = fast.next.next

        # 保存右半部分，断开原链表
        right_head = slow.next
        slow.next = None

        # 分别递归排序
        left = self.sortList(head)
        right = self.sortList(right_head)

        # 合并两条有序链表
        dummy = ListNode(0)
        tail = dummy
        while left is not None and right is not None:
            if left.val <= right.val:
                tail.next = left
                left = left.next
            else:
                tail.next = right
                right = right.next
            tail = tail.next

        # 接上尚未用完的节点
        tail.next = left if left is not None else right
        return dummy.next
```

#strong[#text("复杂度：")]#text(" 时间 O(n log n)。额外空间 O(log n)，来自递归调用栈；合并阶段直接复用原节点。")

#strong[#text("记忆骨架：")]#text(" 单节点结束递归 → 快慢指针找中点 → 保存右半部分并断开 → 递归排序两半 → ")#raw("dummy")#text(" 和 ")#raw("tail")#text(" 合并 → 返回新头节点。")

#jump("toc", "↑ 返回目录")

== #text("23. 合并 K 个升序链表（LeetCode 23）") <lc23>

#strong[方法：] 分治归并 + 原地两两合并

#strong[题目要求：] 给定一个数组，里面每个元素是一条升序链表的头节点。把所有节点合并成一条升序链表，返回新的头节点。数组为空或所有链表为空时，返回 `None`。

#strong[变量定义：] `lists` 保存各组链表的头节点，`k` 是数组长度。`interval` 是本轮两组起点之间的下标间隔，也对应上一轮合成的每组最多覆盖多少条原始链表。`i` 是左组的起点，`i + interval` 是右组的起点。`mergeTwo(a, b)` 接收两条有序链表的头节点，返回合并后的头节点。其中 `dummy` 是临时头节点，`tail` 指向已经接好的末尾。

#strong[核心原理：] 每轮合并相邻的两组，把结果写回左组的起点。第一轮每组最多一条原始链表，第二轮最多两条，第三轮最多四条，所以 `interval` 每轮翻倍。落单的一组保留在原处，下一轮还有机会参与合并。每对输入已经有序，`mergeTwo` 每次接上两个头节点中较小的一个，因而合并后的整组仍有序。

#strong[完整推演：] 三条链表分别为 `lists[0] = 1 → 4 → 5`、`lists[1] = 1 → 3 → 4`、`lists[2] = 2 → 6`，所以 `k = 3`。

#table(
  columns: (auto, auto, 1fr, 1fr),
  table.header([轮次], [间隔], [实际下标与合并对象], [写入 lists\[0\] 的结果]),
  [第一轮], [1], [`range(0, 2, 2)` 取 0，合并 0 和 1], [1 → 1 → 3 → 4 → 4 → 5],
  [第二轮], [2], [`range(0, 1, 4)` 取 0，合并 0 和 2], [1 → 1 → 2 → 3 → 4 → 4 → 5 → 6],
)

两轮的 `i` 都是 0，但右组从 `lists[1]` 变成了 `lists[2]`。旧下标里即使还留着节点引用，后续也只会读取当前组的起点。第二轮结束后 `interval = 4`，已经覆盖全部链表，返回 `lists[0]`。

#strong[为什么这样写 range：] `range(0, k - interval, interval * 2)` 从下标 0 开始，终点不包含在内。右组要存在，必须有 `i + interval < k`，所以终点是 `k - interval`。每次合并覆盖两组，下一对的左组起点要往后跳 `2 * interval`。例如有 8 条链表且 `interval = 2` 时，本轮配对为 `(0, 2)` 和 `(4, 6)`。

#strong[完整代码：]

```python
class Solution:
    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        def mergeTwo(a, b):
            dummy = ListNode(0)
            tail = dummy
            while a and b:
                if a.val <= b.val:
                    tail.next = a
                    a = a.next
                else:
                    tail.next = b
                    b = b.next
                tail = tail.next

            tail.next = a if a else b
            return dummy.next

        k = len(lists)
        if k == 0:
            return None

        interval = 1
        while interval < k:
            for i in range(0, k - interval, interval * 2):
                lists[i] = mergeTwo(lists[i], lists[i + interval])
            interval *= 2

        return lists[0]
```

#strong[复杂度：] 设 `N` 为总节点数。每轮遍历至多 `N` 个节点，共至多 `ceil(log₂ k)` 轮，另外有至多 `k - 1` 次两两合并调用。计入空链表，时间为 O(k + N log k)（k ≥ 2），额外空间为 O(1)，复用原数组与节点。

#strong[记忆骨架：] 间隔从 1 开始 → 每轮成对归并并写回左边 → 步长取两倍间隔 → 间隔翻倍 → 返回下标 0 的结果。

#jump("toc", "↑ 返回目录")

== #text("146. LRU 缓存（LeetCode 146）") <lc146>

#strong[#text("方法：")]#text(" 哈希表 + 双向链表")

#strong[#text("题目要求：")]#text(" 实现容量固定的 LRU 缓存。")#raw("get(key)")#text(" 命中时返回值并刷新使用顺序，未命中返回 ")#raw("-1")#text("。")#raw("put(key, value)")#text(" 更新或插入数据并刷新顺序，超容量时淘汰最久未使用的键。")

#strong[#text("具体例子：")]#text(" 容量为 ")#raw("2")#text("，先插入键 ")#raw("1、2")#text("，此时从旧到新为 ")#raw("1 → 2")#text("。执行 ")#raw("get(1)")#text(" 后顺序变为 ")#raw("2 → 1")#text("。插入键 ")#raw("3")#text(" 会淘汰键 ")#raw("2")#text("，此后 ")#raw("get(2)")#text(" 返回 ")#raw("-1")#text("。")

#strong[#text("核心原理：")]#text(" 字典 ")#raw("cache")#text(" 将键映射到节点，双向链表按最旧到最新排列。")#raw("left")#text(" 和 ")#raw("right")#text(" 是两端的虚拟节点。命中或更新时，将原节点摘下并插到 ")#raw("right")#text(" 前。新节点同时加入字典和链表，容量超限时摘下 ")#raw("left.next")#text("，并从字典删除对应的键。")

#strong[#text("完整代码：")]

```python

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}

        # 两个虚拟节点：左边最旧，右边最新
        self.left = Node(0, 0)
        self.right = Node(0, 0)

        # 初始时，两个虚拟节点相互连接
        self.left.next = self.right
        self.right.prev = self.left

    def remove(self, node):
        # 将 node 从双向链表中摘下
        before = node.prev
        after = node.next

        before.next = after
        after.prev = before

    def add_to_right(self, node):
        # 将 node 插入右侧虚拟节点之前
        before = self.right.prev

        before.next = node
        node.prev = before
        node.next = self.right
        self.right.prev = node

    def get(self, key: int) -> int:
        # 不存在则返回 -1
        if key not in self.cache:
            return -1

        # 找到节点，并移动到最近使用的位置
        node = self.cache[key]
        self.remove(node)
        self.add_to_right(node)

        return node.value

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # 已存在：更新值，并移动到最右边
            node = self.cache[key]
            node.value = value

            self.remove(node)
            self.add_to_right(node)
        else:
            # 不存在：创建新节点
            node = Node(key, value)
            self.cache[key] = node
            self.add_to_right(node)

            # 超出容量：删除最久未使用的节点
            if len(self.cache) > self.capacity:
                oldest = self.left.next
                self.remove(oldest)
                del self.cache[oldest.key]
```

#strong[#text("复杂度：")]#text(" get 和 put 的平均时间均为 O(1)，空间 O(capacity)。")

#strong[#text("记忆骨架：")]#text(" 字典查节点 → 命中移到右端 → 新增同时入表入链 → 超容量从左端淘汰。")

#jump("toc", "↑ 返回目录")

== #text("82. 删除排序链表中的重复元素 II（LeetCode 82）") <lc82>

#strong[方法：] 虚拟头节点 + 双指针

#strong[题目要求：] 输入一条升序链表，删除出现多次的值对应的全部节点，返回新头节点。例如 `1 → 2 → 3 → 3 → 4 → 4 → 5` 的结果是 `1 → 2 → 5`。第 83 题遇到重复值时会保留一个节点，同一输入的结果是 `1 → 2 → 3 → 4 → 5`。

#strong[变量定义：] `head` 是原链表的头节点，`dummy` 是放在它前面的虚拟节点。`prev` 指向最后一个已确认保留的节点，初始指向 `dummy`。`curr` 指向当前要检查的节点，初始指向 `head`。`duplicate_val` 保存当前这组要删除的值。`curr.next` 是后继节点，没有后继时为 `None`。

#strong[两个指针什么时候动：] 链表已经排序，相同的值会连续出现。若当前节点与后继不同值，或已经没有后继，当前节点可以保留，先执行 `prev = curr`，再执行 `curr = curr.next`。若当前节点与后继同值，`prev` 留在原地，让 `curr` 连续跨过整组，最后执行一次 `prev.next = curr`。

#strong[完整推演：] 用 `3a`、`3b` 和 `4a`、`4b` 区分值相同的不同节点。

#table(
  columns: (2fr, auto, auto, 3fr),
  table.header([本步操作], [prev 指向], [curr 指向], [从 dummy 出发能看到的链表]),
  [初始化], [dummy], [1], [1 → 2 → 3a → 3b → 4a → 4b → 5],
  [保留 1], [1], [2], [1 → 2 → 3a → 3b → 4a → 4b → 5],
  [保留 2], [2], [3a], [1 → 2 → 3a → 3b → 4a → 4b → 5],
  [curr 跨过 3a], [2], [3b], [1 → 2 → 3a → 3b → 4a → 4b → 5],
  [curr 跨过 3b], [2], [4a], [1 → 2 → 3a → 3b → 4a → 4b → 5],
  [更新 prev.next], [2], [4a], [1 → 2 → 4a → 4b → 5],
  [curr 跨过 4a], [2], [4b], [1 → 2 → 4a → 4b → 5],
  [curr 跨过 4b], [2], [5], [1 → 2 → 4a → 4b → 5],
  [更新 prev.next], [2], [5], [1 → 2 → 5],
  [保留 5], [5], [None], [1 → 2 → 5],
)

`curr = curr.next` 只移动变量 `curr`，表里原来的连接仍在。直到 `prev.next = curr` 执行，节点 2 才改为直接指向 4a，再改为直接指向 5。由于 `prev` 始终停在 2，紧挨着的两组重复节点可以连续删除。

#strong[虚拟头节点有什么用：] 输入 `1 → 1 → 2 → 3` 时，`prev` 留在 `dummy`。等 `curr` 跨过两个 1 指向 2，更新 `dummy.next` 就得到了新头节点。若重复的一组在尾部，跨过之后 `curr` 为 `None`，相同的赋值会直接断开尾部。最终统一返回 `dummy.next`。

#strong[#text("完整代码：")]

```python

from typing import Optional

class Solution:
    def deleteDuplicates(
        self, head: Optional[ListNode]
    ) -> Optional[ListNode]:

        # 创建虚拟头节点
        dummy = ListNode(0, head)

        # prev 指向最后一个确认需要保留的节点
        prev = dummy

        # curr 指向当前正在检查的节点
        curr = head

        while curr is not None:

            # 当前节点与下一个节点的值相同
            if curr.next is not None and curr.val == curr.next.val:

                # 记录需要删除的重复数字
                duplicate_val = curr.val

                # 跳过所有值等于 duplicate_val 的节点
                while curr is not None and curr.val == duplicate_val:
                    curr = curr.next

                # 将前一个保留节点连接到下一个不同值的节点
                prev.next = curr

            else:
                # 当前数字没有重复，保留该节点
                prev = curr
                curr = curr.next

        return dummy.next
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" 虚拟头 → 检查相邻节点 → 重复整组跳过，单独节点保留 → 返回 dummy.next。")

#jump("toc", "↑ 返回目录")

== #text("92. 反转链表 II（LeetCode 92）") <lc92>

#strong[方法：] 虚拟头节点 + 头插法

#strong[题目要求：] 给定链表头 `head` 和从 1 开始计数的两个位置 `left`、`right`，只反转这个闭区间，返回连接好的链表头。

#strong[变量定义：] `dummy` 是指向原链表的虚拟头节点。`pre` 是反转区间前一个节点，定位后固定。`cur` 是原区间第一个节点，始终留在已反转部分的末尾。`nxt` 每轮引用 `cur.next`，也就是下一个要从原位置摘下、插到区间头部的节点。

#strong[为什么头插可以完成反转：] 初始只有区间的第一个节点算作已处理。每轮把紧挨 `cur` 的未处理节点挪到 `pre` 后，它就排在所有已处理节点前面。比如先把 3 放到 2 前，再把 4 放到 3 前，区间便变成 4 → 3 → 2。后面未处理的节点始终从 `cur.next` 接出去。第一个节点已经在已处理部分，因此执行 `right - left` 次就够了。

#strong[逐步推演：] 对 `1 → 2 → 3 → 4 → 5`，反转第 2 到第 4 个节点。`pre` 指向 1，`cur` 指向 2。

- *第一轮移动 3。* `nxt = cur.next` 保存节点 3。把 2 接到 4，再把 3 接到区间当前的头节点 2，最后把 1 接到 3。链表变成 1 → 3 → 2 → 4 → 5。
- *第二轮移动 4。* `cur` 仍是 2，现在 `cur.next` 是 4。把 2 接到 5，把 4 接到原区间头 3，再把 1 接到 4，得到 1 → 4 → 3 → 2 → 5。

如果 `left = 1`，`pre` 就是 `dummy`。头插会更新 `dummy.next`，所以最终统一返回它。

```python
class Solution:
    def reverseBetween(self, head: Optional[ListNode],
                       left: int, right: int) -> Optional[ListNode]:
        dummy = ListNode(0, head)
        pre = dummy
        for _ in range(left - 1):
            pre = pre.next

        cur = pre.next
        for _ in range(right - left):
            nxt = cur.next
            cur.next = nxt.next  # 摘下后继，接回剩余链表
            nxt.next = pre.next  # 接到当前区间头之前
            pre.next = nxt       # 更新区间头

        return dummy.next
```

#strong[复杂度：] 时间 O(n)，定位与头插总次数至多与链表长度同阶。额外空间 O(1)。

#strong[记忆骨架：] 建虚拟头 → 固定区间前驱和原首节点 → 反复摘下后继并头插 → 返回 dummy.next。

#jump("toc", "↑ 返回目录")

== #text("143. 重排链表（LeetCode 143）") <lc143>

#strong[方法：] 快慢指针 + 反转链表 + 交替合并

#strong[题目要求：] 按原链表的首、尾、第二个、倒数第二个节点交替重排。例如 1 → 2 → 3 → 4 变成 1 → 4 → 2 → 3。函数直接修改节点的 `next`，返回类型为 `None`。

#strong[变量定义：] `head` 是原头节点。`slow`、`fast` 分别每轮走一步、两步。`second` 起初指向后半段的头。`prev` 是已反转部分的头，`curr` 是当前反转的节点，`next_node` 暂存反转前的后继。`first`、`second` 在合并时分别指向两段还没接入的首节点，`first_next`、`second_next` 保存它们原来的后继。

#strong[为什么拆成三步：] 目标顺序一半从头向后取，一半从尾向前取。把后半段反转后，两段都可以沿 `next` 向后取。切分时让前半段与后半段等长，或者多一个中间节点，合并时就能用「后半段还有节点」作为循环条件。

#strong[完整推演：] 对 1 → 2 → 3 → 4，两指针开始都在 1。快指针走到 3，慢指针走到 2。此时快指针无法再走两步，于是保存 `slow.next`，再令 `slow.next = None`，得到 1 → 2 和 3 → 4。反转时先让 3 指向空，再让 4 指向 3，后半段变成 4 → 3。

#table(
  columns: (auto, 1fr, 1fr, 1.25fr),
  table.header([合并轮次], [修改前保存的后继], [本轮改了哪些连接], [接好后的链表]),
  [第 1 轮], [前半段后继是 2，后半段后继是 3], [1 接 4，4 接 2], [1 → 4 → 2],
  [第 2 轮], [两个后继都为空], [2 接 3，3 接空], [1 → 4 → 2 → 3],
)

奇数长度时，中间节点留在前半段末尾。比如 1 → 2 → 3 → 4 → 5 拆成 1 → 2 → 3 和 4 → 5。反转并交替接完后，3 仍然接在末尾。

```python
class Solution:
    def reorderList(self, head: Optional[ListNode]) -> None:
        if not head or not head.next:
            return

        slow = fast = head
        while fast.next and fast.next.next:
            slow = slow.next
            fast = fast.next.next

        second = slow.next
        slow.next = None

        prev = None
        curr = second
        while curr:
            next_node = curr.next
            curr.next = prev
            prev = curr
            curr = next_node

        first, second = head, prev
        while second:
            first_next = first.next
            second_next = second.next

            first.next = second
            second.next = first_next

            first = first_next
            second = second_next
```

#strong[复杂度：] 时间 O(n)，拆分、反转、合并各做一趟线性操作。额外空间 O(1)。

#strong[记忆骨架：] 找前半段末尾 → 保存后半段并断链 → 反转后半段 → 先存两个后继，再交替连边。

#jump("toc", "↑ 返回目录")

= #text("二叉树")

== #text("94. 二叉树的中序遍历（LeetCode 94）") <lc94>

#strong[#text("方法：")]#text(" DFS 递归（左 → 根 → 右）")

#strong[#text("题目要求：")]#text(" 给定二叉树的根节点 ")#raw("root")#text("，返回所有节点的中序遍历结果，依次访问左子树、当前根节点和右子树。")

#strong[#text("具体例子：")]

```text
        1
       / \
      2   3
     / \
    4   5
```

#text("从节点 ")#raw("1")#text(" 出发，先访问其左子树 ")#raw("2")#text("，继续进入节点 ")#raw("4")#text("；返回节点 ")#raw("2")#text(" 时记录 ")#raw("2")#text("，然后记录 ")#raw("5")#text("；左子树完成后记录 ")#raw("1")#text("，最后记录右侧的 ")#raw("3")#text("，因此结果是 ")#raw("[4, 2, 5, 1, 3]")#text("。")

#strong[#text("核心原理：")]#text(" 每一棵左、右子树本身也是二叉树，因此定义 ")#raw("dfs(node)")#text(" 处理“以 ")#raw("node")#text(" 为根的子树”。每层依次执行 ")#raw("dfs(node.left)")#text("、")#raw("res.append(node.val)")#text("、")#raw("dfs(node.right)")#text("；当前层会等待左子树递归返回，再记录自己的值，随后进入右子树。")#raw("node is None")#text(" 时直接返回，避免访问不存在的节点。")

#table(columns: (1fr, 1.2fr, 2.2fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("遍历方式")], [#text("访问顺序")], [#text("代码中记录节点的位置")]),
  table.hline(stroke: .4pt),
  [#text("前序遍历")], [#text("根 → 左 → 右")], [#text("两次递归调用之前")],
  [#text("中序遍历")], [#text("左 → 根 → 右")], [#text("两次递归调用之间")],
  [#text("后序遍历")], [#text("左 → 右 → 根")], [#text("两次递归调用之后")],
  table.hline(stroke: .7pt))

#strong[#text("完整代码：")]

```python
class Solution:
    def inorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        res = []

        def dfs(node):
            if node is None:
                return
            dfs(node.left)
            res.append(node.val)
            dfs(node.right)

        dfs(root)
        return res
```

#text("这里先定义 ")#raw("dfs(node)")#text("，再调用 ")#raw("dfs(root)")#text(" 启动遍历；函数内部的递归调用会逐层处理子树。")

#strong[#text("复杂度：")]#text(" 时间 O(n)，所有节点各访问一次；递归栈 O(h)，结果列表 O(n)，总空间 O(n)。")#raw("h")#text(" 为树高。")

#strong[#text("记忆骨架：")]#text(" 定义 ")#raw("dfs")#text(" → 空节点返回 → 递归左子树 → 保存根节点 → 递归右子树 → 从 ")#raw("dfs(root)")#text(" 启动。")

#jump("toc", "↑ 返回目录")

== #text("104. 二叉树的最大深度（LeetCode 104）") <lc104>

#strong[#text("方法：")]#text(" DFS 递归 + 自底向上返回深度")

#strong[#text("题目要求：")]#text(" 给定根节点 ")#raw("root")#text("，返回根节点到最远叶子节点的最长路径所包含的节点数；空树深度为 0。")

#strong[#text("具体例子：")]

```text
         3          第 1 层
        / \
       9  20        第 2 层
         /  \
        15   7      第 3 层
```

#text("最大深度是 ")#raw("3")#text("。对于另一棵树 ")#raw("1 → {2,3}")#text("、")#raw("2 → {4,5}")#text("，节点 ")#raw("4")#text("、")#raw("5")#text(" 和 ")#raw("3")#text(" 的深度为 1，节点 ")#raw("2")#text(" 的深度为 2，根节点 ")#raw("1")#text(" 的深度为 3。")

#strong[#text("核心原理：")]#text(" 定义 ")#raw("depth(node)")#text(" 为以当前节点为根的子树高度。当前节点的最长路径必须先经过左、右子树之一，因此递归关系是")

#raw("D(node) = 1 + max(D(node.left), D(node.right))")#text("，且 ")#raw("D(None) = 0")#text("。")

#text("递归会先走到最深处的空节点，再逐层返回。与中序遍历使用 ")#raw("res.append()")#text(" 收集结果不同，这题通过 ")#raw("return")#text(" 把子树计算出的深度交给父节点。")

#table(columns: (1fr, 1fr, 1fr, 1fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("子树根节点")], [#text("左子树深度")], [#text("右子树深度")], [#text("返回值")]),
  table.hline(stroke: .4pt),
  [#text("4、5、3")], [#text("0")], [#text("0")], [#text("1")],
  [#text("2")], [#text("1")], [#text("1")], [#text("2")],
  [#text("1")], [#text("2")], [#text("1")], [#text("3")],
  table.hline(stroke: .7pt))

#strong[#text("完整代码：")]

```python
class Solution:
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0

        left_depth = self.maxDepth(root.left)
        right_depth = self.maxDepth(root.right)
        return max(left_depth, right_depth) + 1
```

#text("每次调用 ")#raw("self.maxDepth()")#text(" 时，参数 ")#raw("root")#text(" 都会指向当前正在求深度的子树；只有左右两侧的返回值都得到后，当前这一层才会返回结果。")

#strong[#text("复杂度：")]#text(" 时间 O(n)，每个节点访问一次；递归栈空间 O(h)，平衡树为 O(log n)，退化链状树为 O(n)。")

#strong[#text("记忆骨架：")]#text(" 空树返回 ")#raw("0")#text(" → 分别求左、右深度 → ")#raw("return max(left_depth, right_depth) + 1")#text("。")

#jump("toc", "↑ 返回目录")

== #text("226. 翻转二叉树（LeetCode 226）") <lc226>

#strong[#text("方法：")]#text(" DFS 递归 + 交换左右子树")

#strong[#text("题目要求：")]#text(" 给定二叉树的根节点，交换每一个节点的左、右子树，直接修改原树，并返回根节点。")

#strong[#text("具体例子：")]#text(" 下面是补充的三层示意树，展示翻转前后的结构：")

```text
翻转前：             翻转后：
        1                   1
       / \                 / \
      2   3               3   2
     / \                     / \
    4   5                   5   4
```

#text("更直观地看，根节点的 ")#raw("2")#text(" 和 ")#raw("3")#text(" 互换；原来属于 ")#raw("2")#text(" 的 ")#raw("4")#text(" 和 ")#raw("5")#text("，在该子树内部也互换。因此每个节点都要执行同一项操作。")

#strong[#text("核心原理：")]#text(" 当前节点的关键操作是 ")#raw("root.left, root.right = root.right, root.left")#text("，它交换的是子树引用。交换根节点之后，还要继续调用递归函数处理交换后的左右子树，确保整棵树中的所有节点都发生翻转。遇到 ")#raw("None")#text(" 表示到达递归边界，直接返回。")

#table(columns: (1fr, 1.7fr, 1.7fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("步骤")], [#text("当前操作")], [#text("目的")]),
  table.hline(stroke: .4pt),
  [#text("1")], [#text("检查 ")#raw("root is None")], [#text("递归终止")],
  [#text("2")], [#text("交换 ")#raw("root.left")#text(" 与 ")#raw("root.right")], [#text("翻转当前节点")],
  [#text("3")], [#text("递归处理新左、右子树")], [#text("翻转全部后代")],
  [#text("4")], [#raw("return root")], [#text("返回原根节点引用")],
  table.hline(stroke: .7pt))

#strong[#text("完整代码：")]

```python
class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        if root is None:
            return None

        root.left, root.right = root.right, root.left
        self.invertTree(root.left)
        self.invertTree(root.right)
        return root
```

#text("交换后 ")#raw("root.left")#text(" 对应原来的右子树，")#raw("root.right")#text(" 对应原来的左子树；两侧均继续递归，所以不会遗漏节点。这里原地修改节点连接，递归调用不必重新赋值给左右指针。")

#strong[#text("复杂度：")]#text(" 时间 O(n)，每个节点恰好交换一次；递归栈空间 O(h)，最坏 O(n)。")

#strong[#text("记忆骨架：")]#text(" 空节点返回 → 交换当前左右子树 → 递归翻转两边 → 返回根节点。")

#jump("toc", "↑ 返回目录")

== #text("101. 对称二叉树（LeetCode 101）") <lc101>

#strong[#text("方法：")]#text(" 双节点递归 + 镜像比较")

#strong[#text("题目要求：")]#text(" 判断以 ")#raw("root")#text(" 为根的二叉树是否沿中轴线左右对称。对称返回 ")#raw("True")#text("，否则返回 ")#raw("False")#text("。")

#strong[#text("具体例子：")]

```text
对称：                  不对称：
        1                       1
       / \                     / \
      2   2                   2   2
     / \ / \                   \   \
    3  4 4  3                   3   3
```

#text("左边关于中心轴完全镜像，返回 ")#raw("True")#text("；右边两侧的节点 ")#raw("3")#text(" 都是右孩子，位置不互为镜像，返回 ")#raw("False")#text("。")

#strong[#text("核心原理：")]#text(" 定义 ")#raw("check(left, right)")#text(" 判断两棵子树是否互为镜像，比较顺序为：两个都为空则对称；只有一个为空则不对称；两个值不同则不对称；其余情况必须同时满足“外侧对外侧、内侧对内侧”：")

#raw("check(left.left, right.right) and check(left.right, right.left)")#text("。")

#text("两组镜像比较都要成立。由于 ")#raw("and")#text(" 的短路机制，一旦第一组比较结果是 ")#raw("False")#text("，就可以直接结束当前层判断。")

#table(columns: (1fr, 1fr, 2.1fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("情况")], [#text("返回结果")], [#text("理由")]),
  table.hline(stroke: .4pt),
  [#raw("left")#text(" 和 ")#raw("right")#text(" 都是 ")#raw("None")], [#raw("True")], [#text("两侧同时为空")],
  [#text("只有一侧为 ")#raw("None")], [#raw("False")], [#text("结构不对称")],
  [#raw("left.val != right.val")], [#raw("False")], [#text("镜像位置的节点值不同")],
  [#text("两侧节点值相等")], [#text("递归比较")], [#text("外侧与内侧均需镜像")],
  table.hline(stroke: .7pt))

#strong[#text("完整代码：")]

```python
class Solution:
    def isSymmetric(self, root: Optional[TreeNode]) -> bool:
        def check(left, right):
            if left is None and right is None:
                return True
            if left is None or right is None:
                return False
            if left.val != right.val:
                return False
            return (
                check(left.left, right.right)
                and check(left.right, right.left)
            )

        if root is None:
            return True
        return check(root.left, root.right)
```

#text("本题的递归函数一次接收两个节点；与之前逐棵计算深度不同，这里需要同时沿镜像位置向下比较。空树本身是对称的。")

#strong[#text("复杂度：")]#text(" 时间 O(n)，最坏需检查整棵树；递归栈空间 O(h)，最坏 O(n)。")

#strong[#text("记忆骨架：")]#text(" 同时为空返回 ")#raw("True")#text(" → 只有一侧为空或值不同返回 ")#raw("False")#text(" → 交叉比较 ")#raw("left.left")#text(" 与 ")#raw("right.right")#text("、")#raw("left.right")#text(" 与 ")#raw("right.left")#text("。")

#jump("toc", "↑ 返回目录")

== #text("543. 二叉树的直径（LeetCode 543）") <lc543>

#strong[#text("方法：")]#text(" DFS + 最大深度")

#strong[#text("题目要求：")]#text(" 给定二叉树，求任意两个节点之间最长路径的边数。最长路径不一定经过根节点。")

#strong[#text("具体例子：")]

```text
       1
      / \
     2   3
    / \
   4   5
```

#text("最长路径可以是 ")#raw("4 → 2 → 1 → 3")#text("，共有 3 条边，返回 ")#raw("3")#text("。")

#strong[#text("核心原理：")]#text(" 对每个节点，经过它的最长路径由左子树最大深度和右子树最大深度组成。如果深度按节点数计算，那么经过当前节点的最长路径边数为 ")#raw("left + right")#text("。遍历时用 ")#raw("ans")#text(" 记录所有节点处出现过的最大值。")

#strong[#text("为什么必须对每个节点计算？")]#text(" 考虑以下反例：")

```text
       1
      /
     2
    / \
   3   4
  /     \
 5       6
```

#text("经过根节点 ")#raw("1")#text(" 的最长路径只有 3 条边，但真正的直径是 ")#raw("5 → 3 → 2 → 4 → 6")#text("，共有 4 条边。因此，只计算根节点会遗漏答案。")

#strong[#text("为什么递归返回 ")#raw("max(left, right) + 1")#text("，却用 ")#raw("left + right")#text(" 更新直径？")]#text(" 父节点需要当前子树向下延伸的最大深度，只能选择左边或右边的一条路径；计算经过当前节点的直径时，才允许连接左右两边。")

#strong[#text("完整代码：")]

```python
class Solution:
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        ans = 0

        def dfs(node):
            nonlocal ans
            if node is None:
                return 0
            left = dfs(node.left)
            right = dfs(node.right)
            ans = max(ans, left + right)
            return max(left, right) + 1

        dfs(root)
        return ans
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，每个节点访问一次；递归栈空间 O(h)，最坏为 O(n)。")

#strong[#text("记忆骨架：")]#text(" DFS 求左右深度 → ")#raw("left + right")#text(" 更新直径 → ")#raw("max(left, right) + 1")#text(" 返回深度 → 最终返回 ")#raw("ans")#text("。")

#jump("toc", "↑ 返回目录")

== #text("102. 二叉树的层序遍历（LeetCode 102）") <lc102>

#strong[#text("方法：")]#text(" BFS + 队列")

#strong[#text("题目要求：")]#text(" 按照从上到下、从左到右的顺序逐层遍历二叉树，返回每一层节点值组成的二维列表。")

#strong[#text("具体例子：")]

```text
       3
      / \
     9   20
        /  \
       15   7
```

#text("输出 ")#raw("[[3], [9, 20], [15, 7]]")#text("。")

#strong[#text("核心原理：")]#text(" 层序遍历使用广度优先搜索（BFS）。队列遵循先进先出，先取出本层节点，再将其左右孩子依次加入队尾。关键是每层开始时固定 ")#raw("size = len(queue)")#text("，确保本轮只处理当前层。")

#text("例如：")

```text
       1
      / \
     2   3
    / \
   4   5
```

#text("处理完第一层，队列是 ")#raw("[2, 3]")#text("，此时 ")#raw("size = 2")#text("。取出节点 ")#raw("2")#text(" 后，节点 ")#raw("4、5")#text(" 入队，队列变为 ")#raw("[3, 4, 5]")#text("。虽然队列长度增加到 3，但本轮仍只处理原来的 2 个节点，即 ")#raw("2、3")#text("。这样 ")#raw("4、5")#text(" 就会留到下一层。")

#text("如果直接按照队列不断增长后的长度处理，就会把下一层节点混进当前层。")

#strong[#text("完整代码：")]

```python
from collections import deque

class Solution:
    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        if root is None:
            return []

        res = []
        queue = deque([root])
        while queue:
            size = len(queue)
            level = []
            for _ in range(size):
                node = queue.popleft()
                level.append(node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            res.append(level)
        return res
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，每个节点入队和出队各一次；辅助空间 O(n)，来自队列，结果列表另计。")

#strong[#text("记忆骨架：")]#text(" 根节点入队 → 每层固定 ")#raw("size")#text(" → 弹出本层全部节点 → 左右孩子入队 → 保存当前层 → 队列为空时结束。")

#jump("toc", "↑ 返回目录")

== #text("108. 将有序数组转换为二叉搜索树（LeetCode 108）") <lc108>

#strong[#text("方法：")]#text(" 二分 + 递归建树")

#strong[#text("题目要求：")]#text(" 给定严格递增数组，将其转换为一棵高度平衡的二叉搜索树。要求每个节点左右子树的高度差不超过 1。")

#strong[#text("具体例子：")]#text(" ")#raw("nums = [-10, -3, 0, 5, 9]")#text("，一种合法结果是：")

```text
        0
       / \
     -10  5
       \   \
       -3   9
```

#strong[#text("核心原理：")]#text(" 升序数组中，中点左侧的元素都小于中点，右侧都大于中点，因此可以取中点作为根节点，分别递归构造左右子树。同时，中点能让左右元素数量尽量接近，保证树的高度平衡。")

```text
下标：  0    1   2   3  4
数组：-10   -3   0   5  9
                  ↑
                 根
```

#text("第一次取 ")#raw("mid = 2")#text("，根节点是 ")#raw("0")#text("，左区间为 ")#raw("[0, 1]")#text("，右区间为 ")#raw("[3, 4]")#text("。继续构造左子树时，")#raw("mid = (0 + 1) // 2 = 0")#text("，取 ")#raw("-10")#text(" 为根。")

#text("此时 ")#raw("-10")#text(" 的左子树调用 ")#raw("build(0, -1)")#text("。因为左边界 ")#raw("0")#text(" 大于右边界 ")#raw("-1")#text("，说明区间为空，直接返回 ")#raw("None")#text("；并不会访问数组的 ")#raw("-1")#text(" 下标。")

#strong[#text("完整代码：")]

```python
class Solution:
    def sortedArrayToBST(self, nums: List[int]) -> Optional[TreeNode]:
        def build(left, right):
            if left > right:
                return None
            mid = (left + right) // 2
            root = TreeNode(nums[mid])
            root.left = build(left, mid - 1)
            root.right = build(mid + 1, right)
            return root

        return build(0, len(nums) - 1)
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，每个元素创建一个节点；递归栈空间 O(log n)，新建二叉树本身占用 O(n)。")

#strong[#text("记忆骨架：")]#text(" 有序数组取中点建根 → 左区间递归建左子树 → 右区间递归建右子树 → 空区间返回 ")#raw("None")#text(" → 返回根节点。")

#jump("toc", "↑ 返回目录")

== #text("98. 验证二叉搜索树（LeetCode 98）") <lc98>

#strong[#text("方法：")]#text(" BST + 上下界递归")

#strong[#text("题目要求：")]#text(" 判断一棵二叉树是否为有效的二叉搜索树。每个节点的左子树所有值必须严格小于它，右子树所有值必须严格大于它。")

#strong[#text("具体例子：")]

```text
       5
      / \
     2   7
        /
       4
```

#text("返回 ")#raw("False")#text("，因为节点 ")#raw("4")#text(" 位于根节点 ")#raw("5")#text(" 的右子树，却小于 5。")

#strong[#text("核心原理：")]#text(" BST 的大小限制来自所有祖先节点，仅比较当前节点和直接孩子是不够的。在该例中，")#raw("2 < 5")#text("、")#raw("7 > 5")#text("、")#raw("4 < 7")#text(" 均成立，但节点 ")#raw("4")#text(" 同时必须大于祖先节点 ")#raw("5")#text("。因此，递归过程中需要传递合法范围 ")#raw("lower < node.val < upper")#text("。")

#text("从根节点 ")#raw("5")#text(" 进入右子树 ")#raw("7")#text(" 时，下界更新为 5；再从 ")#raw("7")#text(" 进入左子树 ")#raw("4")#text(" 时，上界更新为 7，此时要求 ")#raw("5 < 4 < 7")#text("，显然不成立，返回 ")#raw("False")#text("。")

#text("关键是进入左子树只收紧上界，进入右子树只提高下界，另一侧边界必须保留，因为它记录了祖先节点的限制。")

#strong[#text("完整代码：")]

```python
class Solution:
    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        def dfs(node, lower, upper):
            if node is None:
                return True
            if not (lower < node.val < upper):
                return False
            return (
                dfs(node.left, lower, node.val)
                and dfs(node.right, node.val, upper)
            )

        return dfs(root, float("-inf"), float("inf"))
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，最坏需要访问全部节点；递归栈空间 O(h)，最坏为 O(n)。")

#strong[#text("记忆骨架：")]#text(" 递归携带合法上下界 → 当前值必须严格位于区间内 → 向左更新上界 → 向右更新下界 → 任一节点越界就返回 ")#raw("False")#text("。")

#jump("toc", "↑ 返回目录")

== #text("230. 二叉搜索树中第 K 小的元素（LeetCode 230）") <lc230>

#strong[#text("方法：")]#text(" BST + 中序遍历")

#strong[#text("题目要求：")]#text(" 给定二叉搜索树和整数 ")#raw("k")#text("，返回其中第 ")#raw("k")#text(" 小的节点值。")

#strong[#text("具体例子：")]

```text
        5
       / \
      3   6
     / \
    2   4
   /
  1
```

#text("当 ")#raw("k = 3")#text(" 时，返回 ")#raw("3")#text("。")

#strong[#text("核心原理：")]#text(" BST 左子树所有值小于根节点，右子树所有值大于根节点，所以按照“左 → 根 → 右”进行中序遍历，会得到升序序列。示例的遍历过程是 ")#raw("1 → 2 → 3 → 4 → 5 → 6")#text("，得到 ")#raw("res = [1, 2, 3, 4, 5, 6]")#text("，第 3 小的元素是 ")#raw("res[2] = 3")#text("。")

#strong[#text("为什么是 ")#raw("k - 1")#text("？")]#text(" 因为 ")#raw("k")#text(" 从 1 开始计数，而 Python 列表下标从 0 开始。如果直接访问 ")#raw("res[k]")#text("，")#raw("k = 3")#text(" 时取到的是第 4 小的元素 ")#raw("4")#text("，因此必须减 1。")

#text("这里使用与第 94 题完全一致的中序遍历写法，先收集升序序列，再取对应元素。")

#strong[#text("完整代码：")]

```python
class Solution:
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        res = []

        def dfs(node):
            if node is None:
                return
            dfs(node.left)
            res.append(node.val)
            dfs(node.right)

        dfs(root)
        return res[k - 1]
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，需要完整中序遍历；额外空间 O(n)，用于保存遍历结果及递归栈。")

#strong[#text("记忆骨架：")]#text(" BST 中序遍历得到升序序列 → 保存到 ")#raw("res")#text(" → 返回 ")#raw("res[k - 1]")#text("。")

#jump("toc", "↑ 返回目录")

== #text("199. 二叉树的右视图（LeetCode 199）") <lc199>

#strong[#text("方法：")]#text(" BFS + 每层最后一个节点")

#strong[#text("题目要求：")]#text(" 从二叉树右侧观察，返回从上到下每一层能够看到的节点值。")

#strong[#text("具体例子：")]

```text
       1
      / \
     2   3
      \   \
       5   4
```

#text("输出 ")#raw("[1, 3, 4]")#text("。")

#strong[#text("核心原理：")]#text(" 右视图要找的是每一层最右边的节点。沿用第 102 题的 BFS 层序遍历，按照从左到右的顺序处理每层节点，只记录该层最后一个节点即可。")

#strong[#text("为什么不能一直沿着 ")#raw("root.right")#text(" 向下走？")]#text(" 看下面的反例：")

```text
       1
      / \
     2   3
      \
       5
```

#text("如果只沿右孩子寻找，会得到 ")#raw("[1, 3]")#text("，但第三层只有节点 ")#raw("5")#text("，从右侧也能看见它，因此正确答案是 ")#raw("[1, 3, 5]")#text("。")

#text("BFS 能按层处理所有节点。每层开始时固定 ")#raw("size")#text("，循环下标从 0 到 ")#raw("size - 1")#text("，当 ")#raw("i == size - 1")#text(" 时，当前节点就是该层最右侧的节点。")

#strong[#text("完整代码：")]

```python
from collections import deque

class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        if root is None:
            return []

        res = []
        queue = deque([root])
        while queue:
            size = len(queue)
            for i in range(size):
                node = queue.popleft()
                if i == size - 1:
                    res.append(node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
        return res
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，每个节点访问一次；辅助空间 O(n)，队列最多需要保存一层的节点。")

#strong[#text("记忆骨架：")]#text(" BFS 逐层遍历 → 每层固定 ")#raw("size")#text(" → 按左、右顺序入队 → ")#raw("i == size - 1")#text(" 时记录节点值。")

#jump("toc", "↑ 返回目录")

== #text("114. 二叉树展开为链表（LeetCode 114）") <lc114>

#strong[#text("方法：")]#text(" 先序遍历 + 栈 + 原地修改指针")

#strong[#text("题目要求：")]#text(" 将二叉树原地展开为一条链表，所有节点的 ")#raw("left")#text(" 都为 ")#raw("None")#text("，")#raw("right")#text(" 指向下一个节点，节点顺序与先序遍历一致。")

#strong[#text("具体例子：")]

```text
        1
       / \
      2   5
     / \   \
    3   4   6
```

#text("先序遍历顺序为 ")#raw("1 → 2 → 3 → 4 → 5 → 6")#text("。展开后，所有节点依次通过 ")#raw("right")#text(" 连接，")#raw("left")#text(" 全部为 ")#raw("None")#text("。")

#strong[#text("核心原理：")]#text(" 先序遍历按照“根 → 左 → 右”访问节点。用栈依次取出节点，每次将它接到已经展开的链表末尾，再更新尾节点。由于栈后进先出，必须先把右孩子入栈，再把左孩子入栈，保证下一轮优先访问左子树。")

#text("例如处理根节点 ")#raw("1")#text("：")

```text
初始栈：       [1]
取出 1 后：    [5, 2]
取出 2 后：    [5, 4, 3]
```

#text("栈最右边是栈顶，因此下一次依次取出 ")#raw("3、4")#text("，再取出 ")#raw("5")#text("，符合先序遍历。")

#strong[#text("为什么必须先保存孩子，再修改指针？")]#text(" 处理节点 ")#raw("2")#text(" 时，原来的左孩子为 ")#raw("3")#text("、右孩子为 ")#raw("4")#text("。如果直接把 ")#raw("node.left")#text(" 清空，就可能失去左子树入口。必须先把 ")#raw("4、3")#text(" 入栈，保存尚未处理的节点，再断开原来的连接，最后把节点 ")#raw("2")#text(" 接到链表尾部。")

#strong[#text("完整代码：")]

```python
class Solution:
    def flatten(self, root: Optional[TreeNode]) -> None:
        if root is None:
            return

        stack = [root]
        prev = None
        while stack:
            node = stack.pop()
            if node.right:
                stack.append(node.right)
            if node.left:
                stack.append(node.left)

            node.left = None
            node.right = None
            if prev is not None:
                prev.right = node
            prev = node
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，每个节点入栈、出栈一次；额外空间 O(h)，来自遍历栈，最坏为 O(n)。")

#strong[#text("记忆骨架：")]#text(" 栈模拟先序遍历 → 先右后左入栈 → 保存孩子后断开旧指针 → ")#raw("prev.right = node")#text(" → 更新 ")#raw("prev")#text(" → 原地形成链表。")

#jump("toc", "↑ 返回目录")

== #text("105. 从前序与中序遍历序列构造二叉树（LeetCode 105）") <lc105>

#strong[#text("方法：")]#text(" 前序定位根 + 中序划分 + 递归建树")

#strong[#text("题目要求：")]#text(" 给定一棵二叉树的前序遍历 ")#raw("preorder")#text(" 和中序遍历 ")#raw("inorder")#text("，还原原来的二叉树并返回根节点。题目保证节点值互不相同。")

#strong[#text("具体例子：")]

```text
preorder = [3, 9, 20, 15, 7]
inorder  = [9, 3, 15, 20, 7]
```

#text("还原结果：")

```text
        3
       / \
      9   20
         /  \
        15   7
```

#strong[#text("核心原理：")]#text(" 前序遍历为“根 → 左 → 右”，因此当前前序序列的第一个未使用节点是当前子树的根；中序遍历为“左 → 根 → 右”，根据根节点在中序数组中的位置，可以划分出左右子树。")

#text("例如第一次取前序数组的 ")#raw("3")#text("：")

```text
中序： [9] | 3 | [15, 20, 7]
       左    根       右
```

#text("左子树只有节点 ")#raw("9")#text("，右子树包含 ")#raw("15、20、7")#text("。进入右子树时，前序数组中下一个未使用节点为 ")#raw("20")#text("；它在中序数组中把 ")#raw("[15, 20, 7]")#text(" 划分为 ")#raw("[15] | 20 | [7]")#text("，确定两个孩子分别为 ")#raw("15")#text(" 和 ")#raw("7")#text("。")

#strong[#text("为什么必须先递归左子树？")]#text(" 前序遍历在根节点之后先访问左子树。如果先构造右子树，就会错误地把节点 ")#raw("9")#text(" 当作右子树的根节点。")

#text("递归使用闭区间 ")#raw("[left, right]")#text("。当 ")#raw("left > right")#text(" 时，子树没有节点，返回 ")#raw("None")#text("。例如构造节点 ")#raw("9")#text(" 的左子树时调用 ")#raw("build(0, -1)")#text("，表示空区间，不会访问 ")#raw("inorder[-1]")#text("。")

#strong[#text("完整代码：")]

```python
class Solution:
    def buildTree(
        self,
        preorder: List[int],
        inorder: List[int]
    ) -> Optional[TreeNode]:
        index_map = {v: i for i, v in enumerate(inorder)}
        pre_idx = 0

        def build(left, right):
            nonlocal pre_idx
            if left > right:
                return None

            root_val = preorder[pre_idx]
            pre_idx += 1
            root = TreeNode(root_val)
            mid = index_map[root_val]
            root.left = build(left, mid - 1)
            root.right = build(mid + 1, right)
            return root

        return build(0, len(inorder) - 1)
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，每个节点创建一次，哈希表定位平均 O(1)；额外空间 O(n)，包括中序索引字典，递归栈另需 O(h)。")

#strong[#text("记忆骨架：")]#text(" 前序依次取根 → 中序找到根的位置 → 切分左右区间 → 先递归建左子树 → 再递归建右子树 → 返回根节点。")

#jump("toc", "↑ 返回目录")

== #text("437. 路径总和 III（LeetCode 437）") <lc437>

#strong[#text("方法：")]#text(" 前缀和 + 哈希表 + DFS 回溯")

#strong[#text("题目要求：")]#text(" 统计二叉树中节点值之和等于 ")#raw("targetSum")#text(" 的路径数量。路径可以从任意节点开始和结束，但必须沿父节点到子节点的方向连续向下。")

#strong[#text("具体例子：")]

```text
           10
          /  \
         5   -3
        / \    \
       3   2   11
      / \   \
     3  -2   1
```

#text("当 ")#raw("targetSum = 8")#text(" 时，有三条合法路径：")#raw("5 → 3")#text("、")#raw("5 → 2 → 1")#text("、")#raw("-3 → 11")#text("，返回 ")#raw("3")#text("。")

#strong[#text("核心原理：")]#text(" 如果从根到当前节点的累计和为 ")#raw("current_sum")#text("，某个历史位置的累计和为 ")#raw("old_sum")#text("，那么从该历史位置之后到当前节点的路径和等于 ")#raw("current_sum - old_sum")#text("。因此只需查找历史前缀和 ")#raw("old_sum = current_sum - targetSum")#text("。")

#text("例如沿着 ")#raw("10 → 5 → 3")#text(" 访问时，当前前缀和为 ")#raw("18")#text("。因为 ")#raw("18 - 8 = 10")#text("，历史前缀和中存在 ")#raw("10")#text("，所以找到路径 ")#raw("5 → 3")#text("。")

#strong[#text("为什么字典必须记录出现次数？")]#text(" 考虑路径 ")#raw("1 → -1 → 1")#text("，目标和为 ")#raw("1")#text("。到最后一个节点时，前缀和为 ")#raw("1")#text("，需要查找历史前缀和 ")#raw("0")#text("。它出现了两次：根节点之前一次，经过 ")#raw("1 → -1")#text(" 后一次，因此有两条符合要求的路径。字典初始化为 ")#raw("{0: 1}")#text("，也使从根节点开始的路径能够被统计。")

#strong[#text("为什么必须回溯？")]#text(" 字典只能包含当前祖先路径上的前缀和。若从左子树返回后不撤销其前缀和，再进入右子树就可能把左右两侧节点拼成不存在的路径。")

```text
       1
      / \
     2   3
```

#text("当目标和为 ")#raw("1")#text(" 时，合法路径只有根节点 ")#raw("1")#text("。左子树访问后产生的前缀和 ")#raw("3")#text("，不能留给右子树使用，否则到右侧节点 ")#raw("3")#text(" 时，可能将 ")#raw("4 - 3 = 1")#text(" 错误地统计为一条路径。退出当前节点时，需要撤销本次加入的前缀和。")

#strong[#text("完整代码：")]

```python
class Solution:
    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> int:
        prefix_count = {0: 1}

        def dfs(node, current_sum):
            if node is None:
                return 0

            current_sum += node.val
            need = current_sum - targetSum
            count = prefix_count.get(need, 0)
            prefix_count[current_sum] = prefix_count.get(current_sum, 0) + 1

            count += dfs(node.left, current_sum)
            count += dfs(node.right, current_sum)

            prefix_count[current_sum] -= 1
            if prefix_count[current_sum] == 0:
                del prefix_count[current_sum]
            return count

        return dfs(root, 0)
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，每个节点访问一次，字典操作平均 O(1)；额外空间 O(h)，来自递归栈和当前路径的前缀和字典。这里在计数归零时删除键，以避免保留已经退出路径的历史前缀和；若只减一而不删键，字典空间最坏可能达到 O(n)。")

#strong[#text("记忆骨架：")]#text(" 初始化 ")#raw("{0: 1}")#text(" → 累加当前前缀和 → 查找 ")#raw("current_sum - targetSum")#text(" → 记录当前前缀和 → 递归左右 → 回溯删除 → 返回路径数。")

#jump("toc", "↑ 返回目录")

== #text("236. 二叉树的最近公共祖先（LeetCode 236）") <lc236>

#strong[#text("方法：")]#text(" DFS 递归 + 自底向上返回节点")

#strong[#text("题目要求：")]#text(" 给定二叉树和两个指定节点 ")#raw("p")#text("、")#raw("q")#text("，找到它们最深的公共祖先。节点可以是自己的祖先，题目保证两个目标节点都存在。")

#strong[#text("具体例子：")]

```text
        3
       / \
      5   1
     / \
    6   2
       / \
      7   4
```

#text("当 ")#raw("p = 5，q = 1")#text(" 时返回节点 ")#raw("3")#text("；当 ")#raw("p = 7，q = 4")#text(" 时返回节点 ")#raw("2")#text("；当 ")#raw("p = 5，q = 4")#text(" 时返回节点 ")#raw("5")#text("。")

#strong[#text("核心原理：")]#text(" 对当前节点分别递归搜索左右子树，递归结果表示这一侧找到了哪个目标节点，或者已经确定的最近公共祖先。遇到空节点返回 ")#raw("None")#text("；遇到 ")#raw("p")#text(" 或 ")#raw("q")#text(" 则直接返回当前节点。")

- #text("左右递归都非空：两个目标分别位于两侧，当前节点就是最近公共祖先，返回 ")#raw("root")#text("。")
- #text("只有一边非空：目标或已确定的祖先位于这一侧，将该结果继续返回上层。")
- #text("两边都为空：当前子树没有目标，返回 ")#raw("None")#text("。")

#text("例如 ")#raw("p = 7，q = 4")#text("，递归到节点 ")#raw("2")#text(" 时左边返回 ")#raw("7")#text("、右边返回 ")#raw("4")#text("，所以节点 ")#raw("2")#text(" 返回自己。继续回到节点 ")#raw("5")#text("，左边返回 ")#raw("None")#text("、右边返回 ")#raw("2")#text("，因此继续返回 ")#raw("2")#text("。回到节点 ")#raw("3")#text(" 后同样向上传递 ")#raw("2")#text("，答案不会被更高的祖先覆盖。")

#strong[#text("为什么遇到目标节点就能直接返回？")]#text(" 例如 ")#raw("p = 5，q = 4")#text("，节点 ")#raw("5")#text(" 本身就是目标，也位于节点 ")#raw("4")#text(" 的祖先路径上，因此最近公共祖先就是 ")#raw("5")#text("，可以直接返回。这个结论利用了题目保证两个目标节点都存在的条件。")

#strong[#text("完整代码：")]

```python
class Solution:
    def lowestCommonAncestor(
        self,
        root: 'TreeNode',
        p: 'TreeNode',
        q: 'TreeNode'
    ) -> 'TreeNode':
        if root is None or root is p or root is q:
            return root

        left = self.lowestCommonAncestor(root.left, p, q)
        right = self.lowestCommonAncestor(root.right, p, q)
        if left is not None and right is not None:
            return root
        return left if left is not None else right
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，最坏访问全部节点；递归栈空间 O(h)，最坏为 O(n)。")

#strong[#text("记忆骨架：")]#text(" 空节点或目标节点直接返回 → 递归左右子树 → 两边非空返回当前节点 → 否则返回非空的一边。")

#jump("toc", "↑ 返回目录")

== #text("103. 二叉树的锯齿形层序遍历（LeetCode 103）") <lc103>

#strong[方法：] BFS 分层 + 隔层反转

#strong[题目要求：] 从根节点开始按层收集节点值，第一层从左到右，下一层从右到左，之后交替。空树返回空列表。

#strong[变量定义：] `root` 是根节点，`queue` 保存等待访问的节点，`level_size` 是开始处理本层时队列中的节点数，`node` 是当前出队的节点，`level` 保存本层节点值，`res` 保存各层的结果，`left_to_right` 记录本层输出方向。

#strong[为什么 BFS 能分层：] 队列先进先出。当前层节点出队时，它的孩子从队尾加入，排在剩余的当前层节点后面。处理前先把队列长度存到 `level_size`，本轮只取这个数量。这样新入队的孩子会留到下一轮。

#strong[为什么只反转本层结果：] 孩子始终按先左后右入队，因此每一层都会按从左到右被取出。需要从右到左时，收集完再对 `level` 调用 `reverse()`。它原地反转列表，返回值是 `None`，所以直接调用即可。

#strong[逐层推演：] 根节点 3 的孩子是 9 和 20，节点 20 的孩子是 15 和 7。

#table(
  columns: (auto, 1fr, 1fr, 1.25fr),
  table.header([层], [本轮开始的队列], [本层输出], [留给下一轮的队列]),
  [1], [`[3]`], [`[3]`], [`[9, 20]`],
  [2], [`[9, 20]`], [`[20, 9]`], [`[15, 7]`],
  [3], [`[15, 7]`], [`[15, 7]`], [`[]`],
)

第二层开始时固定处理 2 个节点。20 的孩子入队后仍留在队列里。反转的是这一层收集到的 `[9, 20]`，第三层仍按 `[15, 7]` 被访问。

```python
from collections import deque

class Solution:
    def zigzagLevelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        if not root:
            return []

        queue = deque([root])
        res = []
        left_to_right = True

        while queue:
            level_size = len(queue)
            level = []
            for _ in range(level_size):
                node = queue.popleft()
                level.append(node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)

            if not left_to_right:
                level.reverse()
            res.append(level)
            left_to_right = not left_to_right

        return res
```

#strong[复杂度：] 时间 O(n)，每个节点只进出队一次，各层反转的总长度至多为节点数。额外空间 O(w)，`w` 为树的最大层宽，队列最多同时容纳相邻两层的一部分，不计返回结果。

#strong[记忆骨架：] 根节点入队 → 固定本层长度 → 孩子先左后右入队 → 按方向决定是否反转本层结果 → 切换方向。

#jump("toc", "↑ 返回目录")

= #text("图论")

== #text("200. 岛屿数量（LeetCode 200）") <lc200>

#strong[#text("方法：")]#text(" 深度优先搜索（DFS）+ 栈")

#strong[#text("题目要求：")]#text(" 给定一个由 ")#raw("\"1\"")#text("（陆地）和 ")#raw("\"0\"")#text("（水）组成的二维网格，统计岛屿数量。水平或垂直相邻的陆地属于同一个岛屿，斜对角不算相连。")

#strong[#text("具体例子：")]

```text
grid = [
    ["1", "1", "0"],
    ["1", "0", "0"],
    ["0", "0", "1"]
]
输出：2
```

#strong[#text("核心原理：")]#text(" 从左到右、从上到下扫描网格。每遇到一个还没有访问过的 ")#raw("\"1\"")#text("，就说明发现了一座新岛屿，数量加一。然后从这块陆地出发，用 DFS 找到所有上下左右相连的陆地，并把它们改成 ")#raw("\"0\"")#text("，表示已经访问过。这里使用显式栈实现 DFS，避免递归层数过深。")

#strong[#text("完整代码：")]

```python
class Solution:
    def numIslands(self, grid: list[list[str]]) -> int:
        if not grid:
            return 0

        rows, cols = len(grid), len(grid[0])
        count = 0
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != "1":
                    continue

                # 发现一块尚未访问的陆地，就是一座新岛屿
                count += 1
                grid[r][c] = "0"
                stack = [(r, c)]
                while stack:
                    x, y = stack.pop()
                    # 检查当前陆地的上下左右
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < rows and
                            0 <= ny < cols and
                            grid[nx][ny] == "1"):
                            grid[nx][ny] = "0"  # 入栈前标记，避免重复访问
                            stack.append((nx, ny))
        return count
```

#strong[#text("复杂度：")]#text(" 时间 O(mn)，额外空间最坏 O(mn)，其中 ")#raw("m")#text("、")#raw("n")#text(" 分别为网格的行数和列数。")

#strong[#text("记忆骨架：")]#text(" 遍历网格 → 遇到陆地就计数 → 栈搜索上下左右 → 将访问过的陆地改成水 → 返回岛屿数量。")

#jump("toc", "↑ 返回目录")

= #text("回溯")

== #text("46. 全排列（LeetCode 46）") <lc46>

#strong[#text("方法：")]#text(" 回溯 + ")#raw("used")#text(" 数组")

#strong[#text("题目要求：")]#text(" 给定一个不包含重复数字的数组 ")#raw("nums")#text("，返回它的所有可能排列。")

#strong[#text("具体例子：")]#text(" ")#raw("nums = [1, 2, 3]")#text("，输出六种排列：")#raw("[1,2,3]")#text("、")#raw("[1,3,2]")#text("、")#raw("[2,1,3]")#text("、")#raw("[2,3,1]")#text("、")#raw("[3,1,2]")#text("、")#raw("[3,2,1]")#text("。")

#strong[#text("核心原理：")]#text(" 用 ")#raw("path")#text(" 记录当前正在构造的排列，用 ")#raw("used")#text(" 记录每个数字是否已经被选过。每次从数组中选择一个尚未使用的数字，加入 ")#raw("path")#text("，然后继续构造下一位。当 ")#raw("path")#text(" 的长度等于数组长度时，一个完整排列就形成了，把它复制到结果中。随后撤销刚才的选择，尝试其他数字。")

#strong[#text("完整代码：")]

```python
class Solution:
    def permute(self, nums: list[int]) -> list[list[int]]:
        result = []
        path = []
        used = [False] * len(nums)

        def backtrack():
            # 已经选够所有数字，得到一个完整排列
            if len(path) == len(nums):
                result.append(path[:])  # 保存当前排列的副本
                return

            for i in range(len(nums)):
                if used[i]:
                    continue  # 这个数字已经在当前排列中
                # 做选择
                used[i] = True
                path.append(nums[i])
                backtrack()  # 继续填写下一位
                # 撤销选择，尝试其他可能
                path.pop()
                used[i] = False

        backtrack()
        return result
```

#strong[#text("复杂度：")]#text(" 时间 O(n·n!)，因为共有 ")#raw("n!")#text(" 个排列，每个排列需要复制 ")#raw("n")#text(" 个元素。除结果集外，辅助空间 O(n)。")

#strong[#text("记忆骨架：")]#text(" 选择未使用的数字 → 加入 ")#raw("path")#text(" → 递归构造下一位 → 保存完整排列 → 撤销选择 → 尝试其他数字。")

#jump("toc", "↑ 返回目录")

= #text("二分查找")

== #text("35. 搜索插入位置（LeetCode 35）") <lc35>

#strong[#text("方法：")]#text(" 二分查找 + 左闭右开区间")

#strong[#text("题目要求：")]#text(" 给定升序数组 ")#raw("nums")#text(" 和整数 ")#raw("target")#text("，如果目标存在，返回它的下标；否则返回保持数组升序时应当插入的位置。要求时间复杂度 O(log n)。")

#strong[#text("具体例子：")]#text(" ")#raw("nums = [1, 3, 5, 6]")#text("。当 ")#raw("target = 5")#text(" 时返回 ")#raw("2")#text("；当 ")#raw("target = 2")#text(" 时返回 ")#raw("1")#text("；当 ")#raw("target = 7")#text(" 时返回 ")#raw("4")#text("。")

#strong[#text("核心原理：")]#text(" 查找目标值等价于寻找数组中第一个大于等于 ")#raw("target")#text(" 的位置。如果目标存在，这个位置就是目标的下标；如果不存在，这个位置就是正确的插入位置。")

#text("采用左闭右开区间 ")#raw("[left, right)")#text("，初始为 ")#raw("[0, len(nums))")#text("。每轮比较中间值：")

- #raw("nums[mid] < target")#text("：中间位置及其左侧都太小，更新 ")#raw("left = mid + 1")#text("。")
- #raw("nums[mid] >= target")#text("：当前中间位置已经满足条件，但左边可能存在更靠前的答案，更新 ")#raw("right = mid")#text("。")

#text("例如 ")#raw("nums = [1, 3, 5, 6]")#text("、")#raw("target = 2")#text("：")

#table(columns: (0.8fr, 1.3fr, 0.8fr, 1.1fr, 2.3fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("轮次")], [#text("搜索区间")], [#raw("mid")], [#text("中间值")], [#text("操作")]),
  table.hline(stroke: .4pt),
  [#text("1")], [#raw("[0, 4)")], [#text("2")], [#text("5")], [#raw("right = 2")],
  [#text("2")], [#raw("[0, 2)")], [#text("1")], [#text("3")], [#raw("right = 1")],
  [#text("3")], [#raw("[0, 1)")], [#text("0")], [#text("1")], [#raw("left = 1")],
  table.hline(stroke: .7pt))

#text("最终 ")#raw("left = right = 1")#text("，返回 1。")

#strong[#text("为什么初始化 ")#raw("right = len(nums)")#text("？")]#text(" 目标可能比所有元素都大，例如 ")#raw("target = 7")#text("，应插在下标 4 处。右边界设为数组长度，才能自然返回这个位置。")

#strong[#text("完整代码：")]

```python
class Solution:
    def searchInsert(self, nums: List[int], target: int) -> int:
        left = 0
        right = len(nums)
        while left < right:
            mid = (left + right) // 2
            if nums[mid] < target:
                left = mid + 1
            else:
                right = mid
        return left
```

#strong[#text("复杂度：")]#text(" 时间 O(log n)，每轮排除约一半候选位置；额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" 寻找第一个 ")#raw(">= target")#text(" 的位置 → 左闭右开区间 → 小于目标更新 ")#raw("left = mid + 1")#text(" → 否则更新 ")#raw("right = mid")#text(" → 返回 ")#raw("left")#text("。")

#jump("toc", "↑ 返回目录")

== #text("74. 搜索二维矩阵（LeetCode 74）") <lc74>

#strong[#text("方法：")]#text(" 二维矩阵虚拟展开 + 二分查找")

#strong[#text("题目要求：")]#text(" 给定矩阵，每行从左到右递增，下一行第一个元素大于上一行最后一个元素。判断 ")#raw("target")#text(" 是否存在，要求时间复杂度 O(log(mn))。")

#strong[#text("具体例子：")]

```text
 1   3   5   7
10  11  16  20
23  30  34  60
```

#raw("target = 3")#text(" 返回 ")#raw("True")#text("；")#raw("target = 13")#text(" 返回 ")#raw("False")#text("。")

#strong[#text("核心原理：")]#text(" 每行内部有序，且下一行第一个数大于上一行最后一个数，因此整个矩阵按行展开后等价于升序数组：")#raw("[1, 3, 5, 7, 10, 11, 16, 20, 23, 30, 34, 60]")#text("。可以直接应用第 35 题的二分模板，不需要真正创建新数组。")

#text("关键是把一维下标转换为二维位置：")#raw("row = mid // n")#text("，")#raw("col = mid % n")#text("，其中 ")#raw("n")#text(" 是每行元素个数。例如每行有 4 个元素，一维下标 ")#raw("mid = 6")#text(" 对应 ")#raw("matrix[1][2] = 16")#text("。")

#text("仍然寻找第一个大于等于目标值的位置，最后检查是否等于目标。例如 ")#raw("target = 3")#text("：")

#table(columns: (0.8fr, 1.3fr, 0.8fr, 1.1fr, 2.3fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("轮次")], [#text("搜索区间")], [#raw("mid")], [#text("对应数值")], [#text("更新")]),
  table.hline(stroke: .4pt),
  [#text("1")], [#raw("[0, 12)")], [#text("6")], [#text("16")], [#raw("right = 6")],
  [#text("2")], [#raw("[0, 6)")], [#text("3")], [#text("7")], [#raw("right = 3")],
  [#text("3")], [#raw("[0, 3)")], [#text("1")], [#text("3")], [#raw("right = 1")],
  [#text("4")], [#raw("[0, 1)")], [#text("0")], [#text("1")], [#raw("left = 1")],
  table.hline(stroke: .7pt))

#text("最终位置下标为 1，对应数值 3，返回 ")#raw("True")#text("。")

#strong[#text("为什么需要检查边界？")]#text(" 如果目标比所有元素都大，最终 ")#raw("left = m * n")#text("，这个位置已经超出矩阵范围，必须先返回 ")#raw("False")#text("，不能直接转换坐标访问。")

#strong[#text("完整代码：")]

```python
class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        m = len(matrix)
        n = len(matrix[0])
        left = 0
        right = m * n
        while left < right:
            mid = (left + right) // 2
            row = mid // n
            col = mid % n
            value = matrix[row][col]
            if value < target:
                left = mid + 1
            else:
                right = mid
        if left == m * n:
            return False
        return matrix[left // n][left % n] == target
```

#strong[#text("复杂度：")]#text(" 时间 O(log(mn))，矩阵共有 mn 个元素；额外空间 O(1)，因为没有创建展开后的数组。")

#strong[#text("记忆骨架：")]#text(" 矩阵按行视为升序数组 → ")#raw("[0, m*n)")#text(" 二分 → ")#raw("mid // n")#text(" 找行、")#raw("mid % n")#text(" 找列 → 找第一个大于等于目标的位置 → 检查是否相等。")

#jump("toc", "↑ 返回目录")

== #text("34. 在排序数组中查找元素的第一个和最后一个位置（LeetCode 34）") <lc34>

#strong[#text("方法：")]#text(" 两次二分查找 + 左右边界")

#strong[#text("题目要求：")]#text(" 给定非递减数组 ")#raw("nums")#text(" 和整数 ")#raw("target")#text("，返回目标值第一次和最后一次出现的下标；如果不存在，返回 ")#raw("[-1, -1]")#text("。要求时间复杂度 O(log n)。")

#strong[#text("具体例子：")]#text(" ")#raw("nums = [5, 7, 7, 8, 8, 10]")#text("。当 ")#raw("target = 8")#text(" 时返回 ")#raw("[3, 4]")#text("；当 ")#raw("target = 6")#text(" 时返回 ")#raw("[-1, -1]")#text("。")

#strong[#text("核心原理：")]#text(" 继续复用第 35 题的 ")#raw("lower_bound(x)")#text("，它寻找第一个大于等于 ")#raw("x")#text(" 的位置。第一次查找 ")#raw("lower_bound(target)")#text(" 得到左边界；第二次查找 ")#raw("lower_bound(target + 1)")#text(" 得到第一个严格大于目标值的位置，减 1 就是右边界。")

```text
下标： 0  1  2  3  4   5
数组： 5  7  7  8  8  10
               ↑     ↑
            start=3  第一个>8的位置=5
```

#text("因此 ")#raw("start = 3")#text("、")#raw("end = 5 - 1 = 4")#text("，返回 ")#raw("[3, 4]")#text("。")

#strong[#text("为什么能够使用 ")#raw("target + 1")#text("？")]#text(" 题目中的元素都是整数，所以严格大于 ")#raw("target")#text(" 的整数必然大于等于 ")#raw("target + 1")#text("。")

#strong[#text("为什么还要检查目标是否存在？")]#text(" 例如 ")#raw("target = 6")#text("，第一次二分返回下标 1，因为第一个大于等于 6 的元素是 7。但 ")#raw("nums[1] != 6")#text("，所以目标不存在，必须返回 ")#raw("[-1, -1]")#text("。空数组或目标比所有元素大时，第一次二分会返回数组长度，也必须先检查越界。")

#strong[#text("完整代码：")]

```python
class Solution:
    def searchRange(self, nums: List[int], target: int) -> List[int]:
        def lower_bound(x):
            left = 0
            right = len(nums)
            while left < right:
                mid = (left + right) // 2
                if nums[mid] < x:
                    left = mid + 1
                else:
                    right = mid
            return left

        start = lower_bound(target)
        if start == len(nums) or nums[start] != target:
            return [-1, -1]
        end = lower_bound(target + 1) - 1
        return [start, end]
```

#strong[#text("复杂度：")]#text(" 时间 O(log n)，最多执行两次二分；额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" ")#raw("lower_bound(target)")#text(" 找左边界 → 判断目标是否存在 → ")#raw("lower_bound(target + 1) - 1")#text(" 找右边界 → 返回 ")#raw("[start, end]")#text("。")

#jump("toc", "↑ 返回目录")

== #text("33. 搜索旋转排序数组（LeetCode 33）") <lc33>

#strong[#text("方法：")]#text(" 二分查找 + 判断有序半区")

#strong[#text("题目要求：")]#text(" 给定一个原本严格递增、经过某次旋转后的数组，所有元素互不相同。返回 ")#raw("target")#text(" 的下标，不存在则返回 ")#raw("-1")#text("，要求时间复杂度 O(log n)。")

#strong[#text("具体例子：")]#text(" ")#raw("nums = [4, 5, 6, 7, 0, 1, 2]")#text("，当 ")#raw("target = 0")#text(" 时返回 ")#raw("4")#text("；当 ")#raw("target = 3")#text(" 时返回 ")#raw("-1")#text("。")

#strong[#text("核心原理：")]#text(" 旋转数组整体不再递增，不能直接按普通二分的大小关系决定搜索方向。例如目标为 0，第一次中间值为 7。如果按照普通二分的“中间值大于目标，所以往左找”，就会把位于右半边的 0 排除。")

#text("由于原始数组严格递增、只经过一次旋转，每轮二分的左右两半至少有一半保持有序。")#strong[#text("先判断哪一半有序，再检查目标是否落在有序半区的数值范围内。")]

#strong[#text("第一种情况：")]#text(" ")#raw("nums[left] <= nums[mid]")#text("，说明左半边有序。")

```text
下标： 0  1  2  3  4  5  6
数组： 4  5  6  7  0  1  2
       └──有序──┘
```

#text("如果 ")#raw("nums[left] <= target < nums[mid]")#text("，目标在左边，更新 ")#raw("right = mid")#text("；否则更新 ")#raw("left = mid + 1")#text("。")

#strong[#text("第二种情况：")]#text(" ")#raw("nums[left] > nums[mid]")#text("，说明旋转断点位于左半边，因此右半边有序。")

```text
下标： 0  1  2  3  4  5  6
数组： 6  7  0  1  2  4  5
                └──有序──┘
```

#text("如果 ")#raw("nums[mid] < target <= nums[right - 1]")#text("，目标在右边，更新 ")#raw("left = mid + 1")#text("；否则更新 ")#raw("right = mid")#text("。")

#strong[#text("为什么先检查 ")#raw("nums[mid] == target")#text("？")]#text(" 后续大小比较仅用于排除搜索区间，当前中间位置已命中时可直接返回。")

#text("例如 ")#raw("nums = [4, 5, 6, 7, 0, 1, 2]")#text("、")#raw("target = 0")#text("：")

#table(columns: (0.8fr, 1.3fr, 0.8fr, 1.1fr, 2.3fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("轮次")], [#text("搜索区间")], [#raw("mid")], [#text("中间值")], [#text("判断与更新")]),
  table.hline(stroke: .4pt),
  [#text("1")], [#raw("[0, 7)")], [#text("3")], [#text("7")], [#text("左半边有序，0 不在其中，")#raw("left = 4")],
  [#text("2")], [#raw("[4, 7)")], [#text("5")], [#text("1")], [#text("左半边有序，0 在左边，")#raw("right = 5")],
  [#text("3")], [#raw("[4, 5)")], [#text("4")], [#text("0")], [#text("命中，返回 4")],
  table.hline(stroke: .7pt))

#strong[#text("完整代码：")]

```python
class Solution:
    def search(self, nums: List[int], target: int) -> int:
        left = 0
        right = len(nums)
        while left < right:
            mid = (left + right) // 2
            if nums[mid] == target:
                return mid

            if nums[left] <= nums[mid]:
                if nums[left] <= target < nums[mid]:
                    right = mid
                else:
                    left = mid + 1
            else:
                if nums[mid] < target <= nums[right - 1]:
                    left = mid + 1
                else:
                    right = mid
        return -1
```

#strong[#text("复杂度：")]#text(" 时间 O(log n)，每轮排除至少一半候选位置；额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" 先判断 ")#raw("mid")#text(" 是否命中 → 判断哪半边有序 → 判断目标是否落在有序半边 → 保留可能包含目标的一半 → 继续二分。")

#jump("toc", "↑ 返回目录")

== #text("153. 寻找旋转排序数组中的最小值（LeetCode 153）") <lc153>

#strong[#text("方法：")]#text(" 二分查找 + 判断旋转断点（仍然使用左闭右开 ")#raw("[left, right)")#text("）。")

#strong[#text("题目要求：")]#text(" 给定一个经过旋转的严格升序数组，所有元素互不相同，返回数组中的")#strong[#text("最小值")]#text("，不是最小值所在的下标。要求时间复杂度 O(log n)。")

#strong[#text("具体例子：")]#text(" ")#raw("nums = [3,4,5,1,2]")#text("，返回数字 1；")#raw("nums = [1,2,3,4]")#text(" 没有发生实际旋转，也返回 1。")

#strong[#text("核心原理：")]#text(" 旋转会使数组中最多出现一个从大数字跳到小数字的位置，最小值就在这个位置的后面。比较 ")#raw("nums[mid]")#text(" 和当前最右边的真实元素 ")#raw("nums[right-1]")#text("：")

- #text("如果 ")#raw("nums[mid] > nums[right-1]")#text("，说明从 ")#raw("mid")#text(" 到最右边之间跨过了旋转断点，最小值一定在 ")#raw("mid")#text(" 右边。排除 ")#raw("mid")#text("，执行 ")#raw("left = mid + 1")#text("。")
- #text("如果 ")#raw("nums[mid] < nums[right-1]")#text("，说明从 ")#raw("mid")#text(" 到右端保持升序；这一段的最小值就是 ")#raw("nums[mid]")#text("。整体的最小值可能就是 ")#raw("mid")#text("，也可能在更左边，所以必须保留 ")#raw("mid")#text("，新的右边界是 ")#raw("right = mid + 1")#text("，保留 ")#raw("[left, mid+1)")#text("。")

#text("这里为什么与第 33 题不同？第 33 题提前检查过 ")#raw("nums[mid] == target")#text("，不命中就能排除 ")#raw("mid")#text("；本题没有检查 ")#raw("mid")#text(" 是否是最小值，因此向左缩小区间时仍需保留它。")

#strong[#text("为什么 ")#raw("mid = (left + right - 1) // 2")#text("？")]#text(" 我们的右边界不包含在区间内，且向左收缩时需要保留 ")#raw("mid")#text("。如果区间只有两个元素 ")#raw("[1,2]")#text("，")#raw("left=0,right=2")#text("，写普通的 ")#raw("(left+right)//2")#text(" 会得到 ")#raw("mid=1")#text("；当右边有序时，")#raw("right=mid+1")#text(" 仍等于 2，区间没有缩小，可能死循环。用 ")#raw("(left+right-1)//2")#text(" 让 ")#raw("mid")#text(" 偏左，保证每轮都会缩小。由于最终只需剩一个数，因此循环条件是 ")#raw("right-left>1")#text("。")

#strong[#text("完整推演：")]#text(" ")#raw("nums = [3,4,5,1,2]")#text("。")

#table(columns: (0.75fr, 1.5fr, 1.2fr, 1.2fr, 2.5fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("轮次")], [#text("搜索区间 ")#raw("[left,right)")], [#text("mid / 值")], [#text("右端真实值")], [#text("更新理由与新范围")]),
  table.hline(stroke: .4pt),
  [#text("1")], [#raw("[0,5)")], [#raw("2 / 5")], [#text("2")], [#raw("5>2")#text("，最小值在 mid 右侧，")#raw("left=3")#text("，变为 ")#raw("[3,5)")],
  [#text("2")], [#raw("[3,5)")], [#raw("3 / 1")], [#text("2")], [#raw("1<2")#text("，保留 mid，")#raw("right=4")#text("，变为 ")#raw("[3,4)")],
  [#text("结束")], [#raw("[3,4)")], [#text("—")], [#text("—")], [#text("只剩下标 3，返回 ")#raw("nums[3]=1")],
  table.hline(stroke: .7pt))

#strong[#text("完整代码：")]

```python
class Solution:
    def findMin(self, nums: List[int]) -> int:
        left, right = 0, len(nums)  # 左闭右开

        while right - left > 1:
            mid = (left + right - 1) // 2  # mid 偏左，防止区间不缩小
            if nums[mid] > nums[right - 1]:
                left = mid + 1          # 最小值必在 mid 右边
            else:
                right = mid + 1         # mid 可能就是最小值，保留它

        return nums[left]
```

#strong[#text("复杂度：")]#text(" 时间 O(log n)，每轮大致排除一半；额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" 初始化 ")#raw("[0,n)")#text(" → ")#raw("mid")#text(" 偏左 → 比较 ")#raw("nums[mid]")#text(" 和 ")#raw("nums[right-1]")#text(" → 大于则 ")#raw("left=mid+1")#text("，否则 ")#raw("right=mid+1")#text(" → 区间只剩一个位置时返回它的值。")

#jump("toc", "↑ 返回目录")

== #text("704. 二分查找（LeetCode 704）") <lc704>

#strong[#text("方法：")]#text(" 二分查找 + 左闭右开区间")

#strong[#text("题目要求：")]#text(" 在严格递增数组 ")#raw("nums")#text(" 中查找 ")#raw("target")#text("，找到则返回下标，否则返回 ")#raw("-1")#text("。")

#strong[#text("具体例子：")]#text(" 在 ")#raw("[-1,0,3,5,9,12]")#text(" 中找 ")#raw("9")#text("。搜索区间依次为 ")#raw("[0,6)")#text("、")#raw("[4,6)")#text("、")#raw("[4,5)")#text("，对应的中点值为 ")#raw("5")#text("、")#raw("12")#text("、")#raw("9")#text("，返回 ")#raw("4")#text("。")

#strong[#text("核心原理：")]#text(" ")#raw("left")#text(" 和 ")#raw("right")#text(" 是候选区间 ")#raw("[left, right)")#text(" 的边界，")#raw("mid")#text(" 是中点下标。若中点值偏小，排除 ")#raw("mid")#text(" 及其左边，令 ")#raw("left = mid + 1")#text("。若偏大，排除 ")#raw("mid")#text(" 及其右边，令 ")#raw("right = mid")#text("。相等时返回 ")#raw("mid")#text("，区间变空时返回 ")#raw("-1")#text("。")

#strong[#text("完整代码：")]

```python

class Solution:
    def search(self, nums: list[int], target: int) -> int:
        left = 0
        right = len(nums)

        # 搜索区间为 [left, right)
        while left < right:
            mid = (left + right) // 2

            if nums[mid] == target:
                return mid

            elif nums[mid] < target:
                # 中间元素太小，去右半边查找
                left = mid + 1

            else:
                # 中间元素太大，去左半边查找
                right = mid

        # 搜索区间为空，目标不存在
        return -1
```

#strong[#text("复杂度：")]#text(" 时间 O(log n)，额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" 初始化 [0, n) → 比较中点 → 缩小候选区间 → 命中返回下标，区间空返回 -1。")

#jump("toc", "↑ 返回目录")

= #text("栈")

== #text("20. 有效的括号（LeetCode 20）") <lc20>

#strong[#text("方法：")]#text(" 栈 + 括号配对")

#strong[#text("题目要求：")]#text(" 字符串 ")#raw("s")#text(" 仅包含 ")#raw("()")#text("、")#raw("[]")#text("、")#raw("{}")#text(" 这三种括号，判断它是否有效。右括号必须与同类型的左括号正确配对，并按照正确的嵌套顺序闭合。")

#strong[#text("具体例子：")]#text(" ")#raw("s = \"([])\"")#text(" 返回 ")#raw("True")#text("；")#raw("s = \"([)]\"")#text(" 返回 ")#raw("False")#text("，因为出现 ")#raw(")")#text(" 时，最近一个尚未闭合的左括号是 ")#raw("[")#text("，类型不匹配；")#raw("s = \"(()\"")#text(" 也返回 ")#raw("False")#text("，因为仍有一个 ")#raw("(")#text(" 没有闭合。")

#strong[#text("核心原理：")]#text(" 栈是后进先出的数据结构。字符串中的右括号应该关闭最近出现、尚未匹配的左括号，刚好对应栈顶。遇到左括号就执行 ")#raw("stack.append(ch)")#text(" 入栈；遇到右括号，就查看最近的左括号并用 ")#raw("stack.pop()")#text(" 从栈顶取出，类型不匹配立即返回 ")#raw("False")#text("；处理完所有字符后，栈必须为空才有效。")

#strong[#text("Python 写法先说明：")]#text(" ")#raw("stack[-1]")#text(" 表示列表的最后一个元素，在列表模拟的栈中就是栈顶，不是栈底；")#raw("stack.pop()")#text(" 会取出并删除栈顶。")#raw("not stack")#text(" 在 ")#raw("stack")#text(" 是列表时，意思是“栈为空”，等价于 ")#raw("len(stack) == 0")#text("；")#raw("if stack")#text(" 则表示非空。注意它们不能与 ")#raw("stack is not None")#text(" 混为一谈：即使 ")#raw("stack=[]")#text("，空列表仍然不是 ")#raw("None")#text("。下面用 ")#raw("len(stack) == 0")#text(" 来判断空栈。")

#strong[#text("完整推演：")]#text(" 输入 ")#raw("s = \"([])\"")#text("，栈中最右边的元素表示栈顶。")

#table(columns: (1fr, 2.2fr, 1.6fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("本轮字符")], [#text("动作")], [#text("操作后 stack")]),
  table.hline(stroke: .4pt),
  [#raw("(")], [#text("左括号，入栈")], [#raw("['(']")],
  [#raw("[")], [#text("左括号，入栈")], [#raw("['(', '[']")],
  [#raw("]")], [#text("与栈顶 ")#raw("[")#text(" 匹配，弹出 ")#raw("[")], [#raw("['(']")],
  [#raw(")")], [#text("与栈顶 ")#raw("(")#text(" 匹配，弹出 ")#raw("(")], [#raw("[]")],
  table.hline(stroke: .7pt))

#text("这时栈为空，返回 ")#raw("True")#text("。反例 ")#raw("\"([)]\"")#text("：读到 ")#raw(")")#text(" 时，栈顶是 ")#raw("[")#text("，与应匹配的 ")#raw("(")#text(" 不同，立即返回 ")#raw("False")#text("。因此，仅检查左右括号的数量相同远远不够。")

#strong[#text("完整代码：")]

```python
class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        pairs = {')': '(', ']': '[', '}': '{'}

        for ch in s:
            if ch in '([{':          # 左括号：先保存起来
                stack.append(ch)
            else:                    # 右括号：匹配最近的左括号
                if len(stack) == 0:
                    return False
                if stack.pop() != pairs[ch]:
                    return False

        return len(stack) == 0      # 没有剩余左括号才有效
```

#strong[#text("复杂度：")]#text(" 时间 O(n)，每个字符最多入栈和出栈一次；辅助空间 O(n)。")

#strong[#text("记忆骨架：")]#text(" 左括号入栈 → 右括号检查空栈、再弹出栈顶比较类型 → 不匹配立即 False → 遍历结束后栈空才 True。")

#jump("toc", "↑ 返回目录")

== #text("155. 最小栈（LeetCode 155）") <lc155>

#strong[#text("方法：")]#text(" 正常栈 + 同步记录最小值的辅助栈")

#strong[#text("题目要求：")]#text(" 设计 ")#raw("MinStack")#text(" 类，支持 ")#raw("push(val)")#text("（入栈）、")#raw("pop()")#text("（出栈）、")#raw("top()")#text("（查看栈顶）、")#raw("getMin()")#text("（取得当前最小值）。所有操作都必须达到 O(1) 时间复杂度。")

#strong[#text("具体例子：")]#text(" 依次执行 ")#raw("push(-2)")#text("、")#raw("push(0)")#text("、")#raw("push(-3)")#text("，此时 ")#raw("top()")#text(" 和 ")#raw("getMin()")#text(" 均返回 -3；执行 ")#raw("pop()")#text(" 后，栈为 ")#raw("[-2,0]")#text("，")#raw("top()")#text(" 返回 0，")#raw("getMin()")#text(" 返回 -2。")

#strong[#text("核心原理：")]#text(" 普通列表栈的 ")#raw("append")#text("、")#raw("pop")#text("、")#raw("[-1]")#text(" 都可在 O(1) 时间完成，但直接 ")#raw("min(stack)")#text(" 需要遍历，耗时 O(n)。只保存一个最小值变量也不够：例如最小值 -3 出栈后，不遍历就不知道上一个最小值是 -2。")

#text("因此使用两个栈：")#raw("self.stack")#text(" 存原始数字；")#raw("self.min_stack")#text(" 与它每次同步入栈、同步出栈，记录每一层对应的“截至当前层时的最小值”。新数字 ")#raw("val")#text(" 入栈后，辅助栈追加 ")#raw("min(val, self.min_stack[-1])")#text("；最小值被弹出时，辅助栈也弹出，于是此前的最小值自然恢复。两个栈长度始终相等。")

#strong[#text("Python 语法先说明：")]#text(" ")#raw("self.min_stack[-1]")#text(" 是辅助栈最后一个元素，也就是栈顶，它保存当前最小值；")#raw("self.stack[0]")#text(" 才是栈底。")#raw("if not self.min_stack")#text(" 的意思是“如果辅助栈为空”，对于列表等价于 ")#raw("if len(self.min_stack) == 0")#text("。")

#strong[#text("完整推演：")]#text(" 列表右侧是栈顶。")

#table(columns: (1.1fr, 1.6fr, 1.6fr, 1fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt), table.header([#text("操作")], [#text("正常栈 ")#raw("stack")], [#text("辅助栈 ")#raw("min_stack")], [#text("当前最小值")]),
  table.hline(stroke: .4pt),
  [#raw("push(-2)")], [#raw("[-2]")], [#raw("[-2]")], [#text("-2")],
  [#raw("push(0)")], [#raw("[-2,0]")], [#raw("[-2,-2]")], [#text("-2")],
  [#raw("push(-3)")], [#raw("[-2,0,-3]")], [#raw("[-2,-2,-3]")], [#text("-3")],
  [#raw("pop()")], [#raw("[-2,0]")], [#raw("[-2,-2]")], [#text("-2")],
  table.hline(stroke: .7pt))

#strong[#text("完整代码：")]

```python
class MinStack:
    def __init__(self):
        self.stack = []
        self.min_stack = []

    def push(self, val: int) -> None:
        self.stack.append(val)
        if not self.min_stack:                 # 等价于 len(self.min_stack) == 0
            self.min_stack.append(val)
        else:
            previous_min = self.min_stack[-1]  # 栈顶保存此前的最小值
            self.min_stack.append(min(val, previous_min))

    def pop(self) -> None:
        self.stack.pop()
        self.min_stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.min_stack[-1]
```

#strong[#text("复杂度：")]#text(" 四种操作都是 O(1) 时间；两个栈各保存至多 n 个元素，辅助空间 O(n)。")

#strong[#text("记忆骨架：")]#text(" 创建普通栈和最小值辅助栈 → push 时同步记录当前最小值 → pop 时两个栈同步弹出 → top 看普通栈顶 → getMin 看辅助栈顶。")

#jump("toc", "↑ 返回目录")

== #text("232. 用栈实现队列（LeetCode 232）") <lc232>

#strong[#text("方法：")]#text(" 双栈 + 按需转移")

#strong[#text("题目要求：")]#text(" 只用两个栈实现队列。")#raw("push(x)")#text(" 在队尾加入元素，")#raw("pop()")#text(" 删除并返回队首，")#raw("peek()")#text(" 查看队首，")#raw("empty()")#text(" 判断队列是否为空。")

#strong[#text("具体例子：")]#text(" 依次压入 ")#raw("1、2、3")#text("，再执行下表中的操作。栈内元素按栈底到栈顶排列。")

#table(columns: (1.2fr, 1fr, 1fr, 1fr), stroke: none, inset: (x: 5pt, y: 4pt),
  table.hline(stroke: .7pt),
  table.header([操作], [#raw("in_stack")], [#raw("out_stack")], [返回值]),
  table.hline(stroke: .4pt),
  [压入 1、2、3], [#raw("[1, 2, 3]")], [#raw("[]")], [—],
  [#raw("peek()")], [#raw("[]")], [#raw("[3, 2, 1]")], [#raw("1")],
  [#raw("pop()")], [#raw("[]")], [#raw("[3, 2]")], [#raw("1")],
  [#raw("push(4)")], [#raw("[4]")], [#raw("[3, 2]")], [—],
  [#raw("pop()")], [#raw("[4]")], [#raw("[3]")], [#raw("2")],
  table.hline(stroke: .7pt))

#strong[#text("核心原理：")]#text(" ")#raw("in_stack")#text(" 接收新元素，")#raw("out_stack")#text(" 的栈顶是当前队首。读取队首时，若 ")#raw("out_stack")#text(" 已空，就把 ")#raw("in_stack")#text(" 逐个弹出并压入 ")#raw("out_stack")#text("，使最早入队的元素来到栈顶。只要 ")#raw("out_stack")#text(" 还有元素，就先处理其中较早入队的一批。两个栈都空时，队列才为空。")

#strong[#text("完整代码：")]

```python

class MyQueue:

    def __init__(self):
        self.in_stack = []
        self.out_stack = []

    def push(self, x: int) -> None:
        # 新元素直接进入 in_stack
        self.in_stack.append(x)

    def pop(self) -> int:
        # out_stack 为空时，才进行元素转移
        if not self.out_stack:
            while self.in_stack:
                self.out_stack.append(self.in_stack.pop())

        # 从 out_stack 弹出队首元素
        return self.out_stack.pop()

    def peek(self) -> int:
        # out_stack 为空时，才进行元素转移
        if not self.out_stack:
            while self.in_stack:
                self.out_stack.append(self.in_stack.pop())

        # 查看队首元素，但不删除
        return self.out_stack[-1]

    def empty(self) -> bool:
        # 两个栈都为空，队列才为空
        return not self.in_stack and not self.out_stack
```

#strong[#text("复杂度：")]#text(" 入队和判空为 O(1)。出队和查看队首的单次最坏时间为 O(n)，均摊为 O(1)，因为每个元素最多转移一次。空间 O(n)。")

#strong[#text("记忆骨架：")]#text(" 新元素入输入栈 → 输出栈空才倒入 → 从输出栈取队首。")

#jump("toc", "↑ 返回目录")

= #text("堆")

== #text("215. 数组中的第 K 个最大元素（LeetCode 215）") <lc215>

#strong[#text("方法：")]#text(" 随机快速选择 + 三路划分")

#strong[#text("题目要求：")]#text(" 给定整数数组 ")#raw("nums")#text(" 和排名 ")#raw("k")#text("，返回按降序排列时位于下标 ")#raw("k - 1")#text(" 的元素，重复值分别占位。")

#strong[#text("具体例子：")]#text(" ")#raw("nums = [3,2,1,5,6,4]")#text("，")#raw("k = 2")#text("。若先选 ")#raw("4")#text("，划分为 ")#raw("[5,6 | 4 | 3,2,1]")#text("，目标下标 ")#raw("1")#text(" 在左段。再选 ")#raw("5")#text("，左段划分为 ")#raw("[6 | 5]")#text("，目标落在等值段，返回 ")#raw("5")#text("。")

#strong[#text("核心原理：")]#text(" 在候选区间 ")#raw("[left, right)")#text(" 随机选基准值 ")#raw("pivot")#text("，把元素原地分成大于、等于、小于三段。")#raw("pos")#text(" 和 ")#raw("equal_end")#text(" 分别是等值段的首尾下标。目标落在这段时直接返回，否则只保留目标所在的左段或右段。集中等值元素后，一次划分即可排除或命中整段重复值。")

#strong[#text("完整代码：")]

```python

import random

class Solution:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        # 按降序排列时，第 k 大对应下标 k-1
        target = k - 1

        # 当前搜索区间：[left, right)
        left = 0
        right = len(nums)

        while True:
            # 随机选基准值，先交换到区间末尾
            pivot_idx = random.randrange(left, right)
            nums[pivot_idx], nums[right - 1] = (
                nums[right - 1], nums[pivot_idx]
            )
            pivot = nums[right - 1]

            # 第一轮：把大于 pivot 的元素放到左侧
            pos = left

            for j in range(left, right - 1):
                if nums[j] > pivot:
                    nums[pos], nums[j] = nums[j], nums[pos]
                    pos += 1

            # 第二轮：把等于 pivot 的元素集中起来
            equal_end = pos

            for j in range(pos, right - 1):
                if nums[j] == pivot:
                    nums[equal_end], nums[j] = (
                        nums[j], nums[equal_end]
                    )
                    equal_end += 1

            # 将基准值放在相等元素区域的末尾
            nums[equal_end], nums[right - 1] = (
                nums[right - 1], nums[equal_end]
            )

            # 目标落在等于 pivot 的区域，直接返回
            if pos <= target <= equal_end:
                return nums[target]

            # 目标在左侧，只搜索大于 pivot 的元素
            elif target < pos:
                right = pos

            # 目标在右侧，只搜索小于 pivot 的元素
            else:
                left = equal_end + 1
```

#strong[#text("复杂度：")]#text(" 期望时间 O(n)，最坏 O(n²)，额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" 目标下标 k - 1 → 随机选基准 → 三路划分 → 命中等值段或缩小区间。")

#jump("toc", "↑ 返回目录")

== #text("912. 排序数组（LeetCode 912）") <lc912>

#strong[#text("方法：")]#text(" 大顶堆排序")

#strong[#text("题目要求：")]#text(" 将整数数组 ")#raw("nums")#text(" 原地升序排序并返回，不使用内置排序函数。")

#strong[#text("具体例子：")]#text(" ")#raw("[5,2,3,1]")#text(" 已经是大顶堆。每轮把堆顶换到末尾，再对剩余前缀下沉。三轮结束后的数组分别为 ")#raw("[3,2,1,5]")#text("、")#raw("[2,1,3,5]")#text(" 和 ")#raw("[1,2,3,5]")#text("。")

#strong[#text("核心原理：")]#text(" 大顶堆的父节点不小于两个子节点，所以堆顶是当前最大值。下沉时，")#raw("i")#text(" 是待调整节点下标，")#raw("child")#text(" 记录较大的子节点。若该子节点大于父节点，就交换并继续向下调整。从最后一个非叶节点向前下沉，建成堆后反复把堆顶放到未排序区间末尾，缩小堆并恢复堆序。")

#strong[#text("完整代码：")]

```python

class Solution:
    def sortArray(self, nums: list[int]) -> list[int]:
        n = len(nums)

        def sift_down(i, size):
            while True:
                # 当前节点的左孩子
                child = 2 * i + 1

                # 没有孩子，停止调整
                if child >= size:
                    break

                # 如果右孩子存在且更大，就选择右孩子
                if child + 1 < size and nums[child + 1] > nums[child]:
                    child += 1

                # 父节点已经不小于较大的孩子
                if nums[i] >= nums[child]:
                    break

                # 交换父节点和较大的孩子
                nums[i], nums[child] = nums[child], nums[i]

                # 继续向下调整
                i = child

        # 第一阶段：从最后一个非叶子节点开始建堆
        for i in range(n // 2 - 1, -1, -1):
            sift_down(i, n)

        # 第二阶段：把最大值逐个放到数组末尾
        for end in range(n - 1, 0, -1):
            nums[0], nums[end] = nums[end], nums[0]

            # 排除已经排序完成的末尾元素
            sift_down(0, end)

        return nums
```

#strong[#text("复杂度：")]#text(" 建堆 O(n)，排序总时间 O(n log n)，额外空间 O(1)。")

#strong[#text("记忆骨架：")]#text(" 从后向前建大顶堆 → 堆顶换到末尾 → 缩堆 → 堆顶下沉。")

#jump("toc", "↑ 返回目录")

= #text("贪心算法")

== #text("121. 买卖股票的最佳时机（LeetCode 121）") <lc121>

#strong[方法：] 贪心 + 维护历史最低价

#strong[题目要求：] 给定按日期排列的股票价格，最多买入和卖出各一次，卖出必须晚于买入。返回最大利润，如果没有盈利的交易，返回 0。

#strong[变量定义：] `prices` 是按日期排列的价格列表，`i` 是当前日期的下标，`price` 是当天的价格。进入本轮时，`min_price` 保存当天之前的最低买入价，`profit` 表示按该最低价买入、今天卖出的利润，`max_profit` 保存截至目前的最大利润，初始值为 0。

#strong[为什么只记最低价：] 固定今天卖出后，卖出价已经确定。此前任何一天都可以买入，因此此前价格最低的那天能带来最大的利润。每一天都作为卖出日检查一次，就覆盖了所有可能产生最优结果的卖出日。

#strong[更新顺序：] 先用此前最低价计算今天卖出的利润，再更新最大利润，最后把今天的价格纳入最低价比较，供后面的日期使用。这样计算每笔候选交易时，买入日期都严格早于卖出日期。

#strong[逐步推演：] 对于 `[7, 1, 5, 3, 6, 4]`，用第一天的价格 7 初始化最低价，当天没有更早的买入日。

#table(
  columns: (auto, auto, 1fr, 1fr, 1.25fr),
  table.header([日期], [当天价格], [卖出前的最低价], [今天卖出的利润], [更新后：最低价 / 最大利润]),
  [第 1 天], [7], [—], [—], [7 / 0],
  [第 2 天], [1], [7], [−6], [1 / 0],
  [第 3 天], [5], [1], [4], [1 / 4],
  [第 4 天], [3], [1], [2], [1 / 4],
  [第 5 天], [6], [1], [5], [1 / 5],
  [第 6 天], [4], [1], [3], [1 / 5],
)

最大利润为 5，对应第 2 天买入、第 5 天卖出。如果价格一直下降，例如 `[7, 6, 4, 3, 1]`，每天卖出都亏损，最大利润保持为 0。

```python
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        min_price = prices[0]
        max_profit = 0

        for i in range(1, len(prices)):
            price = prices[i]
            profit = price - min_price
            max_profit = max(max_profit, profit)

            # 今天的价格只作为后续日期的买入候选
            min_price = min(min_price, price)

        return max_profit
```

#strong[复杂度：] 时间 O(n)，额外空间 O(1)。使用下标从第二天开始遍历，避免用 `prices[1:]` 创建一个切片副本。

#strong[记忆骨架：] 首日初始化最低价 → 用此前最低价计算今天卖出的利润 → 更新最大利润 → 更新最低价。

#jump("toc", "↑ 返回目录")

= #text("动态规划")

== #text("300. 最长递增子序列（LeetCode 300）") <lc300>

#strong[方法：] 一维动态规划 → 贪心 + 二分查找

#strong[题目要求：] 给定整数数组 `nums`，返回最长严格递增子序列的长度。可以跳过元素，但必须保留原顺序。比如 `[2, 3, 7, 18]` 可以从 `[10, 9, 2, 5, 3, 7, 101, 18]` 中按顺序选出，长度为 4。

=== #text("一、先用动态规划理解")

#strong[变量定义：] `i` 是当前考虑的下标，`j` 是它前面的下标。`dp[i]` 表示必须以 `nums[i]` 结尾的最长递增子序列长度。每个元素都能单独形成一条子序列，所以初值都是 1。

#strong[状态转移：] 固定最后一个数 `nums[i]`，检查前面哪些数可以接到它前面。只有 `nums[j] < nums[i]` 时，才可以在以 `nums[j]` 结尾的最优子序列后接上 `nums[i]`，得到长度 `dp[j] + 1`。试过所有可接的 `j` 后取最大值。整条最长子序列可能结束在任意位置，所以最后取 `max(dp)`。

以 `[2, 5, 3, 7]` 为例，以 2 结尾的长度是 1。5 可以接在 2 后面，长度是 2。3 也可以接在 2 后面，长度是 2。到 7 时，接在 5 或 3 后都能得到长度 3，因此 `dp = [1, 2, 2, 3]`。

```python
class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        dp = [1] * len(nums)
        for i in range(len(nums)):
            for j in range(i):
                if nums[j] < nums[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        return max(dp, default=0)
```

#strong[复杂度：] 设 n 为数组长度，时间 O(n²)，额外空间 O(n)。

=== #text("二、为什么可以优化成贪心 + 二分")

#strong[变量定义：] `x` 是本轮读到的数字。`tails[k]` 保存已经扫描过的数字中，长度为 `k + 1` 的严格递增子序列能取得的最小尾值。因此 `len(tails)` 就是当前能达到的最大长度。不同位置的尾值可以来自不同子序列。

#strong[为什么选更小的尾值：] 对同样长度的两条子序列，尾值越小，后面越容易接上新数字。比如长度都为 2 时，尾值 3 比尾值 5 更有用。后面遇到 4，尾值 3 可以接上它，尾值 5 则接不上。因此同一长度只需记住最小尾值。

#strong[为什么能二分：] 任取一条长度为 `k + 2`、尾值为 `tails[k + 1]` 的子序列。去掉末尾后，剩下长度为 `k + 1` 的子序列，其尾值严格小于 `tails[k + 1]`。`tails[k]` 是这个长度的最小尾值，所以也严格小于 `tails[k + 1]`。因此 `tails` 始终严格递增。

#strong[更新规则：] 找到第一个大于等于 `x` 的位置。它前面的尾值都小于 `x`，所以 `x` 可以接在对应的较短子序列后，并成为当前长度的新尾值。若所有尾值都小于 `x`，就追加，最长长度加 1。相等时替换原位，避免把相同数字算作严格递增。

#strong[逐步推演：] 用 `[10, 9, 2, 5, 3, 7, 101, 18]` 从空数组开始。表中的位置从 0 开始。

#table(
  columns: (auto, 1fr, 1.5fr, 1.6fr),
  table.header([本轮 x], [二分位置], [本轮操作], [更新后的 tails]),
  [10], [0], [追加 10], [`[10]`],
  [9], [0], [用 9 替换 10], [`[9]`],
  [2], [0], [用 2 替换 9], [`[2]`],
  [5], [1], [追加 5], [`[2, 5]`],
  [3], [1], [用 3 替换 5], [`[2, 3]`],
  [7], [2], [追加 7], [`[2, 3, 7]`],
  [101], [3], [追加 101], [`[2, 3, 7, 101]`],
  [18], [3], [用 18 替换 101], [`[2, 3, 7, 18]`],
)

最终长度为 4。这个例子里 `tails` 恰好也是一条有效子序列。换成 `[2, 3, 4, 1]`，最后得到 `[1, 3, 4]`，其中 1 实际出现在 4 后面。这个数组记录的是各个长度的最小尾值，正确答案仍是长度 3。

#strong[二分边界：] `left`、`right` 表示左闭右开的搜索区间，`mid` 是中点。若 `tails[mid] < x`，目标位置在右半边。否则保留中点作为候选，让右边界移到 `mid`。结束时 `left` 就是替换或追加的位置。

```python
class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        tails = []

        for x in nums:
            left, right = 0, len(tails)
            while left < right:
                mid = (left + right) // 2
                if tails[mid] < x:
                    left = mid + 1
                else:
                    right = mid

            if left == len(tails):
                tails.append(x)
            else:
                tails[left] = x

        return len(tails)
```

#strong[复杂度：] 时间 O(n log n)，每个数做一次二分。额外空间 O(n)，最多维护 n 个尾值。

#strong[记忆骨架：] DP 固定结尾，枚举前面能接谁 → 同样长度只留最小尾值 → 二分找第一个大于等于当前数的位置 → 能扩就追加，否则替换 → 返回长度。

#jump("toc", "↑ 返回目录")

= #text("多维动态规划")

== #text("5. 最长回文子串（LeetCode 5）") <lc5>

#strong[#text("方法：")]#text(" 中心扩展法")

#strong[#text("题目要求：")]#text(" 给定字符串 ")#raw("s")#text("，找到其中最长的回文子串。回文字符串正着读和反着读相同。")

#strong[#text("具体例子：")]#text(" ")#raw("s = \"babad\"")#text("，返回 ")#raw("\"bab\"")#text("；")#raw("\"aba\"")#text(" 也是正确答案。")

#strong[#text("核心原理：")]#text(" 回文串的中心可能是一个字符，也可能是两个字符之间的空隙。因此遍历每个位置，分别把它当作单字符中心 ")#raw("(i, i)")#text(" 和双字符中心 ")#raw("(i, i + 1)")#text("。每次从中心向两边扩展，只要左右字符相同且没有越界，就继续扩展，并记录更长的回文串。")

#text("奇数长度的回文串以一个字符为中心，例如 ")#raw("\"bab\"")#text("；偶数长度的回文串以两个字符之间的空隙为中心，例如 ")#raw("\"cbbd\"")#text(" 中的 ")#raw("\"bb\"")#text("。两种中心都检查，才能覆盖所有情况。")

#strong[#text("完整代码：")]

```python
class Solution:
    def longestPalindrome(self, s: str) -> str:
        result = ""
        for i in range(len(s)):
            # 情况一：奇数长度，以 s[i] 为中心
            left = right = i
            while left >= 0 and right < len(s) and s[left] == s[right]:
                if right - left + 1 > len(result):
                    result = s[left:right + 1]
                left -= 1
                right += 1

            # 情况二：偶数长度，以 i 和 i+1 之间为中心
            left, right = i, i + 1
            while left >= 0 and right < len(s) and s[left] == s[right]:
                if right - left + 1 > len(result):
                    result = s[left:right + 1]
                left -= 1
                right += 1
        return result
```

#strong[#text("复杂度：")]#text(" 时间 O(n²)，额外空间 O(1)，不计返回的字符串。")

#strong[#text("记忆骨架：")]#text(" 遍历所有中心 → 分别检查奇数和偶数回文 → 左右扩展 → 更新最长回文串。")

#jump("toc", "↑ 返回目录")

== #text("1143. 最长公共子序列（LeetCode 1143）") <lc1143>

#strong[方法：] 二维前缀动态规划

#strong[题目要求：] 给定两个字符串，返回最长公共子序列的长度。子序列允许跳过字符，保留原有顺序。例如 `"ace"` 是 `"abcde"` 的子序列，长度为 3。`"aec"` 改变了原来的顺序。子串则要求字符连续。

#strong[变量定义：] `m`、`n` 是 `text1`、`text2` 的长度。`dp[i][j]` 表示两个字符串分别取前 `i`、`j` 个字符时，最长公共子序列的长度。两个前缀的末尾字符分别是 `text1[i - 1]` 和 `text2[j - 1]`。第 0 行和第 0 列表示至少一个前缀为空，初值都是 0。

#strong[为什么字符相同看左上角：] 例如 `"abc"` 和 `"ac"` 都以 `c` 结尾。先取 `"ab"` 和 `"a"` 的最长公共子序列，再把 `c` 接到末尾，就得到一个长度为 `dp[i - 1][j - 1] + 1` 的公共子序列。这个长度也是上限，因为从任意一条公共子序列中删去最后一个字符，剩下的部分必然能在两个去掉末尾的前缀里找到。

#strong[为什么字符不同看上方和左方：] 例如 `"ab"` 和 `"ac"` 的末尾分别是 `b` 和 `c`。如果两个末尾都被选中，它们就得是同一条公共子序列的最后一个字符，所以至少要舍弃一个。舍弃 `b` 看上方 `dp[i - 1][j]`，舍弃 `c` 看左方 `dp[i][j - 1]`，两种情况取较大值。

#strong[逐格推演：] 用 `"abcde"` 和 `"ace"` 填表。行、列展示的是前缀，`""` 表示空前缀。从左到右、从上到下填写。

#table(
  columns: (1.2fr, 1fr, 1fr, 1fr, 1fr),
  align: center,
  table.header([前缀], [`""`], [`a`], [`ac`], [`ace`]),
  [`""`], [0], [0], [0], [0],
  [`a`], [0], [1], [1], [1],
  [`ab`], [0], [1], [1], [1],
  [`abc`], [0], [1], [2], [2],
  [`abcd`], [0], [1], [2], [2],
  [`abcde`], [0], [1], [2], [*3*],
)

- `dp[1][1]`：两个末尾都是 `a`，左上角 0 加 1，得到 1。
- `dp[2][2]`：`b` 和 `c` 不同，上方和左方都是 1，取最大值得 1。
- `dp[3][2]`：两个末尾都是 `c`，左上角的 1 对应 `"ab"` 和 `"a"`，加 1 得 2。
- `dp[5][3]`：两个末尾都是 `e`，左上角的 2 加 1 得 3，返回这个格子。

```python
class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        m, n = len(text1), len(text2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i - 1] == text2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp[m][n]
```

#strong[复杂度：] 时间 O(mn)，额外空间 O(mn)。每个格子只做一次常数时间的比较和更新。

#strong[记忆骨架：] 定义两个前缀 → 空前缀填 0 → 末尾相同看左上加 1 → 末尾不同取上方和左方最大值 → 返回右下角。

#jump("toc", "↑ 返回目录")

== #text("72. 编辑距离（LeetCode 72）") <lc72>

#strong[方法：] 二维前缀动态规划

#strong[题目要求：] 给定 `word1` 和 `word2`，每次可以插入、删除或替换一个字符，求从 `word1` 变成 `word2` 的最少操作次数。例如 `horse → rorse → rose → ros`，依次替换 h、删除第二个 r、删除 e，共 3 次。

#strong[变量定义：] `m`、`n` 分别是两个字符串的长度。`i`、`j` 分别表示取两个字符串的前多少个字符。`dp[i][j]` 表示把 `word1` 的前 `i` 个字符变成 `word2` 的前 `j` 个字符的最少操作次数。例如 `dp[2][2]` 对应 `ho → ro`，替换一次就够，所以等于 1。前 `i` 个字符的最后一位下标是 `i - 1`。

#strong[初始化：] 从空串变到有 `j` 个字符的目标前缀，需要插入 `j` 次，所以 `dp[0][j] = j`。从有 `i` 个字符的原前缀变到空串，需要删除 `i` 次，所以 `dp[i][0] = i`。表格要留出空前缀的行和列，共 `m + 1` 行、`n + 1` 列。

#strong[为什么看这三个格子：] 如果两个前缀末尾相同，就把这两个字符保留下来，继承左上角 `dp[i-1][j-1]`。例如 `ho → ro` 末尾都是 o，只需处理 `h → r`。如果末尾不同，比较下列三种代价。

#table(
  columns: (auto, auto, 1fr),
  table.header([操作], [参考格子], [这个格子代表什么]),
  [删除], [`dp[i-1][j]`], [删去原前缀的最后一个字符，剩下的原前缀仍需匹配整个目标前缀。],
  [插入], [`dp[i][j-1]`], [先匹配目标前缀的前 `j-1` 个字符，再补上最后一个目标字符。],
  [替换], [`dp[i-1][j-1]`], [先匹配双方去掉末尾后的前缀，再把原前缀末尾换成目标末尾。],
)

三种操作各付出一次，取对应格子的最小值再加 1。表从左到右、从上到下填，所需的三个格子都已经算过。

#strong[逐格推演：] 从 `horse → ros` 的边界开始。空行写 0、1、2、3，空列写 0、1、2、3、4、5。下表按实际顺序计算 15 个内部格子。每个 `min` 中依次列出上、左、左上的值，相同时直接写继承的左上值。

#table(
  columns: (auto, 1fr, 1fr, 1fr),
  table.header([原前缀], [目标 r], [目标 ro], [目标 ros]),
  [h], [`1 + min(1,1,0) = 1`], [`1 + min(2,1,1) = 2`], [`1 + min(3,2,2) = 3`],
  [ho], [`1 + min(1,2,1) = 2`], [同为 o，继承 1], [`1 + min(3,1,2) = 2`],
  [hor], [同为 r，继承 2], [`1 + min(1,2,2) = 2`], [`1 + min(2,2,1) = 2`],
  [hors], [`1 + min(2,4,3) = 3`], [`1 + min(2,3,2) = 3`], [同为 s，继承 2],
  [horse], [`1 + min(3,5,4) = 4`], [`1 + min(3,4,3) = 4`], [`1 + min(2,4,3) = 3`],
)

最后一格比较 e 和 s。删 e 的代价是 `hors → ros` 的 2 次加 1，得到 3。先把 `horse` 变成 `ro` 再插入 s，代价是 4 加 1。把 e 替换成 s，代价是 `hors → ro` 的 3 次加 1。三个方案取最小值，返回 `dp[5][3] = 3`。

#strong[完整代码：]

```python
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        m, n = len(word1), len(word2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if word1[i - 1] == word2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],      # 删除
                        dp[i][j - 1],      # 插入
                        dp[i - 1][j - 1],  # 替换
                    )

        return dp[m][n]
```

#strong[复杂度：] 时间和额外空间均为 O((m + 1)(n + 1))，通常写作 O(mn)。时间主要花在逐格计算，空间用于保存二维表。

#strong[记忆骨架：] 定义两个前缀的最小编辑距离 → 初始化空前缀 → 末尾相同继承左上 → 末尾不同从上、左、左上取最小值加 1 → 返回右下角。

#jump("toc", "↑ 返回目录")
