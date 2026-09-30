#!/usr/bin/env python3
"""tiny_llm.py — the runnable companion to the LLM Internals site.

Six stages, each printing numbers the site's pages quote:
  1. byte-pair encoding trained on a toy corpus
  2. the toy attention example from research/attention-example.md
  3. one transformer block forward pass (RMSNorm, RoPE, GELU, residuals)
  4. one training step: manual backprop, verified by finite differences
  5. greedy decoding with and without a KV cache, asserted identical
  6. the softmax temperature table for research/inference.md

Run: python3 tiny_llm.py   (numpy is the only dependency)
"""

import collections
import time

import numpy as np

np.set_printoptions(precision=3, suppress=True)

GELU_C = 0.7978845608028654  # sqrt(2/pi)


def softmax(z, axis=-1):
    """Overflow-safe softmax: subtract the row max before exponentiating."""
    z = z - np.max(z, axis=axis, keepdims=True)
    e = np.exp(z)
    return e / np.sum(e, axis=axis, keepdims=True)


def check(name, got, want, atol=6e-4):
    got, want = np.asarray(got, float), np.asarray(want, float)
    ok = np.allclose(got, want, atol=atol)
    print(f'  {name}: {got}  expected {want}  {"ok" if ok else "MISMATCH"}')
    assert ok, name


# ---------------------------------------------------------------- stage 1


def merge_word(word, pair, merged):
    """Replace every adjacent occurrence of `pair` inside `word`."""
    parts, i, out = list(word), 0, []
    while i < len(parts) - 1:
        if (parts[i], parts[i + 1]) == pair:
            out.append(merged)
            i += 2
        else:
            out.append(parts[i])
            i += 1
    if i < len(parts):
        out.append(parts[i])
    return tuple(out)


def train_bpe(corpus, num_merges):
    """Learn merges over characters; '</w>' marks each word end."""
    vocab = collections.Counter()
    for word in corpus.split():
        vocab[tuple(list(word) + ['</w>'])] += 1
    symbols = sorted({s for w in vocab for s in w})
    token_to_id = {s: i for i, s in enumerate(symbols)}
    merges = []
    for _ in range(num_merges):
        pairs = collections.Counter()
        for word, freq in vocab.items():
            for i in range(len(word) - 1):
                pairs[(word[i], word[i + 1])] += freq
        if not pairs:
            break
        pair = pairs.most_common(1)[0][0]
        merged = pair[0] + pair[1]
        merges.append((pair, merged))
        token_to_id[merged] = len(token_to_id)
        refreshed = collections.Counter()
        for word, freq in vocab.items():
            refreshed[merge_word(word, pair, merged)] += freq
        vocab = refreshed
    return merges, token_to_id


def bpe_encode(text, merges, token_to_id):
    """Apply learned merges in order, then map subword pieces to ids."""
    ids = []
    for word in text.split():
        parts = tuple(list(word) + ['</w>'])
        for pair, merged in merges:
            parts = merge_word(parts, pair, merged)
        ids.extend(token_to_id[p] for p in parts)
    return ids


def bpe_decode(ids, id_to_token):
    text = ''.join(id_to_token[i] for i in ids)
    return text.replace('</w>', ' ').strip()


def stage_bpe(merges, token_to_id, id_to_token):
    print('== 1. byte-pair encoding on a toy corpus ==')
    for rank, (pair, merged) in enumerate(merges, start=1):
        print(f'  merge {rank:2d}: {pair[0]!r} + {pair[1]!r} -> {merged!r}')
    print(f'  final vocabulary: {len(token_to_id)} tokens')
    text = 'the cat ate the rat.'
    ids = bpe_encode(text, merges, token_to_id)
    print(f'  encode {text!r}')
    print(f'    ids    {ids}')
    print(f'    pieces {[id_to_token[i] for i in ids]}')
    assert bpe_decode(ids, id_to_token) == text
    print('  decode round-trip: ok')


# ---------------------------------------------------------------- stage 2


