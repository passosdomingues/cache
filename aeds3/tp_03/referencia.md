
**Correctness.** In a call of BMSSP, let \(\widetilde{U}\) denote the set that contains all vertices \(v\) with \(d(v)< B\) and the shortest path to \(v\) visits some vertex in \(S\). Then BMSSP should return \(U = \widetilde{U}\) in a successful execution, or \(U = \{u\in \widetilde{U}:d(u)< B^{\prime}\}\) in a partial execution, with all vertices in \(U\) complete.

In the base case where \(l = 0\), \(S\) contains only one vertex \(x\), a Dijkstra-like algorithm starting from \(x\) completes the task.

Otherwise we first shrink \(S\) to a smaller set of pivots \(P\) to insert into \(\mathcal{D}\), with some vertices complete and added into \(W\). Lemma 3.2 ensures that the shortest path of any remaining incomplete vertex \(v\) visits some complete vertex in \(\mathcal{D}\). For any bound \(B_i\leq B\), if \(d(v)< B_i\), the shortest path to \(v\) must also visit some complete vertex \(u\in \mathcal{D}\) with \(d(u)< B_i\). Therefore we can call subprocedure BMSSP on \(B_i\) and \(S_i\).

By inductive hypothesis, each time a recursive call on Line 11 of Algorithm 3 returns, vertices in \(U_i\) are complete. After the algorithm relaxes edges from \(u\in U_i\) and inserts all the updated out-neighbors \(x\) with \(\widehat{d} [x]\in [B_i^{\prime},B)\) into \(\mathcal{D}\), once again any remaining incomplete vertex \(v\) now visits some complete vertex in \(\mathcal{D}\).

Finally, with the complete vertices in \(W\) added, \(U\) contains all vertices required and all these vertices are complete.

**Running time.** The running time is dominated by calls of FindPivots and the overheads inside the data structures \(\mathcal{D}\). By (4) and (5), the running time of FindPivots procedure at node \(x\) is bounded by \(O(|U_x|k)\) so the total running time over all nodes on one depth of \(\mathcal{T}\) is \(O(nk)\). Summing over all depths we get \(O(nk\cdot (\log n) / t) = O(n\log^{2 / 3}n)\).

For the data structure \(\mathcal{D}\) in a call of BMSSP, the total running time is dominated by Insert and Batch Prepend operations. We analyze the running time as follows.

- Vertices in \(P\) can be added to \(\mathcal{D}\) on Line 6. Since \(|P_x| = O(|U_x| / k)\), the total time for nodes of one depth of \(\mathcal{T}\) is \(O(n / k\cdot (t + \log k)) = O(n t / k)\). Summing over all depths we get \(O((n\log n) / k) = O(n\log^{2 / 3}n)\).
- Some vertices already pulled to \(S_i\) can be added back to \(\mathcal{D}\) through BatchPrepend on Line 21. Here we know in every iteration \(i\), \(|S_i|\leq |U_i|\), so the total time for adding back is bounded by \(\sum_{x\in \mathcal{T}}|U_x| \cdot \log k = O(n\log k\cdot (\log n) / t) = O(n\cdot \log^{1 / 3}n\cdot \log \log n)\).
- A vertex \(v\) can be inserted to \(\mathcal{D}\) through edge \((u,v)\) directly on Line 18 if \(B_i\leq d(u) + w_{uv}< B\) or through \(K\) as on Line 20 if \(B_i^{\prime}\leq d(u) + w_{uv}< B_i\). (Note that \(u\in U_i\) is already complete.) Every edge \((u,v)\) can only be relaxed once in each level by (6), but it can be relaxed in multiple levels in an ancestor-descendant path of the recursion tree \(\mathcal{T}\). (Note that the condition on Line 15 is \(\widehat{d} [u] + w_{uv}\leq \widehat{d} [v]\).) However, we can show every edge \((u,v)\) can only lead to \(v\) be directly inserted to \(\mathcal{D}\) by the Insert operation on one level.
   - It can be easily seen that if \(y\) is a descendant of \(x\) in the recursion tree \(\mathcal{T}\), \(B_y\leq B_x\).
   - If \((u,v)\) leads \(v\) to be directly inserted to \(\mathcal{D}\) on Line 18, then \(d(u) + w_{uv}\geq B_i\). Since \(u\in U_i\), for every descendant \(y\) of the current call in the recursion tree \(\mathcal{T}\) satisfying \(u\in U_y\), we have \(B_y\leq B_i\leq d(u) + w_{uv}\), so \(v\) will not be added to \(\mathcal{D}\) through \((u,v)\) in any way in lower levels.
