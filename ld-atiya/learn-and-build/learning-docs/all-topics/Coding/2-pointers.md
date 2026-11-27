# Two Pointers

The two-pointer technique uses two pointers that start at **opposite ends** of
an array and gradually move toward each other, shrinking the search space one
step at a time.

**In this page, we'll cover:**

- A simple problem that illustrates the motivation behind the technique.
- The types of problem for which you should consider using it.
- The variations you'll meet in interviews.

---

## Table of Contents

1. [Problem: Two Sum](#problem-two-sum)
   - [The Brute Force Approach](#the-brute-force-approach)
   - [The Key Insight](#the-key-insight)
   - [Walking Through It](#walking-through-it)
   - [The Code](#the-code)
2. [Summary](#summary)
3. [Variations of the Technique](#variations-of-the-technique)
4. [When Do I Use This?](#when-do-i-use-this)
5. [Cheat Sheet](#cheat-sheet)

---

## Problem: Two Sum

> **Description**
>
> Given a **sorted** array of integers `nums`, determine if there exists a pair
> of numbers that sum to a given `target`.
>
> ```
> Input:  nums = [1,3,4,6,8,10,13], target = 13
> Output: True   (3 + 10 = 13)
>
> Input:  nums = [1,3,4,6,8,10,13], target = 6
> Output: False
> ```

### The Brute Force Approach

The obvious solution is to try every pair:

```python
def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return True
    return False
```

This works, but it examines every one of the `n(n-1)/2` pairs — `O(n²)` time.
Notice that it completely ignores the fact that the array is **sorted**. That
unused information is exactly what we're about to exploit.

### The Key Insight

Place one pointer at each end of the array. These two pointers represent the
pair we are currently considering, and their sum tells us which direction to
move:

```
              sum vs. target
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
  too SMALL       EQUAL          too BIG
      │              │              │
      ▼              ▼              ▼
  move left      found it!      move right
  pointer  ──▶                 ◀── pointer
  (grow sum)                    (shrink sum)
```

Why is this safe? Because the array is sorted:

- If `nums[left] + nums[right] < target`, then `nums[left]` paired with
  *anything* to the left of `right` is even smaller. `nums[left]` can never
  work — **discard the whole row** and move `left` right.
- If `nums[left] + nums[right] > target`, then `nums[right]` paired with
  *anything* to the right of `left` is even bigger. `nums[right]` can never
  work — **discard it** and move `right` left.

Each comparison eliminates an entire set of candidate pairs rather than a single
one. That is what turns `O(n²)` into `O(n)`.

### Walking Through It

`nums = [1, 3, 4, 6, 8, 10, 13]`, `target = 13`

```
Step 1:  1 + 13 = 14  >  13   → too big,   move right ◀──
        ┌───┬───┬───┬───┬───┬────┬────┐
        │ 1 │ 3 │ 4 │ 6 │ 8 │ 10 │ 13 │
        └───┴───┴───┴───┴───┴────┴────┘
          ▲                        ▲
        left                     right

Step 2:  1 + 10 = 11  <  13   → too small, move left ──▶
        ┌───┬───┬───┬───┬───┬────┬────┐
        │ 1 │ 3 │ 4 │ 6 │ 8 │ 10 │ 13 │
        └───┴───┴───┴───┴───┴────┴────┘
          ▲                   ▲
        left                right

Step 3:  3 + 10 = 13  =  13   → found it!  ✓
        ┌───┬───┬───┬───┬───┬────┬────┐
        │ 1 │ 3 │ 4 │ 6 │ 8 │ 10 │ 13 │
        └───┴───┴───┴───┴───┴────┴────┘
              ▲             ▲
            left          right
```

Three comparisons instead of twenty-one.

And the failing case, `target = 6`, where the pointers meet without a match:

```
1 + 13 = 14  > 6   → move right ◀──
1 + 10 = 11  > 6   → move right ◀──
1 +  8 =  9  > 6   → move right ◀──
1 +  6 =  7  > 6   → move right ◀──
1 +  4 =  5  < 6   → move left  ──▶
3 +  4 =  7  > 6   → move right ◀──
                     left == right → stop → False
```

### The Code

```python
def twoSum(nums, target):
    left = 0
    right = len(nums) - 1

    while left < right:
        current = nums[left] + nums[right]

        if current == target:
            return True
        elif current < target:
            left += 1       # need a bigger sum
        else:
            right -= 1      # need a smaller sum

    return False            # pointers met, no pair exists
```

> **Why `left < right` and not `left <= right`?** A pair needs two *distinct*
> elements. Once the pointers meet they'd be reusing the same number, so we stop.

**Complexity Analysis**

| | |
| --- | --- |
| **Time** | `O(n)` — each iteration moves a pointer inward, so the pointers travel at most `n` steps combined. |
| **Space** | `O(1)` — two integer indices, regardless of input size. |

Compared to brute force:

| Approach | Time | Space |
| -------- | ---- | ----- |
| Nested loops | `O(n²)` | `O(1)` |
| Hash set | `O(n)` | `O(n)` |
| **Two pointers** (sorted input) | **`O(n)`** | **`O(1)`** |

---

## Summary

- The two-pointer technique **leverages the fact that the input array is
  sorted** to reduce the number of pairs we consider from `O(n²)` down to `O(n)`.
- The two pointers start at opposite ends of the array, and represent the pair
  of numbers we are currently considering.
- We repeatedly compare the sum of the current pair to the target, and move a
  pointer in a way that **eliminates unnecessary pairs** from our search.

---

## Variations of the Technique

"Two pointers" is a family of patterns. The same idea of two indices moving with
purpose shows up in three shapes:

### Converging (opposite ends)

The pattern above — pointers start at both ends and move toward each other.

```
 ──▶                          ◀──
┌───┬───┬───┬───┬───┬───┬───┐
│   │   │   │   │   │   │   │
└───┴───┴───┴───┴───┴───┴───┘
  ▲                       ▲
left                    right
```

Used for: pair sums in sorted arrays, palindrome checks, container-with-most-water,
reversing in place.

```python
def isPalindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
```

### Same-direction (fast / slow)

Both pointers start at the front and move forward at different rates. One
pointer scans (`fast`), the other marks where the next kept element belongs
(`slow`).

```
┌───┬───┬───┬───┬───┬───┬───┐
│   │   │   │   │   │   │   │
└───┴───┴───┴───┴───┴───┴───┘
      ▲           ▲
    slow        fast
   (write)      (read)
```

Used for: removing duplicates in place, partitioning, moving zeroes to the end.

```python
def removeDuplicates(nums):
    if not nums:
        return 0
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1        # length of the deduplicated prefix
```

> This is the same fast/slow idea used on linked lists to find the middle node
> and detect cycles.

### Two arrays

One pointer per input, each advancing independently — the merge step of merge
sort, or merging two sorted lists.

```
A:  ┌───┬───┬───┐          B:  ┌───┬───┬───┐
    │ 1 │ 3 │ 5 │              │ 2 │ 4 │ 6 │
    └───┴───┴───┘              └───┴───┴───┘
      ▲                          ▲
      i                          j
      └────── take the smaller ──┘
```

---

## When Do I Use This?

Consider the two-pointer technique for questions that involve **searching for a
pair (or more) of items in an array that meet a certain criteria**.

Examples:

- Finding a pair of items that sum to a given target in an array.
- Finding a triplet of items that sum to `0` in a given array.
- Finding the maximum amount of water that can be held between two array items
  representing wall heights.

You should suspect a two-pointer approach when you notice one or more of these
signals:

### 🔹 Input Characteristics

- Array or string
- **Sorted array** (very strong signal)
- Need to process elements from both ends
- Need to compare pairs, subarrays, or characters

### 🔹 Problem Goals

- Find pair / triplet with condition (sum, difference, equality)
- Remove duplicates in-place
- Reverse / check palindrome
- Partition array (evens & odds, colors, etc.)

### 🔹 Constraints Hint

- "Do it in `O(n)` time"
- "In-place" or "constant extra space"
- Avoid nested loops (brute force is `O(n²)`)

> **If the array isn't sorted**, sorting it first costs `O(n log n)` — still
> better than `O(n²)`, and often the intended solution. But if the problem needs
> the *original indices*, sorting destroys them; use a hash map instead.

---

## Cheat Sheet

| Variation | Pointer setup | Typical use |
| --------- | ------------- | ----------- |
| Converging | `left = 0`, `right = n-1` | Pair sums, palindromes, max area |
| Fast / slow | Both at `0`, different speeds | In-place removal, partitioning |
| Two arrays | One index per array | Merging sorted inputs |

**Pitfalls to check before you submit:**

- [ ] Is the array actually sorted? (Converging pointers depend on it.)
- [ ] `while left < right` — not `<=` — when the pair must be two distinct elements.
- [ ] Does every branch move a pointer? A branch that doesn't means an infinite loop.
- [ ] Handled the empty array and single-element array?
- [ ] Skipping duplicates where the problem requires unique pairs (e.g. 3Sum)?

### Practice Problems

| # | Problem | Variation |
| - | ------- | --------- |
| 167 | Two Sum II — Input Array Is Sorted | Converging |
| 125 | Valid Palindrome | Converging |
| 11 | Container With Most Water | Converging |
| 15 | 3Sum | Sort + converging inside a loop |
| 26 | Remove Duplicates from Sorted Array | Fast / slow |
| 283 | Move Zeroes | Fast / slow |
| 88 | Merge Sorted Array | Two arrays |
