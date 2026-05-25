# 协作流程速查

> 给:repo owner(一次性配置)+ partner(日常 PR)。5 min 读完。

---

## 一、一次性配置(owner 做,partner 跳过)

### 1.1 开 branch protection — 必做

路径:**GitHub repo 主页 → Settings → 左侧 Branches → Add branch protection rule**

| 选项 | 设置 | 为啥 |
|---|---|---|
| Branch name pattern | `main` | |
| ☑ Require a pull request before merging | **开** | 不能直推 main |
| └ Require approvals | **0** | 普通文件 PR 不卡 reviewer,自己 merge |
| └ ☑ Require review from Code Owners | **开** | **只对契约文件强制 cross-check**(见 § 1.2 CODEOWNERS) |
| ☑ Restrict force pushes | **开** | 防止 main 被力推覆盖(代价:以后不能再 squash root commit) |
| ☐ Require status checks | 关 | 暂无 CI |

点 **Create**,完事。

> ⚠ 开 protection 后,**之前那种本地 squash + force push 重写历史的操作就不能再做了**。所以分工 / 骨架定下来再开。

### 1.2 建 CODEOWNERS — 分工敲定后

`.github/CODEOWNERS`(4 个核心受保护文件,改坏全员炸):
```
src/models.py         @lele @partnerA @partnerB
config/prompts.yaml   @lele @partnerA @partnerB
config/watchlist.yaml @lele @partnerA @partnerB
scripts/daily_run.py  @lele @partnerA @partnerB
```

**配合 § 1.1 的 "Require review from Code Owners" 一起开**:
- 普通文件(不在 CODEOWNERS 里)→ approvals: 0,自己 merge 不卡
- **上面 4 个核心文件** → 必须等至少 1 个 Code Owner approve 才能 merge,自动挡门
- GitHub 默认禁 self-approve,所以改核心文件的 PR 一定要 cross-check,绕不过去

> `pyproject.toml` **不入** CODEOWNERS —— PR 模板第 4 问已经覆盖,过度上锁拖后腿。

---

## 二、partner 日常工作流

### 2.1 第一次 clone

```powershell
git clone https://github.com/lelelelelelelelelelelelele/rednote_monitor.git
cd rednote_monitor
uv sync                                                         # 装依赖
# 按 README 起 xiaohongshu-mcp(需要单独装,见 README § 2)
```

### 2.2 每次开干

```powershell
git checkout main
git pull                                                        # 拉别人的改动
git checkout -b feat/m2-sentiment                               # 起自己的分支
# ... 写代码 ...
git add src/sentiment/engine.py
git commit -m "M2: first happy path"
git push -u origin feat/m2-sentiment
```

### 2.3 发 PR

1. push 完去 **GitHub repo 首页**
2. 顶部会有一条**黄色横条** "Compare & pull request",点它
3. 描述框**自动加载 PR 模板**,填完 4 个问题
4. 点 **Create pull request**
5. PR 页面下方点 **Merge pull request**(approvals: 0,不卡)
6. 回本地:
   ```powershell
   git checkout main
   git pull
   git branch -d feat/m2-sentiment                              # 删本地分支
   ```

---

## 三、特殊流程:改 4 个核心文件

下面 4 个改坏会让别人模块全炸 —— 走 cross-check 流程:

- `src/models.py` —— 数据契约
- `config/prompts.yaml` —— LLM prompt
- `config/watchlist.yaml` —— ticker 清单
- `scripts/daily_run.py` —— 调度入口

流程:

1. **先在群里 +1** —— 说要改啥、为啥
2. 等大家无异议再动手
3. 走 PR 流程时 CODEOWNERS 会**自动 @ 全员**
4. **必须等至少 1 个 Code Owner approve 才能 merge**(branch protection 强制,绕不过去)
5. 因为 GitHub 禁 self-approve,你必须让别人 approve,**强制 cross-check**

---

## 四、常见坑

| 现象 | 原因 / 处理 |
|---|---|
| `git push origin main` 被拒,提示 *protected branch* | 你想直推 main 了 → 起 feature 分支 `git checkout -b feat/xxx` 再推 |
| PR 描述框没自动加载模板 | 文件名拼错,只能叫 `.github/pull_request_template.md` 或 `.github/PULL_REQUEST_TEMPLATE.md` |
| CODEOWNERS 不 @ 人 | 文件名必须是 `.github/CODEOWNERS`(无扩展名);username 拼错也不会 ping |
| `git pull` 后 merge 冲突 | 在自己分支 `git fetch && git rebase origin/main`,解冲突后 `git push --force-with-lease`(只推自己分支,不是 main) |
| 分支干了一周,main 跑远了 | 每 2-3 天 rebase 一次 main 防漂移(同上命令) |