- Since every edge \((u,v)\) can only lead \(v\) to be directly inserted to \(\mathcal{D}\) by the Insert operation once in the algorithm, the total time is \(O(m(\log k + t)) = O(m\log^{2 / 3}n)\). The time for all edges \((u,v)\) leading \(v\) to be inserted to \(\mathcal{D}\) through \(K\) in one level is \(O(m\log k)\), and in total is \(O(m\log k\cdot (\log n) / t) = O(m\cdot \log^{1 / 3}n\cdot \log \log n)\).

### 3.3 Correctness Analysis

To present the correctness more accurately and compactly, we introduce several notations on the "shortest path tree". Due to the uniqueness of shortest paths, the shortest path tree \(T\) rooted at the source \(s\) can be constructed unambiguously. Define \(T(u)\) as the subtree rooted at \(u\) according to \(d(\cdot)\). An immediate observation is that the shortest path to \(v\) passes through \(u\) if and only if \(v\) is in the subtree rooted at \(u\). For a vertex set \(S\), define \(T(S) = \bigcup_{v\in S} T(v)\), namely the union of the subtrees of \(T(s)\) rooted at vertices in \(S\), or equivalently, the set of vertices whose shortest paths pass through some vertex in \(S\). For a set of vertices \(S \subseteq V\), denote \(S^* = \{v \in S : v \text{ is complete}\}\). Then \(T(S^*) = \bigcup_{v\in S^*} T(v)\) is the union of subtrees of \(T(s)\) rooted at \(S^*\), or the set of vertices whose shortest paths pass through some complete vertex in \(S\). Obviously, \(T(S^*) \subseteq T(S)\). Note that \(T(S^*)\) is sensitive to the progress of the algorithm while \(T(S)\) is a fixed set. Another observation is that, a complete vertex would remain complete, so \(S^*\) and \(T(S^*)\) never lose a member.

For a bound \(B\), denote \(T_{<B}(S) = \{v \in T(S) : d(v) < B\}\). Also note that \(T_{<B}(S)\) coincides with \(\widetilde{U}\) mentioned above. For an interval \([b, B)\), denote \(T_{[b,B)}(S) = \{v \in T(S) : d(v) \in [b, B)\}\).