def stage_toy_attention():
    print('== 2. toy attention — research/attention-example.md ==')
    E = np.array([[0., 1.], [2., 0.], [1., 1.], [1., 0.]])  # the cat ate it
    Wq = np.array([[2., 0.], [0., 1.]])
    Q, K, V = E @ Wq, E.copy(), E.copy()
    S = Q @ K.T / np.sqrt(2)
    S = np.where(np.tril(np.ones_like(S)) > 0, S, -np.inf)
    A = softmax(S)
    out = A @ V
    print('  scores / sqrt(2), causal-masked:')
    print(S)
    print('  attention weights:')
    print(A)
    print('  outputs:')
    print(out)
    check("weights for 'it'", A[3], [0.038, 0.647, 0.157, 0.157])
    check("output for 'it'", out[3], [1.609, 0.196])
    check("output for 'cat'", out[1], [1.993, 0.003])
    check("output for 'ate'", out[2], [1.546, 0.380])


# ------------------------------------------------------------- stages 3-5


def rmsnorm(x, g, eps=1e-6):
    s = np.mean(x * x, axis=-1, keepdims=True) + eps
    return x / np.sqrt(s) * g


def rmsnorm_backward(x, g, dy, eps=1e-6):
    """Return (dL/dx, dL/dg) given dL/dy for y = x/rms(x) * g."""
    d = x.shape[-1]
    s = np.mean(x * x, axis=-1, keepdims=True) + eps
    rs = np.sqrt(s)
    dr = dy * g
    dot = np.sum(dr * x, axis=-1, keepdims=True)
    dx = dr / rs - x * dot / (d * s * rs)
    dg = np.sum(dy * x / rs, axis=0)
    return dx, dg


def rope(x, positions, inverse=False):
    """Rotate (first-half, second-half) dim pairs by pos * theta."""
    dh = x.shape[-1]
    half = dh // 2
    theta = 10000.0 ** (-2.0 * np.arange(half) / dh)
    ang = positions[:, None].astype(float) * theta[None, :]
    cos, sin = np.cos(ang)[:, None, :], np.sin(ang)[:, None, :]
    if inverse:
        sin = -sin
    x1, x2 = x[..., :half], x[..., half:]
    out = np.empty_like(x)
    out[..., :half] = x1 * cos - x2 * sin
    out[..., half:] = x1 * sin + x2 * cos
    return out


def gelu(x):
    return 0.5 * x * (1.0 + np.tanh(GELU_C * (x + 0.044715 * x ** 3)))


def gelu_grad(x):
    u = GELU_C * (x + 0.044715 * x ** 3)
    t = np.tanh(u)
    du = GELU_C * (1.0 + 3.0 * 0.044715 * x ** 2)
    return 0.5 * (1.0 + t) + 0.5 * x * (1.0 - t * t) * du


def init_params(vocab_size, cfg, seed=7):
    d, f = cfg['d_model'], cfg['d_ff']
    rng = np.random.default_rng(seed)

    def normal(*shape, scale=0.3):
        return rng.normal(0.0, scale, shape)

    return {
        'emb': normal(vocab_size, d, scale=0.5),
        'ln1': np.ones(d), 'ln2': np.ones(d), 'lnf': np.ones(d),
        'Wq': normal(d, d), 'Wk': normal(d, d), 'Wv': normal(d, d),
        'Wo': normal(d, d),
        'W1': normal(d, f), 'b1': np.zeros(f),
        'W2': normal(f, d, scale=0.15), 'b2': np.zeros(d),
        'unemb': normal(d, vocab_size, scale=0.5),
    }


def forward(params, ids, cfg, kv=None):
    """One block; kv carries cached keys/values for incremental decoding."""
    H, d_model = cfg['n_heads'], cfg['d_model']
    dh = d_model // H
    x0 = params['emb'][np.asarray(ids)]
    n = x0.shape[0]
    pos0 = 0 if kv is None else kv['k'].shape[0]
    positions = np.arange(pos0, pos0 + n)

    h1 = rmsnorm(x0, params['ln1'])
    q = rope((h1 @ params['Wq']).reshape(n, H, dh), positions)
    k = rope((h1 @ params['Wk']).reshape(n, H, dh), positions)
    v = (h1 @ params['Wv']).reshape(n, H, dh)
    if kv is not None:
        k = np.concatenate([kv['k'], k], axis=0)
        v = np.concatenate([kv['v'], v], axis=0)

    scores = np.einsum('qhd,khd->hqk', q, k) / np.sqrt(dh)
    if kv is None:
        scores = np.where(np.tril(np.ones((n, n))) > 0, scores, -np.inf)
    A = softmax(scores)
    ctx = np.einsum('hqk,khd->qhd', A, v).reshape(n, d_model)
    x1 = x0 + ctx @ params['Wo']

    h2 = rmsnorm(x1, params['ln2'])
    pre = h2 @ params['W1'] + params['b1']
    act = gelu(pre)
    x2 = x1 + act @ params['W2'] + params['b2']

    hf = rmsnorm(x2, params['lnf'])
    logits = hf @ params['unemb']
    cache = dict(x0=x0, h1=h1, q=q, k=k, v=v, A=A, ctx=ctx, x1=x1, h2=h2,
                 pre=pre, act=act, x2=x2, hf=hf, logits=logits,
                 positions=positions, n=n)
    return logits, cache


