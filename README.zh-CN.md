# skillkit

[English](README.md) · [Español](README.es.md) · **中文** · [Deutsch](README.de.md) · [Français](README.fr.md)

一个**可复用脚本**库，供 Agent Skills 调用以操作其沙箱环境。每个脚本都是自包含的命令行工具，
可复制到任意 skill 的 `scripts/` 目录中，或作为共享依赖被引用。

状态：已实现 13 个脚本以确立设计模式，并附带可复制该模式的模板与生成器、一套冒烟测试，
以及一个包含 **23 个类别、共 338 个脚本** 的索引（`catalog.json`，其余标记为 `planned`，
可分批实现）。

## 目录结构

```
skillkit/
├── README.md              # 英文（默认） · 另有 .es .zh-CN .de .fr
├── catalog.json           # 机器可读索引（由 build_catalog.py 生成）
├── build_catalog.py       # 重新生成并校验 catalog.json
├── new-script             # 从模板生成新脚本
├── templates/             # template.bash 与 template.py（固化的模式）
├── tests/run_tests.sh     # 仓库冒烟测试
├── fs/                    # 文件与查找                    → find-files ✓
├── text/                  # 文本与结构化数据
├── docs/                  # 文档与媒体转换
├── containers/            # docker / k8s / openshift       → k8s-get, k8s-rbac-check ✓
├── web/                   # 下载与抓取                     → web-to-markdown ✓
├── net/                   # 网络与诊断
├── vcs/                   # git / mercurial / svn
├── forges/                # github / gitlab / 等           → gh-issue ✓
├── pkg/                   # 包与依赖
├── data/                  # 数据库与数据                   → xlsx-tool ✓
├── crypto/                # 编码 / 加密 / 机密
├── proc/                  # 系统、进程、本地编排
├── quality/               # 测试、lint、质量
├── api/                   # 通用 HTTP/API 客户端           → oauth-token ✓
├── cloud/                 # 云与基础设施                   → coolify-api ✓
├── ai/                    # AI 与大语言模型                → llm-call ✓
├── obs/                   # 可观测性
├── msg/                   # 消息与通知
├── store/                 # 对象存储与备份
├── orch/                  # 工作流编排器                   → kestra-flow ✓
├── validate/              # 模式校验与策略                 → json-schema-validate ✓
├── sec/                   # 安全与供应链                   → secret-scan, container-scan ✓
└── bench/                 # 性能
```

## 设计约定

1. **输出**：数据写入 `stdout`；提示与错误写入 `stderr`。
2. **`--json`**：每个返回数据的脚本都提供结构化输出。
3. **`--help` 始终可用**：即使缺少基础工具或依赖也能正常显示。
   正因如此，在 Python 中依赖的导入放在 `main()` 内部。
4. **检查顺序**：先校验参数（退出码 2），*再*检查依赖（退出码 127）。
   无论工具是否存在，用法错误的报告方式都一致。
5. **内联依赖**（Python）：PEP 723 + `uv run`；无需预先安装。
6. **`--dry-run`**：在所有写入或删除操作中，打印将要执行的确切命令，
   且**既不需要该工具也不需要凭据**（通用预览）。
7. **退出码**：`0` 成功 · `1` 运行错误 · `2` 用法错误 ·
   `127` 缺少工具（· `3` 提取类脚本的“无结果”）。
8. **不硬编码机密**：凭据与令牌一律来自环境变量。
9. **单一职责**：每个脚本只做好一件事，并可组合使用。

## 已实现的脚本

**`fs/find-files`** —— 按名称、类型、扩展名、日期或大小查找文件。
```bash
find-files src --ext py --newer-than 7
find-files . --type d --name 'test*' --json
```

**`web/web-to-markdown`** —— 下载某个 URL 并将其主要内容提取为 Markdown。
PEP 723（需要 `uv`）；`--timeout` 可配置。若直接下载失败，会改用系统 TLS 信任库和
环境代理重试，因此可在带 TLS 检测的企业代理（Fortinet、Zscaler 等）后运行。
```bash
uv run web/web-to-markdown https://example.com/post --json --timeout 20
```

**`containers/k8s-get`** —— 列出或描述 Kubernetes/OpenShift 资源。
连通性探测使用 `/version`（任何已认证用户都可读），因此在 `cluster-info` 会失败的
受限 RBAC 集群中仍可工作。
```bash
k8s-get pods -n falcone -l app=api --wide
KUBECTL=oc k8s-get deployment api -n falcone --json
```

**`forges/gh-issue`** —— 管理 GitHub issue。令牌来自 `GH_TOKEN`/`GITHUB_TOKEN`；
`--dry-run` 会打印确切命令，无需 `gh` 或令牌。
```bash
gh-issue list -R my-org/falcone -s open -l tenant-isolation --json
gh-issue create -R my-org/falcone -t "租户间泄漏" -b "详情…" --dry-run
```

**`validate/json-schema-validate`** —— 针对 JSON Schema 校验 JSON/YAML（支持多文档）。
用于在使用前校验智能体的结构化输出；接受 `-` 从 stdin 读取。PEP 723（需要 `uv`）。
```bash
uv run validate/json-schema-validate ard.json --schema schemas/ard.schema.yaml
kestra-flow logs $EXEC | uv run validate/json-schema-validate - --schema out.json
```