**Lemma 3.6 (Pull Minimum).** Suppose every incomplete vertex \(v\) with \(d(v) < B\) is in \(T(S^*)\). Suppose we split \(S\) into \(X = \{x \in S : \widehat{d}[x] < B\}\) and \(Y = \{x \in S : \widehat{d}[x] \geq B\}\) for some \(B < B\). Then every incomplete vertex \(v\) with \(d(v) < B\) is in \(T(X^*)\). Moreover, for any \(B' < B\), \(T_{<B'}(S) = T_{<B'}(X)\).

**Proof.** For any incomplete vertex \(v\) with \(d(v) < B\), as \(B < B\), by definition, \(v \in T(u)\) for some complete vertex \(u \in S\). Therefore \(\widehat{d}[u] = d(u) \leq d(v) < B\), so \(u \in X\) and thus \(v \in T(X^*)\).

For the second statement, it is clear that \(T_{<B'}(X) \subseteq T_{<B'}(S)\). For any \(v \in T_{<B'}(S)\), since \(d(v) < B' < B < B\), the shortest path to \(v\) passes through some vertex \(x \in S^*\). Now that \(\widehat{d}[x] = d(x) \leq d(v) < B'\), we have \(x \in X\) and \(v \in T_{<B'}(X)\).

Now we are ready to prove the correctness part of Lemma 3.1.

**Lemma 3.7.** We prove the correctness of Algorithm 3 by proving the following statement (the size of \(U\) is dealt with in Lemma 3.9), restated from Lemma 3.1: Given a level \(l \in [0, \lceil (\log n)/t \rceil]\), a bound \(B\) and a set of vertices \(S\) of size \(\leq 2^{lt}\), suppose that every incomplete vertex \(v\) with \(d(v) < B\) is in \(T(S^*)\).

Then, after running Algorithm 3, we have: \(U = T_{<B'}(S)\), and \(U\) is complete.

**Proof.** We prove by induction on \(l\). When \(l = 0\), since \(S = \{x\}\) is a singleton, \(x\) must be complete. Then clearly the classical Dijkstra's algorithm (Algorithm 2) finds the desired \(U = T_{<B'}(S)\) as required. Suppose correctness holds for \(l-1\), we prove that it holds for \(l\). Denote \(D_i\) as the set of vertices (keys) in \(\mathcal{D}\) just before the i-th iteration (at the end of the (i-1)-th iteration), and \(D_i^*\) as the set of complete vertices in \(D_i\) at that time. Next, we prove the following two propositions by induction on increasing order of i:

Immediately before the i-th iteration,

(a) Every incomplete vertex \(v\) with \(d(v) < B\) is in \(T_{[B'_{i-1},B)}(P)\).

(b) \(T_{[B'_{i-1},B)}(P) = T_{<B}(D_i) = T_{<B}(D_i^*)\);

In the base case i = 1, by Lemma 3.2, for every incomplete vertex \(v\) with \(d(v) < B\) (including \(v \in P\)), \(v \in T_{<B}(P^*)\). Then \(d(v) \geq \min_{x\in P^*} d(x) = \min_{x\in P^*} \widehat{d}[x] \geq B'_0\). Thus every such \(v\) is in \(T_{[B'_0,B)}(P)\) (actually \(T_{<B'_0}(P)\) is an empty set) and \(T_{[B'_0,B)}(P) = T_{<B}(P) = T_{<B}(P^*)\). Because \(D_1 = P\), the base case is proved.

Suppose both propositions hold for i. Then each incomplete vertex \(v\) with \(d(v) < B\) is in \(T_{[B'_{i-1},B)}(P) \subseteq T(D_i^*)\). By Lemma 3.3, the suppositions of Lemma 3.6 are met for \(X := S_i\), \(Y := D_i \setminus S_i\), and \(B := B_i\), so every incomplete vertex \(v\) with \(d(v) < B_i\) is in \(T(S_i^*)\); also note \(|S_i| \leq 2^{(l-1)t}\). By induction hypothesis on level \(l-1\), the i-th recursive call is correct and we have \(U_i = T_{<B'_i}(S_i)\) and is complete. Note that \(S_i\) includes all the vertices \(v\) in \(D_i\) such that \(\widehat{d}[v] < B'_i\) and that \(B'_i \leq B\). Thus by Lemma 3.6 and proposition (b) on case i, \(U_i = T_{<B'_i}(S_i) = T_{<B'_i}(D_i) = T_{[B'_{i-1},B'_i)}(P)\) and is complete (thus proving Remark 3.8).

Then, every incomplete vertex \(v\) with \(d(v) < B\) is in \(T_{[B'_{i-1},B)}(P) \setminus T_{[B'_{i-1},B'_i)}(P) = T_{[B'_i,B)}(P)\). Thus, we proved proposition (a) for the (i+1)-th iteration.

Now we prove proposition (b) for the (i+1)-th iteration. Since \(B'_i \geq B'_{i-1}\), from proposition (b) of the i-th iteration, we have \(T_{[B'_i,B)}(P) = T_{[B'_i,B)}(D_i) = T_{[B'_i,B)}(D_i^*)\). Suppose we can show that \(T_{[B'_i,B)}(D_i^*) \subseteq T_{<B}(D_{i+1}^*)\) and \(T_{<B}(D_{i+1}) \subseteq T_{[B'_i,B)}(D_i)\). By definition \(T_{<B}(D_{i+1}^*) \subseteq T_{<B}(D_{i+1})\), then

\[
T_{[B'_i,B)}(P) = T_{[B'_i,B)}(D_i^*) \subseteq T_{<B}(D_{i+1}^*) \subseteq T_{<B}(D_{i+1}) \subseteq T_{[B'_i,B)}(D_i) = T_{[B'_i,B)}(D_i^*),
\]

and by sandwiching, proposition (b) holds for (i+1). Thus it suffices to prove \(T_{[B'_i,B)}(D_i^*) \subseteq T_{<B}(D_{i+1}^*)\) and \(T_{<B}(D_{i+1}) \subseteq T_{[B'_i,B)}(D_i)\).

For any vertex \(y \in D_i^* \setminus D_{i+1}^*\), we have \(y \in S_i\). Note that vertices \(v\) of \(S_i\) with \(\widehat{d}[v] \geq B'_i\) are batch-prepended back to \(D_{i+1}\) on Line 21, so we have \(\widehat{d}[y] < B'_i\). Thus \(y \in U_i\) and is complete. For any vertex \(x \in T_{[B'_i,B)}(y)\), as \(x \notin U_i\), along the shortest path from \(y\) to \(x\), there is an edge \((u, v)\) with \(u \in U_i\) and \(v \notin U_i\). During relaxation, \(v\) is then complete and is added to \(D_{i+1}\), so \(x \in T_{[B'_i,B)}(v) \subseteq T_{<B}(D_{i+1}^*)\).

For any vertex \(v \in D_{i+1} \setminus D_i\), since \(v\) is added to \(D_{i+1}\), there is an edge \((u, v)\) with \(u \in U_i = T_{<B'_i}(D_i)\) and the relaxation of \((u, v)\) is valid (\(\widehat{d}[u] + w_{uv} \leq \widehat{d}[v]\)). Pick the last valid relaxation edge \((u, v)\) for \(v\). If \(v \in T(u)\), then \(v\) is complete, \(d(v) = \widehat{d}[v] \geq B'_i\), and \(v \in T_{[B'_i,B)}(D_i)\); if \(v\) is incomplete, then by proposition (a), \(v \in T_{[B'_i,B)}(P) = T_{[B'_i,B)}(D_i)\); or if \(v\) is complete but \(v \notin T(u)\), we have a contradiction because it implies that relaxation of \((u, v)\) is invalid.

Now that we have proven the propositions, we proceed to prove that the returned \(U = T_{<B'}(S)\) and that \(U\) is complete. Suppose there are \(q\) iterations. We have shown that every \(U_i = T_{[B'_{i-1},B'_i)}(P)\) and is complete, so \(U_i\)'s are also disjoint. By Lemma 3.2, \(W\) contains every vertex in \(T_{<B}(S \setminus P)\) (as they are not in \(T(P)\)) and they are complete; besides, all vertices \(v\) in \(W\) but not in \(T_{<B}(S \setminus P)\) with \(d(v) < B'_q\) are complete (because they are in \(T_{<B'_q}(P)\)). Therefore, \(\{x \in W : \widehat{d}[x] < B'_q\}\) contains every vertex in \(T_{<B'_q}(S \setminus P)\) and is complete. Thus finally \(U := (\bigcup_{i=1}^q U_i) \cup \{x \in W : \widehat{d}[x] < B'_q\}\) equals \(T_{<B'_q}(S)\) and is complete.

**Remark 3.8.** From the proof of Lemma 3.7, \(U_i = T_{[B'_{i-1},B'_i)}(P)\) and they are disjoint and complete. As a reminder, Lemma 3.6 and proposition (b) of Lemma 3.7 prove this.

### 3.4 Time Complexity Analysis

**Lemma 3.9.** Under the same conditions as in Lemma 3.7, where every incomplete vertex \(v\) with \(d(v) < B\) is in \(T_{<B}(S^*)\). After running Algorithm 3, we have \(|U| \leq 4k2^{lt}\). If \(B' < B\), then \(|U| \geq k2^{lt}\).

**Proof.** We can prove this by induction on the number of levels. The base case \(l = 0\) clearly holds. Suppose there are \(q\) iterations. Before the q-th iteration, \(|U| < k2^{lt}\). After the q-th iteration, the number of newly added vertices \(|U_q| \leq 4k2^{(l-1)t}\) (by Lemma 3.7, the assumptions for recursive calls are satisfied), and because \(|W| \leq k|S| \leq k2^{lt}\), we have \(|U| \leq 4k2^{lt}\). If \(\mathcal{D}\) is empty, the algorithm succeeds and quits with \(B' = B\). Otherwise, the algorithm ends partially because \(|U| \geq k2^{lt}\).

**Lemma 3.10.** Immediately before the i-th iteration of Algorithm 3, \(\min_{x\in \mathcal{D}} d(x) \geq B'_{i-1}\).

**Proof.** From the construction of \(\mathcal{D}\), immediately before the i-th iteration of Algorithm 3, \(\min_{v\in \mathcal{D}} \widehat{d}[v] \geq B'_{i-1}\). For \(v \in \mathcal{D}\), if \(v\) is complete, then \(d(v) = \widehat{d}[v] \geq B'_{i-1}\). If \(v\) is incomplete, by proposition (a) of Lemma 3.7, because \(v \in T_{[B'_{i-1},B)}(P)\), \(d(v) \geq B'_{i-1}\).

**Lemma 3.11.** Denote by \(\widetilde{U} \coloneqq T_{<B}(S)\) the set that contains every vertex \(v\) with \(d(v)< B\) and the shortest path to \(v\) visits some vertex of \(S\). After running Algorithm 3, \(\min \{|\widetilde{U}|, k|S|\} \leq |U|\) and \(|S| \leq |U|\).

**Proof.** If it is a successful execution, then \(S \subseteq \widetilde{U} = U\). If it is partial, then \(k|S| \leq k2^{lt} \leq |U|\).

For a vertex set \(U\) and two bounds \(c < d\), denote \(N^+(U) = \{(u,v) : u \in U\}\) as the set of outgoing edges from \(U\), and \(N_{[c,d]}^+(U) = \{(u,v) : u \in U \text{ and } d(u) + w_{uv} \in [c,d)\}\).

**Lemma 3.12 (Time Complexity).** Suppose a large constant \(C\) upper-bounds the sum of the constants hidden in the big-\(O\) notations in all previously mentioned running times: in find-pivots, in the data structure, in relaxation, and all other operations. Algorithm 3 solves the problem in Lemma 3.1 in time

\[
C(k + 2t / k)(l + 1)|U| + C(t + l\log k)|N_{[\min_{x\in S}d(x),B)}^+(U)|.
\]

With \(k = \lfloor \log^{1 / 3}(n)\rfloor\) and \(t = \lfloor \log^{2 / 3}(n)\rfloor\), calling the algorithm with \(l = \lceil (\log n) / t\rceil\), \(S = \{s\}\), \(B = \infty\) takes \(O(m\log^{2 / 3}n)\) time.

**Proof.** We prove by induction on the level \(l\). When \(l = 0\), the algorithm degenerates to the classical Dijkstra's algorithm (Algorithm 2) and takes time \(C|U|\log k\), so the base case is proved. Suppose the time complexity is correct for level \(l - 1\). Now we analyze the time complexity of level \(l\).

By Remark 3.5, each insertion takes amortized time \(C t\) (note that \(\log k < t\)); each batch prepended element takes amortized time \(C \log k\); each pulled term takes amortized constant time. But we may ignore Pull's running time because each pulled term must have been inserted/batch prepended, and the constant of Pull can be covered by \(C\) in those two operations.

By Remark 3.8, \(U_i\)'s are disjoint and \(\sum_{i\geq 1} |U_i| \leq |U|\).

Now we are ready to calculate total running time of Algorithm 3 on level \(l\) by listing all the steps.

By Lemma 3.2, the FindPivots step takes time \(C \cdot \min \{|\widetilde{U}|, k|S|\} k\) and \(|P| \leq \min \{|\widetilde{U}|/k, |S|\}\). Inserting \(P\) into \(\mathcal{D}\) takes time \(C|P|t\). And by Lemma 3.11, their time is bounded by \(C(k + t/k)|U|\).

In the i-th iteration, the sub-routine takes \(C(k + 2t / k)|U_i| + C(t + (l-1)\log k)|N_{[\min_{x\in S_i}d(x),B_i)}^+(U_i)|\) time by the induction hypothesis. Taking the sum, by Lemma 3.10, \(N_{[\min_{x\in S_i}d(x),B_i)}^+(U_i) \subseteq N_{[B_{i-1},B_i)}^+(U_i)\). Then the sum of time spent by all the sub-routines is bounded by

\[
C(k + 2t / k)|U| + \frac{\mathcal{N}_1}{C(t + (l-1)\log k)}\sum_{i\geq 1}|N_{[B_{i-1},B_i)}^+(U_i)|.
\]

In the following relaxation step, for each edge \((u,v)\) originated from \(U_i\), if \(\widehat{d}[u] + w_{uv} \in [B_i, B)\), they are directly inserted; if \(\widehat{d}[u] + w_{uv} \in [B_i', B_i)\), they are batch prepended. Again by Remark 3.8, all \(U_i\)'s are complete, so for the previous statements we can replace \(\widehat{d}[\cdot]\) with \(d(\cdot)\). Thus in total, it takes time

\[
C t \sum_{i\geq 1}|N_{[B_i,B)}^+(U_i)| + C(\log k)\sum_{i\geq 1}|N_{[B_i',B_i)}^+(U_i)|.
\]

Vertices in \(S_i\) were also batch prepended, and this step takes time \(O(\{x \in S_i : \widehat{d}[x] \in [B_i',B_i)\}|\log k)\). This operation takes non-zero time only if \(B_i' < B_i\), i.e., the i-th sub-routine is a partial execution. Thus in total this step takes time \(C\sum_{\text{partial } i}|S_i|\log k \leq (C|U|\log k)/k \leq C|U|t/k\).

Therefore, the total running time on the level \(l\) is

\[
C(k + 2t / k)(l + 1)|U| + \mathcal{N},
\]

where

\[
\mathcal{N} = \overbrace{C(t + (l-1)\log k)}^{\mathcal{N}_1 + \mathcal{N}_2}\sum_{i\geq 1}|N_{[B_{i-1},B_i)}^+(U_i)| + C t\sum_{i\geq 1}|N_{[B_i,B)}^+(U_i)| + C(\log k)\sum_{i\geq 1}|N_{[B_i',B_i)}^+(U_i)|.
\]

For \(\mathcal{N}_1 + \mathcal{N}_2\), because

\[
\sum_{i\geq 1}|N_{[B_{i-1},B_i)}^+(U_i)| + \sum_{i\geq 1}|N_{[B_i,B)}^+(U_i)| = \sum_{i\geq 1}|N_{[B_{i-1},B)}^+(U_i)| \leq |N_{[B_0,B)}^+(U)|,
\]

and \(B_0' \geq \min_{x\in S} d(x)\), it is bounded by \(C(t + (l-1)\log k)|N_{[\min_{x\in S}d(x),B)}^+(U)|\). \(\mathcal{N}_3\) is bounded by \(C(\log k)|N_{[B_0,B)}^+(U)| \leq C(\log k)|N_{[\min_{x\in S}d(x),B)}^+(U)|\).

Therefore \(\mathcal{N} \leq C(t + l\log k)|N_{[\min_{x\in S}d(x),B)}^+(U)|\).

## References

[BCF23] Karl Bringmann, Alejandro Cassis, and Nick Fischer. Negative-Weight Single-Source Shortest Paths in Near-Linear Time: Now Faster! . In 2023 IEEE 64th Annual Symposium on Foundations of Computer Science (FOCS), pages 515-538, Los Alamitos, CA, USA, November 2023. IEEE Computer Society.

[Bel58] Richard Bellman. On a routing problem. Quarterly of Applied Mathematics, 16:87-90, 1958.

[BFP+73] Manuel Blum, Robert W. Floyd, Vaughan Pratt, Ronald L. Rivest, and Robert E. Tarjan. Time bounds for selection. Journal of Computer and System Sciences, 7(4):448-461, 1973.

[BNWN22] Aaron Bernstein, Danupon Nanongkai, and Christian Wulff-Nilsen. Negative-weight single-source shortest paths in near-linear time. In 2022 IEEE 63rd Annual Symposium on Foundations of Computer Science (FOCS), pages 600-611, 2022.

[CKL+22] Li Chen, Rasmus Kyng, Yang P. Liu, Richard Peng, Maximilian Probst Gutenberg, and Sushant Sachdeva. Maximum flow and minimum-cost flow in almost-linear time. In 2022 IEEE 63rd Annual Symposium on Foundations of Computer Science (FOCS), pages 612-623, 2022.

[CKT+16] Shiri Chechik, Haim Kaplan, Mikkel Thorup, Or Zamir, and Uri Zwick. Bottleneck paths and trees and deterministic graphical games. In Nicolas Ollinger and Heribert Vollmer, editors, STACS, volume 47 of LIPIcs, pages 27:1-27:13. Schloss Dagstuhl - Leibniz-Zentrum für Informatik, 2016.

[DGST88] James R. Driscoll, Harold N. Gabow, Ruth Shriraman, and Robert E. Tarjan. Relaxed heaps: An alternative to Fibonacci heaps with applications to parallel computation. Commun. ACM, 31(11):1343-1354, November 1988.

[Dij59] E. W. Dijkstra. A note on two problems in connexion with graphs. Numerische Mathematik, 1:269-271, 1959.

[DLWX18] Ran Duan, Kaifeng Lyu, Hongxun Wu, and Yuanhang Xie. Single-source bottleneck path algorithm faster than sorting for sparse graphs. CoRR, abs/1808.10658, 2018.

[DMSY23] R. Duan, J. Mao, X. Shu, and L. Yin. A randomized algorithm for single-source shortest path on undirected real-weighted graphs. In 2023 IEEE 64th Annual Symposium on Foundations of Computer Science (FOCS), pages 484-492, Los Alamitos, CA, USA, November 2023. IEEE Computer Society.

[Fin24] Jeremy T. Fineman. Single-source shortest paths with negative real weights in \(\tilde{O}(mn^{8/9})\) time. In Proceedings of the 56th Annual ACM Symposium on Theory of Computing, STOC 2024, page 3-14, New York, NY, USA, 2024. Association for Computing Machinery.

[Fre83] Greg N. Frederickson. Data structures for on-line updating of minimum spanning trees. In Proceedings of the Fifteenth Annual ACM Symposium on Theory of Computing, STOC '83, page 252-257, New York, NY, USA, 1983. Association for Computing Machinery.

[FT87] M. L. Fredman and R. E. Tarjan. Fibonacci heaps and their uses in improved network optimization algorithms. JACM, 34(3):596-615, 1987.

[FW93] Michael L. Fredman and Dan E. Willard. Surpassing the information theoretic bound with fusion trees. Journal of Computer and System Sciences, 47(3):424-436, 1993.

[FW94] Michael L. Fredman and Dan E. Willard. Trans-dichotomous algorithms for minimum spanning trees and shortest paths. Journal of Computer and System Sciences, 48(3):533-551, 1994.

[GS78] Leo J. Guibas and Robert Sedgewick. A dichromatic framework for balanced trees. In 19th Annual Symposium on Foundations of Computer Science (sfcs 1978), pages 8-21, 1978.

[GT88] Harold N Gabow and Robert E Tarjan. Algorithms for two bottleneck optimization problems. Journal of Algorithms, 9(3):411-417, 1988.

[Hag00] Torben Hagerup. Improved shortest paths on the word RAM. In Ugo Montanari, José D. P. Rolim, and Emo Welzl, editors, Automata, Languages and Programming, pages 61-72, Berlin, Heidelberg, 2000. Springer Berlin Heidelberg.

[HHR+24] Bernhard Haeupler, Richard Hladík, Václav Rozhoň, Robert E. Tarjan, and Jakub Tětek. Universal optimality of Dijkstra via beyond-worst-case heaps. In 2024 IEEE 65th Annual Symposium on Foundations of Computer Science (FOCS), 2024.

[HJQ24] Yufan Huang, Peter Jin, and Kent Quanrud. Faster single-source shortest paths with negative real weights via proper hop distance, 2024.

[KKT95] David R. Karger, Philip N. Klein, and Robert E. Tarjan. A randomized linear-time algorithm to find minimum spanning trees. J. ACM, 42(2):321-328, March 1995.

[PR05] Seth Pettie and Vijaya Ramachandran. A shortest path algorithm for real-weighted undirected graphs. SIAM Journal on Computing, 34(6):1398-1431, 2005.

[Ram96] Rajeev Raman. Priority queues: Small, monotone and trans-dichotomous. In Proceedings of the Fourth Annual European Symposium on Algorithms, ESA '96, page 121-137, Berlin, Heidelberg, 1996. Springer-Verlag.

[Ram97] Rajeev Raman. Recent results on the single-source shortest paths problem. SIGACT News, 28(2):81-87, June 1997.

[Tho99] Mikkel Thorup. Undirected single-source shortest paths with positive integer weights in linear time. J. ACM, 46(3):362-394, May 1999.

[Tho00a] Mikkel Thorup. Floats, integers, and single source shortest paths. J. Algorithms, 35(2):189-201, May 2000.

[Tho00b] Mikkel Thorup. On RAM priority queues. SIAM Journal on Computing, 30(1):86-109, 2000.

[Tho04] Mikkel Thorup. Integer priority queues with decrease key in constant time and the single source shortest paths problem. Journal of Computer and System Sciences, 69(3):330-353, 2004. Special Issue on STOC 2003.

[Wil64] J. W. J. Williams. Algorithm 232: Heapsort. Communications of the ACM, 7(6):347-348, 1964.

[Wil10] Virginia Vassilevska Williams. Nondecreasing paths in a weighted graph or: How to optimally read a train schedule. ACM Trans. Algorithms, 6(4), September 2010.

[Yao75] Andrew Chi-Chih Yao. An \(O(|E|\log \log |V|)\) algorithm for finding minimum spanning trees. Information Processing Letters, 4(1):21-23, 1975.