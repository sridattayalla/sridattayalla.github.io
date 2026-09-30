# Toy attention worked example (verified numerically)

Fact sheet for: attention page. All numbers below were computed with numpy (script in repo history, re-verified).

## Setup

- 4 tokens: "the", "cat", "ate", "it" (a pronoun whose referent is "cat").
- d_model = d_k = d_v = 2 (paper-computable).
- Hand-picked embedding matrix E (4x2):

```
        dim0 dim1
the      0    1
cat      2    0
ate      1    1
it       1    0
```

- W_q = [[2,0],[0,1]] (scales the first coordinate by 2), W_k = W_v = identity (2x2).

## Step 1: Q, K, V = E @ W_q, E @ W_k, E @ W_v

```
Q = [[0,1],   K = [[0,1],   V = [[0,1],
     [4,0],        [2,0],        [2,0],
     [2,1],        [1,1],        [1,1],
     [2,0]]        [1,0]]        [1,0]]
```

## Step 2: scaled scores S = Q @ K^T / sqrt(2)

```
S =
 the [ 0.707  0.     0.707  0.   ]
 cat [ 0.     5.657  2.828  2.828]
 ate [ 0.707  2.828  2.121  1.414]
 it  [ 0.     2.828  1.414  1.414]
```

- (Unscaled it-row dot products are [0, 4, 2, 2]; the 1/sqrt(d_k)=1/sqrt(2) scaling divides each.)

## Step 3: causal mask (upper triangle set to -inf), then row softmax

```
A =
 the [ 1.     0.     0.     0.   ]
 cat [ 0.003  0.997  0.     0.   ]
 ate [ 0.074  0.620  0.306  0.   ]
 it  [ 0.038  0.647  0.157  0.157]
```

- Row "cat" can only see "the" and "cat" (positions 1-2); columns 3-4 are masked to exactly 0.
- Row "it" (the pronoun) puts 0.647 on "cat" — it found its referent. Hand check of the it-row softmax with max subtraction: scores [0, 2.828, 1.414, 1.414]; subtract max (2.828): [−2.828, 0, −1.414, −1.414]; exp: [0.059, 1, 0.243, 0.243]; sum 1.545; probs [0.038, 0.647, 0.157, 0.157]. Matches.

## Step 4: output = A @ V

```
out =
 the [ 0.     1.   ]
 cat [ 1.993  0.003]
 ate [ 1.546  0.380 ]
 it  [ 1.609  0.196]
```

- The output vector for "it" is [1.609, 0.196] — pulled from its input embedding [1, 0] toward "cat"'s value [2, 0]. Its representation now carries cat-ness, which later layers (and the output projection) can use to predict e.g. "purred".

## Complexity (per head, per layer)

- Scores: n x d_k times d_k x n = O(n^2 * d_k) multiply-adds. Memory for the score matrix: n^2 (this is the quadratic term).
- Output: n x n times n x d_v = O(n^2 * d_v).
- Total attention FLOPs per head per layer ~ O(n^2 * d), vs. per-token FFN/linear work O(n * d^2). Quadratic in sequence length n, linear in d.

## Source IDs

- [toy-attention] this file; recomputed by tools (numpy script embedded in git history of this repo; also asserted in code/tiny_llm.py test).
- [transformer] arXiv:1706.03762 eq. 1 for the formula, section 3.2.1 for the 1/sqrt(d_k) rationale, Figure 1 for the animal/street/it example.