**`ai/llm-call`** —— 调用某个 LLM 端点并返回响应。仅用标准库（无需安装）、使用系统
TLS 信任、兼容 OpenAI 与 Anthropic 两种方言、对 429/5xx 自动重试。私有端点
（vLLM、Ollama、LiteLLM）与公有 API 同样适用。通过
`LLM_BASE_URL`/`LLM_MODEL`/`LLM_API_KEY` 配置。
```bash
echo "总结这份 BRD" | llm-call --system "你是一名架构师" --model qwen2 \
    --base-url http://vllm.internal:8000/v1 --json
```

**`orch/kestra-flow`** —— 通过 REST API 校验、部署并执行 Kestra 流程。
`--wait` 会跟踪执行直至终态；`--dry-run` 无需服务器即可显示请求。
认证方式为令牌（EE/Cloud）或用户名/密码（OSS）。
```bash
kestra-flow validate flows/ard-pipeline.yaml
kestra-flow execute prod brd-to-ard --input brd=s3://bucket/brd.xlsx --wait
```

**`data/xlsx-tool`** —— 检查并转换 Excel（`info`/`sheets`/`csv`/`json`）。
`--sheet` 可用从 1 开始的序号或表名指定。适用于摄取 ARD 流水线中的 Excel BRD。
PEP 723（需要 `uv`）。
```bash
uv run data/xlsx-tool info brd.xlsx --json
uv run data/xlsx-tool json brd.xlsx --sheet Requirements
```

**`containers/k8s-rbac-check`** —— 在 Kubernetes/OpenShift 上审计 RBAC 权限
（`auth can-i`）。支持多个动作、模拟用户或 ServiceAccount，以及 `--list`。
只读。OpenShift 使用 `KUBECTL=oc`。
```bash
k8s-rbac-check get,list,watch pods -n falcone --json
k8s-rbac-check delete secrets -n other-tenant --sa falcone:api   # 隔离是否正常？
```

**`api/oauth-token`** —— 获取并打印 OAuth2 令牌（可组合）。支持
`client_credentials`、`password`、`refresh_token` 与 `device`（带轮询的设备流）等授权。
适用于 Cognito、Keycloak、Auth0 等；`--auth-basic` 以 Basic 头发送凭据；
`--dry-run` 会显示请求并对机密做掩码。
```bash
TOKEN="$(oauth-token client_credentials --scope 'api/read' --auth-basic)"
oauth-token device --scope 'openid profile' --json
```

**`cloud/coolify-api`** —— 通过 v4 API 操作 Coolify：列出应用、服务与数据库，并触发
`deploy`/`start`/`stop`/`restart`。写操作支持无服务器的 `--dry-run`。
通过 `COOLIFY_URL`/`COOLIFY_TOKEN` 配置。
```bash
coolify-api apps --json
coolify-api deploy 9b7c... --force
```

**`sec/secret-scan`** —— 使用 gitleaks（首选）或 trufflehog 扫描泄漏的机密，
自动检测可用工具。默认扫描工作区，或用 `--git-history` 扫描完整历史。
若有发现则返回退出码 1（适合 CI）。
```bash
secret-scan . --git-history --json
secret-scan src --tool trufflehog --only-verified
```

**`sec/container-scan`** —— 使用 trivy（首选）或 grype 扫描镜像或 `--fs` 中的 CVE，
自动检测可用工具。用 `--severity` 设定阈值；若发现指定级别的漏洞则退出码为 1。
```bash
container-scan registry.local/falcone-api:latest --severity CRITICAL,HIGH
container-scan --fs . --ignore-unfixed --json
```

## 测试

```bash
bash tests/run_tests.sh
```

检查语法、无依赖时的帮助信息、用法错误（退出码 2）、功能行为（带 `--json` 的查找、
无凭据的 `--dry-run`、从模板生成）以及目录索引的一致性。它既不需要 `gh` 也不需要
`kubectl`：恰恰用于验证缺少这些工具时脚本能够优雅降级。

## 如何新增脚本

```bash
./new-script text json-query bash -d "查询/转换 JSON" -b jq
```

1. 在生成模板的第 3 节实现逻辑。
2. 在 `build_catalog.py` 的 `SCRIPTS` 中添加条目（完成后再加入 `IMPLEMENTED`）。
3. 重新生成索引：`python3 build_catalog.py`（校验 id、类别与文件）。
4. 运行测试套件：`bash tests/run_tests.sh`。

## skill 如何使用它

在 `SKILL.md` 中指向该脚本并说明何时使用；代码本身不进入上下文（渐进式披露）：

```markdown
## 将网页转换为 Markdown
当你需要某个 URL 的纯净内容时，运行：

    uv run scripts/web-to-markdown <URL> --json

返回一个包含 `title`、`author`、`date` 与 `markdown` 的 JSON 对象。
```

引入该库的两种方式：
- **复制**单个脚本到 skill 的 `scripts/` 中（自包含）。
- **引用**本仓库作为共享依赖（例如 git submodule）。

## 完整索引

`catalog.json` 列出全部 338 个脚本，包含类别、基础工具、状态，以及（对已实现的脚本）
参数、用法示例与备注。`build_catalog.py` 会重新生成它，并在出现重复 id、无效类别，
或标记为已实现却在磁盘上不存在的脚本时**给出清晰的报错**。

## 备注

- 解压后若执行位未保留：`chmod +x <script>`。
- 带 PEP 723 头部的 Python 脚本需要 `uv`（https://docs.astral.sh/uv/）。
- `KUBECTL=oc` 可在 OpenShift 上复用 `containers/` 中的脚本。
- 在公开发布仓库前，请添加许可证（Apache-2.0 或 MIT 与 skills 生态较为契合）。