def ce_loss(logits, targets):
    """Mean cross-entropy; targets[i] is the token that follows position i."""
    probs = softmax(logits)
    picked = probs[np.arange(len(targets)), targets]
    return float(-np.mean(np.log(picked + 1e-300)))


def loss_of(params, cfg, ids):
    logits, _ = forward(params, ids, cfg)
    return ce_loss(logits[:-1], ids[1:])


def backward(params, cfg, ids, cache):
    """Gradients of the mean next-token cross-entropy w.r.t. every param."""
    P = params
    H, d_model = cfg['n_heads'], cfg['d_model']
    dh = d_model // H
    n = cache['n']
    grads = {name: np.zeros_like(val) for name, val in params.items()}

    dlogits = np.zeros_like(cache['logits'])
    dlogits[:-1] = softmax(cache['logits'][:-1])
    dlogits[:-1][np.arange(n - 1), ids[1:]] -= 1.0
    dlogits[:-1] /= (n - 1)

    grads['unemb'] = cache['hf'].T @ dlogits
    dhf = dlogits @ P['unemb'].T
    dx2, grads['lnf'] = rmsnorm_backward(cache['x2'], P['lnf'], dhf)

    dff = dx2
    dact = dff @ P['W2'].T
    grads['W2'] = cache['act'].T @ dff
    grads['b2'] = np.sum(dff, axis=0)
    dpre = dact * gelu_grad(cache['pre'])
    dh2 = dpre @ P['W1'].T
    grads['W1'] = cache['h2'].T @ dpre
    grads['b1'] = np.sum(dpre, axis=0)
    dx1_branch, grads['ln2'] = rmsnorm_backward(cache['x1'], P['ln2'], dh2)
    dx1 = dx2 + dx1_branch

    dattn = dx1
    dctx = (dattn @ P['Wo'].T).reshape(n, H, dh)
    grads['Wo'] = cache['ctx'].T @ dattn
    A, q, k, v = cache['A'], cache['q'], cache['k'], cache['v']
    dA = np.einsum('qhd,khd->hqk', dctx, v)
    dv = np.einsum('hqk,qhd->khd', A, dctx)
    dS = A * (dA - np.sum(dA * A, axis=-1, keepdims=True))
    dq = rope(np.einsum('hqk,khd->qhd', dS, k) / np.sqrt(dh),
              cache['positions'], inverse=True).reshape(n, d_model)
    dk = rope(np.einsum('hqk,qhd->khd', dS, q) / np.sqrt(dh),
              cache['positions'], inverse=True).reshape(n, d_model)
    dv = dv.reshape(n, d_model)
    grads['Wq'] = cache['h1'].T @ dq
    grads['Wk'] = cache['h1'].T @ dk
    grads['Wv'] = cache['h1'].T @ dv
    dh1 = dq @ P['Wq'].T + dk @ P['Wk'].T + dv @ P['Wv'].T
    dx0_branch, grads['ln1'] = rmsnorm_backward(cache['x0'], P['ln1'], dh1)
    np.add.at(grads['emb'], np.asarray(ids), dx1 + dx0_branch)
    return grads


def stage_model(params, cfg, ids, id_to_token):
    print('== 3. one transformer block, forward pass ==')
    logits, cache = forward(params, ids, cfg)
    print(f'  input pieces: {[id_to_token[i] for i in ids]}')
    print(f'  d_model {cfg["d_model"]}, heads {cfg["n_heads"]}, '
          f'd_ff {cfg["d_ff"]}, vocab {len(params["emb"])}')
    print(f'  logits shape {logits.shape}; argmax after first piece: '
          f'{id_to_token[int(np.argmax(logits[0]))]!r}')
    print(f'  last-position attention weights, head 0: {cache["A"][0, -1]}')


def stage_gradients(params, cfg, ids, lr=0.2):
    print('== 4. training step: manual backprop, finite-difference check ==')
    logits, cache = forward(params, ids, cfg)
    loss = ce_loss(logits[:-1], ids[1:])
    grads = backward(params, cfg, ids, cache)
    rng, h, worst = np.random.default_rng(0), 1e-5, 0.0
    for name, tensor in params.items():
        flat, gflat = tensor.reshape(-1), grads[name].reshape(-1)
        picks = rng.choice(flat.size, size=min(3, flat.size), replace=False)
        w = 0.0
        for idx in picks:
            orig = flat[idx]
            flat[idx] = orig + h
            lp = loss_of(params, cfg, ids)
            flat[idx] = orig - h
            lm = loss_of(params, cfg, ids)
            flat[idx] = orig
            num = (lp - lm) / (2 * h)
            w = max(w, abs(num - gflat[idx]) / (1e-6 + abs(gflat[idx])))
        print(f'  dloss/d{name:6s} worst rel err {w:.2e} '
              f'over {len(picks)} picks')
        worst = max(worst, w)
    assert worst < 1e-3, f'gradient check failed: worst rel err {worst:.2e}'
    print(f'  worst relative error across tensors: {worst:.2e} — verified')
    for name in params:
        params[name] = params[name] - lr * grads[name]
    after = loss_of(params, cfg, ids)
    print(f'  loss {loss:.6f} -> {after:.6f} after one step at lr {lr}')
    assert after < loss, 'loss did not decrease'


def greedy(params, cfg, prompt, steps, use_cache):
    out, kv = list(prompt), None
    for _ in range(steps):
        logits, cache = forward(
            params, out if kv is None else [out[-1]], cfg, kv=kv)
        if use_cache:
            kv = {'k': cache['k'], 'v': cache['v']}
        out.append(int(np.argmax(logits[-1])))
    return out


def stage_decode(params, cfg, prompt, steps=10):
    print('== 5. greedy decoding, with and without a KV cache ==')
    t0 = time.perf_counter()
    seq_full = greedy(params, cfg, prompt, steps, use_cache=False)
    t1 = time.perf_counter()
    seq_cache = greedy(params, cfg, prompt, steps, use_cache=True)
    t2 = time.perf_counter()
    assert seq_full == seq_cache, 'cached decode diverged from full recompute'
    p = len(prompt)
    print(f'  prompt {p} pieces, {steps} generated')
    print(f'  full recompute: {sum(p + i for i in range(steps))} '
          f'token-forwards, {1e3 * (t1 - t0):.2f} ms')
    print(f'  kv cache:       {p + steps - 1} '
          f'token-forwards, {1e3 * (t2 - t1):.2f} ms')
    print(f'  identical output: {seq_full == seq_cache}')
    print(f'  generated ids: {seq_full[p:]}')


def stage_temperature():
    print('== 6. softmax temperature — numbers for research/inference.md ==')
    z = np.array([2.0, 1.0, 0.5, -1.0])
    for T in (0.5, 1.0, 2.0):
        probs = softmax(z / T)
        print(f'  T = {T}: [{", ".join(f"{p:.3f}" for p in probs)}]')


def main():
    corpus = ('the cat sat on the mat. '
              'the cat ate the rat. '
              'the rat ate the cat.')
    merges, token_to_id = train_bpe(corpus, 12)
    id_to_token = {i: t for t, i in token_to_id.items()}
    stage_bpe(merges, token_to_id, id_to_token)
    stage_toy_attention()
    cfg = {'d_model': 16, 'n_heads': 2, 'd_ff': 64}
    ids = bpe_encode('the cat ate the rat.', merges, token_to_id)
    params = init_params(len(token_to_id), cfg)
    stage_model(params, cfg, ids, id_to_token)
    stage_gradients(params, cfg, ids)
    stage_decode(params, cfg, ids[:3])
    stage_temperature()
    print('all stages passed')


if __name__ == '__main__':
    main()
